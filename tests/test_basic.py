#!/usr/bin/env python3
"""
아이파킹 자동화 시스템 간단 테스트
"""

from core.automation import IParkingAutomation


def test_basic_functionality():
    """기본 기능 테스트"""
    print("=== 아이파킹 자동화 시스템 테스트 ===")
    
    # 자동화 인스턴스 생성
    automation = IParkingAutomation(headless=True)
    
    try:
        # 1. WebDriver 설정 테스트
        print("1. WebDriver 설정 테스트...")
        if automation.setup_driver():
            print("✓ WebDriver 설정 성공")
        else:
            print("✗ WebDriver 설정 실패")
            return False
        
        # 2. 사이트 접속 테스트
        print("2. 사이트 접속 테스트...")
        if automation.navigate_to_site():
            print("✓ 사이트 접속 성공")
            print(f"  페이지 제목: {automation.driver.title}")
        else:
            print("✗ 사이트 접속 실패")
            return False
        
        # 3. 로그인 테스트
        print("3. 로그인 테스트...")
        if automation.login():
            print("✓ 로그인 성공")
        else:
            print("✗ 로그인 실패")
            return False
        
        # 4. 차량 검색 테스트
        print("4. 차량 검색 테스트...")
        if automation.search_vehicle("1255"):
            print("✓ 차량 검색 성공")
        else:
            print("✗ 차량 검색 실패")
            return False
        
        print("\n=== 모든 기본 기능 테스트 통과 ===")
        return True
        
    except Exception as e:
        print(f"✗ 테스트 중 오류 발생: {e}")
        return False
        
    finally:
        # WebDriver 종료
        automation.close_driver()
        print("WebDriver 종료 완료")


def test_full_automation():
    """전체 자동화 프로세스 테스트"""
    print("\n=== 전체 자동화 프로세스 테스트 ===")
    
    automation = IParkingAutomation(headless=True)
    
    try:
        # 전체 프로세스 실행
        result = automation.run_full_automation("1255")
        
        print(f"실행 결과: {'성공' if result['success'] else '실패'}")
        print(f"실행 시간: {result['execution_time']:.2f}초")
        
        if result['error']:
            print(f"에러: {result['error']}")
        
        print("\n단계별 결과:")
        for step, success in result['steps'].items():
            print(f"  {step}: {'성공' if success else '실패'}")
        
        return result['success']
        
    except Exception as e:
        print(f"✗ 전체 자동화 테스트 중 오류 발생: {e}")
        return False


if __name__ == "__main__":
    # 기본 기능 테스트
    basic_success = test_basic_functionality()
    
    # 전체 자동화 테스트
    full_success = test_full_automation()
    
    print(f"\n=== 테스트 결과 요약 ===")
    print(f"기본 기능 테스트: {'통과' if basic_success else '실패'}")
    print(f"전체 자동화 테스트: {'통과' if full_success else '실패'}")
    
    if basic_success and full_success:
        print("🎉 모든 테스트 통과!")
    else:
        print("❌ 일부 테스트 실패")
