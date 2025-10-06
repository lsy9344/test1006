#!/usr/bin/env python3
"""
아이파킹 상태 정보 추출기
실제 자동화 과정에서 상태 정보를 추출하여 고객용 상태 정보창에 표시할 데이터를 생성
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional
from core.automation import IParkingAutomation


class StatusExtractor:
    """상태 정보 추출 클래스"""
    
    def __init__(self):
        """초기화"""
        self.automation = IParkingAutomation(headless=True)
        self.status_history = []
        self.logger = logging.getLogger(__name__)
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # 상태 메시지 매핑
        self.status_messages = {
            'site_access_success': '사이트 접속 성공',
            'site_access_failed': '사이트 접속 실패',
            'login_success': '로그인 성공',
            'login_failed': '로그인 실패',
            'vehicle_search_success': '차량번호 검색 성공',
            'vehicle_search_failed': '차량번호 입력 실패',
            'vehicle_not_found': '차량을 찾을 수 없습니다',
            'vehicle_selection_success': '차량 선택 성공',
            'vehicle_selection_failed': '차량 선택 실패',
            'discount_application_success': '할인권 적용 완료',
            'discount_application_failed': '할인권 적용 실패',
            'discount_30min_success': '30분 할인권 적용 완료',
            'discount_1hour_success': '1시간 할인권 적용 완료',
            'process_complete': '전체 프로세스 완료',
            'process_failed': '프로세스 실패',
            'error_network': '네트워크 오류',
            'error_timeout': '요청 시간 초과',
            'error_auth': '인증 오류'
        }
    
    def extract_status_from_automation(self, vehicle_number: str = "1255") -> Dict[str, Any]:
        """자동화 과정에서 상태 정보 추출"""
        result = {
            'success': False,
            'status_history': [],
            'current_status': '',
            'progress_percentage': 0,
            'estimated_remaining_time': 0,
            'error_message': None,
            'timestamp': time.time()
        }
        
        try:
            # 자동화 실행
            automation_result = self.automation.run_full_automation(vehicle_number)
            
            # 단계별 상태 정보 추출
            if automation_result['success']:
                result['success'] = True
                result['current_status'] = self.status_messages['process_complete']
                result['progress_percentage'] = 100
                
                # 단계별 상태 메시지 생성
                step_messages = {
                    'site_access': self.status_messages['site_access_success'],
                    'login': self.status_messages['login_success'],
                    'vehicle_search': self.status_messages['vehicle_search_success'],
                    'vehicle_selection': self.status_messages['vehicle_selection_success'],
                    'discount_application': self.status_messages['discount_application_success']
                }
                
                for step, success in automation_result['steps'].items():
                    if success:
                        status_msg = step_messages.get(step, f"{step} 성공")
                        result['status_history'].append({
                            'step': step,
                            'status': 'success',
                            'message': status_msg,
                            'timestamp': time.time()
                        })
                    else:
                        status_msg = f"{step} 실패"
                        result['status_history'].append({
                            'step': step,
                            'status': 'failed',
                            'message': status_msg,
                            'timestamp': time.time()
                        })
                
            else:
                result['success'] = False
                result['current_status'] = self.status_messages['process_failed']
                result['error_message'] = automation_result.get('error', '알 수 없는 오류')
                
                # 실패한 단계까지의 상태 메시지 생성
                for step, success in automation_result['steps'].items():
                    if success:
                        status_msg = f"{step} 성공"
                        result['status_history'].append({
                            'step': step,
                            'status': 'success',
                            'message': status_msg,
                            'timestamp': time.time()
                        })
                    else:
                        status_msg = f"{step} 실패"
                        result['status_history'].append({
                            'step': step,
                            'status': 'failed',
                            'message': status_msg,
                            'timestamp': time.time()
                        })
                        break  # 실패한 단계에서 중단
            
            # 진행률 계산
            if result['status_history']:
                success_count = sum(1 for status in result['status_history'] if status['status'] == 'success')
                total_steps = len(result['status_history'])
                result['progress_percentage'] = int((success_count / total_steps) * 100)
            
            # 예상 남은 시간 계산 (초)
            if result['success']:
                result['estimated_remaining_time'] = 0
            else:
                remaining_steps = 5 - len(result['status_history'])
                result['estimated_remaining_time'] = remaining_steps * 3  # 단계당 3초 예상
            
        except Exception as e:
            result['success'] = False
            result['current_status'] = self.status_messages['error_network']
            result['error_message'] = str(e)
            self.logger.error(f"상태 정보 추출 실패: {e}")
        
        return result
    
    def generate_customer_status_message(self, status_data: Dict[str, Any]) -> str:
        """고객용 상태 메시지 생성"""
        if status_data['success']:
            return f"✅ 주차 할인권 적용이 완료되었습니다! (진행률: {status_data['progress_percentage']}%)"
        else:
            if status_data['error_message']:
                return f"❌ 주차 할인권 적용 중 오류가 발생했습니다: {status_data['error_message']}"
            else:
                return f"⚠️ 주차 할인권 적용이 진행 중입니다... (진행률: {status_data['progress_percentage']}%)"
    
    def generate_detailed_status_report(self, status_data: Dict[str, Any]) -> List[str]:
        """상세 상태 보고서 생성"""
        report = []
        
        report.append(f"📊 주차 할인권 적용 상태 보고서")
        report.append(f"⏰ 시간: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(status_data['timestamp']))}")
        report.append(f"📈 진행률: {status_data['progress_percentage']}%")
        
        if status_data['estimated_remaining_time'] > 0:
            report.append(f"⏳ 예상 남은 시간: {status_data['estimated_remaining_time']}초")
        
        report.append(f"📋 단계별 진행 상황:")
        
        for i, status in enumerate(status_data['status_history'], 1):
            if status['status'] == 'success':
                report.append(f"  {i}. ✅ {status['message']}")
            else:
                report.append(f"  {i}. ❌ {status['message']}")
        
        if status_data['error_message']:
            report.append(f"🚨 오류 메시지: {status_data['error_message']}")
        
        return report
    
    def save_status_data(self, status_data: Dict[str, Any], filename: str = "status_data.json"):
        """상태 데이터를 JSON 파일로 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"상태 데이터 저장 완료: {filename}")
        except Exception as e:
            self.logger.error(f"상태 데이터 저장 실패: {e}")


def main():
    """메인 함수"""
    extractor = StatusExtractor()
    
    print("=== 아이파킹 상태 정보 추출 시작 ===")
    
    # 상태 정보 추출
    status_data = extractor.extract_status_from_automation("1255")
    
    # 고객용 상태 메시지 생성
    customer_message = extractor.generate_customer_status_message(status_data)
    print(f"\n📱 고객용 상태 메시지:")
    print(f"   {customer_message}")
    
    # 상세 상태 보고서 생성
    detailed_report = extractor.generate_detailed_status_report(status_data)
    print(f"\n📊 상세 상태 보고서:")
    for line in detailed_report:
        print(f"   {line}")
    
    # 상태 데이터 저장
    extractor.save_status_data(status_data)
    
    print(f"\n✅ 상태 정보 추출 완료")
    print(f"   - 성공 여부: {'성공' if status_data['success'] else '실패'}")
    print(f"   - 진행률: {status_data['progress_percentage']}%")
    print(f"   - 상태 이력: {len(status_data['status_history'])}개 단계")


if __name__ == "__main__":
    main()
