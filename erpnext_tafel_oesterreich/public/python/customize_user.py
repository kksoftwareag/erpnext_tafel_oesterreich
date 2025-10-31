import frappe


def create_qualifications_doc(user, after_insert):
    qualifications_list = frappe.get_all(
        "Magic User Qualifications", filters={"magic_user": user.name}, fields=["name"]
    )
    if not qualifications_list:
        frappe.get_doc(
            {"doctype": "Magic User Qualifications", "magic_user": user.name}
        ).insert(ignore_permissions=True)
