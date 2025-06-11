#!/bin/bash

project_id="hive-analytics-sandbox"
project_number=$(gcloud projects describe $project_id --format="value(projectNumber)")

##### 1.1.5 서비스 계정에 관리자 권한 부여 제한 #####
# App Engine default SA
gcloud projects remove-iam-policy-binding "$project_id" \
	--member="serviceAccount:${project_id}@appspot.gserviceaccount.com" \
	--role="roles/editor"

# Compute Engine default SA
gcloud projects remove-iam-policy-binding "$project_id" \
	--member="serviceAccount:${project_number}-compute@developer.gserviceaccount.com" \
	--role="roles/editor"


##### 1.3.2 기본 방화벽 정책 삭제 #####
gcloud compute firewall-rules delete default-allow-icmp \
  default-allow-internal \
  default-allow-rdp \
  default-allow-ssh \
  --project=$project_id \
  --quiet

##### 7.1.1 프로젝트 내 기본 네트워크 사용 제한 #####
gcloud compute networks delete default --project=$project_id --quiet
