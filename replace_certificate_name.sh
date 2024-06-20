#!/bin/bash

working_dir="/data/src/iep-git/iep-aws-projects/hive-live/ap-northeast-2/live/load-balancer"
pattern="\"withhivecom-20240712\""

cd $working_dir
ack -l $pattern | grep -v terragrunt-cache

# 2. 추출된 파일 경로를 이용해서 sed로 문자열 치환
# 예를 들어, old_string을 new_string으로 치환
ack -l ${pattern} | grep -v terragrunt-cache | while read file; do
  sed -i "s|${pattern}|\"withhivecom-20250618\"|g" "$file"
done

