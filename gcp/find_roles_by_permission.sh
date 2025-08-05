#!/bin/bash

# 예: ./get_roles_for_permission.sh bigquery.tables.get

permission="$1"

if [[ -z "$permission" ]]; then
  echo "❌ 사용법: $0 <PERMISSION_NAME>"
  echo "예: $0 bigquery.tables.get"
  exit 1
fi

echo "🔍 '${permission}' 권한이 포함된 역할을 조회 중..."

curl -s -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://iam.googleapis.com/v1/roles?view=FULL" \
  | jq --arg perm "$permission" -r '
    .roles[]
    | select(.includedPermissions != null)
    | select(.includedPermissions[] == $perm)
    | .name
  '

