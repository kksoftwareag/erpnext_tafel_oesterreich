from datetime import timedelta

import frappe


def set_mhd_plus_date_on_change(item_group, on_update):
    old_doc = item_group.get_doc_before_save()

    if (
        old_doc
        and old_doc.magic_shelf_life_in_days != item_group.magic_shelf_life_in_days
    ):
        # set item mhd+ date new
        linked_items = frappe.get_all(
            "Item",
            filters={"item_group": item_group.name},
            fields=["name", "magic_best_before_date"],
        )
        if not linked_items:
            return

        for linked_item in linked_items:
            if not linked_item.magic_best_before_date:
                continue
            best_before_date_plus = linked_item.magic_best_before_date + timedelta(
                days=item_group.magic_shelf_life_in_days
            )
            frappe.db.set_value(
                "Item",
                linked_item.name,
                "magic_best_before_date_plus",
                best_before_date_plus,
            )


def update_donor_reference(doc, method):
    connected_donor = frappe.get_all(
        "Magic Donor Groceries Regestration",
        fields=["*"],
        filters={"magic_item_name": doc.web_item_name, "docstatus": 1},
    )

    if connected_donor:
        donor_doc = frappe.get_doc(
            "Magic Donor Groceries Regestration", connected_donor[0].name
        )
        warehouse_table = donor_doc.magic_warehouse_table
        minimum_weight = (
            donor_doc.magic_product_weight_per_warehouse_unit
            * donor_doc.magic_minimum_qty_b2c
        )
        maximum_weight = (
            donor_doc.magic_product_weight_per_warehouse_unit
            * donor_doc.magic_maximum_qty_b2c
        )
        description_text = donor_doc.magic_description
        description_text += (
            "B2C:<br>"
            + "Einheit (Standardmaßeinheit): "
            + donor_doc.magic_warehouse_uom
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
            + str(donor_doc.magic_weight_uom)
        )
        frappe.db.set_value(
            "Website Item", doc.name, "magic_donor_reference", donor_doc.name
        )
        frappe.db.set_value(
            "Website Item", doc.name, "web_long_description", description_text
        )
        frappe.db.set_value(
            "Website Item",
            doc.name,
            "website_warehouse",
            warehouse_table[0].magic_warehouse,
        )
