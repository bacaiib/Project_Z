import xml.etree.ElementTree as eT
from datetime import datetime

from invoicemuster import Invoice, Company, Rechnungsposition


def parse_xml(xml_data):
    root = eT.fromstring(xml_data)

    namespaces = {
        "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
        "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
        "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100"
    }

    rechnungsnummer = root.find(".//rsm:ExchangedDocument/ram:ID", namespaces).text
    datum_raw = root.find(".//udt:DateTimeString", namespaces).text
    datum = datetime.strptime(datum_raw, "%Y%m%d").strftime("%d.%m.%Y")

    company_node = root.find(".//ram:BuyerTradeParty", namespaces)
    company_name = company_node.find("ram:Name", namespaces).text
    address_node = company_node.find("ram:PostalTradeAddress", namespaces)
    street = address_node.find("ram:LineOne", namespaces).text
    zip_code = address_node.find("ram:PostcodeCode", namespaces).text
    city = address_node.find("ram:CityName", namespaces).text

    company = Company(
        name=company_name,
        street=street,
        zip_code=zip_code,
        city=city
    )

    positions = []
    position_nodes = root.findall(".//ram:IncludedSupplyChainTradeLineItem", namespaces)
    for position_node in position_nodes:
        bezeichnung = position_node.find(".//ram:Name", namespaces).text
        anzahl = float(position_node.find(".//ram:BilledQuantity", namespaces).text)
        einzelpreis = float(position_node.find(".//ram:GrossPriceProductTradePrice/ram:ChargeAmount", namespaces).text)
        gesamtpreis = float(position_node.find(".//ram:LineTotalAmount", namespaces).text)
        positions.append(Rechnungsposition(bezeichnung, anzahl, einzelpreis, gesamtpreis))

    zwischensumme = float(root.find(".//ram:TaxBasisTotalAmount", namespaces).text)
    mwst = float(root.find(".//ram:TaxTotalAmount", namespaces).text)
    summe = float(root.find(".//ram:GrandTotalAmount", namespaces).text)

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

#print(parse_xml('factur-x.xml'))