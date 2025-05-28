"""
녹음 및 분석 라우터
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse

from web.models import RecordingResponse
from web.services import session_manager, FileService, AnalysisService

router = APIRouter()

@router.post("/analyze-recording", response_model=RecordingResponse)
async def analyze_recording(
    recording: UploadFile = File(...),
    session_id: str = Form(...),
    section_id: int = Form(...)
):
    """녹음 분석"""
    try:
        # 녹음 파일 저장
        recording_path = FileService.save_recording(recording, session_id, section_id)
        
        # 녹음 분석
        analysis_data = AnalysisService.analyze_recording(session_id, section_id, recording_path)
        
        return RecordingResponse(
            success=True,
            analysis=analysis_data["analysis"],
            feedback=analysis_data["feedback"],
            section=analysis_data["section"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"녹음 분석 실패: {str(e)}")

@router.post("/start-recording/{session_id}/{section_id}")
async def start_recording_session(session_id: str, section_id: int):
    """녹음 세션 시작 (메타데이터 설정)"""
    try:
        coach = session_manager.get_coach(session_id)
        
        # 해당 구간 찾기
        selected_section = None
        for section in coach.practice_sections:
            if section['id'] == section_id:
                selected_section = section
                break
        
        if not selected_section:
            raise HTTPException(status_code=404, detail="선택된 구간을 찾을 수 없습니다.")
        
        return JSONResponse({
            "success": True,
            "section": {
                "name": selected_section['name'],
                "duration": float(selected_section['duration']),
                "start_time": float(selected_section['start_time']),
                "end_time": float(selected_section['end_time'])
            },
            "message": "녹음 준비 완료"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"녹음 세션 시작 실패: {str(e)}")

@router.get("/recording-history/{session_id}")
async def get_recording_history(session_id: str):
    """세션의 녹음 히스토리 조회"""
    try:
        import glob
        import os
        from web.config import get_settings
        
        settings = get_settings()
        recording_pattern = f"{settings.RECORDING_DIR}/{session_id}_*.wav"
        
        recordings = []
        for file_path in glob.glob(recording_pattern):
            filename = os.path.basename(file_path)
            # 파일명에서 section_id 추출
            try:
                section_id = int(filename.split('_')[1].split('.')[0])
                file_size = os.path.getsize(file_path)
                modified_time = os.path.getmtime(file_path)
                
                recordings.append({
                    "section_id": section_id,
                    "filename": filename,
                    "file_size": file_size,
                    "created_at": modified_time
                })
            except (IndexError, ValueError):
                continue
        
        # 생성 시간 기준으로 정렬
        recordings.sort(key=lambda x: x["created_at"], reverse=True)
        
        return JSONResponse({
            "success": True,
            "recordings": recordings
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"녹음 히스토리 조회 실패: {str(e)}")
