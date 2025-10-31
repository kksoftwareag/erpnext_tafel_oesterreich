app_name = "erpnext_tafel_oesterreich"
app_title = "Erpnext Tafel Oesterreich"
app_publisher = "K&K Software AG"
app_description = "New Frappe App for Die Tafel Oesterreich"
app_email = "erpnext-support@kk-software.de"
app_license = "GPL-3.0-only"
# required_apps = []

# Includes in <head>
# ------------------

# fixtures = [{"dt":"Item Group", "filters": [["name", "in", ("Leergut")]]}]
# fixtures = [
#     {
#         "dt": "Print Format",
#         "filters": [
#             [
#                 "name",
#                 "in",
#                 [
#                    "Fahrauftrag Montag",
#                    "Fahrauftrag Dienstag",
#                    "Fahrauftrag Mittwoch",
#                    "Fahrauftrag Donnerstag",
#                    "Fahrauftrag Freitag",
#                    "Fahrauftrag spezifisches Datum",
#                 ],
#             ]
#         ],
#     }
# ]

# include js, css files in header of desk.html
# app_include_css = "/assets/erpnext_tafel_oesterreich/css/erpnext_tafel_oesterreich.css"
# app_include_js = "/assets/erpnext_tafel_oesterreich/js/erpnext_tafel_oesterreich.js"

app_include_js = [
    "/assets/erpnext_tafel_oesterreich/js/donor_groceries_filters.js",
    "/assets/erpnext_tafel_oesterreich/js/customize_item.js",
    "/assets/erpnext_tafel_oesterreich/js/customize_item_group.js",
    "/assets/erpnext_tafel_oesterreich/js/customize_magic_donor_groceries_registration.js",
    "/assets/erpnext_tafel_oesterreich/js/customize_magic_tour_template.js",
    "/assets/erpnext_tafel_oesterreich/js/customize_magic_tour.js",
    "/assets/erpnext_tafel_oesterreich/js/customize_magic_task.js",
    "/assets/erpnext_tafel_oesterreich/js/customize_user.js",
    "/assets/erpnext_tafel_oesterreich/js/customize_sales_order.js",
]

# include js, css files in header of web template
# web_include_css = "/assets/erpnext_tafel_oesterreich/css/erpnext_tafel_oesterreich.css"
web_include_js = ["/assets/erpnext_tafel_oesterreich/js/portal/customize_orders.js"]

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "erpnext_tafel_oesterreich/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "erpnext_tafel_oesterreich/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "erpnext_tafel_oesterreich.utils.jinja_methods",
# 	"filters": "erpnext_tafel_oesterreich.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "erpnext_tafel_oesterreich.install.before_install"
# after_install = "erpnext_tafel_oesterreich.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "erpnext_tafel_oesterreich.uninstall.before_uninstall"
# after_uninstall = "erpnext_tafel_oesterreich.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "erpnext_tafel_oesterreich.utils.before_app_install"
# after_app_install = "erpnext_tafel_oesterreich.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "erpnext_tafel_oesterreich.utils.before_app_uninstall"
# after_app_uninstall = "erpnext_tafel_oesterreich.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpnext_tafel_oesterreich.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
    "Magic Task": "erpnext_tafel_oesterreich.public.python.customize_magic_task_listview.get_permission_query_conditions"
}

has_permission = {
    "Magic Task": "erpnext_tafel_oesterreich.public.python.customize_magic_task_listview.has_permission"
}

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Item Group": {
        "on_update": "erpnext_tafel_oesterreich.public.python.customize_item.set_mhd_plus_date_on_change"
    },
    "Magic Donor Groceries Regestration": {
        "on_submit": [
            "erpnext_tafel_oesterreich.public.python.create_webshop_item.create_item",
            "erpnext_tafel_oesterreich.public.python.create_barcode.create_barcode",
        ]
    },
    "Magic Tour": {
        "on_update": [
            "erpnext_tafel_oesterreich.public.python.customize_magic_tour.delete_links_if_row_deleted",
            "erpnext_tafel_oesterreich.public.python.customize_magic_tour.weight_exceeded_message",
        ],
        "on_submit": "erpnext_tafel_oesterreich.public.python.customize_magic_tour.vehicle_allocated",
    },
    "Magic Tour Items": {
        "on_update": "erpnext_tafel_oesterreich.public.python.customize_magic_tour.check_changed_tour_items_and_set_weight",
    },
    "User": {
        "after_insert": "erpnext_tafel_oesterreich.public.python.customize_user.create_qualifications_doc",
    },
    "Website Item": {
        "after_insert": "erpnext_tafel_oesterreich.public.python.customize_item.update_donor_reference",
    },
    "Delivery Note": {
        "on_submit": "erpnext_tafel_oesterreich.public.python.customize_sales_order.set_tourstatus",
        "on_update_after_submit": "erpnext_tafel_oesterreich.public.python.customize_sales_order.set_tourstatus",
    },
}
# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"erpnext_tafel_oesterreich.tasks.all"
# 	],
# 	"daily": [
# 		"erpnext_tafel_oesterreich.tasks.daily"
# 	],
# 	"hourly": [
# 		"erpnext_tafel_oesterreich.tasks.hourly"
# 	],
# 	"weekly": [
# 		"erpnext_tafel_oesterreich.tasks.weekly"
# 	],
# 	"monthly": [
# 		"erpnext_tafel_oesterreich.tasks.monthly"
# 	],
# }

scheduler_events = {
    "cron": {
        "0 5 * * *": [
            "erpnext_tafel_oesterreich.public.python.best_before_notification.notify_users"
        ],
    },
}


website_route_rules = [
    {"from_route": "/subscriptions", "to_route": "/subscription_web"},
]

# Testing
# -------

# before_tests = "erpnext_tafel_oesterreich.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpnext_tafel_oesterreich.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "erpnext_tafel_oesterreich.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["erpnext_tafel_oesterreich.utils.before_request"]
# after_request = ["erpnext_tafel_oesterreich.utils.after_request"]

# Job Events
# ----------
# before_job = ["erpnext_tafel_oesterreich.utils.before_job"]
# after_job = ["erpnext_tafel_oesterreich.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"erpnext_tafel_oesterreich.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
