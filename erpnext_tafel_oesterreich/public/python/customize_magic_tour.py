import json

import frappe


def set_tour_name_in_items(magic_tour, item_table_name):
    table = getattr(magic_tour, item_table_name, None)

    if not table:
        return

    for row in table:
        if row.magic_items_link:
            magic_items_doc = frappe.get_doc("Magic Tour Items", row.magic_items_link)
            if not magic_items_doc.magic_tour:
                frappe.db.set_value(
                    "Magic Tour Items",
                    row.magic_items_link,
                    "magic_tour",
                    magic_tour.name,
                )


@frappe.whitelist()
def fetch_tour(tourname):
    if tourname:
        tour_template = frappe.get_doc("Magic Tour Template", tourname)
        return tour_template


def weight_exceeded_message(magic_tour, on_update):
    if magic_tour.magic_tour_type == "Tour für Woche planen":
        exceeded_weight_days = []
        day_names = {
            "monday": "Montag",
            "tuesday": "Dienstag",
            "wednesday": "Mittwoch",
            "thursday": "Donnerstag",
            "friday": "Freitag",
        }

        for day in day_names:
            transport_weight_attr = "magic_transport_weight_" + day
            permissible_load_attr = "magic_permissible_load_kg_" + day
            overloaded_attr = "magic_vehicle_overloaded_" + day
            vehicle_attr = "magic_vehicle_" + day

            transport_weight = getattr(magic_tour, transport_weight_attr) or 0
            permissible_load = getattr(magic_tour, permissible_load_attr) or 0
            overload = getattr(magic_tour, overloaded_attr)
            vehicle = getattr(magic_tour, vehicle_attr)

            if vehicle and float(transport_weight) > float(permissible_load):
                exceeded_weight_days.append(day_names[day])
                if not overload:
                    frappe.db.set_value("Magic Tour", magic_tour.name, overloaded_attr, 1)
            else:
                if overload:
                    frappe.db.set_value("Magic Tour", magic_tour.name, overloaded_attr, 0)

        if exceeded_weight_days != []:
            exceeded_days_str = ", ".join(exceeded_weight_days)
            frappe.msgprint(
                frappe._(
                    f"Warnung❗<br><br>Für folgende Tage wurde die zulässige Zuladung des Fahrzeugs überschritten:<br>{exceeded_days_str}<br><br>Bitte die Ladungen entsprechend anpassen."
                )
            )

    elif magic_tour.magic_tour_type == "Tour für Datum planen":
        vehicle = magic_tour.magic_vehicle_for_date
        transport_weight = magic_tour.magic_transport_weight_for_date or 0
        permissible_load = magic_tour.magic_permissible_load_kg_for_date or 0
        overload = magic_tour.magic_vehicle_overloaded_for_date

        if vehicle and float(transport_weight) > float(permissible_load):
            if not overload:
                frappe.db.set_value(
                    "Magic Tour", magic_tour.name, "magic_vehicle_overloaded_for_date", 1
                )
            frappe.msgprint(
                frappe._(
                    "Warnung❗<br><br>Die zulässige Zuladung des Fahrzeugs wurde überschritten.<br>Bitte die Ladungen entsprechend anpassen."
                )
            )

        else:
            if overload:
                frappe.db.set_value(
                    "Magic Tour", magic_tour.name, "magic_vehicle_overloaded_for_date", 0
                )


@frappe.whitelist()
def set_tour_items(
    magic_tour_name, item_table_name, all_items=True, items_pick_list=None
):
    doc_changes = False
    processed_customers = set()
    magic_tour = frappe.get_doc("Magic Tour", magic_tour_name)

    if isinstance(items_pick_list, str):
        try:
            items_pick_list = json.loads(items_pick_list)
        except json.JSONDecodeError:
            frappe.throw(frappe._("Ungültiges Format für Artikel."))

    # Dictionaries to map table names to their corresponding vehicle and weight variables
    table_to_vehicle = {
        "magic_monday_table": "magic_vehicle_monday",
        "magic_tuesday_table": "magic_vehicle_tuesday",
        "magic_wednesday_table": "magic_vehicle_wednesday",
        "magic_thursday_table": "magic_vehicle_thursday",
        "magic_friday_table": "magic_vehicle_friday",
        "magic_items_table_for_date": "magic_vehicle_for_date",
    }

    table_to_weight = {
        "magic_monday_table": "magic_transport_weight_monday",
        "magic_tuesday_table": "magic_transport_weight_tuesday",
        "magic_wednesday_table": "magic_transport_weight_wednesday",
        "magic_thursday_table": "magic_transport_weight_thursday",
        "magic_friday_table": "magic_transport_weight_friday",
        "magic_items_table_for_date": "magic_transport_weight_for_date",
    }

    # Get the specific table, vehicle, and weight variables based on the item_table_name
    table = getattr(magic_tour, item_table_name, None)
    vehicle = getattr(magic_tour, table_to_vehicle.get(item_table_name), None)
    weight_var = table_to_weight[item_table_name]
    weight = getattr(magic_tour, weight_var, 0)

    if not weight:
        weight = 0

    total_weight = float(weight) or 0

    if table:
        if (all_items or all_items == "true") and not items_pick_list:
            for row in table:
                if not row.magic_customer or row.magic_customer in processed_customers:
                    continue

                items, weight_per_row = get_items_and_total_weight(row.magic_customer)
                if items:
                    doc_changes = True
                    if not row.magic_items_link:
                        tour_items_doc = frappe.get_doc(
                            {
                                "doctype": "Magic Tour Items",
                                "magic_tour_items_table": items,
                            }
                        ).insert()
                        tour_items_doc_name = tour_items_doc.name
                        row.magic_items_link = tour_items_doc_name
                    else:
                        tour_items_doc_name = row.magic_items_link
                        tour_items_doc = frappe.get_doc(
                            "Magic Tour Items", tour_items_doc_name
                        )
                        for item in items:
                            tour_items_doc.append("magic_tour_items_table", item)
                        tour_items_doc.save()

                    frappe.db.set_value(
                        "Magic Tour Tabel",
                        row.name,
                        "magic_items_link",
                        tour_items_doc_name,
                    )
                    total_weight = float(total_weight) + float(weight_per_row)
                    create_delivery_notes(row, vehicle)

                processed_customers.add(row.magic_customer)

        else:
            if items_pick_list:
                added_items = set()
                for row in table:
                    if not row.magic_customer:
                        continue

                    tour_items = []
                    total_weight_new_items = 0

                    for item in items_pick_list:
                        # check if item already added to customer, if not add
                        item_id = item["name"]
                        if (
                            item_id not in added_items
                            and item["customer"] == row.magic_customer
                        ):
                            total_weight_per_item, delivery_qty = get_item_weight(
                                item, item["undelivered_qty"]
                            )
                            doc_changes = True
                            tour_items.append(
                                {
                                    "magic_so_detail": item["name"],
                                    "magic_item_code": item["item_code"],
                                    "magic_item_name": item["item_name"],
                                    "magic_qty": item["undelivered_qty"],
                                    "magic_uom": item["uom"],
                                    "magic_total_transport_weight": total_weight_per_item,
                                    "magic_sales_order": item["sales_order_name"],
                                    "magic_warehouse": item["warehouse"],
                                }
                            )
                            added_items.add(item_id)
                            total_weight_new_items += float(total_weight_per_item)

                    if tour_items:
                        if not row.magic_items_link:
                            tour_items_doc = frappe.get_doc(
                                {
                                    "doctype": "Magic Tour Items",
                                    "magic_tour_items_table": tour_items,
                                }
                            ).insert()
                            tour_items_doc_name = tour_items_doc.name
                            row.magic_items_link = tour_items_doc_name
                        else:
                            tour_items_doc_name = row.magic_items_link
                            tour_items_doc = frappe.get_doc(
                                "Magic Tour Items", tour_items_doc_name
                            )
                            for tour_item in tour_items:
                                tour_items_doc.append("magic_tour_items_table", tour_item)
                            tour_items_doc.save()

                        frappe.db.set_value(
                            "Magic Tour Tabel",
                            row.name,
                            "magic_items_link",
                            tour_items_doc_name,
                        )
                        total_weight += float(total_weight_new_items)
                        create_delivery_notes(row, vehicle)

    if doc_changes:
        frappe.db.set_value("Magic Tour", magic_tour.name, weight_var, total_weight)
        set_tour_name_in_items(magic_tour, item_table_name)
        weight_exceeded_message(magic_tour, "custom")

    return doc_changes, len(processed_customers)


def get_items_and_total_weight(customer):
    # get sales orders and delivery notes
    sales_orders = frappe.get_all(
        "Sales Order",
        filters=[["status", "like", "%To Deliver%"], ["customer", "=", customer]],
        fields=["name"],
    )
    if not sales_orders:
        return None, None

    sales_order_items = []
    tour_items = []
    total_weight = 0

    for sales_order in sales_orders:
        sales_order_doc = frappe.get_doc("Sales Order", sales_order.name)
        for so_item in sales_order_doc.items:
            sales_order_items.append(so_item)

    for item in sales_order_items:
        total_weight_per_item, delivery_qty = get_item_weight(item)

        if delivery_qty > 0:
            tour_items.append(
                {
                    "magic_so_detail": item.name,
                    "magic_item_code": item.item_code,
                    "magic_item_name": item.item_name,
                    "magic_qty": delivery_qty,
                    "magic_uom": item.uom,
                    "magic_total_transport_weight": total_weight_per_item,
                    "magic_sales_order": item.parent,
                    "magic_warehouse": item.warehouse,
                }
            )

        total_weight += total_weight_per_item

    return tour_items, total_weight


def get_item_weight(item, qty=0):
    total_weight_per_item = 0
    collected_qty = 0

    if isinstance(item, dict):
        item_code = item.get("item_code")
        warehouse = item.get("warehouse")
        uom = item.get("uom")
        name = item.get("name")
    else:
        item_code = getattr(item, "item_code", None)
        warehouse = getattr(item, "warehouse", None)
        uom = getattr(item, "uom", None)
        name = getattr(item, "name", None)

    if qty == 0:
        delivered_qty = frappe.db.get_value("Sales Order Item", name, "delivered_qty")
        delivery_qty = getattr(item, "qty", 0) - delivered_qty
    else:
        delivery_qty = qty

    stock_entry_details = frappe.get_all(
        "Stock Entry Detail",
        filters={
            "docstatus": 1,
            "t_warehouse": warehouse,
            "item_code": item_code,
            "uom": uom,
        },
        fields=["name", "qty", "magic_transport_weight_per_warehouse_unit", "parent"],
        order_by="creation desc",
    )

    if stock_entry_details:
        for stock_entry_detail in stock_entry_details:
            stock_entry = frappe.get_doc("Stock Entry", stock_entry_detail.parent)
            if stock_entry.stock_entry_type in ["Material Transfer", "Material Receipt"]:
                if collected_qty == delivery_qty:
                    break
                available_qty = stock_entry_detail.qty
                if available_qty >= delivery_qty:
                    needed_qty = delivery_qty
                    collected_qty = delivery_qty
                elif available_qty < delivery_qty:
                    needed_qty = available_qty
                    collected_qty += needed_qty
                total_weight_per_item += (
                    stock_entry_detail.magic_transport_weight_per_warehouse_unit
                    * needed_qty
                )

    return total_weight_per_item, delivery_qty


def create_delivery_notes(tour_items_row, vehicle):
    if not tour_items_row.magic_items_link:
        return

    tour_items = frappe.get_all(
        "Magic Tour Items Table",
        filters={"parent": tour_items_row.magic_items_link},
        fields=["*"],
    )
    if not tour_items:
        return

    for tour_item in tour_items:
        if tour_item.magic_delivery_note or not tour_item.magic_sales_order:
            continue

        sales_order_doc = frappe.get_doc("Sales Order", tour_item.magic_sales_order)
        if sales_order_doc.status in [
            "Draft",
            "On Hold",
            "Cancelled",
            "Completed",
            "Closed",
        ]:
            continue

        items = []
        for item in sales_order_doc.items:
            if (
                item.name == tour_item.magic_so_detail
                and item.item_code == tour_item.magic_item_code
                and item.uom == tour_item.magic_uom
                and item.qty >= tour_item.magic_qty
            ):
                qty = tour_item.magic_qty

                if frappe.db.get_value(
                    "Magic Tour Items Table", tour_item.name, "magic_delivery_note"
                ):
                    continue
                items.append(
                    {
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "customer_item_code": item.customer_item_code,
                        "description": item.description,
                        "brand": item.brand,
                        "item_group": item.item_group,
                        "image": item.image,
                        "qty": qty,
                        "stock_uom": item.stock_uom,
                        "uom": item.uom,
                        "conversion_factor": item.conversion_factor,
                        "price_list_rate": item.price_list_rate,
                        "base_price_list_rate": item.base_price_list_rate,
                        "margin_type": item.margin_type,
                        "margin_rate_or_amount": item.margin_rate_or_amount,
                        "rate_with_margin": item.rate_with_margin,
                        "discount_percentage": item.discount_percentage,
                        "discount_amount": item.discount_amount,
                        "base_rate_with_margin": item.base_rate_with_margin,
                        "rate": item.rate,
                        "amount": item.amount,
                        "base_rate": item.base_rate,
                        "base_amount": item.base_amount,
                        "net_rate": item.net_rate,
                        "net_amount": item.net_amount,
                        "base_net_rate": item.base_net_rate,
                        "base_net_amount": item.base_net_amount,
                        "pricing_rules": item.pricing_rules,
                        "stock_uom_rate": item.stock_uom_rate,
                        "weight_per_unit": item.weight_per_unit,
                        "total_weight": item.total_weight,
                        "weight_uom": item.weight_uom,
                        "warehouse": item.warehouse,
                        "against_sales_order": sales_order_doc.name,
                        "so_detail": item.name,
                    }
                )
        if items:
            try:
                delivery_note = frappe.get_doc(
                    {
                        "doctype": "Delivery Note",
                        "customer": sales_order_doc.customer,
                        "tax_id": sales_order_doc.tax_id,
                        "cost_center": sales_order_doc.cost_center,
                        "project": sales_order_doc.project,
                        "currency": sales_order_doc.currency,
                        "conversion_rate": sales_order_doc.conversion_rate,
                        "selling_price_list": sales_order_doc.selling_price_list,
                        "price_list_currency": sales_order_doc.price_list_currency,
                        "plc_conversion_rate": sales_order_doc.plc_conversion_rate,
                        "ignore_pricing_rule": sales_order_doc.ignore_pricing_rule,
                        "set_warehouse": sales_order_doc.set_warehouse,
                        "customer_address": sales_order_doc.customer_address,
                        "address_display": sales_order_doc.address_display,
                        "contact_person": sales_order_doc.contact_person,
                        "contact_display": sales_order_doc.contact_display,
                        "contact_mobile": sales_order_doc.contact_mobile,
                        "contact_email": sales_order_doc.contact_email,
                        "shipping_address_name": sales_order_doc.shipping_address_name,
                        "shipping_address": sales_order_doc.shipping_address,
                        "dispatch_address_name": sales_order_doc.dispatch_address_name,
                        "dispatch_address": sales_order_doc.dispatch_address,
                        "company_address": sales_order_doc.company_address,
                        "company_address_display": sales_order_doc.company_address_display,
                        "tc_name": sales_order_doc.tc_name,
                        "terms": sales_order_doc.terms,
                        "per_billed": sales_order_doc.per_billed,
                        "transporter_name": vehicle,
                        "letter_head": sales_order_doc.letter_head,
                        "base_grand_total": sales_order_doc.base_grand_total,
                        "base_rounded_total": sales_order_doc.base_rounded_total,
                        "grand_total": sales_order_doc.grand_total,
                        "net_total": sales_order_doc.net_total,
                        "total": sales_order_doc.total,
                        "rounded_total": sales_order_doc.rounded_total,
                        "items": items,
                    }
                ).insert(ignore_permissions=True)
                frappe.db.set_value(
                    "Magic Tour Items Table",
                    tour_item.name,
                    "magic_delivery_note",
                    delivery_note.name,
                )
                delivery_note.submit()
                frappe.db.commit()

            except Exception:
                frappe.msgprint(
                    frappe._(
                        "Lieferschein konnte nicht erstellt oder gebucht werden. Bitte manuell prüfen."
                    )
                )


def check_changed_tour_items_and_set_weight(magic_tour_items, on_update):
    set_weight = False
    old_doc = magic_tour_items.get_doc_before_save()
    if old_doc:
        for old_item in old_doc.magic_tour_items_table:
            item_deleted = False

            if magic_tour_items.magic_tour_items_table:
                for item in magic_tour_items.magic_tour_items_table:
                    if old_item.name == item.name:
                        if item.magic_qty <= 0:
                            item_deleted = True
                            update_delivery_note(
                                item.magic_so_detail,
                                item.magic_qty,
                                frappe.db.get_value(
                                    "Magic Tour Items Table",
                                    item.name,
                                    "magic_delivery_note",
                                ),
                                delete=True,
                            )
                            frappe.delete_doc("Magic Tour Items Table", item.name)
                            break
                        else:
                            if old_item.magic_qty != item.magic_qty:
                                # set item weight and total weight
                                new_weight = (
                                    old_item.magic_total_transport_weight
                                    / old_item.magic_qty
                                    * item.magic_qty
                                )
                                frappe.db.set_value(
                                    "Magic Tour Items Table",
                                    item.name,
                                    "magic_total_transport_weight",
                                    new_weight,
                                )
                                set_weight = True
                                update_delivery_note(
                                    item.magic_so_detail,
                                    item.magic_qty,
                                    frappe.db.get_value(
                                        "Magic Tour Items Table",
                                        item.name,
                                        "magic_delivery_note",
                                    ),
                                )
                                break

            if item_deleted:
                set_weight = True

        if set_weight:
            magic_tour_table = frappe.get_all(
                "Magic Tour Tabel",
                filters={"magic_items_link": magic_tour_items.name},
                fields=["name", "parent"],
            )
            if magic_tour_table:
                set_total_weight(magic_tour_table[0].parent)


def set_total_weight(magic_tour_name):
    magic_tour = frappe.get_doc("Magic Tour", magic_tour_name)

    table_vars = []
    weight_vars = []
    overloaded_vars = []
    permissible_load_vars = []

    if magic_tour.magic_tour_type == "Tour für Woche planen":
        table_vars = [
            "magic_monday_table",
            "magic_tuesday_table",
            "magic_wednesday_table",
            "magic_thursday_table",
            "magic_friday_table",
        ]
        weight_vars = [
            "magic_transport_weight_monday",
            "magic_transport_weight_tuesday",
            "magic_transport_weight_wednesday",
            "magic_transport_weight_thursday",
            "magic_transport_weight_friday",
        ]
        overloaded_vars = [
            "magic_vehicle_overloaded_monday",
            "magic_vehicle_overloaded_tuesday",
            "magic_vehicle_overloaded_wednesday",
            "magic_vehicle_overloaded_thursday",
            "magic_vehicle_overloaded_friday",
        ]
        permissible_load_vars = [
            "magic_permissible_load_kg_monday",
            "magic_permissible_load_kg_tuesday",
            "magic_permissible_load_kg_wednesday",
            "magic_permissible_load_kg_thursday",
            "magic_permissible_load_kg_friday",
        ]

    elif magic_tour.magic_tour_type == "Tour für Datum planen":
        table_vars = ["magic_items_table_for_date"]
        weight_vars = ["magic_transport_weight_for_date"]
        overloaded_vars = ["magic_vehicle_overloaded_for_date"]
        permissible_load_vars = ["magic_permissible_load_kg_for_date"]

    for idx, var in enumerate(table_vars):
        total_weight = 0
        table = getattr(magic_tour, var)
        permissible_load = getattr(magic_tour, permissible_load_vars[idx])
        overload = getattr(magic_tour, overloaded_vars[idx])

        for row in table:
            if row.magic_items_link:
                magic_tour_items = frappe.get_doc(
                    "Magic Tour Items", row.magic_items_link
                )
                if magic_tour_items.magic_tour_items_table:
                    for item in magic_tour_items.magic_tour_items_table:
                        total_weight += item.magic_total_transport_weight

        frappe.db.set_value("Magic Tour", magic_tour_name, weight_vars[idx], total_weight)

        if total_weight > permissible_load:
            if not overload:
                frappe.db.set_value(
                    "Magic Tour", magic_tour.name, overloaded_vars[idx], 1
                )
        else:
            if overload:
                frappe.db.set_value(
                    "Magic Tour", magic_tour.name, overloaded_vars[idx], 0
                )

    frappe.msgprint(
        frappe._("Um die aktuellen Gewichte zu sehen bitte die Seite einmal neu laden.")
    )


def update_delivery_note(item_so_detail, qty, delivery_note, delete=False):
    # update delivery note if qty is changed or item removed in tour
    new_delivery_note_name = None
    if not delivery_note:
        return

    delivery_note_doc = frappe.get_doc("Delivery Note", delivery_note)
    if delivery_note_doc.docstatus != 2:
        delivery_note_doc.cancel()

    for item in delivery_note_doc.items:
        if item.so_detail == item_so_detail:
            if delete:
                delivery_note_doc.items.remove(item)
            else:
                item.qty = qty
            break

    if delivery_note_doc.items:
        new_delivery_note = delivery_note_doc
        new_delivery_note.name = None
        new_delivery_note.docstatus = 0
        new_delivery_note.insert(ignore_permissions=True)
        new_delivery_note.submit()
        new_delivery_note_name = new_delivery_note.name

    tour_items = frappe.get_all(
        "Magic Tour Items Table",
        filters={"magic_delivery_note": delivery_note},
        fields=["name"],
    )
    if tour_items:
        for tour_item in tour_items:
            frappe.db.set_value(
                "Magic Tour Items Table",
                tour_item.name,
                "magic_delivery_note",
                new_delivery_note_name,
            )

    return new_delivery_note_name


def delete_links_if_row_deleted(magic_tour, on_update):
    table_vars = []

    if magic_tour.magic_tour_type == "Tour für Woche planen":
        table_vars = [
            "magic_monday_table",
            "magic_tuesday_table",
            "magic_wednesday_table",
            "magic_thursday_table",
            "magic_friday_table",
        ]

    elif magic_tour.magic_tour_type == "Tour für Datum planen":
        table_vars = ["magic_items_table_for_date"]

    old_doc = magic_tour.get_doc_before_save()
    if old_doc:
        for var in table_vars:
            old_table = getattr(old_doc, var)
            new_table = getattr(magic_tour, var)
            for old_row in old_table:
                row_deleted = True
                for new_row in new_table:
                    if old_row.name == new_row.name:
                        row_deleted = False
                        break

                if row_deleted and old_row.magic_items_link:
                    set_total_weight(magic_tour.name)
                    tour_items_doc = frappe.get_doc(
                        "Magic Tour Items", old_row.magic_items_link
                    )
                    if tour_items_doc.magic_tour_items_table:
                        for item in tour_items_doc.magic_tour_items_table:
                            if item.magic_delivery_note:
                                try:
                                    delivery_note_doc = frappe.get_doc(
                                        "Delivery Note", item.magic_delivery_note
                                    )
                                    if delivery_note_doc.docstatus != 2:
                                        delivery_note_doc.cancel()
                                except Exception:
                                    pass

                    frappe.delete_doc("Magic Tour Items", old_row.magic_items_link)


def vehicle_allocated(doc, method):
    tuple_list = [[None, None]]

    if doc.magic_tour_type == "Tour für Woche planen":
        tuple_list = [
            ["magic_monday_date", "magic_vehicle_monday"],
            ["magic_tuesday_date", "magic_vehicle_tuesday"],
            ["magic_wednesday_date", "magic_vehicle_wednesday"],
            ["magic_thursday_date", "magic_vehicle_thursday"],
            ["magic_friday_date", "magic_vehicle_friday"],
        ]

    elif doc.magic_tour_type == "Tour für Datum planen":
        tuple_list = [["magic_date_single_tour", "magic_vehicle_for_date"]]

    for tuple in tuple_list:
        doc_tour_date = getattr(doc, tuple[0])
        doc_vehicle = getattr(doc, tuple[1])
        if doc_tour_date and doc_vehicle:
            filtered_tour_list = frappe.get_all(
                "Magic Tour",
                fields=["*"],
                filters={tuple[0]: doc_tour_date, tuple[1]: doc_vehicle, "docstatus": 1},
            )
            if len(filtered_tour_list) > 1:
                frappe.throw(
                    "Fahrzeug "
                    + doc_vehicle
                    + " bereits für den "
                    + str(doc_tour_date)
                    + " verplant: "
                    + "<a target='_blank' href="
                    + frappe.utils.get_url()
                    + "/app/magic-tour?"
                    + tuple[0]
                    + "="
                    + str(doc_tour_date)
                    + "&docstatus=1"
                    "> Gebuchte Touren</a> "
                )


@frappe.whitelist()
def get_filters(filters=None):
    conditions = []

    if isinstance(filters, str):
        try:
            filters = json.loads(filters)
        except json.JSONDecodeError:
            frappe.throw("Ungültige Filterstruktur.")

    if filters and isinstance(filters, dict) and filters.get("parent"):
        # Format the parent IDs correctly
        parent_list = ", ".join([f"'{parent}'" for parent in filters["parent"][1]])
        conditions.append(f"soi.parent IN ({parent_list})")

    conditions.append("soi.docstatus = 1")

    conditions_str = " AND ".join(conditions) if conditions else "1=1"

    query = f"""
        SELECT
            soi.name AS name,
            so.customer AS customer,
            so.customer_name AS customer_name,
            soi.item_code AS item_code,
            soi.item_name AS item_name,
            soi.uom AS uom,
            (soi.qty - soi.delivered_qty) AS undelivered_qty,
            so.name AS sales_order_name,
            soi.warehouse AS warehouse
        FROM
            `tabSales Order Item` soi
        LEFT JOIN
            `tabSales Order` so ON so.name = soi.parent
        WHERE
            {conditions_str}
        GROUP BY
            soi.name
        HAVING
            undelivered_qty > 0
    """

    return frappe.db.sql(query, as_dict=True)
