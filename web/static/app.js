// AI 보컬 코치 웹 애플리케이션 JavaScript

// 전역 변수
let sessionId = null;
let selectedSection = null;
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let recordingTimer = null;
let recordingStartTime = null;

// API 기본 설정
const API_BASE = '/api';

// 초기화
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI 보컬 코치 애플리케이션 시작');
    checkBrowserSupport();
});

// 파일 업로드
async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) return;

    // 파일 크기 확인 (100MB 제한)
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
        showAlert('error', '파일 크기가 너무 큽니다. (최대 100MB)');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    showProgress('uploadProgress', 0);
    
    try {
        const response = await fetch(`${API_BASE}/upload-song`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            sessionId = result.session_id;
            showAlert('success', `✅ 업로드 완료: ${file.name}`);
            document.getElementById('analyzeBtn').disabled = false;
            activateStep(2);
            hideProgress('uploadProgress');
        } else {
            throw new Error(result.error || '업로드 실패');
        }
    } catch (error) {
        showAlert('error', `❌ 업로드 실패: ${error.message}`);
        hideProgress('uploadProgress');
    }
}

// 노래 분석
async function analyzeSong() {
    if (!sessionId) return;

    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.innerHTML = '<span class="loading"></span> 분석 중...';
    analyzeBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/analyze-song/${sessionId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('success', `✅ 분석 완료: ${result.sections.length}개 구간 생성`);
            displaySections(result.sections);
            activateStep(3);
        } else {
            throw new Error(result.error || '분석 실패');
        }
    } catch (error) {
        showAlert('error', `❌ 분석 실패: ${error.message}`);
    } finally {
        analyzeBtn.innerHTML = '🔍 노래 분석하기';
        analyzeBtn.disabled = false;
    }
}

// 구간 표시
function displaySections(sections) {
    const grid = document.getElementById('sectionsGrid');
    grid.innerHTML = '';
    
    sections.forEach((section, index) => {
        const card = document.createElement('div');
        card.className = 'section-card';
        card.onclick = () => selectSection(section, card);
        
        const difficultyClass = `difficulty-${section.difficulty}`;
        const difficultyEmoji = getDifficultyEmoji(section.difficulty);
        
        card.innerHTML = `
            <h4>${section.name}</h4>
            <p>⏱️ 길이: ${section.duration.toFixed(1)}초</p>
            <p>🎵 구간: ${section.start_time.toFixed(1)}s - ${section.end_time.toFixed(1)}s</p>
            <p>난이도: ${difficultyEmoji} 
                <span class="difficulty-badge ${difficultyClass}">${section.difficulty}</span>
            </p>
        `;
        
        grid.appendChild(card);
    });
}

// 구간 선택
function selectSection(section, cardElement) {
    // 이전 선택 해제
    document.querySelectorAll('.section-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // 새 선택
    cardElement.classList.add('selected');
    selectedSection = section;
    
    const sectionInfo = document.getElementById('selectedSectionInfo');
    sectionInfo.innerHTML = `
        <div class="alert alert-info section-info">
            <h4>선택된 구간: ${section.name}</h4>
            <p><strong>길이:</strong> ${section.duration.toFixed(1)}초</p>
            <p><strong>난이도:</strong> ${getDifficultyEmoji(section.difficulty)} ${section.difficulty}</p>
            <p>준비되면 아래 녹음 버튼을 눌러주세요.</p>
        </div>
    `;
    
    document.getElementById('recordBtn').disabled = false;
    activateStep(4);
}

// 녹음 토글
async function toggleRecording() {
    if (!isRecording) {
        await startRecording();
    } else {
        await stopRecording();
    }
}

// 녹음 시작
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                sampleRate: 44100
            }
        });
        
        mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm;codecs=opus'
        });
        audioChunks = [];
        
        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            await uploadRecording(audioBlob);
            
            // 스트림 정리
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start(100);
        isRecording = true;
        recordingStartTime = Date.now();
        
        updateRecordingUI(true);
        startRecordingTimer();
        
        // 자동 중지 타이머
        setTimeout(() => {
            if (isRecording) {
                stopRecording();
            }
        }, (selectedSection.duration + 1) * 1000);
        
    } catch (error) {
        console.error('녹음 시작 실패:', error);
        showAlert('error', '마이크 접근 권한이 필요합니다.');
    }
}

// 녹음 중지
async function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        updateRecordingUI(false);
        stopRecordingTimer();
    }
}

// 녹음 UI 업데이트
function updateRecordingUI(recording) {
    const recordBtn = document.getElementById('recordBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    
    if (recording) {
        recordBtn.classList.add('recording');
        recordBtn.innerHTML = '⏹️<br>중지';
        recordingStatus.innerHTML = `
            <div class="alert alert-info">
                🔴 녹음 중... 
                <div class="recording-timer" id="recordingTimer">00:00</div>
                <p>최대 ${selectedSection.duration.toFixed(1)}초</p>
            </div>
        `;
    } else {
        recordBtn.classList.remove('recording');
        recordBtn.innerHTML = '🎤<br>녹음';
        recordingStatus.innerHTML = `
            <div class="alert alert-info">📤 분석 중...</div>
        `;
    }
}

// 녹음 타이머
function startRecordingTimer() {
    recordingTimer = setInterval(() => {
        if (recordingStartTime) {
            const elapsed = (Date.now() - recordingStartTime) / 1000;
            const minutes = Math.floor(elapsed / 60);
            const seconds = Math.floor(elapsed % 60);
            const timerElement = document.getElementById('recordingTimer');
            if (timerElement) {
                timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        }
    }, 100);
}

function stopRecordingTimer() {
    if (recordingTimer) {
        clearInterval(recordingTimer);
        recordingTimer = null;
    }
    recordingStartTime = null;
}

// 녹음 업로드 및 분석
async function uploadRecording(audioBlob) {
    const formData = new FormData();
    formData.append('recording', audioBlob, 'recording.webm');
    formData.append('session_id', sessionId);
    formData.append('section_id', selectedSection.id);
    
    try {
        const response = await fetch(`${API_BASE}/analyze-recording`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result.analysis, result.feedback);
            activateStep(5);
        } else {
            throw new Error(result.error || '분석 실패');
        }
        
    } catch (error) {
        showAlert('error', `❌ 분석 실패: ${error.message}`);
    }
}

// 결과 표시
function displayResults(analysis, feedback) {
    const scores = analysis.scores || {};
    const feedbacks = feedback.feedbacks || [];
    
    let resultsHtml = '<div class="score-display">';
    
    // 점수 카드들
    Object.entries(scores).forEach(([category, score]) => {
        const percentage = (score * 100).toFixed(1);
        const emoji = getScoreEmoji(score);
        const categoryName = getCategoryName(category);
        const scoreClass = getScoreClass(score);
        
        resultsHtml += `
            <div class="score-card">
                <h5>${emoji} ${categoryName}</h5>
                <div class="score-value ${scoreClass}">${percentage}점</div>
            </div>
        `;
    });
    
    resultsHtml += '</div>';
    
    // 피드백
    if (feedbacks.length > 0) {
        resultsHtml += `
            <div class="feedback-list">
                <h5>💡 피드백</h5>
                <ul>
        `;
        feedbacks.forEach(fb => {
            resultsHtml += `<li>${fb}</li>`;
        });
        resultsHtml += '</ul></div>';
    }
    
    document.getElementById('analysisResults').innerHTML = resultsHtml;
    createResultsChart(scores);
}

// 결과 차트
function createResultsChart(scores) {
    const ctx = document.getElementById('resultsChart');
    if (!ctx) return;
    
    if (window.myChart) {
        window.myChart.destroy();
    }
    
    const categories = Object.keys(scores);
    const values = Object.values(scores).map(v => (v * 100).toFixed(1));
    const categoryNames = categories.map(getCategoryName);
    
    window.myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categoryNames,
            datasets: [{
                label: '점수',
                data: values,
                backgroundColor: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, max: 100 }
            }
        }
    });
}

// 세션 초기화
function resetSession() {
    if (confirm('새로 시작하시겠습니까?')) {
        location.reload();
    }
}

// 유틸리티 함수들
function activateStep(stepNumber) {
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });
    document.getElementById(`step${stepNumber}`).classList.add('active');
}

function showAlert(type, message) {
    const alertHtml = `<div class="alert alert-${type}">${message}</div>`;
    const activeStep = document.querySelector('.step.active');
    if (activeStep) {
        const existingAlert = activeStep.querySelector('.alert');
        if (existingAlert) existingAlert.remove();
        activeStep.insertAdjacentHTML('beforeend', alertHtml);
    }
}

function showProgress(progressId, value = 0) {
    const progressElement = document.getElementById(progressId);
    progressElement.style.display = 'block';
    progressElement.querySelector('.progress-bar').style.width = `${value}%`;
}

function hideProgress(progressId) {
    document.getElementById(progressId).style.display = 'none';
}

function getDifficultyEmoji(difficulty) {
    const emojis = { 'easy': '🟢', 'medium': '🟡', 'hard': '🔴' };
    return emojis[difficulty] || '🟡';
}

function getScoreEmoji(score) {
    if (score >= 0.9) return '🌟';
    if (score >= 0.8) return '🎉';
    if (score >= 0.7) return '👏';
    if (score >= 0.6) return '👍';
    return '💪';
}

function getScoreClass(score) {
    if (score >= 0.8) return 'score-excellent';
    if (score >= 0.7) return 'score-good';
    if (score >= 0.5) return 'score-fair';
    return 'score-poor';
}

function getCategoryName(category) {
    const names = {
        'pitch': '음정',
        'breath': '호흡', 
        'pronunciation': '발음',
        'vocal_onset': '성대 접촉'
    };
    return names[category] || category;
}

function checkBrowserSupport() {
    if (!window.MediaRecorder) {
        showAlert('warning', '이 브라우저는 녹음을 지원하지 않습니다.');
    }
}
