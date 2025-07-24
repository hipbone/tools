#!/bin/bash

echo "🔍 사용 불가능한 kubeconfig context 찾기..."
echo

# 모든 context 가져오기
contexts=$(kubectl config get-contexts -o name)

for ctx in $contexts; do
  echo -n "⏳ $ctx ... "
  
  # context 테스트 (namespace 조회 시도)
  if ! kubectl --context="$ctx" get ns --request-timeout=5s >/dev/null 2>&1; then
    echo "❌ 연결 실패"
  else
    echo "✅ 정상"
  fi
done
