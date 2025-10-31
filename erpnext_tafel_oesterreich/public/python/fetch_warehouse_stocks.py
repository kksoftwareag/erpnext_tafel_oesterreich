import frappe


@frappe.whitelist()
def fetch_warehouse(item_name):
    return frappe.get_all("Bin", fields=["*"], filters={"item_code": item_name})
