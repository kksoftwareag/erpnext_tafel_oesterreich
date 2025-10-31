from datetime import date, datetime

import frappe


@frappe.whitelist()
def set_supplier_name(supplier):
    return frappe.get_doc("Supplier", supplier).supplier_name


def check_warehouse_qty(doc, method):
    warehouse_table = doc.magic_warehouse_table
    qty_sum = 0
    for warehouse in warehouse_table:
        qty_sum += warehouse.magic_qty
    if qty_sum > doc.magic_amount_warehouse_unit:
        frappe.throw(
            "Gesamtmenge in der Lagerzuordnung um "
            + str(qty_sum - doc.magic_amount_warehouse_unit)
            + " überschritten."
        )
    create_material_receipt(doc)


def create_material_receipt(doc, item_document, donor_data):
    now = datetime.now()
    stock_entry = frappe.get_doc(
        {
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Receipt",
            "posting_date": date.today(),
            "posting_time": now.strftime("%H:%M:%S"),
            "magic_supplier": donor_data.magic_supplier_link,
            "items": [
                {
                    "s_warehouse": "",
                    "t_warehouse": donor_data.magic_warehouse_link,
                    "item_code": item_document.item_code,
                    "magic_best_before_date": donor_data.magic_best_before_date,
                    "magic_best_before_date_plus": donor_data.magic_best_before_date_plus,
                    "qty": donor_data.magic_amount_warehouse_unit,
                    "uom": donor_data.magic_warehouse_uom,
                    "stock_uom": donor_data.magic_warehouse_uom,
                    "allow_zero_valuation_rate": 1,
                    "magic_product_weight_per_warehouse_unit": donor_data.magic_product_weight_per_warehouse_unit,
                    "magic_transport_weight_per_warehouse_unit": donor_data.magic_transport_weight_per_warehouse_unit,
                    "magic_bundle_consists_of": donor_data.magic_bundle_consists_of,
                }
            ],
            "magic_donor_reference": donor_data.name,
        }
    ).insert()
    stock_entry.submit()
