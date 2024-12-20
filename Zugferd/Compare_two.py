import fitz
from Extract_pdf import extract_invoice_data_from_pdf
from Extract_xml import parse_xml
from Update_xml import update_xml_tree


def collect_attributes(obj, prefix=""):
    collected = {}

    if hasattr(obj, "__dataclass_fields__"):
        for field in obj.__dataclass_fields__:
            value = getattr(obj, field)
            collected.update(collect_attributes(value, prefix=f"{prefix}{field}."))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            collected.update(collect_attributes(item, prefix=f"{prefix}[{i}]."))
    else:
        collected[prefix[:-1]] = obj

    return collected

def check_difference(rechnung1, rechnung2):
    unterschiede = {}
    for key, value in rechnung1.items():
        if rechnung1[key] != rechnung2[key]:
            unterschiede[key] = rechnung2[key]
            print(f"{rechnung1[key]} vs {rechnung2[key]}")
    return unterschiede

def change_difference(collected, unterschiede):
    for key, value in unterschiede.items():
        if key in collected:
            collected[key] = value
    return collected

def generate_xpdf(pdf_path, new_root, output_path):
    doc = fitz.open(pdf_path)
    doc.embfile_del(0)
    new_xml = new_root
    doc.embfile_add("factur-x.xml", new_xml, desc="ZUGFeRD XML")
    doc.save(output_path)

def extract(pdf_path):
    doc = fitz.open(pdf_path)

    for i in range(doc.embfile_count()):
        file_info = doc.embfile_info(i)
        file_name = file_info["name"]
        print(f"Extrahiere: {file_name}")

        file_data = doc.embfile_get(i)
        return file_data

def main(pdf_path, upload_path):
    xml = extract(pdf_path)
    invoice1 = parse_xml(xml)
    invoice2 = extract_invoice_data_from_pdf(pdf_path)
    rechnung1 = collect_attributes(invoice1)
    rechnung2 = collect_attributes(invoice2)
    unterschiede = check_difference(rechnung1, rechnung2)
    user_input = input("Es wurden Unterschiede gefunden. Möchten Sie diese ändern und eine neue PDF erstellen? (ja/nein): ").strip().lower()

    if user_input == "ja":
        change_difference(rechnung1, unterschiede)
        root = update_xml_tree(xml, rechnung2)
        generate_xpdf(pdf_path, root, upload_path)
        print("Die Änderungen wurde übernommen und ein neue PDF wurde erstellt!")
    elif user_input == "nein":
        print("Änderungen nicht übernommen. Der prozess wurde abgebrochen")
        return
    else:
        print("Ungültige Eingabe. Cioa!!!")
        return
    # print(rechnung1[16])
    # print(check_difference(rechnung1, rechnung2))
    # print(change_difference(rechnung1, check_difference(rechnung1, rechnung2)))
    # print(rechnung1)
    # print(update_xml_tree(xml, rechnung2))
# xml = extract(r"C:\Users\Roman\Downloads\validator\validator\Rechnung-M_4291_a3_x.pdf")
# invoice1 = parse_xml(xml)
# invoice2 = extract_invoice_data_from_pdf(r"C:\Users\Roman\Downloads\validator\validator\Rechnung-M_4291_a3_x.pdf")
# rechnung1 = collect_attributes(invoice1)
# rechnung2 = collect_attributes(invoice2)
# unterschiede = check_difference(rechnung1, rechnung2)
# change_difference(rechnung1, unterschiede)
# print(rechnung1)
# print(rechnung2)
# print(unterschiede)



#main(r"C:\Users\Roman\Downloads\validator\validator\Rechnung-M_4291_a3_x.pdf", r"C:\Users\Roman\Downloads\validator\validator\newpdf_a3_x.pdf")
#iterate_dataclass(invoice2)

# if invoice1 == invoice2:
#     print("Die Rechnungen sind identisch.")
# else:
#     print("Die Rechnungen unterscheiden sich.")
#
# print(check_difference(invoice1, invoice2))
#
# for i in range(len(invoice1.positions)):
#     print(f"{invoice1.positions[i]}")
# for key, value in invoice2:
#     print(f"{key}: {value}")