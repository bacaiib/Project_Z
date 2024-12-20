import xml.etree.ElementTree as eT
from datetime import datetime


def update_xml_tree(file_data, collected):
    root = eT.fromstring(file_data)

    namespaces = {
        "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
        "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
        "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100"
    }

    root.find(".//rsm:ExchangedDocument/ram:ID", namespaces).text = collected["rechnungsnummer"]

    datum_raw = datetime.strptime(collected["datum"], "%d.%m.%Y").strftime("%Y%m%d")
    root.find(".//udt:DateTimeString", namespaces).text = datum_raw

    company_node = root.find(".//ram:BuyerTradeParty", namespaces)
    company_node.find("ram:Name", namespaces).text = collected["company.name"]

    address_node = company_node.find("ram:PostalTradeAddress", namespaces)
    address_node.find("ram:LineOne", namespaces).text = collected["company.street"]
    address_node.find("ram:PostcodeCode", namespaces).text = collected["company.zip_code"]
    address_node.find("ram:CityName", namespaces).text = collected["company.city"]

    position_nodes = root.findall(".//ram:IncludedSupplyChainTradeLineItem", namespaces)

    for i, position_node in enumerate(position_nodes):
            position_node.find(".//ram:Name", namespaces).text = str(collected[f"positions.[{i}].bezeichnung"])
            position_node.find(".//ram:BilledQuantity", namespaces).text = str(collected[f"positions.[{i}].anzahl"])
            position_node.find(".//ram:GrossPriceProductTradePrice/ram:ChargeAmount", namespaces).text = str(collected[f"positions.[{i}].einzelpreis"])
            position_node.find(".//ram:LineTotalAmount", namespaces).text = str(collected[f"positions.[{i}].gesamtpreis"])

    root.find(".//ram:TaxBasisTotalAmount", namespaces).text = str(collected["zwischensumme"])
    root.find(".//ram:TaxTotalAmount", namespaces).text = str(collected["mwst"])
    root.find(".//ram:GrandTotalAmount", namespaces).text = str(collected["summe"])

    return eT.tostring(root, encoding="utf-8", xml_declaration=True)