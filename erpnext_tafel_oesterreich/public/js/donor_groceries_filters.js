frappe.ui.form.on("Magic Donor Groceries Regestration", {
  setup: function (frm) {
    frm.set_query("magic_item_link", function () {
      return {
        filters: [["Item", "custom_status", "=", "Sammelartikel"]],
      };
    });
    frm.set_query("magic_warehouse_link", function () {
      return {
        filters: [["Warehouse", "is_group", "=", 0]],
      };
    });
    frm.fields_dict["magic_empties_table"].grid.get_field(
      "magic_empties_item",
    ).get_query = function () {
      return {
        filters: [["Item", "magic_item_maingroup", "=", "Leergut"]],
      };
    };
    frm.fields_dict["magic_warehouse_table"].grid.get_field(
      "magic_warehouse",
    ).get_query = function () {
      return {
        filters: [["Warehouse", "is_group", "=", 0]],
      };
    };
  },
  magic_item_link: function (frm) {
    set_best_before_date_plus(frm);
  },
  magic_best_before_date: function (frm) {
    set_best_before_date_plus(frm);
  },
});

function set_best_before_date_plus(frm) {
  if (frm.doc.magic_best_before_date && frm.doc.magic_item_link) {
    frappe.db.get_doc("Item", frm.doc.magic_item_link).then((item_doc) => {
      let best_before_date_plus = new Date(frm.doc.magic_best_before_date);
      best_before_date_plus.setDate(
        best_before_date_plus.getDate() + item_doc.magic_shelf_life_in_days,
      );
      frm.set_value("magic_best_before_date_plus", best_before_date_plus);
    });
  }
}
