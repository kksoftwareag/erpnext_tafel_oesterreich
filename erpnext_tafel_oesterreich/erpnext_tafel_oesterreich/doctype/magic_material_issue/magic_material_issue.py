# Copyright (c) 2024, K&K Software AG and contributors
# For license information, please see license.txt

from datetime import date, datetime

import frappe
from frappe.model.document import Document


class MagicMaterialIssue(Document):
    def on_submit(self):
        self.create_material_issue()

    def create_material_issue(self):
        now = datetime.now()
        items = []
        for item in self.magic_warehouse_table:
            if item.magic_material_issue_amount == 0:
                continue
            if item.magic_material_issue_amount > item.magic_qty:
                frappe.throw(
                    "Auszubuchunde Menge in Zeile "
                    + str(item.idx)
                    + " größer als Menge im Lager."
                )
                return
            items.append(
                {
                    "s_warehouse": item.magic_warehouse,
                    "t_warehouse": "",
                    "item_code": self.magic_item,
                    "qty": item.magic_material_issue_amount,
                }
            )
        if items:
            stock_entry = frappe.get_doc(
                {
                    "doctype": "Stock Entry",
                    "stock_entry_type": "Material Issue",
                    "posting_date": date.today(),
                    "posting_time": now.strftime("%H:%M:%S"),
                    "items": items,
                    "custom_matrial_issue_doc": self.name,
                }
            ).insert()
            stock_entry.submit()

        if self.magic_empties_check and len(self.magic_empties_table) > 0:
            items = []
            for item in self.magic_empties_table:
                if item.magic_qty == 0:
                    continue
                empties_item = frappe.get_doc("Item", item.magic_empties_item)
                items.append(
                    {
                        "s_warehouse": "",
                        "t_warehouse": item.magic_warehouse,
                        "item_code": item.magic_empties_item,
                        "qty": item.magic_qty,
                        "stock_uom": empties_item.stock_uom,
                        "allow_zero_valuation_rate": 1,
                    }
                )
            if items:
                stock_entry = frappe.get_doc(
                    {
                        "doctype": "Stock Entry",
                        "stock_entry_type": "Material Receipt",
                        "posting_date": date.today(),
                        "posting_time": now.strftime("%H:%M:%S"),
                        "items": items,
                        "custom_matrial_issue_doc": self.name,
                    }
                ).insert()
                stock_entry.submit()
