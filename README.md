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

### 지원 입력 포맷

`terraform apply` 또는 `terraform output` 후 출력되는 HCL 형식을 그대로 붙여넣기

```hcl
instance = {
  "axyl-work-test-c01" = {
    "availability_zone" = "ap-seoul-1"
    "bwp_attachment_id" = null
    "cpu"               = 4
    "disk"              = [
      "vHDD / 50",
      "vHDD / 10",
    ]
    "id"                = "ins-gdt2v2dz"
    "memory"            = 8
    "private_ip"        = "10.25.21.3"
    "public_ip"         = "150.109.236.78"
    "state"             = "running"
  }
}
```

여러 output 블록을 연속으로 붙여넣어도 모두 파싱된다.

### 사용법

**1. 대화형 (붙여넣기)**

```bash
python tf_vmcreate_output_to_csv.py
# 프롬프트에 terraform output 내용을 붙여넣고 Ctrl+D
```

**2. 파일로 입력**

```bash
python tf_vmcreate_output_to_csv.py output.txt
python tf_vmcreate_output_to_csv.py output.txt result.csv  # 출력 파일명 지정
```

**3. 파이프**

```bash
terraform output | python tf_vmcreate_output_to_csv.py
```

스크립트 경로에 **instance_info.csv** 파일이 생성된다. (엑셀에서 바로 열 수 있도록 UTF-8 BOM 인코딩)

### CSV 컬럼

| 컬럼 | 설명 |
|------|------|
| name | 인스턴스 이름 (output의 key) |
| availability_zone | 가용 영역 |
| id | 인스턴스 ID |
| cpu | vCPU 수 |
| memory | 메모리 (GB) |
| disk | 디스크 목록 (`, ` 구분) |
| public_ip | 공인 IP |
| private_ip | 사설 IP |
| state | 상태 |
| os | OS 정보 (수동 입력용, 기본값 공백) |

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
