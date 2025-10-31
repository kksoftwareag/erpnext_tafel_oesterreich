import unicodedata

import frappe


def create_barcode(doc, method):
    if not frappe.db.exists(
        "Magic Barcode",
        {
            "magic_donor_registration_id": doc.name,
        },
    ):
        new_barcode_doc = frappe.get_doc(
            {
                "doctype": "Magic Barcode",
                "magic_item": doc.magic_item_link,
                "magic_description": doc.magic_description,
                "magic_best_before_date_plus": doc.magic_best_before_date_plus,
                "magic_warehouse": doc.magic_warehouse_link,
                "magic_amount_warehouse_unit": doc.magic_amount_warehouse_unit,
                "magic_donor_registration_id": doc.name,
                "magic_barcode": unicodedata.normalize(
                    "NFD", doc.magic_item_link + "_" + doc.name
                )
                .encode("ascii", "ignore")
                .decode("utf-8"),
            }
        )
        new_barcode_doc.insert()
