frappe.ui.form.on("Item", {
  refresh(frm) {
    frm.set_query("magic_item_maingroup", () => {
      return {
        filters: {
          is_group: 1,
        },
      };
    });
    if (frm.doc.magic_item_maingroup) {
      filter_item_undergroup(frm);
    }
  },
  magic_item_maingroup(frm) {
    frm.set_value("item_group", "");
    filter_item_undergroup(frm);
  },
});

function filter_item_undergroup(frm) {
  frm.set_query("item_group", () => {
    return {
      filters: {
        parent_item_group: frm.doc.magic_item_maingroup,
        is_group: 0,
      },
    };
  });
}
