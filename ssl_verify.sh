#!/bin/bash

SSL_DIR="/etc/mgmt/ssl"
DOMAINS='
'

TLDS='
'

echo ""
echo "===== curl을 이용한 실시간 인증서 검증 ====="
for domain in ${DOMAINS}
do
	echo ""
	echo "curl 요청 검증 : ${domain}"
	curl -IvsL --resolve ${domain}:443:127.0.0.1 https://${domain} 2>&1 | egrep 'start|expire|subjectAltName|issuer'
done

echo ""
echo "===== openssl을 이용한 인증서 파일 직접 검증 ====="
for tld in ${TLDS}
do
	echo ""
	echo "${tld} 인증서 내용:"
	CRT_FILE="${SSL_DIR}/${tld}/${tld}_crt.pem"

	if [[ -f "${CRT_FILE}" ]]; then
		openssl x509 -in "${CRT_FILE}" -noout -subject --issuer -dates
		echo "> SAN(DNS) :"
		openssl x509 -in "${CRT_FILE}" -noout -text | grep -A1 "Subject Alternative Name"
	else
		echo "X 인증서 파일이 존재하지 않음 : ${CRT_FILE}"
	fi
done
