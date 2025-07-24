#!/bin/bash

profiles=`cat profilelist.txt`
region="ap-northeast-2"

for profile in $profiles
do
    echo "profile : ${profile}"
    clusters=$(aws eks list-clusters --profile $profile --output text --query 'clusters[*]')

    if [[ -z "$clusters" ]]; then
	echo "클러스터가 없습니다."
	continue
    fi
    for cluster in $clusters; do
        echo "${profile} : ${cluster} 등록"
	aws eks update-kubeconfig --region ${region} --name "${cluster}" --profile "${profile}" --alias "${cluster}"
    done
done
