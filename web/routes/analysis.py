"""
노래 분석 라우터
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List

from web.models import AnalysisResponse, Section
from web.services import session_manager, AnalysisService

router = APIRouter()

@router.post("/analyze-song/{session_id}", response_model=AnalysisResponse)
async def analyze_song(session_id: str):
    """노래 분석 및 구간 생성"""
    try:
        sections_data = AnalysisService.analyze_song(session_id)
        
        # Pydantic 모델로 변환
        sections = [Section(**section_data) for section_data in sections_data]
        
        return AnalysisResponse(
            success=True,
            sections=sections,
            message=f"{len(sections)}개 연습 구간 생성 완료"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")

@router.get("/sections/{session_id}")
async def get_sections(session_id: str):
    """세션의 연습 구간 목록 조회"""
    try:
        coach = session_manager.get_coach(session_id)
        
        sections = []
        for section in coach.practice_sections:
            sections.append({
                "id": section['id'],
                "name": section['name'],
                "start_time": float(section['start_time']),
                "end_time": float(section['end_time']),
                "duration": float(section['duration']),
                "difficulty": section.get('difficulty', 'medium')
            })
        
        return JSONResponse({
            "success": True,
            "sections": sections
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"구간 조회 실패: {str(e)}")

@router.get("/section/{session_id}/{section_id}")
async def get_section_detail(session_id: str, section_id: int):
    """특정 구간의 상세 정보 조회"""
    try:
        coach = session_manager.get_coach(session_id)
        
        # 해당 구간 찾기
        selected_section = None
        for section in coach.practice_sections:
            if section['id'] == section_id:
                selected_section = section
                break
        
        if not selected_section:
            raise HTTPException(status_code=404, detail="구간을 찾을 수 없습니다.")
        
        return JSONResponse({
            "success": True,
            "section": {
                "id": selected_section['id'],
                "name": selected_section['name'],
                "start_time": float(selected_section['start_time']),
                "end_time": float(selected_section['end_time']),
                "duration": float(selected_section['duration']),
                "difficulty": selected_section.get('difficulty', 'medium')
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"구간 상세 조회 실패: {str(e)}")
