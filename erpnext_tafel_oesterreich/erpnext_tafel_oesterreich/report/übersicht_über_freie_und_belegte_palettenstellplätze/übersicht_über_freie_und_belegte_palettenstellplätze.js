// Copyright (c) 2024, K&K Software AG and contributors
// For license information, please see license.txt

frappe.query_reports["Übersicht über freie und belegte Palettenstellplätze"] = {
  filters: [
    {
      fieldname: "company",
      label: __("Company"),
      fieldtype: "Link",
      options: "Company",
      reqd: 1,
      default: frappe.defaults.get_user_default("Company"),
    },
    {
      fieldname: "warehouse",
      label: __("Warehouse"),
      fieldtype: "Link",
      options: "Warehouse",
      get_query: function () {
        return {
          filters: {
            is_group: 1,
          },
        };
      },
    },
  ],
  initial_depth: 3,
  tree: true,
  parent_field: "parent_warehouse",
  name_field: "warehouse",
};
