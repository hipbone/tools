#!/bin/bash

profiles='
iep-manage-iac
hive-live-iac
iep-rnd-aws-iac
hive-sandbox-iac
hive-test-iac
'

# 인스턴스가 없는 계정
## hive-ses-iac
## hive-issueboard-iac
## hivev4-live-iac
## cp-etl-rnd-iac
## cp-security-rnd-iac
## cp-gameplatform-rnd-iac
## com2usplatform-live-iac
## com2usplatform-sandbox-iac

for profile in $profiles
do
    echo ""
    echo ${profile}
    echo ""
    aws ec2 describe-instances --query 'Reservations[*].Instances[*].PublicIpAddress' --output text --profile $profile

    # Name, IP, AZ 출력
    # aws ec2 describe-instances --query "Reservations[*].Instances[*].{Name:Tags[?Key=='Name']|[0].Value,IP:PublicIpAddress,AZ:Placement.AvailabilityZone}" --output text --profile $profile
done
