# Task 02: 아이파킹 API 기반 자동화 시스템 구축

## 프로젝트 개요
- **프로젝트명**: 아이파킹 멤버 사이트 API 기반 자동화 시스템 구축
- **목적**: Task 01에서 분석한 API를 활용한 자동화 프로그램 개발
- **현재 상태**: API 분석 완료, 자동화 시스템 구축 시작
- **담당자**: 개발팀
- **완료 예정일**: 2025년 10월 20일

## Task 01 완료 내용

### ✅ 완료된 작업
1. **Chrome DevTools MCP를 활용한 API 분석**
   - 아이파킹 멤버 사이트 실제 접속 및 테스트
   - 로그인 → 차량 검색 → 할인권 적용 전체 플로우 분석
   - 네트워크 요청/응답 구조 파악

2. **주요 API 엔드포인트 식별**
   - `POST /api/members/store/list/{userId}` - 매장 목록 조회
   - `GET /api/members/notice/alram/popup` - 알림 팝업 조회
   - `POST /api/members/discount/carlist` - 차량 검색
   - `POST /api/members/discount/apply/list` - 할인권 적용 목록
   - `POST /api/members/discount/product/list` - 할인권 상품 목록

3. **인증 시스템 분석**
   - 인증 토큰: `b0f43959-1656-467f-a2ad-b88eecc36236` (UUID 형태)
   - 토큰 기반 인증 구조 확인
   - 공통 헤더 구조 파악

4. **문서화 완료**
   - `아이파킹_API_분석_결과.md` 작성
   - API 호출 플로우 정리
   - 보안 및 인증 정보 정리

### 📋 생성된 문서
- `아이파킹_자동화_지침서.md` - UI 자동화 프로세스 가이드
- `아이파킹_API_분석_결과.md` - Chrome DevTools MCP 분석 결과
- `task01.md` - API 분석 작업 계획서

## Task 02 목표

### 주요 목표
1. **자동화 시스템 구축**: 분석한 API를 활용한 자동화 프로그램 개발
2. **에러 처리 구현**: 네트워크 오류 및 API 에러 처리 로직 구현
3. **안정성 확보**: 재시도 로직 및 예외 상황 대응 구현
4. **테스트 및 검증**: 자동화 시스템의 정상 작동 확인

### 성공 기준
- 로그인부터 할인권 적용까지 전체 프로세스 자동화
- 에러 상황별 적절한 대응 로직 구현
- 95% 이상의 성공률 달성
- 운영 환경에서 안정적 동작

## 현재 상황 분석

### ✅ 확보된 정보
- 전체 프로세스 플로우
- 주요 API 엔드포인트 5개
- 인증 토큰 구조
- 공통 헤더 정보
- 테스트 계정 및 환경

### ❌ 부족한 정보
- 각 API의 요청/응답 바디 구조
- 에러 코드 및 메시지 목록
- 토큰 만료 시간 및 갱신 방법
- 로그인 API 호출 방법

### ⚠️ 기술적 한계
- 로그인 API 부재로 순수 API 기반 자동화 불가
- 하이브리드 방식 (UI + API) 필요
- 토큰 관리 복잡성

## 개발 접근법

### Phase 1: UI 자동화 기반 프로토타입 (1주)
**목표**: 기본 기능 구현 및 검증

**작업 내용**:
- Chrome DevTools MCP 또는 Selenium 활용
- 로그인 → 차량 검색 → 할인권 적용 플로우 구현
- 기본적인 에러 처리 로직 추가
- 테스트 시나리오 작성 및 실행

**산출물**:
```python
# 기본 자동화 스크립트 예시
class IParkingAutomation:
    def __init__(self):
        self.driver = None
        self.token = None
    
    def login(self, username, password):
        # UI 자동화를 통한 로그인
        pass
    
    def search_vehicle(self, vehicle_number):
        # 차량번호 검색
        pass
    
    def apply_discount(self, discount_type):
        # 할인권 적용
        pass
```

### Phase 2: 추가 API 분석 (1주)
**목표**: 요청/응답 구조 상세 분석

**작업 내용**:
- Chrome DevTools MCP로 각 API 상세 분석
- 요청 바디 JSON 구조 파악
- 응답 데이터 구조 분석
- 에러 응답 구조 확인

**산출물**:
- API 상세 스펙 문서
- 요청/응답 예시
- 에러 코드 매핑

### Phase 3: 하이브리드 방식 구현 (2주)
**목표**: UI 로그인 + API 호출 방식 구현

**작업 내용**:
- UI로 로그인하여 토큰 획득
- 획득한 토큰으로 API 직접 호출
- 에러 처리 및 재시도 로직 구현
- 성능 최적화 및 안정성 개선

**산출물**:
```python
# 하이브리드 자동화 클래스 예시
class IParkingHybridAutomation:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
    
    def login_ui(self, username, password):
        # UI 자동화로 로그인 및 토큰 획득
        pass
    
    def call_api(self, endpoint, data):
        # 획득한 토큰으로 API 호출
        pass
```

## 테스트 시나리오

### 1. 기본 기능 테스트
```python
def test_basic_flow():
    """기본 플로우 테스트"""
    automation = IParkingAutomation()
    
    # 1. 로그인
    assert automation.login("dtctrit2704", "dtctrit2704")
    
    # 2. 차량 검색
    result = automation.search_vehicle("1255")
    assert result.success
    
    # 3. 할인권 적용
    result = automation.apply_discount("30분할인권")
    assert result.success
```

### 2. 에러 처리 테스트
```python
def test_error_handling():
    """에러 처리 테스트"""
    automation = IParkingAutomation()
    
    # 잘못된 로그인 정보
    result = automation.login("wrong", "wrong")
    assert not result.success
    assert "로그인 실패" in result.message
    
    # 존재하지 않는 차량번호
    result = automation.search_vehicle("9999")
    assert not result.success
    assert "차량을 찾을 수 없습니다" in result.message
```

### 3. 성능 테스트
```python
def test_performance():
    """성능 테스트"""
    automation = IParkingAutomation()
    
    start_time = time.time()
    
    # 전체 프로세스 실행
    automation.login("dtctrit2704", "dtctrit2704")
    automation.search_vehicle("1255")
    automation.apply_discount("30분할인권")
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # 30초 이내 완료되어야 함
    assert execution_time < 30
```

## 검증 방법

### 1. 기능 검증
- [ ] 로그인 성공률 100%
- [ ] 차량 검색 성공률 95% 이상
- [ ] 할인권 적용 성공률 95% 이상
- [ ] 전체 프로세스 완료 시간 30초 이내

### 2. 에러 처리 검증
- [ ] 네트워크 오류 시 재시도 로직 작동
- [ ] API 에러 시 적절한 메시지 표시
- [ ] 로그인 실패 시 명확한 에러 처리
- [ ] 차량 검색 실패 시 대응 로직

### 3. 안정성 검증
- [ ] 연속 10회 실행 시 성공률 90% 이상
- [ ] 메모리 누수 없음
- [ ] 예외 상황에서도 안전한 종료
- [ ] 로그 파일 정상 생성

## 위험 요소 및 대응 방안

### 기술적 위험
**위험**: 로그인 API 부재로 인한 구현 복잡성  
**대응**: UI 자동화 기반으로 시작하여 점진적 개선

**위험**: 토큰 만료 시 자동 갱신 문제  
**대응**: 토큰 만료 시간 모니터링 및 재로그인 로직 구현

**위험**: 사이트 구조 변경으로 인한 호환성 문제  
**대응**: 버전 관리 및 호환성 체크 로직 구현

### 일정 위험
**위험**: 예상보다 복잡한 에러 처리로 인한 지연  
**대응**: 우선순위 기반 단계별 진행 및 중간 점검

**위험**: 테스트 환경 부족으로 인한 검증 지연  
**대응**: 모의 테스트 시나리오 준비 및 자동화 테스트 구현

## 필요한 도구 및 리소스

### 개발 도구
- Python 3.8+
- Selenium WebDriver 또는 Chrome DevTools MCP
- requests 라이브러리
- pytest (테스트 프레임워크)
- Git (버전 관리)

### 테스트 환경
- 테스트 계정: dtctrit2704/dtctrit2704
- 테스트 차량번호: 1255
- Chrome 브라우저
- 네트워크 연결

### 참고 자료
- `아이파킹_API_분석_결과.md`
- `아이파킹_자동화_지침서.md`
- Chrome DevTools MCP 사용법

## 성공 지표

### 정량적 지표
- 자동화 성공률: 95% 이상
- 평균 실행 시간: 30초 이내
- 에러 처리 커버리지: 90% 이상
- 코드 테스트 커버리지: 80% 이상

### 정성적 지표
- 안정적인 동작
- 명확한 에러 메시지
- 유지보수 용이한 구조
- 확장 가능한 아키텍처

## 다음 단계 (Task 03)

### 후속 작업 계획
1. **모니터링 및 알림 시스템 구현**
2. **대시보드 및 관리 도구 개발**
3. **성능 최적화 및 안정성 개선**
4. **운영 환경 배포 및 모니터링**

### 전달 사항
- 완성된 자동화 시스템
- 테스트 시나리오 및 결과
- 에러 처리 가이드
- 운영 매뉴얼

## 작업 계획

### 즉시 시작 가능한 작업
1. **개발 환경 설정**
   - Python 3.8+ 설치 및 가상환경 구성
   - Selenium WebDriver 또는 Chrome DevTools MCP 설정
   - 필요한 라이브러리 설치 (requests, pytest 등)

2. **기본 프로토타입 개발**
   - UI 자동화 기반 로그인 기능 구현
   - 차량 검색 기능 구현
   - 할인권 적용 기능 구현

3. **추가 API 분석**
   - Chrome DevTools MCP로 요청/응답 바디 상세 분석
   - 에러 응답 구조 분석
   - 토큰 관리 방법 확인

### 작업 우선순위
1. **높음**: UI 자동화 기반 프로토타입 개발
2. **중간**: 추가 API 분석 및 문서화
3. **낮음**: 하이브리드 방식 구현 및 최적화

---

**문서 작성일**: 2025년 10월 06일  
**문서 버전**: 1.0  
**다음 검토일**: 2025년 10월 13일
