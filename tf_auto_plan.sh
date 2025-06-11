#!/bin/bash

working_dir='/home/hipbone/src/iep-git/iep-terraform'
# 로그 디렉토리
LOG_DIR="/home/hipbone/tf-logs"
mkdir -p $LOG_DIR

cd $working_dir
changed_dirs=$(git ls-files -m | xargs -n1 dirname | sort -u | grep ^compute)

INIT_FAIL=()
PLAN_FAIL=()
PLAN_CHANGES=()
APPLY_SUCCESS=()

echo "[INFO] Terraform Auto Runner Started"

for DIR in $changed_dirs; do
    echo "----- [$DIR] -----"

    cd "$DIR" || {
        echo "[SKIP] $DIR not found"
        continue
    }
    INIT_LOG="$LOG_DIR/init_${DIR//\//_}.log"
    PLAN_LOG="$LOG_DIR/plan_${DIR//\//_}.log"

    echo "[INIT] Running terraform init in $DIR"
    terraform init -input=false >"$INIT_LOG" 2>&1
    if [ $? -ne 0 ]; then
        echo "[ERROR] Init failed for $DIR"
        INIT_FAIL+=("$DIR")
        cd - >/dev/null
        continue
    fi

    echo "[PLAN] Running terraform plan in $DIR"
    terraform plan -input=false -out=tfplan >"$PLAN_LOG" 2>&1
    if [ $? -ne 0 ]; then
        echo "[ERROR] Plan failed for $DIR"
        PLAN_FAIL+=("$DIR")
        cd - >/dev/null
        continue
    fi

    # 변경 있는지 확인
    if grep -q "No changes. Infrastructure is up-to-date." "$PLAN_LOG"; then
        echo "[SKIP] No changes in $DIR"
    else
        echo "[CHANGE] Detected changes in $DIR"
        PLAN_CHANGES+=("$DIR")
    fi
    #     echo "[APPLY] Applying changes in $DIR"
    #     terraform apply -auto-approve tfplan >>"$PLAN_LOG" 2>&1
    #     if [ $? -eq 0 ]; then
    #         APPLY_SUCCESS+=("$DIR")
    #     else
    #         echo "[ERROR] Apply failed in $DIR"
    #     fi
    # fi

    # # 정리
    # rm -f tfplan
    # cd - >/dev/null
done

echo ""
echo "======================================"
echo "[SUMMARY]"
echo "Init Failures    : ${#INIT_FAIL[@]} (${INIT_FAIL[*]})"
echo "Plan Failures    : ${#PLAN_FAIL[@]} (${PLAN_FAIL[*]})"
echo "Planned Changes  : ${#PLAN_CHANGES[@]} (${PLAN_CHANGES[*]})"
# echo "Applied Successfully : ${#APPLY_SUCCESS[@]} (${APPLY_SUCCESS[*]})"
echo "Plan Logs in     : $LOG_DIR"
echo "======================================"
