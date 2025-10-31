variable "PROJECT_NAME" {}
variable "BUILD_NUMBER" {}
variable "BRANCH_MAPPED" {}
variable "FRAPPE_VERSION" {}
variable "CUSTOM_APP_NAME" {}
variable "NODE_VERSION" {}
variable "PYTHON_VERSION" {}
variable "APPS_JSON_BASE64" {}

target "default" {
    dockerfile = "Containerfile"
    tags = [
      "quay.io/kksoftware/erpnext-${PROJECT_NAME}:latest",
      "quay.io/kksoftware/erpnext-${PROJECT_NAME}:${BUILD_NUMBER}",
      "quay.io/kksoftware/erpnext-${PROJECT_NAME}:${BRANCH_MAPPED}"
    ]
    args = {
      "FRAPPE_BRANCH" = FRAPPE_VERSION
      "CUSTOM_APP_NAME" = CUSTOM_APP_NAME
      "NODE_VERSION" = NODE_VERSION
      "PYTHON_VERSION" = PYTHON_VERSION
      "APPS_JSON_BASE64" = APPS_JSON_BASE64
    }
}