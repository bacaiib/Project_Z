import re

import pdfplumber

from invoicemuster import Invoice, Company, Rechnungsposition


def extract_invoice_data_from_pdf(pdf_path: str) -> Invoice:
    # Open the PDF using pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        # Extract text from the first page (assuming it's a one-page invoice)
        page = pdf.pages[0]
        text = page.extract_text()

    # Extract Rechnungsnummer
    rechnungsnummer = re.search(r"M-\d{4,}", text)
    rechnungsnummer = rechnungsnummer.group() if rechnungsnummer else None

    # Extract Date (Datum)
    datum = re.search(r"\d{2}.\d{2}.\d{4}", text)
    datum = datum.group() if datum else None

    # Extract Company Information
    company_match = re.search(r"(.+)\n(.+)\n(\d{5}) (.+)", text)
    if company_match:
        company_name = company_match.group(1)
        street = company_match.group(2)
        zip_code = company_match.group(3)
        city = company_match.group(4)
    else:
        company_name = street = zip_code = city = None

    company = Company(
        name=company_name,
        street=street,
        zip_code=zip_code,
        city=city
    )

    # Parse position items
    positions = []
    position_lines = re.findall(r"(.+?)\s+(\d+)\s+([\d,]+)e\s+([\d,]+)e", text)
    for line in position_lines:
        bezeichnung, anzahl, einzelpreis, gesamtpreis = line
        positions.append(
            Rechnungsposition(
                bezeichnung=bezeichnung,
                anzahl=float(anzahl.replace(",", ".")),
                einzelpreis=float(einzelpreis.replace(",", ".")),
                gesamtpreis=float(gesamtpreis.replace(",", "."))
            )
        )

    # Extract Zwischensumme, Mwst, Summe
    zwischensumme = re.search(r"Zwischensumme\s+\(?netto\)?\s+([\d,]+)e", text)
    mwst = re.search(r"MwSt\.\s+\(?19\s?%\)?\s+([\d,]+)e", text)
    summe = re.search(r"Summe\s+([\d,]+)e", text)

    zwischensumme = float(zwischensumme.group(1).replace(",", ".")) if zwischensumme else None
    mwst = float(mwst.group(1).replace(",", ".")) if mwst else None
    summe = float(summe.group(1).replace(",", ".")) if summe else None

    # Create the Invoice dataclass instance
    invoice = Invoice(
        rechnungsnummer=rechnungsnummer,
        datum=datum,
        company=company,
        positions=positions,
        zwischensumme=zwischensumme,
        mwst=mwst,
        summe=summe
    )

    return invoice

#print(extract_invoice_data_from_pdf('Rechnung-M_4291.pdf'))

