#!/usr/bin/env python3
"""
아이파킹 API 분석기 v2
Chrome DevTools Protocol을 사용하여 네트워크 요청을 직접 캡처
"""

import time
import json
import logging
from typing import Dict, Any, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


class IParkingAPIAnalyzerV2:
    """아이파킹 API 분석 클래스 v2"""
    
    def __init__(self):
        """초기화"""
        self.driver = None
        self.api_calls = []
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
    
    def setup_driver(self) -> bool:
        """Chrome WebDriver 설정 (CDP 활성화)"""
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
            
            self.logger.info("Chrome WebDriver 설정 완료 (CDP 활성화)")
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
    
    def capture_network_requests(self) -> List[Dict[str, Any]]:
        """네트워크 요청 캡처 (CDP 사용)"""
        try:
            # 네트워크 요청 로그 수집
            logs = self.driver.get_log('performance')
            
            api_calls = []
            for log in logs:
                try:
                    message = json.loads(log['message'])
                    
                    if message['message']['method'] == 'Network.responseReceived':
                        response = message['message']['params']['response']
                        request = message['message']['params'].get('request', {})
                        
                        # API 요청만 필터링
                        if 'api' in response['url'] or 'members' in response['url']:
                            api_call = {
                                'url': response['url'],
                                'method': request.get('method', 'GET'),
                                'status': response['status'],
                                'headers': response.get('headers', {}),
                                'timestamp': log['timestamp']
                            }
                            api_calls.append(api_call)
                            
                except (json.JSONDecodeError, KeyError) as e:
                    continue
            
            return api_calls
            
        except Exception as e:
            self.logger.error(f"네트워크 요청 캡처 실패: {e}")
            return []
    
    def analyze_login_api(self) -> Dict[str, Any]:
        """로그인 API 분석"""
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
            
            # 네트워크 요청 분석
            api_calls = self.capture_network_requests()
            
            # 로그인 관련 API 필터링
            login_apis = []
            for call in api_calls:
                if any(keyword in call['url'] for keyword in ['login', 'auth', 'oauth', 'members']):
                    login_apis.append(call)
            
            return {
                'success': True,
                'api_calls': login_apis,
                'total_calls': len(api_calls)
            }
            
        except Exception as e:
            self.logger.error(f"로그인 API 분석 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_vehicle_search_api(self) -> Dict[str, Any]:
        """차량 검색 API 분석"""
        try:
            # 차량번호 입력
            vehicle_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1234']"))
            )
            vehicle_field.clear()
            vehicle_field.send_keys(self.test_vehicle)
            
            # 검색 버튼 클릭
            search_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '검색')]")
            self.driver.execute_script("arguments[0].click();", search_button)
            
            time.sleep(3)  # API 요청 완료 대기
            
            # 네트워크 요청 분석
            api_calls = self.capture_network_requests()
            
            # 차량 검색 관련 API 필터링
            search_apis = []
            for call in api_calls:
                if any(keyword in call['url'] for keyword in ['carlist', 'vehicle', 'search', 'discount']):
                    search_apis.append(call)
            
            return {
                'success': True,
                'api_calls': search_apis,
                'total_calls': len(api_calls)
            }
            
        except Exception as e:
            self.logger.error(f"차량 검색 API 분석 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_discount_api(self) -> Dict[str, Any]:
        """할인권 관련 API 분석"""
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
            
            # 네트워크 요청 분석
            api_calls = self.capture_network_requests()
            
            # 할인권 관련 API 필터링
            discount_apis = []
            for call in api_calls:
                if any(keyword in call['url'] for keyword in ['discount', 'apply', 'product']):
                    discount_apis.append(call)
            
            return {
                'success': True,
                'api_calls': discount_apis,
                'total_calls': len(api_calls)
            }
            
        except Exception as e:
            self.logger.error(f"할인권 API 분석 실패: {e}")
            return {'success': False, 'error': str(e)}
    
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
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """전체 API 분석 실행"""
        result = {
            'success': False,
            'login_analysis': {},
            'vehicle_search_analysis': {},
            'discount_analysis': {},
            'all_api_calls': []
        }
        
        try:
            # WebDriver 설정
            if not self.setup_driver():
                result['error'] = "WebDriver 설정 실패"
                return result
            
            # 1. 로그인 API 분석
            self.logger.info("로그인 API 분석 시작")
            login_result = self.analyze_login_api()
            result['login_analysis'] = login_result
            
            # 2. 차량 검색 API 분석
            self.logger.info("차량 검색 API 분석 시작")
            search_result = self.analyze_vehicle_search_api()
            result['vehicle_search_analysis'] = search_result
            
            # 3. 할인권 API 분석
            self.logger.info("할인권 API 분석 시작")
            discount_result = self.analyze_discount_api()
            result['discount_analysis'] = discount_result
            
            # 전체 API 호출 수집
            all_calls = []
            if login_result.get('success'):
                all_calls.extend(login_result.get('api_calls', []))
            if search_result.get('success'):
                all_calls.extend(search_result.get('api_calls', []))
            if discount_result.get('success'):
                all_calls.extend(discount_result.get('api_calls', []))
            
            result['all_api_calls'] = all_calls
            result['success'] = True
            
            self.logger.info("전체 API 분석 완료")
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"API 분석 실패: {e}")
            
        finally:
            self.close_driver()
        
        return result
    
    def save_analysis_results(self, results: Dict[str, Any], filename: str = "api_analysis_results_v2.json"):
        """분석 결과를 JSON 파일로 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            self.logger.info(f"분석 결과 저장 완료: {filename}")
        except Exception as e:
            self.logger.error(f"분석 결과 저장 실패: {e}")


def main():
    """메인 함수"""
    analyzer = IParkingAPIAnalyzerV2()
    
    print("=== 아이파킹 API 분석 v2 시작 ===")
    results = analyzer.run_full_analysis()
    
    if results['success']:
        print("✓ API 분석 완료")
        
        # 결과 출력
        print(f"\n로그인 API 분석:")
        if results['login_analysis'].get('success'):
            print(f"  - API 호출 수: {len(results['login_analysis'].get('api_calls', []))}")
            for call in results['login_analysis'].get('api_calls', []):
                print(f"    {call['method']} {call['url']} (상태: {call['status']})")
        
        print(f"\n차량 검색 API 분석:")
        if results['vehicle_search_analysis'].get('success'):
            print(f"  - API 호출 수: {len(results['vehicle_search_analysis'].get('api_calls', []))}")
            for call in results['vehicle_search_analysis'].get('api_calls', []):
                print(f"    {call['method']} {call['url']} (상태: {call['status']})")
        
        print(f"\n할인권 API 분석:")
        if results['discount_analysis'].get('success'):
            print(f"  - API 호출 수: {len(results['discount_analysis'].get('api_calls', []))}")
            for call in results['discount_analysis'].get('api_calls', []):
                print(f"    {call['method']} {call['url']} (상태: {call['status']})")
        
        print(f"\n전체 API 호출 수: {len(results['all_api_calls'])}")
        
        # 결과 저장
        analyzer.save_analysis_results(results)
        
    else:
        print(f"✗ API 분석 실패: {results.get('error', '알 수 없는 오류')}")


if __name__ == "__main__":
    main()
