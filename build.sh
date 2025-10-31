#!/bin/bash

export PROJECT_NAME="tafel_oesterreich"
export CUSTOM_APP_NAME="erpnext_tafel_oesterreich"
export PYTHON_VERSION="3.11.12"
export NODE_VERSION="18.20.8"
export FRAPPE_VERSION="v15.63.1"
BRANCH_MAPPED_1=${BRANCH/refs\/heads\//""}
export BRANCH_MAPPED=${BRANCH_MAPPED_1/\//"-"}

APPS_JSON="[
  {
    \"url\": \"https://github.com/frappe/erpnext\",
    \"branch\": \"v15.57.5\"
  },
  {
    \"url\": \"https://github.com/frappe/hrms\",
    \"branch\": \"v15.43.0\"
  },
    {
    \"url\": \"https://github.com/frappe/payments\",
    \"branch\": \"version-15\"
  },
  {
    \"url\": \"https://github.com/kksoftwareag/webshop.git\",
    \"branch\": \"feature/add-qty-and-uom-to-list-view\"
  }
]"
APPS_JSON_BASE64=$(echo "${APPS_JSON}" | base64 --wrap=0)
export APPS_JSON_BASE64

if [[ $BRANCH == "pr" ]];
then
  docker buildx bake --pull
  exit $?
else
  docker buildx bake --pull --push
  exit $?
fi