#!/usr/bin/env python3
"""
쿠폰 적용 팝업 처리 테스트 스크립트
수정된 팝업 처리 로직을 검증합니다.
"""

import time
import logging
from core.automation import IParkingAutomation

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_popup_handling():
    """팝업 처리 로직 테스트"""
    automation = IParkingAutomation(headless=False)
    
    try:
        # WebDriver 설정
        if not automation.setup_driver():
            logger.error("WebDriver 설정 실패")
            return False
        
        # 사이트 접속
        if not automation.navigate_to_site():
            logger.error("사이트 접속 실패")
            return False
        
        # 로그인
        if not automation.login():
            logger.error("로그인 실패")
            return False
        
        # 차량 검색
        if not automation.search_vehicle():
            logger.error("차량 검색 실패")
            return False
        
        # 차량 선택
        if not automation.select_vehicle():
            logger.error("차량 선택 실패")
            return False
        
        # 할인권 적용 (팝업 처리 테스트)
        logger.info("=== 팝업 처리 테스트 시작 ===")
        start_time = time.time()
        
        if automation.apply_discount():
            end_time = time.time()
            logger.info(f"✓ 할인권 적용 성공 (소요시간: {end_time - start_time:.2f}초)")
            return True
        else:
            logger.error("✗ 할인권 적용 실패")
            return False
            
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {e}")
        return False
        
    finally:
        automation.close_driver()

def main():
    """메인 함수"""
    print("=== 쿠폰 적용 팝업 처리 테스트 ===")
    print("수정된 팝업 처리 로직을 검증합니다.")
    print()
    
    success = test_popup_handling()
    
    if success:
        print("\n🎉 팝업 처리 테스트 성공!")
        print("두 번째 팝업이 정상적으로 처리되었습니다.")
    else:
        print("\n❌ 팝업 처리 테스트 실패!")
        print("팝업 처리 로직을 다시 확인해주세요.")

if __name__ == "__main__":
    main()
