#!/bin/bash
set -uo pipefail

usage() {
	cat <<EOF
사용법: $(basename "$0") [옵션] <PROJECT_ID>

GCP 프로젝트에 보안 기준(CIS) 초기 설정을 적용합니다.

인자:
  PROJECT_ID    초기화할 GCP 프로젝트 ID (필수)

옵션:
  -y, --yes       확인 프롬프트 없이 진행
  -n, --dry-run   실제 변경 없이 수행될 작업만 출력
  -h, --help      도움말 출력

예시:
  $(basename "$0") hive-aas-test
  $(basename "$0") --yes hive-aas-test
  $(basename "$0") --dry-run hive-aas-test
EOF
}

# dry-run이면 실제 실행 대신 명령을 출력(stderr), 아니면 실제 실행
run() {
	if [ "$dry_run" = true ]; then
		echo "  [dry-run] $*" >&2
	else
		"$@"
	fi
}

# 인자 파싱 (project_id, assume_yes, dry_run 설정)
parse_args() {
	assume_yes=false
	dry_run=false
	project_id=""
	while [ $# -gt 0 ]; do
		case "$1" in
			-y | --yes) assume_yes=true; shift ;;
			-n | --dry-run) dry_run=true; shift ;;
			-h | --help) usage; exit 0 ;;
			-*) echo "오류: 알 수 없는 옵션: $1" >&2; usage >&2; exit 1 ;;
			*)
				if [ -z "$project_id" ]; then
					project_id="$1"
				else
					echo "오류: 인자가 너무 많습니다: $1" >&2
					usage >&2
					exit 1
				fi
				shift ;;
		esac
	done

	if [ -z "$project_id" ]; then
		echo "오류: PROJECT_ID가 필요합니다." >&2
		echo "" >&2
		usage >&2
		exit 1
	fi
}

# 사전 점검: gcloud 설치 / 인증 / 프로젝트 접근 확인 (project_number 설정)
preflight() {
	if ! command -v gcloud >/dev/null 2>&1; then
		echo "오류: gcloud CLI를 찾을 수 없습니다. Google Cloud SDK를 설치하세요." >&2
		exit 1
	fi
	if [ -z "$(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null)" ]; then
		echo "오류: 활성화된 gcloud 인증 계정이 없습니다. 'gcloud auth login'을 먼저 실행하세요." >&2
		exit 1
	fi
	project_number=$(gcloud projects describe "$project_id" --format="value(projectNumber)" 2>/dev/null)
	if [ -z "$project_number" ]; then
		echo "오류: 프로젝트 '$project_id'에 접근할 수 없거나 존재하지 않습니다." >&2
		exit 1
	fi
}

# 전역 변수 초기화 (preflight 이후 project_number 사용 가능)
init_vars() {
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
}

# 파괴적 작업 실행 전 확인 (dry-run / --yes 시 건너뜀)
confirm() {
	{ [ "$assume_yes" = true ] || [ "$dry_run" = true ]; } && return 0
	cat <<EOF

다음 작업이 프로젝트 '$project_id'에 적용됩니다 (일부는 되돌릴 수 없습니다):
  - 기본 SA(App Engine/Compute Engine)에서 roles/editor 제거
  - 기본 방화벽 규칙 4개 삭제 (default-allow-icmp/internal/rdp/ssh)
  - 기본 VPC 네트워크(default) 삭제
  - 로그 라우터 싱크 생성 및 pub/sub 게시 권한 부여
EOF
	printf "계속하시겠습니까? [y/N] "
	read -r answer
	case "$answer" in
		[yY] | [yY][eE][sS]) ;;
		*) echo "취소되었습니다."; exit 0 ;;
	esac
}

# roles/editor 바인딩이 있을 때만 제거 (멱등)
remove_editor_binding() {
	local member="$1"
	if gcloud projects get-iam-policy "$project_id" \
		--flatten="bindings[].members" \
		--filter="bindings.role=roles/editor AND bindings.members=$member" \
		--format="value(bindings.role)" 2>/dev/null | grep -q .; then
		run gcloud projects remove-iam-policy-binding "$project_id" \
			--member="$member" --role="roles/editor" >/dev/null
		echo "  - roles/editor 제거: $member"
	else
		echo "  - roles/editor 없음 (건너뜀): $member"
	fi
}

##### 1.1.5 서비스 계정에 관리자 권한 부여 제한 #####
restrict_default_sa_roles() {
	echo "[1.1.5] 기본 SA의 roles/editor 제거"
	remove_editor_binding "$app_engine_sa"     # App Engine default SA
	remove_editor_binding "$compute_engine_sa" # Compute Engine default SA
}

##### 1.3.2 기본 방화벽 정책 삭제 #####
delete_default_firewall_rules() {
	echo "[1.3.2] 기본 방화벽 규칙 삭제"
	local rule
	for rule in default-allow-icmp default-allow-internal default-allow-rdp default-allow-ssh; do
		if gcloud compute firewall-rules describe "$rule" --project="$project_id" >/dev/null 2>&1; then
			run gcloud compute firewall-rules delete "$rule" --project="$project_id" --quiet
			echo "  - 삭제: $rule"
		else
			echo "  - 없음 (건너뜀): $rule"
		fi
	done
}

##### 7.1.1 프로젝트 내 기본 네트워크 사용 제한 #####
delete_default_network() {
	echo "[7.1.1] 기본 VPC 네트워크(default) 삭제"
	if gcloud compute networks describe default --project="$project_id" >/dev/null 2>&1; then
		run gcloud compute networks delete default --project="$project_id" --quiet
		echo "  - 삭제: default"
	else
		echo "  - 없음 (건너뜀): default"
	fi
}

##### 5.1.1 로그 라우터 싱크 생성 #####
create_log_sink() {
	echo "[5.1.1] 로그 라우터 싱크 생성/업데이트: $sink_name"
	if gcloud logging sinks describe "$sink_name" --project="$project_id" >/dev/null 2>&1; then
		run gcloud logging sinks update "$sink_name" \
			"pubsub.googleapis.com/$topic" \
			--log-filter="$log_filter" \
			--project="$project_id"
		echo "  - 업데이트: $sink_name"
	else
		run gcloud logging sinks create "$sink_name" \
			"pubsub.googleapis.com/$topic" \
			--log-filter="$log_filter" \
			--project="$project_id"
		echo "  - 생성: $sink_name"
	fi
}

##### 로그 라우터 싱크 계정에 pub/sub 게시 권한 부여 #####
grant_pubsub_publisher() {
	echo "[권한] 로그 싱크 SA에 pub/sub 게시 권한 부여"
	logging_sa=$(gcloud logging sinks describe "$sink_name" --project="$project_id" --format="value(writerIdentity)" 2>/dev/null)
	if [ -z "$logging_sa" ]; then
		if [ "$dry_run" = true ]; then
			echo "  [dry-run] 싱크가 아직 없어 writerIdentity 확인 불가. 싱크 생성 후 권한 부여가 진행됩니다." >&2
			return 0
		fi
		echo "오류: 로그 싱크 '$sink_name'의 서비스 계정(writerIdentity)을 가져오지 못했습니다." >&2
		exit 1
	fi
	run gcloud pubsub topics add-iam-policy-binding "$topic" \
		--member="$logging_sa" \
		--role="roles/pubsub.publisher" \
		--project="$project_id"
	echo "  - 권한 부여 대상: $logging_sa"
}

### 수행 결과 출력 ###
report() {
	echo ""
	echo "##############################"
	echo "########## GCP 프로젝트 초기화 결과 : ${project_id} ##########"
	echo "##############################"

	echo "1. 기본 SA 계정 권한 확인 - App Engine Default SA"
	gcloud projects get-iam-policy "$project_id" \
		--flatten="bindings[].members" \
		--filter="bindings.members:$app_engine_sa" \
		--format="table(bindings.role)"
	echo ""

	echo "2. 기본 SA 계정 권한 확인 - Compute Engine Default SA"
	gcloud projects get-iam-policy "$project_id" \
		--flatten="bindings[].members" \
		--filter="bindings.members:$compute_engine_sa" \
		--format="table(bindings.role)"
	echo ""

	echo "3. VPC Network 목록"
	gcloud compute networks list --project="$project_id"
	echo ""

	echo "4. Firewall Rules 목록"
	gcloud compute firewall-rules list --project="$project_id" --format=json
	echo ""

	echo "5. 로그 라우터 싱크 정보 - ${sink_name}"
	gcloud logging sinks describe "$sink_name" --project="$project_id"
	echo ""

	echo "6. 로그 라우터 싱크 서비스 계정에 pub/sub 게시 권한 부여 확인"
	gcloud pubsub topics get-iam-policy "$topic" --project="$project_id" \
		--flatten="bindings[].members" \
		--filter="bindings.role:roles/pubsub.publisher AND bindings.members:$logging_sa" \
		--format="table(bindings.role, bindings.members)"
}

main() {
	parse_args "$@"
	preflight
	init_vars
	confirm

	[ "$dry_run" = true ] && echo "=== DRY-RUN 모드: 실제 변경은 수행하지 않습니다 ==="

	restrict_default_sa_roles
	delete_default_firewall_rules
	delete_default_network
	create_log_sink
	grant_pubsub_publisher
	report
}

main "$@"
