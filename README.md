# 아이파킹 자동화 시스템

아이파킹 멤버 사이트의 차량번호 검색 및 할인권 적용을 자동화하는 시스템입니다.

## 기능

- ✅ 로그인 자동화
- ✅ 차량번호 검색
- ✅ 할인권 적용
- ✅ 에러 처리 및 재시도 로직
- ✅ 팝업 자동 처리
- ✅ 로깅 시스템

## 설치 및 설정

### 1. 가상환경 활성화
```bash
source venv/bin/activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. Chrome 브라우저 설치
Chrome 브라우저가 설치되어 있어야 합니다. ChromeDriver는 자동으로 설치됩니다.

## 사용법

### 기본 사용법
```python
from core.automation import IParkingAutomation

# 자동화 인스턴스 생성
automation = IParkingAutomation(headless=False)

# 전체 프로세스 실행
result = automation.run_full_automation("1255")

# 결과 확인
print(f"성공: {result['success']}")
print(f"실행 시간: {result['execution_time']:.2f}초")
```

### 단계별 사용법
```python
from core.automation import IParkingAutomation

automation = IParkingAutomation()

# 1. WebDriver 설정
automation.setup_driver()

# 2. 사이트 접속
automation.navigate_to_site()

# 3. 로그인
automation.login("username", "password")

# 4. 차량 검색
automation.search_vehicle("1255")

# 5. 차량 선택
automation.select_vehicle()

# 6. 할인권 적용
automation.apply_discount("30분할인권")

# 7. WebDriver 종료
automation.close_driver()
```

## 테스트

### 전체 테스트 실행
```bash
pytest test_automation.py -v
```

### 개별 테스트 실행
```bash
python test_automation.py
```

### 메인 스크립트 실행
```bash
python -m core.automation
```

## 설정

### 테스트 계정 정보
- 아이디: `dtctrit2704`
- 비밀번호: `dtctrit2704`
- 테스트 차량번호: `1255`

### 헤드리스 모드
```python
# 헤드리스 모드로 실행 (브라우저 창 없이)
automation = IParkingAutomation(headless=True)
```

## API 정보

### 주요 엔드포인트
- `POST /api/members/store/list/{userId}` - 매장 목록 조회
- `GET /api/members/notice/alram/popup` - 알림 팝업 조회
- `POST /api/members/discount/carlist` - 차량 검색
- `POST /api/members/discount/apply/list` - 할인권 적용 목록
- `POST /api/members/discount/product/list` - 할인권 상품 목록

### 인증 토큰
- 형식: UUID 형태의 문자열
- 획득: 로그인 성공 시 자동 획득
- 사용: 모든 API 요청의 `authorization` 헤더에 포함

## 에러 처리

### 일반적인 에러
- **로그인 실패**: 계정 정보 확인
- **차량 검색 실패**: 차량번호 확인
- **할인권 적용 실패**: 잔여 횟수 확인
- **네트워크 오류**: 연결 상태 확인

### 재시도 로직
- 네트워크 오류 시 자동 재시도
- 팝업 처리 실패 시 재시도
- 타임아웃 설정: 30초

## 로깅

### 로그 레벨
- `INFO`: 일반적인 정보
- `ERROR`: 에러 발생
- `DEBUG`: 상세 디버그 정보

### 로그 형식
```
2025-01-XX XX:XX:XX - INFO - 로그인 성공
2025-01-XX XX:XX:XX - ERROR - 차량 검색 실패
```

## 성능 지표

### 목표 성능
- 자동화 성공률: 95% 이상
- 평균 실행 시간: 30초 이내
- 에러 처리 커버리지: 90% 이상

### 모니터링
- 실행 시간 측정
- 단계별 성공/실패 추적
- 에러 로그 수집

## 문제 해결

### 일반적인 문제
1. **ChromeDriver 오류**: Chrome 브라우저 업데이트 확인
2. **로그인 실패**: 계정 정보 및 네트워크 연결 확인
3. **차량 검색 실패**: 차량번호 형식 확인
4. **할인권 적용 실패**: 잔여 횟수 및 네트워크 상태 확인

### 디버깅
```python
# 상세 로그 활성화
import logging
logging.basicConfig(level=logging.DEBUG)

# 헤드리스 모드 비활성화 (브라우저 창 표시)
automation = IParkingAutomation(headless=False)
```

## 개발 정보

### 프로젝트 구조
```
chromeDT_test/
├── core/                    # 핵심 자동화 모듈
│   ├── __init__.py
│   ├── automation.py        # 메인 자동화 클래스
│   └── config.py           # 설정 관리
├── analysis/               # API 분석 모듈
│   ├── __init__.py
│   ├── api_analyzer.py     # API 분석기
│   └── status_analyzer.py  # 상태 분석기
├── monitoring/             # 모니터링 모듈
│   ├── __init__.py
│   └── extractor.py       # 상태 정보 추출기
├── web/                    # 웹 인터페이스 모듈
│   ├── __init__.py
│   ├── server.py          # 웹 서버
│   └── dashboard.html     # 대시보드
├── tests/                  # 테스트 모듈
│   ├── __init__.py
│   ├── test_basic.py      # 기본 테스트
│   └── test_popup.py      # 팝업 테스트
├── utils/                  # 유틸리티 모듈
│   ├── __init__.py
│   └── helpers.py         # 헬퍼 함수들
├── config/                 # 설정 파일들
│   ├── __init__.py
│   └── settings.py        # 설정 관리
├── data/                   # 데이터 파일들
├── docs/                   # 문서 (기존 유지)
├── venv/                   # 가상환경 (기존 유지)
├── requirements.txt        # 의존성 (기존 유지)
└── README.md              # 프로젝트 문서 (기존 유지)
```

### 기술 스택
- **Python 3.8+**: 메인 프로그래밍 언어
- **Selenium**: 웹 자동화 프레임워크
- **Chrome WebDriver**: 브라우저 자동화
- **pytest**: 테스트 프레임워크
- **requests**: HTTP 요청 라이브러리

## 라이선스

이 프로젝트는 개인 사용을 위한 것입니다.

## 연락처

프로젝트 관련 문의사항이 있으시면 이슈를 등록해 주세요.

---

**개발 완료일**: 2025년 1월 6일  
**버전**: 1.0.0  
**다음 업데이트**: API 하이브리드 방식 구현 예정
