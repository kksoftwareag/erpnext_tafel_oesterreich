# Copyright (c) 2024, K&K Software AG and contributors
# For license information, please see license.txt

from datetime import date

import frappe


def execute(filters=None):
    columns = [
        {
            "label": "Artikel",
            "fieldname": "item",
            "fieldtype": "Link",
            "options": "Item",
            "width": 200,
        },
        {
            "label": "Menge",
            "fieldname": "actual_qty",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": "MHD+",
            "fieldname": "best_before_plus",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": "Lagerplatz",
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 200,
        },
    ]
    data = []

    stock_entry_items = frappe.get_all(
        "Stock Entry Detail",
        fields=["*"],
        filters={"magic_best_before_date_plus": [">", date.today()]},
    )
    days_before_sending_mail = frappe.get_doc(
        "Magic Best Before Configuration"
    ).magic_days_best_before_plus
    for item in stock_entry_items:
        date_difference = item.magic_best_before_date_plus - date.today()
        if date_difference.days == days_before_sending_mail:
            data.append(
                {
                    "item": item.item_code,
                    "actual_qty": str(item.qty),
                    "best_before_plus": str(item.magic_best_before_date_plus),
                    "warehouse": item.t_warehouse,
                }
            )

    return columns, data
