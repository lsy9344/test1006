#!/usr/bin/env python3
"""
아이파킹 멤버 사이트 자동화 시스템
Task 02: API 기반 자동화 시스템 구축

기능:
- 로그인 자동화
- 차량번호 검색
- 할인권 적용
- 에러 처리 및 재시도 로직
"""

import time
import logging
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import requests

from .config import Config
from utils.helpers import setup_logging, measure_time, create_result_dict


class IParkingAutomation:
    """아이파킹 멤버 사이트 자동화 클래스"""
    
    def __init__(self, headless: bool = False):
        """
        초기화
        
        Args:
            headless: 헤드리스 모드 여부
        """
        self.driver = None
        self.token = None
        self.session = requests.Session()
        self.headless = headless
        
        # 설정 로드
        self.config = Config()
        self.config.update_from_env()
        
        # 로깅 설정
        self.logger = setup_logging(self.config.log_level, self.config.log_format)
        
        # 설정 값들
        self.base_url = self.config.base_url
        self.test_account = self.config.test_account
        self.test_vehicle = self.config.test_vehicle
        
    def setup_driver(self) -> bool:
        """
        Chrome WebDriver 설정
        
        Returns:
            bool: 설정 성공 여부
        """
        try:
            chrome_options = Options()
            for option in self.config.get_chrome_options(self.headless):
                chrome_options.add_argument(option)
            
            # ChromeDriver 자동 설치 및 설정
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 타임아웃 설정
            self.driver.implicitly_wait(self.config.implicit_wait)
            self.driver.set_page_load_timeout(self.config.page_load_timeout)
            
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
    
    def navigate_to_site(self) -> bool:
        """
        아이파킹 사이트 접속
        
        Returns:
            bool: 접속 성공 여부
        """
        try:
            self.driver.get(self.base_url)
            self.logger.info(f"사이트 접속: {self.base_url}")
            
            # 초기 팝업 처리
            self._handle_initial_popups()
            
            return True
            
        except Exception as e:
            self.logger.error(f"사이트 접속 실패: {e}")
            return False
    
    def _handle_initial_popups(self):
        """초기 팝업 처리"""
        try:
            # Skip 버튼 클릭 (JavaScript로 클릭하여 요소 가림 문제 해결)
            skip_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Skip')]"))
            )
            self.driver.execute_script("arguments[0].click();", skip_button)
            self.logger.info("Skip 팝업 처리 완료")
            
        except TimeoutException:
            self.logger.info("Skip 팝업 없음")
        
        try:
            # "다시 보지 않기" 버튼 클릭 (JavaScript로 클릭하여 요소 가림 문제 해결)
            dont_show_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '다시 보지 않기')]"))
            )
            self.driver.execute_script("arguments[0].click();", dont_show_button)
            self.logger.info("고객센터 안내 팝업 처리 완료")
            
        except TimeoutException:
            self.logger.info("고객센터 안내 팝업 없음")
    
    def login(self, username: str = None, password: str = None) -> bool:
        """
        로그인 수행
        
        Args:
            username: 아이디 (기본값: 테스트 계정)
            password: 비밀번호 (기본값: 테스트 계정)
            
        Returns:
            bool: 로그인 성공 여부
        """
        try:
            username = username or self.test_account["username"]
            password = password or self.test_account["password"]
            
            # 아이디 입력
            username_field = WebDriverWait(self.driver, self.config.element_wait_timeout).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='아이디']"))
            )
            username_field.clear()
            username_field.send_keys(username)
            
            # 비밀번호 입력
            password_field = self.driver.find_element(By.XPATH, "//input[@placeholder='비밀번호']")
            password_field.clear()
            password_field.send_keys(password)
            
            # 로그인 버튼 클릭 (JavaScript로 클릭하여 요소 가림 문제 해결)
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '로그인')]")
            self.driver.execute_script("arguments[0].click();", login_button)
            
            self.logger.info("로그인 버튼 클릭 완료")
            
            # 로그인 후 팝업 처리
            self._handle_login_popups()
            
            # 로그인 성공 확인
            if self._is_logged_in():
                self.logger.info("로그인 성공")
                return True
            else:
                self.logger.error("로그인 실패")
                return False
                
        except Exception as e:
            self.logger.error(f"로그인 실패: {e}")
            return False
    
    def _handle_login_popups(self):
        """로그인 후 팝업 처리"""
        try:
            # 첫 번째 팝업 닫기 (JavaScript로 클릭하여 요소 가림 문제 해결)
            close_button1 = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '닫기')]"))
            )
            self.driver.execute_script("arguments[0].click();", close_button1)
            self.logger.info("첫 번째 팝업 처리 완료")
            
            # 두 번째 팝업 닫기 (JavaScript로 클릭하여 요소 가림 문제 해결)
            close_button2 = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '닫기')]"))
            )
            self.driver.execute_script("arguments[0].click();", close_button2)
            self.logger.info("두 번째 팝업 처리 완료")
            
        except TimeoutException:
            self.logger.info("로그인 후 팝업 없음")
    
    def _is_logged_in(self) -> bool:
        """로그인 상태 확인"""
        try:
            # 메인 페이지 요소 확인
            WebDriverWait(self.driver, self.config.element_wait_timeout).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1234']"))
            )
            return True
        except TimeoutException:
            return False
    
    def search_vehicle(self, vehicle_number: str = None) -> bool:
        """
        차량번호 검색
        
        Args:
            vehicle_number: 차량번호 (기본값: 테스트 차량번호)
            
        Returns:
            bool: 검색 성공 여부
        """
        try:
            vehicle_number = vehicle_number or self.test_vehicle
            
            # 차량번호 입력
            vehicle_field = WebDriverWait(self.driver, self.config.element_wait_timeout).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='1234']"))
            )
            vehicle_field.clear()
            vehicle_field.send_keys(vehicle_number)
            
            # 검색 버튼 클릭 (JavaScript로 클릭하여 요소 가림 문제 해결)
            search_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '검색')]")
            self.driver.execute_script("arguments[0].click();", search_button)
            
            self.logger.info(f"차량번호 검색: {vehicle_number}")
            
            # 검색 결과 확인
            if self._wait_for_search_results():
                self.logger.info("차량 검색 성공")
                return True
            else:
                self.logger.error("차량 검색 실패")
                return False
                
        except Exception as e:
            self.logger.error(f"차량 검색 실패: {e}")
            return False
    
    def _wait_for_search_results(self) -> bool:
        """검색 결과 대기"""
        try:
            # 차량 선택 버튼이 나타날 때까지 대기
            WebDriverWait(self.driver, self.config.element_wait_timeout).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '차량 선택')]"))
            )
            return True
        except TimeoutException:
            return False
    
    def select_vehicle(self) -> bool:
        """
        검색된 차량 선택
        
        Returns:
            bool: 선택 성공 여부
        """
        try:
            # 차량 선택 버튼 클릭 (JavaScript로 클릭하여 요소 가림 문제 해결)
            select_button = WebDriverWait(self.driver, self.config.element_wait_timeout).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '차량 선택')]"))
            )
            self.driver.execute_script("arguments[0].click();", select_button)
            
            self.logger.info("차량 선택 완료")
            
            # 할인권 적용 페이지로 이동 확인
            if self._wait_for_discount_page():
                self.logger.info("할인권 적용 페이지 이동 성공")
                return True
            else:
                self.logger.error("할인권 적용 페이지 이동 실패")
                return False
                
        except Exception as e:
            self.logger.error(f"차량 선택 실패: {e}")
            return False
    
    def _wait_for_discount_page(self) -> bool:
        """할인권 적용 페이지 대기"""
        try:
            # 할인권 적용 버튼이 나타날 때까지 대기
            WebDriverWait(self.driver, self.config.element_wait_timeout).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '적용')]"))
            )
            return True
        except TimeoutException:
            return False
    
    def apply_discount(self, discount_type: str = "30분할인권") -> bool:
        """
        할인권 적용
        
        Args:
            discount_type: 할인권 타입 ("30분할인권" 또는 "1시간할인권")
            
        Returns:
            bool: 적용 성공 여부
        """
        try:
            # 할인권 적용 버튼 클릭 (JavaScript로 클릭하여 요소 가림 문제 해결)
            self.logger.info(f"할인권 적용 버튼 찾는 중: {discount_type}")
            apply_button = WebDriverWait(self.driver, self.config.element_wait_timeout).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '적용')]"))
            )
            self.driver.execute_script("arguments[0].click();", apply_button)
            
            self.logger.info(f"할인권 적용 버튼 클릭: {discount_type}")
            
            # 확인 팝업 처리
            if self._handle_discount_popups():
                self.logger.info(f"할인권 적용 성공: {discount_type}")
                return True
            else:
                self.logger.error(f"할인권 적용 실패: {discount_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"할인권 적용 실패: {e}")
            # 디버깅을 위해 현재 페이지의 모든 버튼 출력
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                self.logger.info(f"현재 페이지의 버튼 수: {len(buttons)}")
                for i, button in enumerate(buttons[:10]):  # 처음 10개만 출력
                    try:
                        text = button.text
                        self.logger.info(f"버튼 {i+1}: '{text}'")
                    except:
                        self.logger.info(f"버튼 {i+1}: 텍스트 읽기 실패")
            except Exception as debug_e:
                self.logger.error(f"디버깅 정보 수집 실패: {debug_e}")
            return False
    
    def _handle_discount_popups(self) -> bool:
        """할인권 적용 팝업 처리"""
        try:
            # 첫 번째 팝업: "적용하시겠습니까?" 팝업에서 확인 클릭
            self.logger.info("첫 번째 팝업 대기 중...")
            confirm_button = WebDriverWait(self.driver, self.config.element_wait_timeout).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '확인')]"))
            )
            self.driver.execute_script("arguments[0].click();", confirm_button)
            self.logger.info("첫 번째 팝업 (적용 확인) 처리 완료")
            
            # 잠시 대기
            time.sleep(1)
            
            # 두 번째 팝업: "할인권 1장이 적용되었습니다." 팝업에서 확인 클릭
            self.logger.info("두 번째 팝업 대기 중...")
            success_button = WebDriverWait(self.driver, self.config.element_wait_timeout).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '확인')]"))
            )
            self.driver.execute_script("arguments[0].click();", success_button)
            self.logger.info("두 번째 팝업 (적용 완료) 처리 완료")
            
            # 쿠폰 적용 완료
            self.logger.info("쿠폰 적용 팝업 처리 완료")
            return True
            
        except TimeoutException as e:
            self.logger.error(f"할인권 적용 팝업 처리 실패: {e}")
            # 현재 페이지의 모든 버튼을 로그로 출력하여 디버깅
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                self.logger.info(f"현재 페이지의 버튼 수: {len(buttons)}")
                for i, button in enumerate(buttons[:5]):  # 처음 5개만 출력
                    try:
                        text = button.text
                        self.logger.info(f"버튼 {i+1}: '{text}'")
                    except:
                        self.logger.info(f"버튼 {i+1}: 텍스트 읽기 실패")
            except Exception as debug_e:
                self.logger.error(f"디버깅 정보 수집 실패: {debug_e}")
            return False
    
    @measure_time
    def run_full_automation(self, vehicle_number: str = None) -> Dict[str, Any]:
        """
        전체 자동화 프로세스 실행
        
        Args:
            vehicle_number: 차량번호 (기본값: 테스트 차량번호)
            
        Returns:
            Dict[str, Any]: 실행 결과
        """
        start_time = time.time()
        
        try:
            # 1. WebDriver 설정
            if not self.setup_driver():
                return create_result_dict(False, error="WebDriver 설정 실패")
            
            # 2. 사이트 접속
            if not self.navigate_to_site():
                return create_result_dict(False, error="사이트 접속 실패")
            
            # 3. 로그인
            if not self.login():
                return create_result_dict(False, error="로그인 실패")
            
            # 4. 차량 검색
            if not self.search_vehicle(vehicle_number):
                return create_result_dict(False, error="차량 검색 실패")
            
            # 5. 차량 선택
            if not self.select_vehicle():
                return create_result_dict(False, error="차량 선택 실패")
            
            # 6. 할인권 적용
            if not self.apply_discount():
                return create_result_dict(False, error="할인권 적용 실패")
            
            self.logger.info("전체 자동화 프로세스 완료")
            return create_result_dict(True, message="자동화 프로세스 성공")
            
        except Exception as e:
            self.logger.error(f"자동화 프로세스 실패: {e}")
            return create_result_dict(False, error=str(e))
            
        finally:
            self.close_driver()


def main():
    """메인 함수"""
    automation = IParkingAutomation(headless=False)
    result = automation.run_full_automation()
    
    print("\n=== 자동화 실행 결과 ===")
    print(f"성공: {result['success']}")
    
    if 'execution_time' in result:
        print(f"실행 시간: {result['execution_time']:.2f}초")
    
    if result.get("error"):
        print(f"에러: {result['error']}")
    
    if result.get("message"):
        print(f"메시지: {result['message']}")
    
    print(f"타임스탬프: {result.get('timestamp_formatted', 'N/A')}")


if __name__ == "__main__":
    main()
