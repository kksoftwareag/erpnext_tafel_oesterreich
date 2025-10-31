frappe.ui.form.on("User", {
  refresh(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__("Qualifikationen"), () => {
        frappe.db
          .get_doc("Magic User Qualifications", frm.doc.name)
          .then(() => {
            let url =
              window.location.origin +
              "/app/magic-user-qualifications/" +
              frm.doc.name;
            window.location.href = url;
          });
      });
    }
  },
});
