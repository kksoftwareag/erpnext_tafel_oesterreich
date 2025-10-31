frappe.ui.form.on("Magic Tour Template", {
  magic_tour_active(frm) {
    if (frm.doc.magic_tour_active == 1) {
      frm.doc.status = "aktiv";
    } else if (frm.doc.magic_tour_active == 0) {
      frm.doc.status = "inaktiv";
    }
  },
});
