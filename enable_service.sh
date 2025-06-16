#!/bin/bash

# 사용법: ./enable_apis.sh your-project-id

if [ -z "$1" ]; then
  echo "프로젝트 ID를 인자로 입력해주세요."
  echo "예: ./enable_apis.sh my-gcp-project"
  exit 1
fi

PROJECT_ID="$1"

APIS=(
  serviceusage.googleapis.com
  dns.googleapis.com
  bigquery-json.googleapis.com
  cloudkms.googleapis.com
  cloudresourcemanager.googleapis.com
  monitoring.googleapis.com
  logging.googleapis.com
  iam.googleapis.com
  storage-component.googleapis.com
  sql-component.googleapis.com
  compute.googleapis.com
  appengine.googleapis.com
  storage.googleapis.com
  cloudfunctions.googleapis.com
  file.googleapis.com
  redis.googleapis.com
  dataproc.googleapis.com
  bigtableadmin.googleapis.com
  essentialcontacts.googleapis.com
  accessapproval.googleapis.com
)

echo "[$PROJECT_ID] 프로젝트에 API를 활성화합니다..."

for api in "${APIS[@]}"; do
  echo "enabling: $api"
  gcloud services enable "$api" --project="$PROJECT_ID"
done

echo "모든 API가 활성화되었습니다."
