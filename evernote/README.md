# Evernote Backup

Evernote 노트를 백업하고 내보내기 위한 도구

## 사전 준비

### 1. evernote-backup 패키지 설치

```bash
pip install evernote-backup
```

또는 requirements.txt를 사용하여 설치:

```bash
pip install -r requirements.txt
```

## 백업 절차

### 1. Evernote 계정 초기화 및 로그인

```bash
evernote-backup init-db --oauth
```

- 브라우저가 열리고 Evernote 로그인 페이지로 이동됩니다
- Evernote 계정으로 로그인하고 권한을 승인합니다
- 인증이 완료되면 `en_backup.db` 파일이 생성됩니다

### 2. 노트 동기화

```bash
evernote-backup sync
```

- Evernote 계정의 모든 노트를 로컬 데이터베이스(`en_backup.db`)에 동기화합니다
- 정기적으로 이 명령을 실행하여 최신 노트를 유지할 수 있습니다

### 3. 노트 내보내기 (예정)

동기화된 노트를 다양한 형식으로 내보낼 수 있습니다.

```bash
evernote-backup export [출력_디렉토리]
```

## 파일 구조

- `en_backup.db`: Evernote 노트가 저장된 SQLite 데이터베이스
- `requirements.txt`: 필요한 Python 패키지 목록

## 참고 사항

- 백업 데이터베이스는 SQLite 형식으로 저장됩니다
- 대용량 노트북의 경우 동기화에 시간이 걸릴 수 있습니다
- 인증 토큰은 데이터베이스에 안전하게 저장됩니다
