#!/usr/bin/env python3
"""
아이파킹 API 상태 정보 분석기
실제 API 응답을 캡처하여 상태 정보를 분석하고 고객용 상태 정보창을 위한 데이터를 추출
"""

import time
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


class IParkingAPIStatusAnalyzer:
    """아이파킹 API 상태 정보 분석 클래스"""
    
    def __init__(self):
        """초기화"""
        self.driver = None
        self.session = requests.Session()
        self.auth_token = None
        self.logger = logging.getLogger(__name__)
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # 설정
        self.base_url = "http://members.iparking.co.kr"
        self.test_account = {
            "username": "dtctrit2704",
            "password": "dtctrit2704"
        }
        self.test_vehicle = "1255"
        
        # 상태 정보 매핑
        self.status_messages = {
            'login_success': '로그인 성공',
            'login_failed': '로그인 실패',
            'vehicle_search_success': '차량 검색 성공',
            'vehicle_search_failed': '차량번호 입력 실패',
            'vehicle_not_found': '차량을 찾을 수 없습니다',
            'discount_apply_success': '할인권 적용 완료',
            'discount_apply_failed': '할인권 적용 실패',
            'discount_30min': '30분 할인권 적용 완료',
            'discount_1hour': '1시간 할인권 적용 완료',
            'parking_start': '주차 시작',
            'parking_end': '주차 종료',
            'error_network': '네트워크 오류',
            'error_timeout': '요청 시간 초과',
            'error_auth': '인증 오류'
        }
    
    def setup_driver(self) -> bool:
        """Chrome WebDriver 설정"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--log-level=0")
            
            # Chrome DevTools Protocol 활성화
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            # ChromeDriver 자동 설치 및 설정
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 타임아웃 설정
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            # CDP 활성화
            self.driver.execute_cdp_cmd('Network.enable', {})
            self.driver.execute_cdp_cmd('Runtime.enable', {})
            
            self.logger.info("Chrome WebDriver 설정 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"WebDriver 설정 실패: {e}")
            return False
    
    def close_driver(self):
        """WebDriver 종료"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("WebDriver 종료")
    
    def capture_api_responses(self) -> List[Dict[str, Any]]:
        """API 응답 캡처"""
        try:
            # 네트워크 요청 로그 수집
            logs = self.driver.get_log('performance')
            
            api_responses = []
            for log in logs:
                try:
                    message = json.loads(log['message'])
                    
                    if message['message']['method'] == 'Network.responseReceived':
                        response = message['message']['params']['response']
                        request = message['message']['params'].get('request', {})
                        
                        # API 요청만 필터링
                        if 'api' in response['url'] or 'members' in response['url']:
                            api_response = {
                                'url': response['url'],
                                'method': request.get('method', 'GET'),
                                'status': response['status'],
                                'headers': response.get('headers', {}),
                                'timestamp': log['timestamp']
                            }
                            api_responses.append(api_response)
                            
                except (json.JSONDecodeError, KeyError) as e:
                    continue
            
            return api_responses
            
        except Exception as e:
            self.logger.error(f"API 응답 캡처 실패: {e}")
            return []
    
    def analyze_login_status(self) -> Dict[str, Any]:
        """로그인 상태 분석"""
        try:
            self.driver.get(self.base_url)
            time.sleep(2)
            
            # 초기 팝업 처리
            self._handle_initial_popups()
            
            # 로그인 수행
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='아이디']"))
            )
            username_field.clear()
            username_field.send_keys(self.test_account["username"])
            
            password_field = self.driver.find_element(By.XPATH, "//input[@placeholder='비밀번호']")
            password_field.clear()
            password_field.send_keys(self.test_account["password"])
            
            # 로그인 버튼 클릭
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '로그인')]")
            self.driver.execute_script("arguments[0].click();", login_button)
            
            # 로그인 후 팝업 처리
            self._handle_login_popups()
            
            time.sleep(3)  # API 요청 완료 대기
            
            # 로그인 성공 확인
            if self._is_logged_in():
                # 인증 토큰 추출
                self.auth_token = self._extract_auth_token()
                
                return {
                    'status': 'success',
                    'message': self.status_messages['login_success'],
                    'auth_token': self.auth_token,
                    'timestamp': time.time()
                }
            else:
                return {
                    'status': 'failed',
                    'message': self.status_messages['login_failed'],
                    'error': '로그인 실패',
                    'timestamp': time.time()
                }
                
        except Exception as e:
            self.logger.error(f"로그인 상태 분석 실패: {e}")
            return {
                'status': 'error',
                'message': self.status_messages['error_network'],
                'error': str(e),
                'timestamp': time.time()
            }
    
    def analyze_vehicle_search_status(self, vehicle_number: str = None) -> Dict[str, Any]:
        """차량 검색 상태 분석"""
        try:
            vehicle_number = vehicle_number or self.test_vehicle
            
            # 차량번호 입력
            vehicle_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1234']"))
            )
            vehicle_field.clear()
            vehicle_field.send_keys(vehicle_number)
            
            # 검색 버튼 클릭
            search_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '검색')]")
            self.driver.execute_script("arguments[0].click();", search_button)
            
            time.sleep(3)  # API 요청 완료 대기
            
            # 검색 결과 확인
            if self._wait_for_search_results():
                # 차량 정보 추출
                vehicle_info = self._extract_vehicle_info()
                
                return {
                    'status': 'success',
                    'message': self.status_messages['vehicle_search_success'],
                    'vehicle_number': vehicle_number,
                    'vehicle_info': vehicle_info,
                    'timestamp': time.time()
                }
            else:
                return {
                    'status': 'failed',
                    'message': self.status_messages['vehicle_not_found'],
                    'vehicle_number': vehicle_number,
                    'error': '차량을 찾을 수 없습니다',
                    'timestamp': time.time()
                }
                
        except Exception as e:
            self.logger.error(f"차량 검색 상태 분석 실패: {e}")
            return {
                'status': 'error',
                'message': self.status_messages['vehicle_search_failed'],
                'error': str(e),
                'timestamp': time.time()
            }
    
    def analyze_discount_status(self, discount_type: str = "30분할인권") -> Dict[str, Any]:
        """할인권 적용 상태 분석"""
        try:
            # 차량 선택
            select_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '차량 선택')]"))
            )
            self.driver.execute_script("arguments[0].click();", select_button)
            
            time.sleep(3)  # 페이지 로드 대기
            
            # 할인권 적용 버튼 클릭
            apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '적용')]"))
            )
            self.driver.execute_script("arguments[0].click();", apply_button)
            
            # 확인 팝업 처리
            confirm_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '확인')]"))
            )
            self.driver.execute_script("arguments[0].click();", confirm_button)
            
            # 두 번째 팝업 처리 (할인권 적용 완료 팝업)
            try:
                success_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '확인')]"))
                )
                self.driver.execute_script("arguments[0].click();", success_button)
                self.logger.info("두 번째 팝업 처리 완료")
            except TimeoutException:
                self.logger.info("두 번째 팝업 없음")
            
            time.sleep(3)  # API 요청 완료 대기
            
            # 적용 결과 확인
            if self._check_discount_applied():
                # 할인권 정보 추출
                discount_info = self._extract_discount_info()
                
                return {
                    'status': 'success',
                    'message': self.status_messages[f'discount_{discount_type.replace("할인권", "").replace("분", "")}'],
                    'discount_type': discount_type,
                    'discount_info': discount_info,
                    'timestamp': time.time()
                }
            else:
                return {
                    'status': 'failed',
                    'message': self.status_messages['discount_apply_failed'],
                    'discount_type': discount_type,
                    'error': '할인권 적용 실패',
                    'timestamp': time.time()
                }
                
        except Exception as e:
            self.logger.error(f"할인권 적용 상태 분석 실패: {e}")
            return {
                'status': 'error',
                'message': self.status_messages['discount_apply_failed'],
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _extract_auth_token(self) -> Optional[str]:
        """인증 토큰 추출"""
        try:
            # localStorage에서 토큰 추출
            token = self.driver.execute_script("return localStorage.getItem('auth_token');")
            if token:
                return token
            
            # 쿠키에서 토큰 추출
            cookies = self.driver.get_cookies()
            for cookie in cookies:
                if 'token' in cookie['name'].lower():
                    return cookie['value']
            
            # 네트워크 요청에서 토큰 추출
            logs = self.driver.get_log('performance')
            for log in logs:
                try:
                    message = json.loads(log['message'])
                    if message['message']['method'] == 'Network.requestWillBeSent':
                        headers = message['message']['params']['request'].get('headers', {})
                        if 'authorization' in headers:
                            return headers['authorization']
                except:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"인증 토큰 추출 실패: {e}")
            return None
    
    def _extract_vehicle_info(self) -> Dict[str, Any]:
        """차량 정보 추출"""
        try:
            # 차량 정보가 표시되는 요소 찾기
            vehicle_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'vehicle') or contains(@class, 'car')]")
            
            vehicle_info = {}
            for element in vehicle_elements:
                text = element.text
                if text:
                    vehicle_info['display_text'] = text
                    break
            
            return vehicle_info
            
        except Exception as e:
            self.logger.error(f"차량 정보 추출 실패: {e}")
            return {}
    
    def _extract_discount_info(self) -> Dict[str, Any]:
        """할인권 정보 추출"""
        try:
            # 할인권 정보가 표시되는 요소 찾기
            discount_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'discount') or contains(@class, 'ticket')]")
            
            discount_info = {}
            for element in discount_elements:
                text = element.text
                if text:
                    discount_info['display_text'] = text
                    break
            
            return discount_info
            
        except Exception as e:
            self.logger.error(f"할인권 정보 추출 실패: {e}")
            return {}
    
    def _is_logged_in(self) -> bool:
        """로그인 상태 확인"""
        try:
            # 메인 페이지 요소 확인
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1234']"))
            )
            return True
        except TimeoutException:
            return False
    
    def _wait_for_search_results(self) -> bool:
        """검색 결과 대기"""
        try:
            # 차량 선택 버튼이 나타날 때까지 대기
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '차량 선택')]"))
            )
            return True
        except TimeoutException:
            return False
    
    def _check_discount_applied(self) -> bool:
        """할인권 적용 확인"""
        try:
            # 적용 완료 메시지 확인
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '적용') or contains(text(), '완료')]"))
            )
            return True
        except TimeoutException:
            return False
    
    def _handle_initial_popups(self):
        """초기 팝업 처리"""
        try:
            skip_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Skip')]"))
            )
            self.driver.execute_script("arguments[0].click();", skip_button)
            self.logger.info("Skip 팝업 처리 완료")
        except TimeoutException:
            self.logger.info("Skip 팝업 없음")
        
        try:
            dont_show_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '다시 보지 않기')]"))
            )
            self.driver.execute_script("arguments[0].click();", dont_show_button)
            self.logger.info("고객센터 안내 팝업 처리 완료")
        except TimeoutException:
            self.logger.info("고객센터 안내 팝업 없음")
    
    def _handle_login_popups(self):
        """로그인 후 팝업 처리"""
        try:
            close_button1 = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '닫기')]"))
            )
            self.driver.execute_script("arguments[0].click();", close_button1)
            self.logger.info("첫 번째 팝업 처리 완료")
        except TimeoutException:
            self.logger.info("첫 번째 팝업 없음")
        
        try:
            close_button2 = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '닫기')]"))
            )
            self.driver.execute_script("arguments[0].click();", close_button2)
            self.logger.info("두 번째 팝업 처리 완료")
        except TimeoutException:
            self.logger.info("두 번째 팝업 없음")
    
    def run_full_status_analysis(self) -> Dict[str, Any]:
        """전체 상태 분석 실행"""
        result = {
            'success': False,
            'login_status': {},
            'vehicle_search_status': {},
            'discount_status': {},
            'all_status_messages': [],
            'timestamp': time.time()
        }
        
        try:
            # WebDriver 설정
            if not self.setup_driver():
                result['error'] = "WebDriver 설정 실패"
                return result
            
            # 1. 로그인 상태 분석
            self.logger.info("로그인 상태 분석 시작")
            login_status = self.analyze_login_status()
            result['login_status'] = login_status
            result['all_status_messages'].append(login_status['message'])
            
            if login_status['status'] != 'success':
                result['error'] = "로그인 실패"
                return result
            
            # 2. 차량 검색 상태 분석
            self.logger.info("차량 검색 상태 분석 시작")
            search_status = self.analyze_vehicle_search_status()
            result['vehicle_search_status'] = search_status
            result['all_status_messages'].append(search_status['message'])
            
            if search_status['status'] != 'success':
                result['error'] = "차량 검색 실패"
                return result
            
            # 3. 할인권 적용 상태 분석
            self.logger.info("할인권 적용 상태 분석 시작")
            discount_status = self.analyze_discount_status()
            result['discount_status'] = discount_status
            result['all_status_messages'].append(discount_status['message'])
            
            result['success'] = True
            self.logger.info("전체 상태 분석 완료")
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"상태 분석 실패: {e}")
            
        finally:
            self.close_driver()
        
        return result
    
    def save_status_results(self, results: Dict[str, Any], filename: str = "api_status_results.json"):
        """상태 분석 결과를 JSON 파일로 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            self.logger.info(f"상태 분석 결과 저장 완료: {filename}")
        except Exception as e:
            self.logger.error(f"상태 분석 결과 저장 실패: {e}")


def main():
    """메인 함수"""
    analyzer = IParkingAPIStatusAnalyzer()
    
    print("=== 아이파킹 API 상태 정보 분석 시작 ===")
    results = analyzer.run_full_status_analysis()
    
    if results['success']:
        print("✓ 상태 분석 완료")
        
        # 결과 출력
        print(f"\n로그인 상태:")
        print(f"  - 상태: {results['login_status']['status']}")
        print(f"  - 메시지: {results['login_status']['message']}")
        if 'auth_token' in results['login_status']:
            print(f"  - 인증 토큰: {results['login_status']['auth_token'][:20]}...")
        
        print(f"\n차량 검색 상태:")
        print(f"  - 상태: {results['vehicle_search_status']['status']}")
        print(f"  - 메시지: {results['vehicle_search_status']['message']}")
        if 'vehicle_info' in results['vehicle_search_status']:
            print(f"  - 차량 정보: {results['vehicle_search_status']['vehicle_info']}")
        
        print(f"\n할인권 적용 상태:")
        print(f"  - 상태: {results['discount_status']['status']}")
        print(f"  - 메시지: {results['discount_status']['message']}")
        if 'discount_info' in results['discount_status']:
            print(f"  - 할인권 정보: {results['discount_status']['discount_info']}")
        
        print(f"\n전체 상태 메시지:")
        for i, message in enumerate(results['all_status_messages'], 1):
            print(f"  {i}. {message}")
        
        # 결과 저장
        analyzer.save_status_results(results)
        
    else:
        print(f"✗ 상태 분석 실패: {results.get('error', '알 수 없는 오류')}")


if __name__ == "__main__":
    main()
