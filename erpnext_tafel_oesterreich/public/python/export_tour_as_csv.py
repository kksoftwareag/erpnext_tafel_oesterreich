import csv
from io import StringIO

import frappe


@frappe.whitelist()
def export_tour(docname):
    tour_doc = frappe.get_doc("Magic Tour", docname)

    csv_data = [["Straße", "Postleitzahl", "Ort"]]

    if tour_doc.magic_tour_type == "Tour für Woche planen":
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            table_name = f"magic_{day.lower()}_table"
            for row in tour_doc.get(table_name, []):
                csv_data = append_csv_data(row, csv_data)

    elif tour_doc.magic_tour_type == "Tour für Datum planen":
        for row in tour_doc.get("magic_items_table_for_date", []):
            csv_data = append_csv_data(row, csv_data)

    csv_file = StringIO()
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(csv_data)
    csv_file.seek(0)

    return {
        "filename": docname + ".csv",
        "filecontent": csv_file.getvalue(),
        "type": "download",
    }


def get_address(doctype, name):
    address = frappe.get_all(
        "Address",
        filters=[
            ["Dynamic Link", "link_doctype", "=", doctype],
            ["Dynamic Link", "link_name", "=", name],
        ],
        fields=["address_line1", "pincode", "city"],
    )
    if address:
        return address[0]

    return None


def append_csv_data(row, csv_data):
    supplier = row.get("magic_supplier")
    customer = row.get("magic_customer")

    if supplier:
        address = get_address("Supplier", supplier)
        if address:
            csv_data.append(
                [address["address_line1"], address["pincode"], address["city"]]
            )

    if customer:
        address = get_address("Customer", customer)
        if address:
            csv_data.append(
                [address["address_line1"], address["pincode"], address["city"]]
            )

    return csv_data
