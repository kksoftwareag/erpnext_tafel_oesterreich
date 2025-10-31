import urllib

import frappe


@frappe.whitelist()
def send_mail_to_enrolled_user_and_responsible_staff(
    name_of_doc, magic_name_of_doc, enrolled_user, responsible_person
):
    url_encoded_name = urllib.parse.quote(name_of_doc)
    link = frappe.utils.get_url() + "/app" + "/magic-task/" + url_encoded_name

    message = f"""<p>Hallo ERPNext User,</p>
        <p>{enrolled_user} hat sich von der Tätigkeit {magic_name_of_doc} abgemeldet, was mit dieser E-Mail bestätigt wird.</p>
        <p><a href={link}><b>Link zur Tätigkeit</b></a></p>
        <br>
        <p>Viele Grüße,</p>
        <p>dein ERPNext</p>"""

    subject = f"""Bestätigungsmail Abmeldung {enrolled_user} von Tätigkeit {magic_name_of_doc}"""
    send_mail(subject, [enrolled_user, responsible_person], message)


def send_mail(subject, recipient, message):
    frappe.sendmail(recipients=recipient, subject=subject, message=message, now=True)
