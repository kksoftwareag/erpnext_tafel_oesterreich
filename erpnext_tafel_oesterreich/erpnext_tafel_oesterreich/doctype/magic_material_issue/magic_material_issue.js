// Copyright (c) 2024, K&K Software AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Magic Material Issue", {
  magic_item(frm) {
    for (var i = 0; i < frm.doc.magic_warehouse_table.length; i++) {
      frm.get_field("magic_warehouse_table").grid.grid_rows[i].remove();
    }
    fetch_warehouse_table_values(frm);
  },
  setup(frm) {
    frm.fields_dict["magic_empties_table"].grid.get_field(
      "magic_empties_item",
    ).get_query = function () {
      return {
        filters: [["Item", "magic_item_maingroup", "=", "Leergut"]],
      };
    };
    frm.set_df_property("magic_warehouse_table", "cannot_delete_rows", true);
    frm.set_df_property(
      "magic_warehouse_table",
      "cannot_delete_all_rows",
      true,
    );
    frm.set_df_property("magic_warehouse_table", "cannot_add_rows", true);
    frm.fields_dict.magic_warehouse_table.$wrapper
      .find(".grid-row-check")
      .hide();
  },
});

function fetch_warehouse_table_values(frm) {
  frappe.call({
    method:
      "erpnext_tafel_oesterreich.public.python.fetch_warehouse_stocks.fetch_warehouse",
    args: {
      item_name: frm.doc.magic_item,
    },
    callback: function (r) {
      if (r.message.lenght != 0) {
        for (let i = 0; i < r.message.length; i++) {
          if (r.message[i].actual_qty > 0) {
            var child = frm.add_child("magic_warehouse_table");
            frappe.model.set_value(
              child.doctype,
              child.name,
              "magic_warehouse",
              r.message[i].warehouse,
            );
            frappe.model.set_value(
              child.doctype,
              child.name,
              "magic_qty",
              r.message[i].actual_qty,
            );
          }
        }
      }
    },
  });
  frm.set_df_property("magic_warehouse_table", "cannot_delete_rows", true);
  frm.set_df_property("magic_warehouse_table", "cannot_delete_all_rows", true);
  frm.set_df_property("magic_warehouse_table", "cannot_add_rows", true);
  frm.fields_dict.magic_warehouse_table.$wrapper.find(".grid-row-check").hide();
}

frappe.ui.form.on("Magic Material Issue Table", {
  magic_material_issue_amount: function (frm) {
    let notice_text = "";
    for (let i = 0; i < frm.doc.magic_warehouse_table.length; i++) {
      if (
        frm.doc.magic_warehouse_table[i].magic_qty -
          frm.doc.magic_warehouse_table[i].magic_material_issue_amount ==
        0
      ) {
        notice_text +=
          "Restmenge im Lager " +
          frm.doc.magic_warehouse_table[i].magic_warehouse +
          " ist gleich 0 <br>";
      }
    }
    if (notice_text != "") {
      frm.set_intro("");
      frm.set_intro(notice_text);
    }
  },
});
