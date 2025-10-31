# Copyright (c) 2024, K&K Software AG and contributors
# For license information, please see license.txt

# import frappe


from collections import defaultdict
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


def get_warehouse_balance(filters: StockFilter) -> dict[str, float]:
    query_filters_sle = {"is_cancelled": 0, "docstatus": ("<", 2)}
    query_filters_company = {}

    if filters.get("company"):
        query_filters_sle["company"] = filters["company"]
        query_filters_company["company"] = filters["company"]

    warehouse_balance_dict = {}

    warehouses = frappe.get_all(
        "Warehouse",
        fields=["name"],
        filters=query_filters_company,
    )

    for warehouse in warehouses:
        warehouse_balance = 0
        sle_entries = frappe.get_all(
            "Stock Ledger Entry",
            fields=["item_code", "qty_after_transaction", "creation"],
            filters={"warehouse": warehouse.name, **query_filters_sle},
            order_by="creation desc",
        )

        if sle_entries:
            article_entries = defaultdict(list)
            for entry in sle_entries:
                article_entries[entry["item_code"]].append(entry)

            for entries in article_entries.items():
                sorted_entries = sorted(
                    entries, key=lambda x: x["creation"], reverse=True
                )
                latest_entry = sorted_entries[0]
                warehouse_balance += latest_entry["qty_after_transaction"]

            warehouse_balance_dict[warehouse.name] = warehouse_balance

    return warehouse_balance_dict


def get_child_warehouses_recursive(warehouse_name):
    child_warehouses = frappe.get_all(
        "Warehouse",
        filters={"parent_warehouse": warehouse_name},
        fields=["name", "parent_warehouse", "is_group"],
        order_by="lft",
    )
    all_child_warehouses = []
    for child_warehouse in child_warehouses:
        all_child_warehouses.append(child_warehouse)
        if child_warehouse["is_group"]:
            child_warehouses_recursive = get_child_warehouses_recursive(
                child_warehouse["name"]
            )
            all_child_warehouses.extend(child_warehouses_recursive)
    return all_child_warehouses


def get_warehouses(report_filters: StockFilter):
    company = report_filters.get("company")
    selected_warehouse = report_filters.get("warehouse")

    if selected_warehouse:
        child_warehouses = get_child_warehouses_recursive(selected_warehouse)
        selected_warehouse_data = frappe.get_doc("Warehouse", selected_warehouse)
        child_warehouses.insert(0, selected_warehouse_data.as_dict())
        return child_warehouses

    return frappe.get_all(
        "Warehouse",
        fields=["name", "parent_warehouse", "is_group"],
        filters={"company": company},
        order_by="lft",
    )


def count_free_and_occupied(child_warehouses, warehouses):
    free_count = 0
    occupied_count = 0

    for child in child_warehouses:
        if child.is_group:
            child_child_warehouses = [
                c for c in warehouses if c.parent_warehouse == child.name
            ]
            child_free_count, child_belegt_count = count_free_and_occupied(
                child_child_warehouses, warehouses
            )
            free_count += child_free_count
            occupied_count += child_belegt_count
        elif child.stock_balance == "frei":
            free_count += 1
        elif child.stock_balance == "belegt":
            occupied_count += 1
    return free_count, occupied_count


def get_data(filters: StockFilter):
    warehouse_balance = get_warehouse_balance(filters)
    warehouses = get_warehouses(filters)

    for warehouse in warehouses:
        if not warehouse.is_group:
            stock_balance = warehouse_balance.get(warehouse.name, 0) or 0.0
            if stock_balance > 0:
                warehouse.stock_balance = "belegt"
            else:
                warehouse.stock_balance = "frei"

    # second loop because stock balance is set here
    for warehouse in warehouses:
        if warehouse.is_group:
            child_warehouses = [
                child for child in warehouses if child.parent_warehouse == warehouse.name
            ]
            frei_count, belegt_count = count_free_and_occupied(
                child_warehouses, warehouses
            )
            warehouse.stock_balance = f"{frei_count} frei, {belegt_count} belegt"

    update_indent(warehouses)

    return warehouses


def update_indent(warehouses):
    for warehouse in warehouses:

        def add_indent(warehouse, indent):
            warehouse.indent = indent
            for child in warehouses:
                if child.parent_warehouse == warehouse.name:
                    add_indent(child, indent + 1)

        if warehouse.is_group:
            add_indent(warehouse, warehouse.indent or 0)


def get_columns(filters: StockFilter) -> list[dict]:
    columns = [
        {
            "label": "Lagerplätze",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 200,
        },
        {
            "label": "frei/belegt",
            "fieldname": "stock_balance",
            "fieldtype": "Data",
            "width": 150,
        },
    ]

    return columns
