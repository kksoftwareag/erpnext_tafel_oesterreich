frappe.ui.form.on("Sales Order", {
  refresh(frm) {
    frm.get_field("custom_magic_html_for_reference_text").$wrapper.empty();
    if (frm.doc.custom_magic_is_reference_for_auto_repeat) {
      frm
        .get_field("custom_magic_html_for_reference_text")
        .$wrapper.append(
          '<h2 style="color: red; font-weight: bold; text-align: center;">🚧 Bitte lesen! 🚧 Dieses Dokument ist ein Referenzdokument für Abonnements von Organisationen oder wurde automatisch im Rahmen eines Abonnements erstellt. Auf gar keinen Fall löschen oder buchen!</h2>',
        );
    }
  },
});
