# tools

시스템 운영 시 필요한 다양한 도구를 모아 놓는다.

## 파이썬 환경 - 공통

### Ubuntu & Debian

```bash
python3.x -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## genpasswd.py

비밀번호 생성시

### 환경

* lang : python 3.12

### 사용법

```bash
python genpasswd.py
```

## migration_check.py

서버 또는 서비스 이전 시 도메인, 방화벽, 서비스 환경 구성을 확인하기 위한 스크립트

### 환경

* lang : python 3.12

### 사용법

```bash
# migration_check.py 파일에 사용자 변수 설정 
file_path = "list"  # 파일명
hc_path = "/check"  # 테스트 호출할 URL의 Path
ssl_verify = False  # SSL 인증서 검증을 할지 여부 - 서비스 도메인의 경우 옵션을 활성화해서 인증서도 검증한다.

python migration_check.py
```