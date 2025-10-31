frappe.ui.form.on("Magic Donor Groceries Regestration", {
  magic_supplier_link(frm) {
    frappe.call({
      method:
        "erpnext_tafel_oesterreich.public.python.customize_magic_donor_groceries_registration.set_supplier_name",
      args: {
        supplier: frm.doc.magic_supplier_link,
      },
      callback: function (r) {
        frm.set_value("magic_supplier_actual_name", r.message);
      },
    });
  },
  magic_item_link(frm) {
    frm.set_value("magic_item_name", frm.doc.magic_item_link);
    frappe.db.get_doc("Item", frm.doc.magic_item_link).then((item_doc) => {
      frm.set_value("magic_description_box", item_doc.description);
      frm.set_value("magic_description", item_doc.description);
      frm.set_value(
        "magic_temperature_range",
        item_doc.magic_temperature_range,
      );
      frm.set_value("magic_warehouse_uom", item_doc.stock_uom);
      frm.set_value("magic_weight_uom", item_doc.weight_uom);
      frm.set_value("magic_item_maingroup", item_doc.magic_item_maingroup);
      frm.set_value("magic_secondary_item_group", item_doc.item_group);
      for (var i = 0; i < frm.doc.magic_uoms.length; i++) {
        frm.get_field("magic_uoms").grid.grid_rows[i].remove();
      }
      for (let i = 0; i < item_doc.uoms.length; i++) {
        var child = frm.add_child("magic_uoms");
        frappe.model.set_value(
          child.doctype,
          child.name,
          "uom",
          item_doc.uoms[i].uom,
        );
        frappe.model.set_value(
          child.doctype,
          child.name,
          "conversion_factor",
          item_doc.uoms[i].conversion_factor,
        );
      }
    });
  },
  magic_amount_warehouse_unit(frm) {
    if (frm.doc.magic_transport_weight_per_warehouse_unit) {
      frm.set_value(
        "magic_total_transport_weight",
        frm.doc.magic_amount_warehouse_unit *
          frm.doc.magic_transport_weight_per_warehouse_unit,
      );
    }
  },
  magic_transport_weight_per_warehouse_unit(frm) {
    if (frm.doc.magic_amount_warehouse_unit) {
      frm.set_value(
        "magic_total_transport_weight",
        frm.doc.magic_amount_warehouse_unit *
          frm.doc.magic_transport_weight_per_warehouse_unit,
      );
    }
  },
});
