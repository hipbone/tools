#!/bin/bash

# 추출
## git status . | grep network | awk '{print $2}'
# Terraform Root 디렉토리에서 실행
# list 예시
## network/com2usplatform/aws-com2usplatform-live-ap-northeast-1/com2usplatform-vpc/security-group-instance.tf


list="
"

for i in $list; do
    terraform -chdir=$(dirname $i) init
    terraform -chdir=$(dirname $i) plan
done
