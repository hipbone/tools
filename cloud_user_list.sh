
profiles='
hive-live
iep-manage
hive-ses
hive-issueboard
hivev4-live
cp-etl-rnd
iep-rnd-aws
hive-sandbox
com2usplatform-live
com2usplatform-sandbox
hive-test
cp-gameplatform-rnd
cp-security-rnd
'

for i in $profiles
do
    echo "===== $i ====="
    echo ""
    echo ""
    # aws iam list-users --profile $i --output text | egrep '0nlyou|yuna05|hipbone'
    aws iam list-users --profile $i --output text >> ~/result
done
