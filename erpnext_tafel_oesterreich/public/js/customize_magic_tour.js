frappe.ui.form.on("Magic Tour", {
  onload(frm) {
    const vehicle_fields = [
      "magic_vehicle_template",
      "magic_vehicle_monday",
      "magic_vehicle_tuesday",
      "magic_vehicle_wednesday",
      "magic_vehicle_thursday",
      "magic_vehicle_friday",
      "magic_vehicle_for_date",
    ];
    vehicle_fields.forEach((field) => {
      frm.set_query(field, () => {
        return {
          filters: {
            custom_magic_is_vehicle: 1,
          },
        };
      });
    });
  },
  magic_tour_link(frm) {
    frappe.call({
      method:
        "erpnext_tafel_oesterreich.public.python.customize_magic_tour.fetch_tour",
      args: {
        tourname: frm.doc.magic_tour_link,
      },
      callback: function (r) {
        if (r.message) {
          frm.set_value(
            "magic_tour_table_display",
            r.message.magic_fetch_deliver_tabel,
          );
        } else {
          frm.set_value("magic_tour_table_display", []);
        }
      },
    });
  },
  magic_fetch_tour(frm) {
    frappe.call({
      method:
        "erpnext_tafel_oesterreich.public.python.customize_magic_tour.fetch_tour",
      args: {
        tourname: frm.doc.magic_tour_link,
      },
      callback: function (r) {
        let tour_loaded = 0;
        if (frm.doc.magic_tour_type == "Tour für Woche planen") {
          if (frm.doc.magic_monday_check == 1) {
            frm.set_value(
              "magic_monday_table",
              r.message.magic_fetch_deliver_tabel,
            );
            frm.set_value(
              "magic_vehicle_monday",
              frm.doc.magic_vehicle_template,
            );
            tour_loaded = 1;
          }
          if (frm.doc.magic_tuesday_check == 1) {
            frm.set_value(
              "magic_tuesday_table",
              r.message.magic_fetch_deliver_tabel,
            );
            frm.set_value(
              "magic_vehicle_tuesday",
              frm.doc.magic_vehicle_template,
            );
            tour_loaded = 1;
          }
          if (frm.doc.magic_wednesday_check == 1) {
            frm.set_value(
              "magic_wednesday_table",
              r.message.magic_fetch_deliver_tabel,
            );
            frm.set_value(
              "magic_vehicle_wednesday",
              frm.doc.magic_vehicle_template,
            );
            tour_loaded = 1;
          }
          if (frm.doc.magic_thursday_check == 1) {
            frm.set_value(
              "magic_thursday_table",
              r.message.magic_fetch_deliver_tabel,
            );
            frm.set_value(
              "magic_vehicle_thursday",
              frm.doc.magic_vehicle_template,
            );
            tour_loaded = 1;
          }
          if (frm.doc.magic_friday_check == 1) {
            frm.set_value(
              "magic_friday_table",
              r.message.magic_fetch_deliver_tabel,
            );
            frm.set_value(
              "magic_vehicle_friday",
              frm.doc.magic_vehicle_template,
            );
            tour_loaded = 1;
          }
        } else if (frm.doc.magic_tour_type == "Tour für Datum planen") {
          frm.set_value(
            "magic_items_table_for_date",
            r.message.magic_fetch_deliver_tabel,
          );
          frm.set_value(
            "magic_vehicle_for_date",
            frm.doc.magic_vehicle_template,
          );
          tour_loaded = 1;
        }
        if (tour_loaded) {
          frappe.msgprint(
            frappe._(
              "Tour wurde für ausgewählte Wochentage erfolgreich geladen. Speichern erforderlich.",
            ),
          );
        }
      },
    });
  },
  refresh(frm) {
    frm.add_custom_button(__("CSV Export"), () => {
      frappe.call({
        method:
          "erpnext_tafel_oesterreich.public.python.export_tour_as_csv.export_tour",
        args: {
          docname: frm.doc.name,
        },
        callback: function (response) {
          if (response.message) {
            var filename = response.message.filename;
            var filecontent = response.message.filecontent;

            var downloadLink = document.createElement("a");
            downloadLink.href =
              "data:text/csv;charset=utf-8," + encodeURIComponent(filecontent);
            downloadLink.download = filename;
            downloadLink.click();
          } else {
            frappe.msgprint(frappe._("Ein Fehler ist aufgetreten."));
          }
        },
      });
    });
    //set message to top if overload
    var overloaded_vars = [
      "magic_vehicle_overloaded_monday",
      "magic_vehicle_overloaded_tuesday",
      "magic_vehicle_overloaded_wednesday",
      "magic_vehicle_overloaded_thursday",
      "magic_vehicle_overloaded_friday",
      "magic_vehicle_overloaded_for_date",
    ];
    var hasOverloaded = overloaded_vars.some(function (variable) {
      return frm.doc[variable] === 1;
    });
    var weekdays = {
      monday: "Montag",
      tuesday: "Dienstag",
      wednesday: "Mittwoch",
      thursday: "Donnerstag",
      friday: "Freitag",
    };
    if (hasOverloaded) {
      let message = "";
      if (frm.doc.magic_tour_type == "Tour für Woche planen") {
        var exceeded_days = [];
        overloaded_vars.forEach(function (variable) {
          if (frm.doc[variable] === 1) {
            var day = variable.split("_").pop();
            exceeded_days.push(weekdays[day]);
          }
        });
        var exceeded_days_str = exceeded_days.join(", ");
        message = frappe._(
          "Warnung❗<br><br>Für folgende Tage wurde die zulässige Zuladung des Fahrzeugs überschritten:<br>" +
            exceeded_days_str +
            "<br><br>Bitte die Ladungen entsprechend anpassen.",
        );
      } else if (frm.doc.magic_tour_type == "Tour für Datum planen") {
        message = frappe._(
          "Warnung❗<br><br>Die zulässige Zuladung des Fahrzeugs wurde überschritten.<br>Bitte die Ladungen entsprechend anpassen.",
        );
      }

      frm.set_intro(message, "red");
    }
    if (frm.is_new()) {
      frm.set_df_property("magic_tour_type", "hidden", 0);
    } else {
      frm.set_df_property("magic_tour_type", "hidden", 1);
    }
  },
  magic_add_all_items_for_date(frm) {
    set_tour_items(frm, "magic_items_table_for_date");
  },
  magic_add_all_items_monday(frm) {
    set_tour_items(frm, "magic_monday_table");
  },
  magic_add_all_items_tuesday(frm) {
    set_tour_items(frm, "magic_tuesday_table");
  },
  magic_add_all_items_wednesday(frm) {
    set_tour_items(frm, "magic_wednesday_table");
  },
  magic_add_all_items_thursday(frm) {
    set_tour_items(frm, "magic_thursday_table");
  },
  magic_add_all_items_friday(frm) {
    set_tour_items(frm, "magic_friday_table");
  },
  magic_pick_items_for_date(frm) {
    item_pick_list(frm, "magic_items_table_for_date");
  },
  magic_pick_items_monday(frm) {
    item_pick_list(frm, "magic_monday_table");
  },
  magic_pick_items_tuesday(frm) {
    item_pick_list(frm, "magic_tuesday_table");
  },
  magic_pick_items_wednesday(frm) {
    item_pick_list(frm, "magic_wednesday_table");
  },
  magic_pick_items_thursday(frm) {
    item_pick_list(frm, "magic_thursday_table");
  },
  magic_pick_items_friday(frm) {
    item_pick_list(frm, "magic_friday_table");
  },
});

frappe.ui.form.on("Magic Tour Items", {
  onload(frm) {
    frm.get_field("magic_tour_items_table").grid.cannot_add_rows = true;
    frm.get_field("magic_tour_items_table").grid.cannot_delete_rows = true;
  },
  magic_back_to_tour(frm) {
    if (!frm.is_new()) {
      let url =
        window.location.origin + "/app/magic-tour/" + frm.doc.magic_tour;
      window.location.href = url;
    }
  },
  refresh: function (frm) {
    frm.set_df_property("magic_tour_items_table", "cannot_add_rows", true); // Hide add row button
    frm.set_df_property("magic_tour_items_table", "cannot_delete_rows", true); // Hide delete button
    frm.set_df_property(
      "magic_tour_items_table",
      "cannot_delete_all_rows",
      true,
    ); // Hide delete all button
  },
});

frappe.ui.form.on("Magic Tour", {
  magic_show_articles_monday(frm) {
    create_dialog(frm.doc.magic_monday_table);
  },

  magic_show_articles_tuesday(frm) {
    create_dialog(frm.doc.magic_tuesday_table);
  },

  magic_show_articles_wednesday(frm) {
    create_dialog(frm.doc.magic_wednesday_table);
  },

  magic_show_articles_thursday(frm) {
    create_dialog(frm.doc.magic_thursday_table);
  },

  magic_show_articles_friday(frm) {
    create_dialog(frm.doc.magic_friday_table);
  },

  magic_show_articles_for_date(frm) {
    create_dialog(frm.doc.magic_items_table_for_date);
  },
});

function create_dialog(table_of_day) {
  var all_articles = [];

  for (var element of table_of_day) {
    if (!element.magic_items_link) {
      continue;
    }

    var customer_doc = null;
    frappe.call({
      method: "frappe.client.get",
      args: {
        doctype: "Customer",
        name: element.magic_customer,
      },
      async: false,
      callback: function (response) {
        customer_doc = response.message;
      },
    });

    frappe.call({
      method: "frappe.client.get",
      args: {
        doctype: "Magic Tour Items",
        name: element.magic_items_link,
      },
      async: false,
      callback: function (response) {
        var doc = response.message;
        if (doc) {
          for (var article_item of doc.magic_tour_items_table) {
            article_item.delivery_place = customer_doc.customer_name;
            all_articles.push(article_item);
          }
        }
      },
    });
  }

  if (!all_articles || all_articles.length === 0) {
    frappe.msgprint(frappe._("An diesem Tag gibt es noch keine Artikel."));
    return;
  }

  let d = new frappe.ui.Dialog({
    title: "Artikel an diesem Tag",
    fields: [
      {
        label: "Artikel",
        fieldname: "item_table",
        fieldtype: "Table",
        cannot_add_rows: true,
        in_place_edit: false,
        read_only: 1,
        fields: [
          {
            fieldname: "item",
            fieldtype: "Data",
            options: `{{ items }}`,
            in_list_view: 1,
            label: "Artikel",
            read_only: 1,
          },
          {
            fieldname: "qty",
            fieldtype: "Data",
            default: 0,
            in_list_view: 1,
            label: "Anzahl",
            read_only: 1,
          },
          {
            fieldname: "weight",
            fieldtype: "Data",
            default: 0,
            in_list_view: 1,
            label: "Gewicht",
            read_only: 1,
          },
          {
            fieldname: "delivery_place",
            fieldtype: "Data",
            in_list_view: 1,
            label: "Lieferung an",
            read_only: 1,
          },
        ],
        data: all_articles.map(function (x) {
          return {
            item: x.magic_item_code,
            qty: x.magic_qty,
            weight: x.magic_total_transport_weight,
            delivery_place: x.delivery_place,
          };
        }),
      },
    ],
    size: "extra-large", // small, large, extra-large
    primary_action_label: "Schließen",
    primary_action() {
      d.hide();
    },
  });
  d.fields_dict["item_table"].grid.wrapper.find(".btn-open-row").hide();

  d.set_df_property("item_table", "cannot_delete_rows", true); // Hide delete button
  d.set_df_property("item_table", "cannot_delete_all_rows", true); // Hide delete all button
  d.show();
}

function set_tour_items(frm, item_table_name) {
  if (!frm.is_new() && !frm.doc.__islocal) {
    frappe.confirm(
      __(
        "Sind Sie sicher, dass Sie alle offenen Bedarfsmeldungen für die Sozialeinrichtungen der Tabelle hinzufügen wollen?",
      ),
      function () {
        frappe.call({
          method:
            "erpnext_tafel_oesterreich.public.python.customize_magic_tour.set_tour_items",
          args: {
            magic_tour_name: frm.doc.name,
            item_table_name: item_table_name,
            all_items: true,
          },
          callback: function (r) {
            if (r.message[0] == true) {
              frm.reload_doc();
              frappe.msgprint(frappe._("Waren wurden hinzugefügt."));
            } else {
              if (r.message[1] == 0) {
                frappe.msgprint(
                  frappe._(
                    "Bitte fügen Sie der Tabelle erst Sozialeinrichtungen hinzu.",
                  ),
                );
              } else {
                frappe.msgprint(
                  frappe._(
                    "Es gibt keine offenen Bedarfsmeldungen für die Sozialeinrichtungen in der Tabelle.",
                  ),
                );
              }
            }
          },
        });
      },
    );
  } else {
    frappe.msgprint(frappe._("Bitte erst das Dokument speichern!"));
  }
}

function item_pick_list(frm, item_table_name) {
  if (!frm.is_new() && !frm.doc.__islocal) {
    get_child_items({
      frm: frm,
      item_table_name: item_table_name,
    });
  } else {
    frappe.msgprint(frappe._("Bitte erst das Dokument speichern!"));
  }
}

function get_child_items(opts) {
  const frm = opts.frm;
  const item_table_name = opts.item_table_name;

  if (!frm || !item_table_name) {
    frappe.msgprint(
      frappe._("Fehler: Form oder Tabellenname nicht definiert."),
    );
    return;
  }

  let customers = [];
  if (frm.doc[item_table_name] && frm.doc[item_table_name].length > 0) {
    for (let row of frm.doc[item_table_name]) {
      if (row.magic_customer && !customers.includes(row.magic_customer)) {
        customers.push(row.magic_customer);
      }
    }
  }

  if (customers.length === 0) {
    frappe.msgprint(
      frappe._("Es gibt keine Sozialeinrichtungen in der Tabelle."),
    );
    return;
  }

  frappe.call({
    method: "frappe.client.get_list",
    args: {
      doctype: "Sales Order",
      filters: [
        ["customer", "in", customers],
        ["docstatus", "=", 1],
        [
          "status",
          "not in",
          ["Draft", "On Hold", "Cancelled", "Completed", "Closed"],
        ],
      ],
      fields: ["name"],
      limit_page_length: 10000,
    },
    callback: function (r) {
      if (r.message && r.message.length > 0) {
        let sales_order_names = r.message.map((so) => so.name);

        let query_args = {
          query:
            "erpnext_tafel_oesterreich.public.python.customize_magic_tour.get_filters",
          filters: {
            parent: ["in", sales_order_names],
          },
        };

        frappe.call({
          method: query_args.query,
          args: {
            filters: query_args.filters,
          },
          callback: function (data_response) {
            if (data_response.message && data_response.message.length > 0) {
              let data = data_response.message.map((d) => {
                return {
                  name: d.name,
                  customer: d.customer,
                  customer_name: d.customer_name,
                  item_code: d.item_code,
                  item_name: d.item_name,
                  original_undelivered_qty: d.undelivered_qty,
                  undelivered_qty: d.undelivered_qty,
                  uom: d.uom,
                  sales_order_name: d.sales_order_name,
                  warehouse: d.warehouse,
                };
              });

              let dialog_fields = [
                {
                  fieldname: "trans_items",
                  fieldtype: "Table",
                  label: "Items",
                  cannot_add_rows: true,
                  cannot_delete_rows: true,
                  fields: [
                    {
                      fieldname: "customer_name",
                      label: "Customer",
                      fieldtype: "Data",
                      in_list_view: 1,
                      reqd: 1,
                      read_only: 1,
                    },
                    {
                      fieldname: "item_code",
                      label: "Item Code",
                      fieldtype: "Link",
                      options: "Item",
                      in_list_view: 1,
                      reqd: 1,
                      read_only: 1,
                    },
                    {
                      fieldname: "item_name",
                      label: "Item Name",
                      fieldtype: "Data",
                      in_list_view: 1,
                      reqd: 1,
                      read_only: 1,
                    },
                    {
                      fieldname: "undelivered_qty",
                      label: "Menge",
                      fieldtype: "Float",
                      in_list_view: 1,
                      precision: 2,
                      read_only: 0,
                    },
                    {
                      fieldname: "uom",
                      label: "UOM",
                      fieldtype: "Link",
                      options: "UOM",
                      in_list_view: 1,
                      reqd: 1,
                      read_only: 1,
                    },
                  ],
                  data: data,
                },
              ];

              let dialog = new frappe.ui.Dialog({
                title: __("Waren zu Tour hinzufügen"),
                fields: dialog_fields,
                size: "large",
                primary_action_label: __("Hinzufügen"),
                primary_action: function () {
                  let trans_items = dialog.get_values()["trans_items"];
                  let valid = trans_items.every(
                    (item) =>
                      item.undelivered_qty <= item.original_undelivered_qty &&
                      item.undelivered_qty >= 1,
                  );
                  let selected_items =
                    dialog.fields_dict.trans_items.grid.get_selected_children();

                  if (!valid) {
                    frappe.msgprint(
                      frappe._(
                        "Die eingegebene Menge darf nicht größer als die nicht bestellte Menge sein und nicht kleiner als 1.",
                      ),
                    );
                    return;
                  }

                  if (selected_items.length === 0) {
                    frappe.msgprint(
                      frappe._("Es wurden keine Artikel ausgewählt."),
                    );
                    return;
                  }

                  frappe.call({
                    method:
                      "erpnext_tafel_oesterreich.public.python.customize_magic_tour.set_tour_items",
                    args: {
                      magic_tour_name: frm.doc.name,
                      item_table_name: item_table_name,
                      all_items: false,
                      items_pick_list: JSON.stringify(selected_items),
                    },
                    callback: function (r) {
                      if (r.message[0] == true) {
                        frm.reload_doc();
                        frappe.msgprint(frappe._("Waren wurden hinzugefügt."));
                      } else {
                        if (r.message[1] == 0) {
                          frappe.msgprint(
                            frappe._(
                              "Bitte fügen Sie der Tabelle erst Sozialeinrichtungen hinzu.",
                            ),
                          );
                        } else {
                          frappe.msgprint(
                            frappe._(
                              "Es gibt keine offenen Bedarfsmeldungen für die Sozialeinrichtungen in der Tabelle.",
                            ),
                          );
                        }
                      }
                    },
                  });
                  dialog.hide();
                },
              });

              dialog.show();
            } else {
              frappe.msgprint(
                frappe._(
                  "Es gibt keine Bedarfsmeldungen für die ausgewählten Sozialeinrichtungen.",
                ),
              );
            }
          },
        });
      } else {
        frappe.msgprint(
          frappe._(
            "Es gibt keine Bedarfsmeldungen für die ausgewählten Sozialeinrichtungen.",
          ),
        );
      }
    },
  });
}
