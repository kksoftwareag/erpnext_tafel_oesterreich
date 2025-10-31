import frappe


def execute():
    tour_list = frappe.get_all("Magic Tour", fields=["name", "magic_tour_type"])
    for tour in tour_list:
        if not tour.magic_tour_type:
            frappe.db.set_value(
                "Magic Tour", tour.name, "magic_tour_type", "Tour für Woche planen"
            )
