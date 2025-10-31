frappe.ui.form.on("Magic Task", {
  onload(frm) {
    frm.set_query("magic_vehicle", "magic_vehicles", () => {
      return {
        filters: {
          custom_magic_is_vehicle: 1,
        },
      };
    });
  },
});

frappe.ui.form.on("Magic Task", {
  refresh(frm) {
    frm.add_custom_button(__("Für Tätigkeit anmelden"), function () {
      // Check if the user is already enrolled
      let is_user_enrolled = frm.doc.magic_enrolled_users.some(function (row) {
        return row.magic_enrolled_user === frappe.user.name;
      });

      if (is_user_enrolled) {
        frappe.throw("Du bist bereits für diese Tätigkeit angemeldet!");
      }

      frappe.confirm(
        "Möchtest Du dich für diese Tätigkeit wirklich anmelden? (Das Dokument wird im Anschluss gespeichert und die Anmeldung ist damit abgeschlossen)",
        () => {
          // action to perform if Yes is selected
          let new_row = frm.add_child("magic_enrolled_users"); // Add a new row to the 'items' table
          new_row.magic_enrolled_user = frappe.user.name;

          frm.save();
        },
        () => {
          // action to perform if No is selected
        },
      );
    });

    frm.add_custom_button(__("Von Tätigkeit abmelden"), function () {
      // Check if the user is already enrolled
      let is_user_enrolled = frm.doc.magic_enrolled_users.some(function (row) {
        return row.magic_enrolled_user === frappe.user.name;
      });

      if (!is_user_enrolled) {
        frappe.throw("Du bist nicht für diese Tätigkeit angemeldet!");
      }

      frappe.confirm(
        "Möchtest Du dich für diese Tätigkeit wirklich abmelden? (Das Dokument wird im Anschluss gespeichert und die Abmeldung ist damit abgeschlossen)",
        () => {
          // Iteriere durch die Zeilen der Tabelle, um die passende zu finden
          let row_to_remove = null;
          frm.doc.magic_enrolled_users.forEach(function (row, index) {
            if (row.magic_enrolled_user === frappe.user.name) {
              row_to_remove = index;
            }
          });

          // Wenn die Zeile gefunden wurde, entferne sie
          if (row_to_remove !== null) {
            frm
              .get_field("magic_enrolled_users")
              .grid.grid_rows[row_to_remove].remove();
          }

          frm.save();

          frappe.call({
            method:
              "erpnext_tafel_oesterreich.public.python.customize_magic_task.send_mail_to_enrolled_user_and_responsible_staff",
            args: {
              name_of_doc: frm.doc.name,
              magic_name_of_doc: frm.doc.magic_name,
              enrolled_user: frappe.user.name,
              responsible_person: frm.doc.magic_task_responsible_person,
            },
            async: true,
            callback: function () {},
          });
        },
        () => {
          // action to perform if No is selected
        },
      );
    });
  },
});
