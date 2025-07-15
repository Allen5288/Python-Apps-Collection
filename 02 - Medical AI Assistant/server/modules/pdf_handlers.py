import os
import shutil
from fastapi import UploadFile
import tempfile

UPLOAD_DIR = "./uploaded_docs"

def save_uploaded_files(files: list[UploadFile]) -> list[str]:
    """
    Save uploaded files to the server's upload directory.
    
    Args:
        files (list[UploadFile]): List of uploaded files.
        
    Returns:
        list[str]: List of file paths where the files are saved.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_paths = []

    for file in files:
        temp_file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(temp_file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_paths.append(temp_file_path)

    return file_paths