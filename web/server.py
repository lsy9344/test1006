#!/usr/bin/env python3
"""
아이파킹 상태 정보 서버
고객들에게 실시간 상태 정보를 제공하는 웹 서버
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import time
import threading
from flask import Flask, render_template_string, jsonify, request
from monitoring.extractor import StatusExtractor
import logging

# Flask 앱 설정
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 전역 변수
status_extractor = StatusExtractor()
current_status = None
status_lock = threading.Lock()

# HTML 템플릿
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>아이파킹 주차 할인권 적용 상태</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .status-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            padding: 40px;
            max-width: 600px;
            width: 100%;
            text-align: center;
        }

        .header {
            margin-bottom: 30px;
        }

        .header h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
        }

        .header p {
            color: #666;
            font-size: 16px;
        }

        .status-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            border-left: 5px solid #28a745;
        }

        .status-card.error {
            border-left-color: #dc3545;
        }

        .status-card.warning {
            border-left-color: #ffc107;
        }

        .status-message {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }

        .progress-container {
            margin-bottom: 20px;
        }

        .progress-bar {
            width: 100%;
            height: 12px;
            background: #e9ecef;
            border-radius: 6px;
            overflow: hidden;
            margin-bottom: 10px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            border-radius: 6px;
            transition: width 0.3s ease;
        }

        .progress-text {
            font-size: 14px;
            color: #666;
            font-weight: 500;
        }

        .steps-container {
            text-align: left;
            margin-bottom: 25px;
        }

        .step-item {
            display: flex;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #e9ecef;
        }

        .step-item:last-child {
            border-bottom: none;
        }

        .step-icon {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-size: 12px;
            font-weight: bold;
        }

        .step-icon.success {
            background: #28a745;
            color: white;
        }

        .step-icon.failed {
            background: #dc3545;
            color: white;
        }

        .step-icon.pending {
            background: #6c757d;
            color: white;
        }

        .step-text {
            flex: 1;
            font-size: 14px;
            color: #333;
        }

        .step-time {
            font-size: 12px;
            color: #666;
        }

        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #f5c6cb;
        }

        .estimated-time {
            background: #d1ecf1;
            color: #0c5460;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #bee5eb;
        }

        .refresh-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
        }

        .refresh-btn:hover {
            transform: translateY(-2px);
        }

        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            color: #666;
            font-size: 14px;
        }

        .loading {
            display: none;
        }

        .loading.show {
            display: block;
        }

        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
            .status-container {
                padding: 20px;
                margin: 10px;
            }
            
            .header h1 {
                font-size: 24px;
            }
            
            .status-message {
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <div class="status-container">
        <div class="header">
            <h1>🚗 아이파킹 주차 할인권</h1>
            <p>실시간 적용 상태를 확인하세요</p>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>상태 정보를 불러오는 중...</p>
        </div>

        <div id="status-content">
            <div class="status-card" id="status-card">
                <div class="status-message" id="status-message">
                    주차 할인권 적용이 진행 중입니다...
                </div>
                
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
                    </div>
                    <div class="progress-text" id="progress-text">진행률: 0%</div>
                </div>

                <div class="estimated-time" id="estimated-time" style="display: none;">
                    ⏳ 예상 남은 시간: <span id="remaining-time">0</span>초
                </div>

                <div class="error-message" id="error-message" style="display: none;">
                    🚨 오류가 발생했습니다: <span id="error-text"></span>
                </div>

                <div class="steps-container" id="steps-container">
                    <div class="step-item">
                        <div class="step-icon pending">1</div>
                        <div class="step-text">사이트 접속</div>
                        <div class="step-time" id="step1-time">대기 중...</div>
                    </div>
                    <div class="step-item">
                        <div class="step-icon pending">2</div>
                        <div class="step-text">로그인</div>
                        <div class="step-time" id="step2-time">대기 중...</div>
                    </div>
                    <div class="step-item">
                        <div class="step-icon pending">3</div>
                        <div class="step-text">차량번호 검색</div>
                        <div class="step-time" id="step3-time">대기 중...</div>
                    </div>
                    <div class="step-item">
                        <div class="step-icon pending">4</div>
                        <div class="step-text">차량 선택</div>
                        <div class="step-time" id="step4-time">대기 중...</div>
                    </div>
                    <div class="step-item">
                        <div class="step-icon pending">5</div>
                        <div class="step-text">할인권 적용</div>
                        <div class="step-time" id="step5-time">대기 중...</div>
                    </div>
                </div>
            </div>

            <button class="refresh-btn" onclick="refreshStatus()">🔄 상태 새로고침</button>
        </div>

        <div class="footer">
            <p>아이파킹 주차 할인권 자동화 시스템 v2.0</p>
            <p>마지막 업데이트: <span id="last-update">-</span></p>
        </div>
    </div>

    <script>
        let statusData = null;
        let updateInterval = null;

        // 상태 데이터 로드
        async function loadStatusData() {
            try {
                const response = await fetch('/api/status');
                if (response.ok) {
                    statusData = await response.json();
                    updateStatusDisplay();
                } else {
                    console.error('상태 데이터를 불러올 수 없습니다.');
                }
            } catch (error) {
                console.error('상태 데이터 로드 오류:', error);
            }
        }

        // 상태 표시 업데이트
        function updateStatusDisplay() {
            if (!statusData) return;

            const statusCard = document.getElementById('status-card');
            const statusMessage = document.getElementById('status-message');
            const progressFill = document.getElementById('progress-fill');
            const progressText = document.getElementById('progress-text');
            const estimatedTime = document.getElementById('estimated-time');
            const remainingTime = document.getElementById('remaining-time');
            const errorMessage = document.getElementById('error-message');
            const errorText = document.getElementById('error-text');
            const lastUpdate = document.getElementById('last-update');

            // 상태 카드 스타일 업데이트
            if (statusData.success) {
                statusCard.className = 'status-card';
                statusMessage.textContent = '✅ 주차 할인권 적용이 완료되었습니다!';
            } else if (statusData.error_message) {
                statusCard.className = 'status-card error';
                statusMessage.textContent = '❌ 주차 할인권 적용 중 오류가 발생했습니다';
                errorMessage.style.display = 'block';
                errorText.textContent = statusData.error_message;
            } else {
                statusCard.className = 'status-card warning';
                statusMessage.textContent = '⚠️ 주차 할인권 적용이 진행 중입니다...';
            }

            // 진행률 업데이트
            progressFill.style.width = statusData.progress_percentage + '%';
            progressText.textContent = `진행률: ${statusData.progress_percentage}%`;

            // 예상 남은 시간 업데이트
            if (statusData.estimated_remaining_time > 0) {
                estimatedTime.style.display = 'block';
                remainingTime.textContent = statusData.estimated_remaining_time;
            } else {
                estimatedTime.style.display = 'none';
            }

            // 단계별 상태 업데이트
            updateStepStatus();

            // 마지막 업데이트 시간
            const updateTime = new Date(statusData.timestamp * 1000);
            lastUpdate.textContent = updateTime.toLocaleString('ko-KR');
        }

        // 단계별 상태 업데이트
        function updateStepStatus() {
            const stepNames = ['site_access', 'login', 'vehicle_search', 'vehicle_selection', 'discount_application'];
            const stepTexts = ['사이트 접속', '로그인', '차량번호 검색', '차량 선택', '할인권 적용'];

            stepNames.forEach((stepName, index) => {
                const stepIcon = document.querySelector(`.step-item:nth-child(${index + 1}) .step-icon`);
                const stepTime = document.getElementById(`step${index + 1}-time`);

                const stepStatus = statusData.status_history.find(status => status.step === stepName);
                
                if (stepStatus) {
                    if (stepStatus.status === 'success') {
                        stepIcon.className = 'step-icon success';
                        stepIcon.textContent = '✓';
                        stepTime.textContent = '완료';
                    } else {
                        stepIcon.className = 'step-icon failed';
                        stepIcon.textContent = '✗';
                        stepTime.textContent = '실패';
                    }
                } else {
                    stepIcon.className = 'step-icon pending';
                    stepIcon.textContent = index + 1;
                    stepTime.textContent = '대기 중...';
                }
            });
        }

        // 상태 새로고침
        function refreshStatus() {
            document.getElementById('loading').classList.add('show');
            document.getElementById('status-content').style.display = 'none';
            
            setTimeout(() => {
                loadStatusData().then(() => {
                    document.getElementById('loading').classList.remove('show');
                    document.getElementById('status-content').style.display = 'block';
                });
            }, 1000);
        }

        // 자동 새로고침 설정
        function startAutoRefresh() {
            updateInterval = setInterval(() => {
                loadStatusData();
            }, 3000); // 3초마다 업데이트
        }

        // 페이지 로드 시 초기화
        document.addEventListener('DOMContentLoaded', function() {
            loadStatusData();
            startAutoRefresh();
        });

        // 페이지 언로드 시 인터벌 정리
        window.addEventListener('beforeunload', function() {
            if (updateInterval) {
                clearInterval(updateInterval);
            }
        });
    </script>
</body>
</html>
'''


def update_status_background():
    """백그라운드에서 상태 정보 업데이트"""
    global current_status
    
    while True:
        try:
            logger.info("상태 정보 업데이트 시작")
            
            # 상태 정보 추출
            status_data = status_extractor.extract_status_from_automation("1255")
            
            # 상태 데이터 업데이트
            with status_lock:
                current_status = status_data
            
            logger.info(f"상태 정보 업데이트 완료: {status_data['success']}")
            
            # 30초마다 업데이트
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"상태 정보 업데이트 실패: {e}")
            time.sleep(10)  # 오류 시 10초 후 재시도


@app.route('/')
def index():
    """메인 페이지"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/status')
def get_status():
    """상태 정보 API"""
    with status_lock:
        if current_status:
            return jsonify(current_status)
        else:
            return jsonify({
                'success': False,
                'status_history': [],
                'current_status': '상태 정보를 불러오는 중...',
                'progress_percentage': 0,
                'estimated_remaining_time': 0,
                'error_message': None,
                'timestamp': time.time()
            })


@app.route('/api/refresh', methods=['POST'])
def refresh_status():
    """상태 정보 강제 새로고침"""
    try:
        logger.info("상태 정보 강제 새로고침 요청")
        
        # 상태 정보 추출
        status_data = status_extractor.extract_status_from_automation("1255")
        
        # 상태 데이터 업데이트
        with status_lock:
            global current_status
            current_status = status_data
        
        return jsonify({
            'success': True,
            'message': '상태 정보가 새로고침되었습니다.',
            'data': status_data
        })
        
    except Exception as e:
        logger.error(f"상태 정보 새로고침 실패: {e}")
        return jsonify({
            'success': False,
            'message': f'상태 정보 새로고침 실패: {str(e)}'
        }), 500


@app.route('/api/status/history')
def get_status_history():
    """상태 이력 조회"""
    with status_lock:
        if current_status and 'status_history' in current_status:
            return jsonify(current_status['status_history'])
        else:
            return jsonify([])


def main():
    """메인 함수"""
    logger.info("아이파킹 상태 정보 서버 시작")
    
    # 백그라운드 상태 업데이트 스레드 시작
    status_thread = threading.Thread(target=update_status_background, daemon=True)
    status_thread.start()
    
    # Flask 서버 시작
    app.run(host='0.0.0.0', port=5001, debug=True)


if __name__ == "__main__":
    main()
