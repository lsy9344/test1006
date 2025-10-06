# 아이파킹 멤버 사이트 API 분석 결과

## 개요
Chrome DevTools MCP를 사용하여 아이파킹 멤버 사이트의 실제 API 호출을 분석한 결과입니다.

## 분석 일시
- 분석 일시: 2025년 10월 06일
- 테스트 계정: dtctrit2704 / dtctrit2704
- 테스트 차량번호: 1255

## 주요 발견사항

### 1. 인증 시스템
- **인증 토큰**: `b0f43959-1656-467f-a2ad-b88eecc36236`
- **토큰 형식**: UUID 형태의 문자열
- **토큰 획득**: 로그인 성공 시 자동으로 획득
- **토큰 사용**: 모든 API 요청의 `authorization` 헤더에 포함

### 2. 로그인 프로세스
로그인은 UI를 통해서만 가능하며, 별도의 로그인 API 호출은 확인되지 않았습니다.
로그인 성공 후 다음 API들이 자동으로 호출됩니다:

#### 2.1 매장 목록 조회
```
POST http://members.iparking.co.kr/api/members/store/list/dtctrit2704
Headers:
- authorization: b0f43959-1656-467f-a2ad-b88eecc36236
- referer: http://members.iparking.co.kr/html/home.html
- content-type: application/json;charset=UTF-8
- version: 2.0.0
```

#### 2.2 알림 팝업 조회
```
GET http://members.iparking.co.kr/api/members/notice/alram/popup?_=1759722798063
Headers:
- accept: application/json, text/javascript, */*; q=0.01
- content-type: application/json;charset=UTF-8
- version: 2.0.0
- referer: http://members.iparking.co.kr/
```

### 3. 차량 검색 API

#### 3.1 차량 검색
```
POST http://members.iparking.co.kr/api/members/discount/carlist
Headers:
- authorization: b0f43959-1656-467f-a2ad-b88eecc36236
- referer: http://members.iparking.co.kr/html/car-search-list.html
- content-type: application/json;charset=UTF-8
- version: 2.0.0
```

**특징**:
- 차량번호 4자리 입력 시 호출
- 검색 결과는 차량 이미지와 함께 표시
- 차량 선택 시 할인권 적용 페이지로 이동

### 4. 할인권 관련 API

#### 4.1 할인권 적용 목록 조회
```
POST http://members.iparking.co.kr/api/members/discount/apply/list
Headers:
- authorization: b0f43959-1656-467f-a2ad-b88eecc36236
- referer: http://members.iparking.co.kr/html/discount-ticket-apply.html
- content-type: application/json;charset=UTF-8
- version: 2.0.0
```

#### 4.2 할인권 상품 목록 조회
```
POST http://members.iparking.co.kr/api/members/discount/product/list
Headers:
- authorization: b0f43959-1656-467f-a2ad-b88eecc36236
- referer: http://members.iparking.co.kr/html/discount-ticket-apply.html
- content-type: application/json;charset=UTF-8
- version: 2.0.0
```

### 5. 공통 헤더 구조
모든 API 요청에서 공통적으로 사용되는 헤더:

```
authorization: {토큰}
referer: {현재 페이지 URL}
user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36
accept: application/json, text/javascript, */*; q=0.01
content-type: application/json;charset=UTF-8
version: 2.0.0
```

### 6. 응답 헤더 구조
모든 API 응답에서 공통적으로 확인되는 헤더:

```
cache-control: no-cache, no-store, max-age=0, must-revalidate
connection: keep-alive
content-encoding: gzip
content-type: application/json;charset=UTF-8
server: nginx/1.20.1
set-cookie: Path=/; HttpOnly; Secure
x-application-context: members-service:iparking:8094
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
```

## API 호출 플로우

### 1. 로그인 후 초기화
1. 사이트 접속 → 로그인 페이지
2. 로그인 성공 → 메인 페이지 로드
3. 자동 호출:
   - 매장 목록 조회 API
   - 알림 팝업 조회 API

### 2. 차량 검색
1. 차량번호 입력 (4자리)
2. 검색 버튼 클릭
3. 차량 검색 API 호출
4. 검색 결과 표시
5. 차량 선택 → 할인권 적용 페이지로 이동

### 3. 할인권 적용
1. 할인권 적용 목록 조회 API 호출
2. 할인권 상품 목록 조회 API 호출
3. 할인권 적용/취소 버튼 클릭
4. 확인 팝업 처리
5. 적용 완료

## 주요 API 엔드포인트 요약

| 기능 | 메서드 | 엔드포인트 | 설명 |
|------|--------|------------|------|
| 매장 목록 | POST | `/api/members/store/list/{userId}` | 사용자별 매장 목록 조회 |
| 알림 팝업 | GET | `/api/members/notice/alram/popup` | 알림 팝업 정보 조회 |
| 차량 검색 | POST | `/api/members/discount/carlist` | 차량번호로 차량 검색 |
| 할인권 적용 목록 | POST | `/api/members/discount/apply/list` | 현재 적용된 할인권 목록 |
| 할인권 상품 목록 | POST | `/api/members/discount/product/list` | 보유한 할인권 상품 목록 |

## 보안 및 인증

### 인증 토큰 관리
- 토큰은 로그인 시 자동으로 획득
- 모든 API 요청에 `authorization` 헤더로 포함
- 토큰 만료 시 재로그인 필요

### 보안 헤더
- `x-frame-options: SAMEORIGIN` - 클릭재킹 방지
- `x-content-type-options: nosniff` - MIME 타입 스니핑 방지
- `set-cookie: HttpOnly; Secure` - 쿠키 보안 설정

## 에러 처리

### 네트워크 에러
- 일부 이미지 요청에서 `net::ERR_BLOCKED_BY_ORB` 에러 발생
- Google Analytics 요청에서 `net::ERR_ABORTED` 에러 발생
- 이는 정상적인 동작으로 보임

### API 응답
- 모든 주요 API는 200 상태 코드로 성공 응답
- 응답 본문은 gzip으로 압축되어 전송

## 다음 단계

### 추가 분석 필요사항
1. **요청 바디 구조**: 각 API의 요청 바디 상세 분석
2. **응답 데이터 구조**: 각 API의 응답 데이터 상세 분석
3. **에러 응답**: 에러 상황별 응답 구조 분석
4. **토큰 갱신**: 토큰 만료 시 갱신 방법 확인

### 자동화 구현 방안
1. **로그인 자동화**: UI 자동화를 통한 로그인
2. **API 호출 자동화**: 획득한 토큰으로 직접 API 호출
3. **에러 처리**: 네트워크 오류 및 API 에러 처리 로직 구현
4. **재시도 로직**: 실패 시 재시도 메커니즘 구현

## 결론

아이파킹 멤버 사이트의 주요 API 구조를 성공적으로 분석했습니다. 
인증 토큰 기반의 RESTful API를 사용하며, 모든 요청에 공통 헤더가 포함됩니다.
이 분석 결과를 바탕으로 API 기반 자동화 시스템을 구축할 수 있습니다.

---

**분석 완료일**: 2025년 10월 06일  
**분석 도구**: Chrome DevTools MCP  
**분석자**: AI Assistant
