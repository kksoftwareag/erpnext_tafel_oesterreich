import frappe


def execute():
    user_list = frappe.get_all("User", fields=["name"])
    if not user_list:
        return

    for user in user_list:
        qualifications_list = frappe.get_all(
            "Magic User Qualifications",
            filters={"magic_user": user.name},
            fields=["name"],
        )
        if not qualifications_list:
            frappe.get_doc(
                {"doctype": "Magic User Qualifications", "magic_user": user.name}
            ).insert()
