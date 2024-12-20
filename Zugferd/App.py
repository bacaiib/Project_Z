import os
from flask import Flask, request, render_template
from Compare_two import*
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
DOWNLOADS_FOLDER = os.path.join(STATIC_FOLDER, 'downloads')
app = Flask(__name__, static_folder=STATIC_FOLDER)

if not os.path.exists(DOWNLOADS_FOLDER):
    os.makedirs(DOWNLOADS_FOLDER)
@app.route('/')
def upload_form():
    return render_template('upload.html')

global_data = {}
@app.route('/process', methods=['POST'])
def process_file():
    # output_buffer = io.StringIO()
    # sys.stdout = output_buffer
    uploaded_file = request.files.get('pdf')
    #output_path = r"C:\Users\Roman\Downloads\validator\validator" #request.form.get('output_path')
    #new_name = request.form.get('new_name')

    if not uploaded_file: #or not output_path:
        return "Bitte eine Datei hochladen und einen Speicherpfad angeben.", 400

    # output_dir = os.path.join('static', 'downloads')
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)

    #output_dir = os.path.dirname(output_path)
    # try:
    #     if not os.path.exists(output_dir):
    #         os.makedirs(output_dir)
    #     if not os.access(output_dir, os.W_OK):
    #         return f"Fehler: Keine Schreibrechte für {output_dir}", 400
    # except Exception as e:
    #     return f"Fehler bei der Erstellung des Ausgabe-Verzeichnisses: {str(e)}", 500

    temp_path = os.path.join('./uploads', uploaded_file.filename)
    if not os.path.exists('./uploads'):
        os.makedirs('./uploads')
    uploaded_file.save(temp_path)

    #output_path = os.path.join(DOWNLOADS_FOLDER, new_name)
    # upload_folder = "./uploads"
    # if not os.path.exists(upload_folder):
    #     os.makedirs(upload_folder)
    #
    # temp_path = f"./uploads/{uploaded_file.filename}"
    # uploaded_file.save(temp_path)

    xml = extract(temp_path)
    invoice1 = parse_xml(xml)
    invoice2 = extract_invoice_data_from_pdf(temp_path)
    invoice_1 = collect_attributes(invoice1)
    invoice_2 = collect_attributes(invoice2)
    differences = check_difference(invoice_1, invoice_2)

    global_data['temp_path'] = temp_path
    global_data['xml'] = xml
    global_data['invoice_1'] = invoice_1
    global_data['invoice_2'] = invoice_2
    global_data['differences'] = differences

    # prepared_differences = [
    #     {
    #         "key": key,
    #         "value_1": invoice_1[key],  # Wert aus invoice_1
    #         "value_2": invoice_2[key]  # Wert aus invoice_2
    #     }
    #     for key in differences.keys()
    # ]

    return render_template('differences.html', differences=differences, invoice_1=invoice_1, invoice_2=invoice_2)

@app.route('/confirm', methods=['POST'])
def confirm_changes():
    decision = request.form.get('decision')
    new_name = request.form.get('new_name')
    if decision == "ja":
        try:
            if not new_name.endswith('.pdf'):
                return "Der Dateiname muss mit '.pdf' enden."

            output_path = os.path.join(DOWNLOADS_FOLDER, new_name)

            if os.path.exists(output_path):
                os.remove(output_path)

            updated_data = change_difference(global_data['invoice_1'], global_data['differences'])
            root = update_xml_tree(global_data['xml'], updated_data)
            generate_xpdf(global_data['temp_path'], root, output_path=output_path)

            print(f"Datei wurde gespeichert unter: {output_path}")

        except Exception as e:
            return f"Fehler beim Speichern der Datei: {str(e)}", 500

        download_link = f"/static/downloads/{new_name}"
        print(f"Generierter Download-Link: {download_link}")
        return f"Datei verarbeitet. <a href='{download_link}' download>Download</a>"

    else:
        return "Änderungen verworfen"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

