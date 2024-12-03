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


## tf_vmcreate_output_to_csv.py

테라폼으로 VM을 생성한 뒤 출력되는 output 데이터를 팀에서 관리하는 문서에 맞게 가공하는 스크립트

### 환경

* lang : python 3.12

### 사용법

다음과 같이 data 변수에 output 데이터를 복사

```python
data = [
    {
        "availability_zone": "ap-seoul-1",
        "cpu": 8,
        "disk": ["vHDD / 50", "vHDD / 10", "vHDD / 100"],
        "id": "ins-e24fwcbb",
        "memory": 8,
        "name": "hostname-was-live-01",
        "os": "Rocky 8.8",
        "private_ip": "10.11.31.111",
        "public_ip": "43.128.156.111",
    }
]
```

스크립트 실행

```bash
python tf_vmcreate_output_to_csv.py
```

스크립트 경로에 **instance_info.csv** 파일이 생성된다.

## delete_sg_check.sh

서버 반납 시 반납 대상 서버의 SG 정책을 삭제하기 위해 검사하는 스크립트
ack 도구를 이용해서 프로젝트 경로의 문자열을 검사한다.

### 사용법

```bash
bash delete_sg_check.sh
```

git diff 테스트

## extract_noti.py

AWS 호스트 장애 또는 네트워크 이슈로 인해 대량의 Ping Fail이 발생할 경우 리스트를 추출하기 위한 스크립트

### 사용법

알람의 내용을 복사해서 data.txt 파일에 붙여 넣고 다음을 실행

```python
python extract_noti.py
```
