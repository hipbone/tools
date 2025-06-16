#!/bin/bash

project_id="hive-aas-test"
project_number=$(gcloud projects describe $project_id --format="value(projectNumber)")
app_engine_sa="serviceAccount:${project_id}@appspot.gserviceaccount.com"
compute_engine_sa="serviceAccount:${project_number}-compute@developer.gserviceaccount.com"
sink_name="gcp-iep-audit-log-sync"
topic="projects/iep-manage/topics/gcp-iep-audit-log"
log_filter="
logName=(\"projects/$project_id/logs/cloudaudit.googleapis.com%2Factivity\" OR \"projects/$project_id/logs/cloudaudit.googleapis.com%2Fdata_access\")
AND -protoPayload.serviceName=\"bigquerybiengine.googleapis.com\" AND -protoPayload.serviceName=\"bigquery.googleapis.com\" AND -protoPayload.serviceName=\"k8s.io\" AND
        -protoPayload.resourceName=\"projects/$project_id/global/firewalls/blacklist-deny-0\" AND 
        -protoPayload.resourceName=\"projects/$project_id/global/firewalls/blacklist-deny-1\" AND 
        -protoPayload.resourceName=\"projects/$project_id/global/firewalls/blacklist-deny-2\" AND 
        -protoPayload.resourceName=\"projects/$project_id/global/firewalls/blacklist-deny-3\" AND 
        -protoPayload.resourceName=\"projects/$project_id/global/firewalls/blacklist-deny-4\" AND 
        -protoPayload.resourceName=\"projects/$project_id/global/firewalls/blacklist-deny-5\" AND 
        -protoPayload.resourceName=\"projects/$project_id/global/firewalls/blacklist-deny-6\" AND 
        -protoPayload.resourceName=\"projects/$project_id/global/firewalls/blacklist-deny-7\" AND 
        -protoPayload.resourceName=\"projects/$project_id/global/firewalls/blacklist-deny-8\" AND 
        -protoPayload.resourceName=\"projects/$project_id/global/firewalls/blacklist-deny-9\" AND 
        -protoPayload.resourceName=\"projects/$project_id/global/firewalls/blacklist-deny-10\" AND 
        -protoPayload.resourceName=\"projects/$project_id/global/firewalls/blacklist-deny-11\"
"

##### 1.1.5 서비스 계정에 관리자 권한 부여 제한 #####
# App Engine default SA
gcloud projects remove-iam-policy-binding "$project_id" \
	--member="$app_engine_sa" \
	--role="roles/editor"

# Compute Engine default SA
gcloud projects remove-iam-policy-binding "$project_id" \
	--member="$compute_engine_sa" \
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


##### 5.1.1 로그 라우터 싱크 생성 #####
gcloud logging sinks create "$sink_name" \
    "pubsub.googleapis.com/$topic" \
    --log-filter="$log_filter" \
    --project=$project_id

## 로그 라우터 싱크 서비스 계정 가져오기 ##
logging_sa=$(gcloud logging sinks describe $sink_name --project=$project_id --format="value(writerIdentity)")

# --member="serviceAccount:service-1014411968784@gcp-sa-logging.iam.gserviceaccount.com" \
  
##### 로그 라우터 싱크 계정에 pub/sub 게시 권한 부여 #####
gcloud pubsub topics add-iam-policy-binding $topic \
  --member="$logging_sa" \
  --role=roles/pubsub.publisher \
  --project=$project_id

### 수행 결과 ###
echo "##############################"
echo "########## GCP 프로젝트 초기화 : ${project_id} ##########"
echo "1. 기본 SA 계정 권한 확인 - App Engine Default SA"
echo ""
gcloud projects get-iam-policy $project_id \
  --flatten="bindings[].members" \
  --filter="bindings.members:$app_engine_sa" \
  --format="table(bindings.role)"
echo "2. 기본 SA 계정 권한 확인 - Compute Engine Default SA"
echo ""
gcloud projects get-iam-policy $project_id \
  --flatten="bindings[].members" \
  --filter="bindings.members:$compute_engine_sa" \
  --format="table(bindings.role)"
echo "3. VPC Network 목록"
gcloud compute networks list --project=$project_id
echo ""
echo "4. Firewall Rules 목록"
gcloud compute firewall-rules list --project=$project_id --format=json
echo ""
echo "5. 로그 라우터 싱크 정보 - ${sink_name}"
gcloud logging sinks describe gcp-iep-audit-log-sync --project=${project_id}
echo ""
echo "6. 로그 라우터 싱크 서비스 계정에 pub/sub 게시 권한 부여 확인"
echo ""
gcloud pubsub topics get-iam-policy $topic --project=$project_id \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/pubsub.publisher AND bindings.members:$logging_sa" \
  --format="table(bindings.role, bindings.members)"
