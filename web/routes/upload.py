"""
파일 업로드 라우터
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from web.models import UploadResponse, ErrorResponse
from web.services import session_manager, FileService

router = APIRouter()

@router.post("/upload-song", response_model=UploadResponse)
async def upload_song(file: UploadFile = File(...)):
    """노래 파일 업로드"""
    try:
        # 파일 형식 검증
        if not FileService.validate_audio_file(file):
            raise HTTPException(
                status_code=400, 
                detail="지원하지 않는 파일 형식입니다. (지원: MP3, WAV, FLAC, M4A, OGG)"
            )
        
        # 새 세션 생성
        session_id = session_manager.create_session()
        
        # 파일 저장
        upload_path = FileService.save_uploaded_file(file, session_id)
        
        return UploadResponse(
            success=True,
            session_id=session_id,
            filename=file.filename,
            message="파일 업로드 완료"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"업로드 실패: {str(e)}")

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """세션 삭제"""
    try:
        session_manager.delete_session(session_id)
        
        return JSONResponse({
            "success": True,
            "message": "세션이 삭제되었습니다."
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 삭제 실패: {str(e)}")
