#!/usr/bin/env python3
"""
아이파킹 자동화 시스템 테스트
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import time
from core.automation import IParkingAutomation

print("hdddddddi")

# 프로젝트 루트 경로를 sys.path에 추가합니다.
# (pytest.ini 설정이나 `python -m pytest` 사용을 권장합니다.)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestIParkingAutomation:
    """아이파킹 자동화 테스트 클래스"""
@pytest.fixture(scope="function")
def automation():
    """IParkingAutomation 인스턴스를 생성하고 테스트 후 정리하는 fixture"""
    auto = IParkingAutomation(headless=True)
    # yield 키워드로 테스트 함수에 auto 객체를 전달합니다.
    yield auto
    # 테스트 함수가 끝나면 아래 코드가 실행됩니다.
    if auto.driver:
        auto.close_driver()

def test_driver_setup(automation):
    """WebDriver 설정 및 종료 테스트"""
    assert automation.setup_driver() is True
    assert automation.driver is not None
    
    def __init__(self):
        """테스트 클래스 초기화""" 
        self.automation = IParkingAutomation(headless=True)
    automation.close_driver()
    assert automation.driver is None

def test_site_access(automation):
    """사이트 접속 테스트"""
    assert automation.setup_driver() is True
    assert automation.navigate_to_site() is True
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        pass
    title = automation.driver.title.lower()
    assert any(keyword in title for keyword in ["아이파킹", "i parking", "로그인", "login"])

def test_login_process(automation):
    """로그인 프로세스 테스트"""
    assert automation.setup_driver() is True
    assert automation.navigate_to_site() is True
    
    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        if hasattr(self, 'automation') and self.automation.driver:
            self.automation.close_driver()
    result = automation.login()
    assert result is True
    assert automation._is_logged_in() is True

def test_vehicle_search(automation):
    """차량 검색 테스트"""
    assert automation.setup_driver() is True
    assert automation.navigate_to_site() is True
    assert automation.login() is True
    
    def test_driver_setup(self):
        """WebDriver 설정 테스트"""
        assert self.automation.setup_driver() == True
        assert self.automation.driver is not None
        
        # WebDriver 종료
        self.automation.close_driver()
        assert self.automation.driver is None
    result = automation.search_vehicle("1255")
    assert result is True
    assert automation._wait_for_search_results() is True

def test_full_automation():
    """전체 자동화 프로세스 테스트"""
    # 이 테스트는 전체 흐름을 확인하므로 독립적인 인스턴스를 사용합니다.
    automation = IParkingAutomation(headless=True)
    result = automation.run_full_automation("1255")
    
    def test_site_access(self):
        """사이트 접속 테스트"""
        assert self.automation.setup_driver() == True
        assert self.automation.navigate_to_site() == True
        
        # 페이지 제목 확인 (아이파킹 또는 로그인 관련 키워드)
        title = self.automation.driver.title.lower()
        assert any(keyword in title for keyword in ["아이파킹", "i parking", "로그인", "login"])
    assert result["success"] is True, f"자동화 실패: {result.get('error')}"
    assert result["execution_time"] < 30
    
    def test_login_process(self):
        """로그인 프로세스 테스트"""
        assert self.automation.setup_driver() == True
        assert self.automation.navigate_to_site() == True
        
        # 로그인 시도
        result = self.automation.login()
        
        # 로그인 성공 여부 확인
        if result:
            assert self.automation._is_logged_in() == True
        else:
            # 로그인 실패 시 에러 메시지 확인
            assert "로그인" in self.automation.driver.page_source
    assert all(result["steps"].values())

def test_error_handling_invalid_vehicle():
    """잘못된 차량번호로 에러 처리 테스트"""
    automation = IParkingAutomation(headless=True)
    result = automation.run_full_automation("9999")
    
    def test_vehicle_search(self):
        """차량 검색 테스트"""
        assert self.automation.setup_driver() == True
        assert self.automation.navigate_to_site() == True
        assert self.automation.login() == True
        
        # 차량 검색
        result = self.automation.search_vehicle("1255")
        
        if result:
            # 검색 결과 확인
            assert self.automation._wait_for_search_results() == True
        else:
            # 검색 실패 시 에러 메시지 확인
            assert "검색" in self.automation.driver.page_source
    
    def test_full_automation(self):
        """전체 자동화 프로세스 테스트"""
        result = self.automation.run_full_automation("1255")
        
        # 실행 시간 확인 (30초 이내)
        assert result["execution_time"] < 30
        
        # 단계별 결과 확인
        if result["success"]:
            assert result["steps"]["site_access"] == True
            assert result["steps"]["login"] == True
            assert result["steps"]["vehicle_search"] == True
            assert result["steps"]["vehicle_selection"] == True
            assert result["steps"]["discount_application"] == True
        else:
            # 실패 시 에러 메시지 확인
            assert result["error"] is not None
    
    def test_error_handling(self):
        """에러 처리 테스트"""
        # 잘못된 차량번호로 테스트
        result = self.automation.run_full_automation("9999")
        
        # 에러 처리 확인
        if not result["success"]:
            assert result["error"] is not None
            assert "실패" in result["error"] or "에러" in result["error"]
    assert result["success"] is False
    assert result["error"] is not None
    assert "차량" in result["error"] and "실패" in result["error"]


def test_performance():
    """성능 테스트"""
    automation = IParkingAutomation(headless=True)
    
    start_time = time.time()
    result = automation.run_full_automation()
    end_time = time.time()
    
    execution_time = end_time - start_time
    
    # 30초 이내 완료되어야 함
    assert execution_time < 30
    
    # 실행 시간과 측정 시간이 비슷해야 함
    assert abs(execution_time - result["execution_time"]) < 1


def test_concurrent_execution():
    """동시 실행 테스트"""
    # 여러 인스턴스 동시 실행 테스트
    automations = [IParkingAutomation(headless=True) for _ in range(3)]
    
    results = []
    for automation in automations:
        result = automation.run_full_automation()
        results.append(result)
    
    # 모든 실행이 완료되어야 함
    for result in results:
        assert result["execution_time"] > 0
        assert result["error"] is not None or result["success"] is not None


if __name__ == "__main__":
    # 개별 테스트 실행
    test_automation = TestIParkingAutomation()
    
    print("=== WebDriver 설정 테스트 ===")
    test_automation.test_driver_setup()
    print("✓ WebDriver 설정 테스트 통과")
    
    print("\n=== 사이트 접속 테스트 ===")
    test_automation.test_site_access()
    print("✓ 사이트 접속 테스트 통과")
    
    print("\n=== 로그인 프로세스 테스트 ===")
    test_automation.test_login_process()
    print("✓ 로그인 프로세스 테스트 통과")
    
    print("\n=== 차량 검색 테스트 ===")
    test_automation.test_vehicle_search()
    print("✓ 차량 검색 테스트 통과")
    
    print("\n=== 전체 자동화 프로세스 테스트 ===")
    test_automation.test_full_automation()
    print("✓ 전체 자동화 프로세스 테스트 통과")
    
    print("\n=== 에러 처리 테스트 ===")
    test_automation.test_error_handling()
    print("✓ 에러 처리 테스트 통과")
    
    print("\n=== 성능 테스트 ===")
    test_performance()
    print("✓ 성능 테스트 통과")
    
    print("\n=== 모든 테스트 완료 ===")
