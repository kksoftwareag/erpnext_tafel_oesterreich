frappe.ui.form.on("Item Group", {
  parent_item_group(frm) {
    frappe.db
      .get_doc("Item Group", frm.doc.parent_item_group)
      .then((item_group_doc) => {
        frm.set_value(
          "magic_shelf_life_in_days",
          item_group_doc.magic_shelf_life_in_days,
        );
      });
  },
});
