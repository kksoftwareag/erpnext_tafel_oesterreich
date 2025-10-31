// Copyright (c) 2024, K&K Software AG and contributors
// For license information, please see license.txt

frappe.query_reports["Leergut"] = {
  filters: [
    {
      fieldname: "supplier",
      label: __("Supplier"),
      fieldtype: "Link",
      options: "Supplier",
    },
    {
      fieldname: "start_date",
      label: __("Startdatum"),
      fieldtype: "Date",
      reqd: 1,
    },
    {
      fieldname: "end_date",
      label: __("Enddatum"),
      fieldtype: "Date",
      reqd: 1,
    },
    {
      fieldname: "item",
      label: __("Item"),
      fieldtype: "Link",
      options: "Item",
      get_query: function () {
        return {
          filters: {
            magic_item_maingroup: "Leergut",
          },
        };
      },
    },
  ],
};
