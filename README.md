# Tiny Second-hand Shopping Platform

보안 코딩 과제를 위해 제작한 Flask 기반 교육용 중고거래 플랫폼입니다. 회원 인증, 상품 CRUD/검색, 1:1 메시지, 사용자·상품 신고, 관리자 관리, 가상 포인트 송금과 자동 보안 테스트를 포함합니다. 송금은 실제 금융기관과 연결되지 않는 내부 포인트 기능입니다.

## 주요 기능

- 회원가입, 로그인, 로그아웃, 프로필 수정
- 비밀번호 단방향 해시 저장, 정지 계정 로그인 차단
- 상품 등록·조회·수정·삭제, 상태 변경, 키워드 검색
- 판매자와의 1:1 메시지 및 대화 목록
- 사용자·상품 신고, 동일 대상 중복 신고 방지
- 가상 포인트 송금, 비밀번호 재확인, 잔액 검증, 거래 내역
- 관리자 사용자 정지/해제, 상품 숨김/복구, 신고 승인/기각
- 관리자 작업 로그와 최근 송금 조회
- CSRF, XSS, SQL Injection, IDOR, 입력 검증, 안전한 오류 페이지 대응

## 빠른 실행

Python 3.11 이상이 필요합니다.

```bash
git clone <YOUR_REPOSITORY_URL>
cd tiny-secondhand-platform
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell에서는 다음 명령으로 가상환경을 활성화합니다.

```powershell
.venv\Scripts\Activate.ps1
```

의존성을 설치하고 환경 파일을 준비합니다.

```bash
pip install -r requirements.txt
cp .env.example .env
```

`.env`의 `SECRET_KEY`를 충분히 긴 임의 문자열로 변경하세요. 개발 DB를 초기화하고 서버를 실행합니다.

```bash
flask --app run.py init-db
python run.py
```

브라우저에서 `http://127.0.0.1:5000`을 엽니다.

## 기본 관리자 계정 생성 방법

소스 코드에는 공용 기본 비밀번호를 넣지 않았습니다. 다음 명령으로 원하는 관리자 계정을 안전하게 생성합니다.

```bash
flask --app run.py create-admin
```

프롬프트에 관리자 아이디와 8자 이상의 비밀번호를 입력합니다. 예시 아이디는 `admin`이지만 비밀번호는 직접 정해야 합니다. 이미 존재하는 아이디는 거부됩니다.

비대화형 환경에서는 Flask CLI 입력을 직접 제공하기보다, 로컬 터미널에서 위 명령을 실행하는 방식을 권장합니다.

## 테스트

```bash
pytest -q
```

완성본 기준 결과:

```text
15 passed in 2.77s
```

테스트는 인증, 비밀번호 해시, 중복 계정, 정지 계정, 상품 CRUD·검색, 음수 가격, 타인 상품 수정/삭제, XSS 이스케이프, 메시지, 중복 신고, 정상/비정상 송금, 중복 송금, 관리자 권한, CSRF 거부를 검증합니다.

## 보안 설계

- **CSRF:** Flask-WTF 전역 보호와 모든 POST 폼의 토큰
- **인증:** Flask-Login 세션, HTTPOnly/SameSite 쿠키, 정지 상태 확인
- **비밀번호:** Werkzeug의 솔트 포함 강한 단방향 해시
- **SQL Injection:** SQLAlchemy ORM과 바인딩된 조건식
- **XSS:** Jinja 자동 이스케이프 유지, 사용자 입력에 `safe` 필터 미사용
- **IDOR:** 상품 수정·삭제 시 서버에서 판매자 ID 또는 관리자 역할 확인
- **입력 검증:** 길이, 형식, 숫자 범위, 존재 여부를 서버에서 검사
- **송금:** 자기 송금·음수·잔액 초과 차단, 비밀번호 재확인, 고유 멱등키, 단일 DB 커밋
- **오류 처리:** 400/401/403/404/500 사용자용 화면, 내부 예외 세부정보 미노출
- **관리자:** 역할 기반 접근 제어와 중요 작업 로그

운영 환경에서는 HTTPS를 사용하고 `.env`에서 `SESSION_COOKIE_SECURE=1`로 설정하세요. SQLite는 수업·시연 규모에 적합하며, 다중 서버 운영 시에는 행 잠금과 높은 동시성을 지원하는 PostgreSQL로 이전해야 합니다.

## 프로젝트 구조

```text
tiny-secondhand-platform/
├── app/
│   ├── __init__.py          # 앱 팩토리, 오류 처리, CLI
│   ├── decorators.py        # 관리자/정상 계정 권한 검사
│   ├── extensions.py        # DB, 로그인, CSRF
│   ├── forms.py             # 서버 입력 검증
│   ├── models.py            # 6개 핵심 데이터 모델
│   ├── routes/              # 기능별 Blueprint
│   ├── static/style.css
│   └── templates/
├── tests/                   # pytest 보안·기능 테스트
├── CHECKLIST.md
├── SECURITY_LOG.md
├── DEVELOPMENT_REPORT.pdf
├── config.py
├── run.py
├── requirements.txt
└── .env.example
```

## 데이터 모델

- `User`: 계정, 역할, 상태, 포인트 잔액
- `Product`: 판매자, 상품 정보, 판매/숨김 상태
- `Message`: 송신자, 수신자, 메시지 내용
- `Report`: 신고자, 대상 유형/번호, 사유, 처리 상태
- `Transfer`: 송신자, 수신자, 금액, 멱등키
- `AdminLog`: 관리자 조치와 대상

## 사용 시나리오

1. 일반 사용자 두 명을 회원가입합니다.
2. 첫 번째 사용자가 상품을 등록합니다.
3. 두 번째 사용자가 상품 상세에서 판매자에게 메시지를 보냅니다.
4. 두 번째 사용자가 판매자 아이디로 가상 포인트를 송금합니다.
5. 문제가 있는 상품 또는 사용자를 신고합니다.
6. 관리자 계정으로 접속해 신고를 검토하고 사용자·상품 상태를 변경합니다.

## 제출 자료

- `SECURITY_LOG.md`: 개발 중 발견·수정한 보안 약점 기록
- `CHECKLIST.md`: 요구사항 및 테스트 체크리스트
- `DEVELOPMENT_REPORT.pdf`: 요구사항부터 유지보수까지의 개발 전 과정 보고서 초안

## 알려진 제한 사항

- 이미지 업로드와 실시간 WebSocket 채팅은 필수 범위에서 제외했습니다.
- 메시지는 상품별 채팅방이 아닌 사용자 간 1:1 대화입니다.
- 실제 결제·계좌 연동은 하지 않습니다.
- 교육용 SQLite 구성은 고부하 운영을 대상으로 하지 않습니다.
- 로그인 속도 제한과 이메일 인증은 향후 확장 항목입니다.

## GitHub 제출 전 확인

```bash
git status
pytest -q
git add .
git commit -m "Complete secure tiny second-hand platform"
git branch -M main
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin main
```

`.env`, `instance/`, `*.db`, 가상환경이 커밋되지 않았는지 반드시 확인하세요.
