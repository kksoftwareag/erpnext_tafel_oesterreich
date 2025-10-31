import json
from datetime import timedelta

import frappe
from frappe import _
from frappe.utils import getdate


def get_context(context):
    context.no_cache = 1

    context.items = "\n".join(
        item.name
        for item in frappe.get_all(
            "Item", fields=["name"], filters=[["disabled", "=", "0"]]
        )
    )

    intervalls = [
        _("Daily"),
        _("Weekly"),
        _("Monthly"),
        _("Quarterly"),
        _("Half-yearly"),
        _("Yearly"),
    ]
    context.subscription_intervalls = "\n".join(interval for interval in intervalls)

    intervalls_weekly = [
        _("Monday"),
        _("Tuesday"),
        _("Wednesday"),
        _("Thursday"),
        _("Friday"),
        _("Saturday"),
    ]
    context.intervalls_weekly = "\n".join(
        interval_weekly for interval_weekly in intervalls_weekly
    )

    logged_in_user = frappe.session.user
    customers_linked_with_user = frappe.get_all(
        "Customer", filters=[["Portal User", "user", "=", logged_in_user]]
    )

    if customers_linked_with_user:
        linked_sales_order_templates_with_user = frappe.get_all(
            "Sales Order",
            fields=["name"],
            filters=[
                ["docstatus", "=", 0],
                ["customer", "=", customers_linked_with_user[0].name],
            ],
        )

    context.subscriptions = []
    for linked_sales_order in linked_sales_order_templates_with_user:
        # check if linked sales order is a reference in an active auto repeat doc
        linked_auto_repeats_with_sales_order = frappe.get_all(
            "Auto Repeat",
            fields=["name"],
            filters=[
                ["reference_document", "=", linked_sales_order.name],
                ["disabled", "=", 0],
            ],
        )

        for auto_repeat in linked_auto_repeats_with_sales_order:
            context.subscriptions.append(
                {
                    "sales_order_template_doc": frappe.get_doc(
                        "Sales Order", linked_sales_order, ignore_permissions=True
                    ),
                    "auto_repeat_doc": frappe.get_doc(
                        "Auto Repeat", auto_repeat.name, ignore_permissions=True
                    ),
                }
            )

    return context


def create_sales_order_template(start_date_casted, logged_in_user, item_table):
    sales_order_template = frappe.get_doc(
        {
            "doctype": "Sales Order",
            "customer": logged_in_user,
            "items": [
                {"item_code": item_table_entry["item"], "qty": item_table_entry["qty"]}
                for item_table_entry in item_table
            ],
            "delivery_date": start_date_casted + timedelta(days=7),
            "custom_magic_is_reference_for_auto_repeat": 1,
        }
    )

    sales_order_template.insert(ignore_permissions=True)

    return sales_order_template


def create_auto_repeat_doc(
    start_date_casted,
    end_date_casted,
    sales_order_template_name,
    intervall_of_subscription,
    day_of_execution,
    execution_in_last_day_of_month,
    execution_weekly_table,
):
    intervalls = {
        _("Daily"): "Daily",
        _("Weekly"): "Weekly",
        _("Monthly"): "Monthly",
        _("Quarterly"): "Quarterly",
        _("Half-yearly"): "Half-yearly",
        _("Yearly"): "Yearly",
    }
    translated_intervall = intervalls[intervall_of_subscription]

    week_days = {
        _("Monday"): "Monday",
        _("Tuesday"): "Tuesday",
        _("Wednesday"): "Wednesday",
        _("Thursday"): "Thursday",
        _("Friday"): "Friday",
        _("Saturday"): "Saturday",
    }

    auto_repeat_doc = frappe.get_doc(
        {
            "doctype": "Auto Repeat",
            "reference_doctype": "Sales Order",
            "reference_document": sales_order_template_name,
            "submit_on_creation": 1,
            "start_date": start_date_casted,
            "end_date": end_date_casted if end_date_casted else None,
            "frequency": translated_intervall,
            "repeat_on_day": int(day_of_execution) if day_of_execution else None,
            "repeat_on_last_day": int(execution_in_last_day_of_month)
            if execution_in_last_day_of_month
            else None,
            "repeat_on_days": [
                {"day": week_days[weekly_day["Wochentag"]]}
                for weekly_day in execution_weekly_table
            ]
            if execution_weekly_table
            else None,
        }
    )

    auto_repeat_doc.insert(ignore_permissions=True)

    return auto_repeat_doc


@frappe.whitelist()
def generate_sales_invoice_and_auto_repeat(data):
    data_dict = json.loads(data)

    try:
        start_date_casted = getdate(data_dict["start_date"])
        end_date_casted = (
            getdate(data_dict["end_date"]) if "end_date" in data_dict else None
        )
    except Exception:
        return {
            0,
            "Das umwandeln des Datums ist fehlgeschlagen. 🚩 Wurde in der Eingabe das richtige Format eingehalten?",
        }

    try:
        logged_in_user = frappe.session.user
        customers_linked_with_user = frappe.get_all(
            "Customer", filters=[["Portal User", "user", "=", logged_in_user]]
        )
        customer_doc_for_logged_in_user = frappe.get_doc(
            "Customer", customers_linked_with_user[0].name, ignore_permissions=True
        )
    except Exception:
        return {
            0,
            "Der aktuelle User ist in keiner Organistaion als Portal Nutzer hinterlegt. 🚩 Bitte anlegen.",
        }

    try:
        sales_order_template = create_sales_order_template(
            start_date_casted,
            customer_doc_for_logged_in_user.name,
            data_dict["item_table"],
        )
    except Exception:
        return {
            0,
            "Das anlegen der Auftragsvorlage hat nicht funktioniert. 🚩 Bitte an Support wenden oder nochmal versuchen",
        }

    try:
        create_auto_repeat_doc(
            start_date_casted,
            end_date_casted,
            sales_order_template.name,
            data_dict["intervall_of_subscription"],
            data_dict["day_of_execution"] if "day_of_execution" in data_dict else None,
            data_dict["execution_in_last_day_of_month"]
            if "execution_in_last_day_of_month" in data_dict
            else None,
            data_dict["execution_weekly_table"]
            if "execution_weekly_table" in data_dict
            else None,
        )
    except Exception:
        return {
            0,
            "Das anlegen des Abonnements hat nicht funktioniert. 🚩 Bitte an Support wenden oder nochmal versuchen",
        }

    return [
        1,
        "Abonnement wurde erfolgreich angelegt. Bitte die Seite einmal neu laden und das Abonnement erscheint in der Listenansicht. ✅",
    ]


def update_sales_order_template(sales_order_template_name, item_table):
    sales_order_doc = frappe.get_doc(
        "Sales Order", sales_order_template_name, ignore_permissions=True
    )

    sales_order_doc.items.clear()
    [
        sales_order_doc.append(
            "items",
            {"item_code": item_table_entry["item"], "qty": item_table_entry["qty"]},
        )
        for item_table_entry in item_table
    ]

    sales_order_doc.save(ignore_permissions=True)

    return sales_order_doc


def update_auto_repeat_doc(
    auto_repeat_doc_name,
    end_date_casted,
    intervall_of_subscription,
    day_of_execution,
    execution_in_last_day_of_month,
    execution_weekly_table,
):
    intervalls = {
        _("Daily"): "Daily",
        _("Weekly"): "Weekly",
        _("Monthly"): "Monthly",
        _("Quarterly"): "Quarterly",
        _("Half-yearly"): "Half-yearly",
        _("Yearly"): "Yearly",
    }
    translated_intervall = intervalls[intervall_of_subscription]

    week_days = {
        _("Monday"): "Monday",
        _("Tuesday"): "Tuesday",
        _("Wednesday"): "Wednesday",
        _("Thursday"): "Thursday",
        _("Friday"): "Friday",
        _("Saturday"): "Saturday",
    }

    # Fetch the existing Auto Repeat document
    existing_auto_repeat_doc = frappe.get_doc(
        "Auto Repeat", auto_repeat_doc_name
    )  # Replace auto_repeat_doc_name with the name of the existing document

    # Update the document with new data
    existing_auto_repeat_doc.end_date = end_date_casted if end_date_casted else None
    existing_auto_repeat_doc.frequency = translated_intervall
    existing_auto_repeat_doc.repeat_on_day = (
        int(day_of_execution) if day_of_execution else None
    )
    existing_auto_repeat_doc.repeat_on_last_day = (
        int(execution_in_last_day_of_month) if execution_in_last_day_of_month else None
    )
    existing_auto_repeat_doc.repeat_on_days.clear() if execution_weekly_table else None
    [
        existing_auto_repeat_doc.append(
            "repeat_on_days", {"day": week_days[weekly_day["Wochentag"]]}
        )
        for weekly_day in execution_weekly_table
    ] if execution_weekly_table else None

    # Save the updated document
    existing_auto_repeat_doc.save(ignore_permissions=True)

    return existing_auto_repeat_doc


@frappe.whitelist()
def update_sales_invoice_and_auto_repeat(
    data, sales_order_template_name, auto_repeat_doc_name
):
    data_dict = json.loads(data)

    try:
        end_date_casted = (
            getdate(data_dict["end_date"]) if "end_date" in data_dict else None
        )
    except Exception:
        return {
            0,
            "Das umwandeln des Datums ist fehlgeschlagen. 🚩 Wurde in der Eingabe das richtige Format eingehalten?",
        }

    try:
        update_sales_order_template(sales_order_template_name, data_dict["item_table"])
    except Exception:
        return {
            0,
            "Das updaten der Auftragsvorlage hat nicht funktioniert. 🚩 Bitte an Support wenden oder nochmal versuchen",
        }

    try:
        update_auto_repeat_doc(
            auto_repeat_doc_name,
            end_date_casted,
            data_dict["intervall_of_subscription"],
            data_dict["day_of_execution"] if "day_of_execution" in data_dict else None,
            data_dict["execution_in_last_day_of_month"]
            if "execution_in_last_day_of_month" in data_dict
            else None,
            data_dict["execution_weekly_table"]
            if "execution_weekly_table" in data_dict
            else None,
        )
    except Exception:
        return {
            0,
            "Das updaten des Abonnements hat nicht funktioniert. 🚩 Bitte an Support wenden oder nochmal versuchen",
        }

    return {
        1,
        "Abonnement wurde erfolgreich bearbeitet. Bitte die Seite einmal neu laden und die Änderungen erscheinen in der Listenansicht ✅",
    }
