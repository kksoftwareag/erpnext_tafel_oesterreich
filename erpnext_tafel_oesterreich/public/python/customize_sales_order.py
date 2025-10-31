import frappe


@frappe.whitelist()
def cancel_sales_order_from_portal(sales_order_name):
    try:
        sales_order_doc = frappe.get_doc("Sales Order", sales_order_name)
        if (
            sales_order_doc.magic_tourstatus
            and "tour geplant" in sales_order_doc.magic_tourstatus.lower()
        ):
            return (
                False,
                "Die Bestellung kann nicht mehr storniert werden, da sie bereits für die Tour eingeplant wurde. Bitte wenden Sie sich bei Fragen direkt an uns.",
            )
        sales_order_doc.docstatus = 2
        sales_order_doc.save(ignore_permissions=True)

        try:
            if sales_order_doc.items[0].prevdoc_docname:
                quotation_doc = frappe.get_doc(
                    "Quotation", sales_order_doc.items[0].prevdoc_docname
                )
                quotation_doc.docstatus = 2
                quotation_doc.save(ignore_permissions=True)
        except Exception:
            pass
        return True, ""
    except Exception:
        return (
            False,
            "Fehler: Bestellung konnte nicht storniert werden, bitte wenden Sie sich direkt an uns.",
        )


def set_tourstatus(delivery_note, method):
    # method = on_submit and on_update_after_submit
    if delivery_note.docstatus == 2:
        return

    # check if status exists, otherwise insert it
    tourstatus = frappe.get_all("Magic Status", filters={"name": "in Tour geplant"})
    if not tourstatus:
        try:
            frappe.get_doc(
                {
                    "doctype": "Magic Status",
                    "magic_status": "in Tour geplant",
                    "name": "in Tour geplant",
                }
            ).insert()
        except Exception:
            pass

    for item in delivery_note.items:
        if item.against_sales_order:
            sales_order = frappe.get_doc("Sales Order", item.against_sales_order)
            if (
                sales_order
                and sales_order.per_delivered == 100
                and sales_order.docstatus != 2
            ):
                tour_items = frappe.get_all(
                    "Magic Tour Items Table",
                    filters={"magic_delivery_note": delivery_note.name},
                )
                if not tour_items:
                    continue
                if not sales_order.magic_tourstatus or sales_order.magic_tourstatus == "":
                    frappe.db.set_value(
                        "Sales Order",
                        sales_order.name,
                        "magic_tourstatus",
                        "in Tour geplant",
                    )
