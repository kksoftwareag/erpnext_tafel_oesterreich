from datetime import date

import frappe


def notify_users():
    user_table = frappe.get_all(
        "Magic E-Mail Table",
        fields=["*"],
        filters={"parent": "Magic Best Before Configuration"},
    )
    days_before_sending_mail = frappe.get_doc(
        "Magic Best Before Configuration"
    ).magic_days_best_before_plus

    recipients = [user.magic_user_link for user in user_table]
    stock_entry_items = frappe.get_all(
        "Stock Entry Detail",
        fields=["*"],
        filters={"magic_best_before_date_plus": [">", date.today()]},
    )

    if len(stock_entry_items) == 0:
        return

    table_rows = get_rows(stock_entry_items, days_before_sending_mail)

    if table_rows:
        message = (
            """
        <p>Hallo ERPNext User,</p>
        <p>folgende Produkte werden das MHD+ Datum in """
            + str(days_before_sending_mail)
            + """ Tagen erreichen:</p><br>
            <table>
                <tr>
                    <th>Artikel</th>
                    <th>Menge</th>
                    <th>MHD+</th>
                    <th>Lagerplatz</th>
                </tr>
                """
            + table_rows
            + """
            </table><br>
        <p>Viele Grüße,</p>
        <p>dein ERPNext</p>
        """
        )

        frappe.sendmail(
            recipients=recipients,
            subject="Produkte vom Ablauf in "
            + str(days_before_sending_mail)
            + " Tagen betroffen!",
            message=message,
        )


def get_rows(items, days_before_sending_mail):
    table_rows = ""
    for item in items:
        date_difference = item.magic_best_before_date_plus - date.today()
        if date_difference.days == days_before_sending_mail:
            table_rows += (
                """
                <tr>
                    <td>"""
                + item.item_code
                + """</td>
                    <td>"""
                + str(item.qty)
                + """</td>
                    <td>"""
                + str(item.magic_best_before_date_plus)
                + """</td>
                    <td> <a href="""
                + frappe.utils.get_url()
                + """/app/stock-entry/"""
                + item.parent
                + """>"""
                + item.t_warehouse
                + """</a></td>
                </tr>
            """
            )
    return table_rows
