# Copyright (c) 2024, K&K Software AG and contributors
# For license information, please see license.txt

# import frappe


from typing import Any, TypedDict

import frappe


class StockFilter(TypedDict):
    company: str | None
    warehouse: str | None


SLEntry = dict[str, Any]


def execute(filters=None):
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)

    return columns, data


def get_columns(filters: StockFilter) -> list[dict]:
    columns = [
        {
            "label": "Lieferant",
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 300,
        },
        {
            "label": "Artikel",
            "fieldname": "item",
            "fieldtype": "Link",
            "options": "Item",
            "width": 300,
        },
        {
            "label": "Menge",
            "fieldname": "amount",
            "fieldtype": "Int",
            "width": 200,
        },
    ]

    return columns


def is_leergut_group(item_group_name):
    if item_group_name == "Leergut":
        return True

    item_group_doc = frappe.get_doc("Item Group", item_group_name)

    if item_group_doc.parent_item_group:
        return is_leergut_group(item_group_doc.parent_item_group)

    else:
        return False


def stock_entry_item_clears_filter(filters, stock_entry_doc, stock_entry_item):
    if filters.get("item") and filters.get("item") != stock_entry_item.item_code:
        return False

    return True


def get_data(filters: StockFilter):
    stock_entries_fitlers = [
        ["posting_date", "between", [filters.get("start_date"), filters.get("end_date")]],
        ["stock_entry_type", "in", ["Material Receipt", "Material Issue"]],
    ]

    if filters.get("supplier"):
        stock_entries_fitlers.append(["magic_supplier", "=", filters.get("supplier")])

    stock_entries_list = frappe.get_all(
        "Stock Entry",
        filters=stock_entries_fitlers,
        order_by="posting_date asc, posting_time asc",
        fields=["name"],
    )

    stock_entries_formated = []

    suppliers_with_items = []

    for stock_entry in stock_entries_list:
        stock_entry_doc = frappe.get_doc("Stock Entry", stock_entry.name)

        for item in stock_entry_doc.items:
            item_doc = frappe.get_doc("Item", item.item_code)

            if is_leergut_group(item_doc.item_group) and stock_entry_item_clears_filter(
                filters, stock_entry_doc, item
            ):
                row = []

                if stock_entry_doc.magic_supplier:
                    supplier_doc = frappe.get_doc(
                        "Supplier", stock_entry_doc.magic_supplier
                    )

                    row.append(supplier_doc.supplier_name)

                    if [
                        supplier_doc.supplier_name,
                        item.item_name,
                    ] not in suppliers_with_items:
                        suppliers_with_items.append(
                            [supplier_doc.supplier_name, item.item_name]
                        )

                else:
                    row.append("")

                row.append(item.item_name)

                if stock_entry_doc.stock_entry_type == "Material Receipt":
                    row.append(item.qty)

                elif stock_entry_doc.stock_entry_type == "Material Issue":
                    row.append(item.qty * (-1))

                stock_entries_formated.append(row)

    result = []

    for supplier_with_item in suppliers_with_items:
        item_sum = 0
        row = []

        for stock_entry in stock_entries_formated:
            if (
                stock_entry[0] == supplier_with_item[0]
                and stock_entry[1] == supplier_with_item[1]
            ):
                item_sum += stock_entry[2]

        row.append(supplier_with_item[0])
        row.append(supplier_with_item[1])
        row.append(item_sum)
        result.append(row)

    return result
