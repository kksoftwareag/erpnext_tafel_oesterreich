from datetime import date, datetime

import frappe


def create_item(doc, method):
    if doc.magic_item_name:
        description_text = ""
        image_path = ""
        publish_item = 0

        if len(doc.magic_warehouse_table) < 1:
            frappe.throw(frappe._("Bitte Lager in Tabelle setzen."))

        if doc.magic_description:
            description_text = doc.magic_description
        if doc.magic_image_attachment:
            image_path = doc.magic_image_attachment
        if doc.magic_published_in_webshop:
            publish_item = 1
        uoms = []
        if len(doc.magic_uoms) > 0:
            for uom in doc.magic_uoms:
                uoms.append(
                    {
                        "doctype": "UOM Conversion Detail",
                        "uom": uom.uom,
                        "conversion_factor": uom.conversion_factor,
                    },
                )
        template_item = frappe.get_doc("Item", doc.magic_item_link)

        minimum_weight = (
            doc.magic_product_weight_per_warehouse_unit * doc.magic_minimum_qty_b2c
        )
        maximum_weight = (
            doc.magic_product_weight_per_warehouse_unit * doc.magic_maximum_qty_b2c
        )

        description_text += (
            "B2C:<br>"
            + "Einheit (Standardmaßeinheit): "
            + doc.magic_warehouse_uom
            + "<br>"
            + "Mindestabnahmemenge: "
            + str(minimum_weight)
            + " kg"
            + "<br>"
            + "Maximalabnahmemenge: "
            + str(maximum_weight)
            + " kg"
            + "<br>"
            + "UOM (Gewichtsmaßeinheit): "
            + str(template_item.weight_uom)
        )
        item = frappe.get_doc(
            {
                "doctype": "Item",
                "item_code": doc.magic_item_name,
                "item_name": doc.magic_item_name,
                "stock_uom": doc.magic_warehouse_uom,
                "magic_item_maingroup": doc.magic_item_maingroup,
                "item_group": doc.magic_secondary_item_group,
                "custom_status": "Webshopartikel",
                "magic_donor_reference": doc.name,
                "description": description_text,
                "uoms": uoms if len(uoms) > 0 else None,
            }
        ).insert()
        check_warehouse_qty(item, doc)
        if doc.magic_published_in_webshop == 1:
            create_and_link_webshop_item(
                item, description_text, image_path, doc, publish_item
            )
    else:
        frappe.throw(frappe._("Kein Sammelartikel ausgewählt"))


def check_warehouse_qty(item_document, doc):
    warehouse_table = doc.magic_warehouse_table
    qty_sum = 0
    for warehouse in warehouse_table:
        qty_sum += warehouse.magic_qty
    if qty_sum != doc.magic_amount_warehouse_unit:
        frappe.throw(
            frappe._("Gesamtmenge der Lagerzuordnung muss gleich der Menge sein.")
        )
    create_material_receipt(item_document, doc, warehouse_table)


def create_material_receipt(item_document, donor_data, warehouse_table):
    now = datetime.now()

    for warehouse in warehouse_table:
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
                        "t_warehouse": warehouse.magic_warehouse,
                        "item_code": item_document.item_code,
                        "magic_best_before_date": donor_data.magic_best_before_date,
                        "magic_best_before_date_plus": donor_data.magic_best_before_date_plus,
                        "qty": warehouse.magic_qty,
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


def create_and_link_webshop_item(
    item_document, description_text, image_path, donor_data, publish_item
):
    warehouse_table = donor_data.magic_warehouse_table

    if not frappe.db.exists(
        "Website Item",
        {
            "item_code": item_document.item_code,
        },
    ):
        website_item_document = frappe.get_doc(
            {
                "doctype": "Website Item",
                "web_item_name": item_document.item_name,
                "item_name": item_document.item_name,
                "item_group": item_document.item_group,
                "item_code": item_document.item_code,
                "website_warehouse": warehouse_table[0].magic_warehouse,
                "web_long_description": description_text,
                "website_image": image_path,
                "published": publish_item,
            }
        )
        website_item_document.insert(ignore_permissions=True, ignore_links=True)
        frappe.db.set_value(
            "Website Item",
            website_item_document.name,
            "magic_donor_reference",
            donor_data.name,
        )
