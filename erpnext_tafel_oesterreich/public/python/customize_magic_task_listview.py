from datetime import datetime

import frappe
from frappe import _


def get_qualifications_of_user(user):
    # Get Qualifikations of User
    if not frappe.db.exists("Magic User Qualifications", {"name": user}):
        frappe.throw(
            _(
                "Der aktuell eingeloggte User hat keine Qualifikationen gesetzt und kann demnach keine Tätigkeiten einsehen. Bitte Qualifikationen setzen."
            )
        )
    else:
        magic_user_qualification_doc = frappe.get_doc("Magic User Qualifications", user)
        if not magic_user_qualification_doc.magic_qualifications:
            frappe.throw(
                _(
                    "Der aktuell eingeloggte User hat keine Qualifikationen gesetzt und kann demnach keine Tätigkeiten einsehen. Bitte Qualifikationen setzen."
                )
            )
        else:
            user_qualifications = [
                qualification.magic_qualification
                for qualification in magic_user_qualification_doc.magic_qualifications
            ]
            return user_qualifications


def filter_matching_tasks_for_user(user_qualifications):
    # Get all Tasks, wich have minimum one matching qualification of the user
    magic_tasks_with_matching_qualifikation = frappe.get_all(
        "Magic Task",
        filters=[
            [
                "Magic Multiple Qualifications",
                "magic_qualification",
                "in",
                ", ".join(user_qualifications),
            ],
            ["magic_date", ">=", datetime.now().date()],
        ],
    )

    final_task_list = []
    for magic_task in magic_tasks_with_matching_qualifikation:
        magic_task_doc = frappe.get_doc("Magic Task", magic_task.name)
        needed_qualifications = [
            qualification.magic_qualification
            for qualification in magic_task_doc.magic_qualifications
        ]

        if all(
            qualification in user_qualifications
            for qualification in needed_qualifications
        ):
            final_task_list.append(magic_task)

    final_task_list = [f"'{task.name}'" for task in final_task_list]
    return final_task_list


def get_permission_query_conditions(user):
    if not user:
        user = frappe.session.user

    # System Manager darf immer alles sehen
    if "System Manager" in frappe.get_roles(user):
        return None

    user_qualifications = get_qualifications_of_user(user)
    final_task_list = filter_matching_tasks_for_user(user_qualifications)

    if not final_task_list:
        frappe.throw(
            _(
                "Aktuell gibt es keine Aufgaben die für deine Qualifikationen geeignet sind. Bitte versuche es zu einem späteren Zeitpunkt nochmal oder frage einfach persönlich nach. 😊"
            )
        )
    else:
        return """(`tabMagic Task`.name IN ({}) )""".format(", ".join(final_task_list))


def has_permission(doc, user):
    # System Manager darf immer alles sehen
    if "System Manager" in frappe.get_roles(user):
        return True

    user_qualifications = get_qualifications_of_user(user)
    needed_qualifications = [
        qualification.magic_qualification for qualification in doc.magic_qualifications
    ]

    if all(
        qualification in user_qualifications for qualification in needed_qualifications
    ):
        return True
    else:
        frappe.throw(
            "Der eingeloggte User hat nicht die notwendigen Qualifikationen, um diese Tätigkeit einsehen zu können."
        )
        return False
