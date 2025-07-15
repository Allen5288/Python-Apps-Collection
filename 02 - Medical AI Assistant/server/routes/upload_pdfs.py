from fastapi import APIRouter, UploadFile, File
from typing import List
from modules.load_vectorstore import load_vectorStore
from fastapi.responses import JSONResponse
from logger import logger

router = APIRouter()


@router.post("/upload_pdfs/")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    try:
        # Process the PDF file contents (e.g., extract text, metadata)
        logger.info(f"Received uploaded file")
        load_vectorStore(files)
        logger.info(f"Document added to vectorstore")
        return {"message": "PDFs uploaded and processed successfully"}
    except Exception as e:
        logger.exception(f"Error uploading PDFs: {e}")
        return JSONResponse(
            status_code=500, content={"message": "Error uploading PDFs"}
        )
