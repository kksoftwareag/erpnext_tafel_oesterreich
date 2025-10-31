//check if we are in an order
if (window.location.href.indexOf("orders/") != -1) {
  let indicator_pill_span =
    document.getElementsByClassName("indicator-pill")[0];
  const acceptedStatus = ["Storniert", "Cancelled", "Abgesagt"];

  if (acceptedStatus.includes(indicator_pill_span.innerText)) {
    document.getElementById("pay-for-order").remove();
    document.getElementsByClassName("dropdown-toggle")[0].remove();
  }
  let page_header_action_block_div = document.querySelector(
    ".page-header-actions-block",
  );
  let dropdown_menu_ul =
    page_header_action_block_div.querySelector(".dropdown-menu");

  let dropdown_item_a = document.createElement("a");
  dropdown_item_a.classList.add("dropdown-item");
  dropdown_item_a.target = "_blank";
  dropdown_item_a.rel = "noopener noreferrer";
  dropdown_item_a.setAttribute("id", "dropdown-cancel-option");
  dropdown_item_a.innerText = frappe._("Stornieren");

  dropdown_item_a.addEventListener("click", function () {
    let confirmationModal = `
            <div class="modal" tabindex="-1" role="dialog">
                <div class="modal-dialog" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Stornierung bestätigen</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <p>Bist du sicher, dass du diese Bestellung stornieren möchtest?</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-dismiss="modal">Abbrechen</button>
                            <button type="button" class="btn btn-primary">Ja</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

    // HTML in die Seite einfügen
    document.body.insertAdjacentHTML("beforeend", confirmationModal);

    // Modalfenster anzeigen
    let modal = document.querySelector(".modal");
    $(modal).modal("show");

    // Aktion beim Klicken auf "Ja"
    let yesButton = modal.querySelector(".btn-primary");
    yesButton.addEventListener("click", function () {
      cancel_order_in_portal_orders();
      $(modal).modal("hide");
    });

    // Aufräumen nach dem Schließen des Modalfensters
    $(modal).on("hidden.bs.modal", function () {
      modal.remove();
    });
  });

  dropdown_menu_ul.appendChild(dropdown_item_a);
}

function cancel_order_in_portal_orders() {
  frappe.call({
    method:
      "erpnext_tafel_oesterreich.public.python.customize_sales_order.cancel_sales_order_from_portal",
    args: {
      sales_order_name: window.location.href.split("orders/")[1],
    },
    callback: (r) => {
      if (r.message[0]) {
        let indicator_pill_span =
          document.getElementsByClassName("indicator-pill")[0];
        indicator_pill_span.innerText = frappe._("Storniert");
        indicator_pill_span.classList.remove("orange");
        indicator_pill_span.classList.add("red");
        document.getElementById("pay-for-order").remove();
        document.getElementsByClassName("dropdown-toggle")[0].remove();
      } else {
        frappe.throw(frappe._(r.message[1]));
      }
    },
  });
}
