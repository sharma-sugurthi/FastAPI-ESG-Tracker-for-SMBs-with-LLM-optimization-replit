"""
CSV upload and processing API endpoints.
"""

import os
import uuid
from typing import Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
import aiofiles
import pandas as pd

try:
    from app.models.user import User
    from app.models.csv_data import CSVUploadResponse, CSVTemplate
    from app.core.security import get_current_active_user
    from app.services.csv_service import csv_service
    from app.core.config import settings
except Exception:
    from user import User
    from csv_data import CSVUploadResponse, CSVTemplate
    from security import get_current_active_user
    from csv_service import csv_service
    from config import settings
from datetime import datetime

router = APIRouter()


@router.post("/csv-upload", response_model=CSVUploadResponse)
async def upload_csv_file(
    file: UploadFile = File(...),
    use_llm_for_missing: bool = Form(True),
    industry: str = Form("retail"),
    company_name: Optional[str] = Form(None),
    column_mapping: Optional[str] = Form(None),  # JSON string
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload and process ESG CSV file.
    
    Accepts CSV or Excel files with ESG metrics and processes them with
    optional LLM suggestions for missing values.
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in csv_service.supported_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format. Supported formats: {csv_service.supported_formats}"
            )
        
        # Check file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > csv_service.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {csv_service.max_file_size} bytes"
            )
        
        # Generate unique upload ID and filename
        upload_id = str(uuid.uuid4())
        safe_filename = f"{upload_id}_{file.filename}"
        file_path = os.path.join(settings.upload_dir, safe_filename)
        
        # Save uploaded file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Parse column mapping if provided
        parsed_column_mapping = None
        if column_mapping:
            try:
                import json
                parsed_column_mapping = json.loads(column_mapping)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid column mapping JSON"
                )
        
        # Process the file
        processing_result = await csv_service.process_csv_file(
            file_path=file_path,
            use_llm_for_missing=use_llm_for_missing,
            column_mapping=parsed_column_mapping,
            industry=industry
        )
        
        # Save processed data if successful
        download_url = None
        if processing_result.status in ["valid", "partial"]:
            processed_file_path = csv_service.save_processed_data(
                processing_result.processed_data,
                safe_filename
            )
            download_url = f"/upload/download/{upload_id}"
        
        # Calculate ESG score if data is valid
        if processing_result.processed_data:
            # Convert processed data to ESG answers format for scoring
            try:
                from app.models.esg import ESGAnswer
                from app.api.esg import calculate_esg_score
            except Exception:
                from esg import ESGAnswer
                from esg import calculate_esg_score
            
            answers = []
            for row_data in processing_result.processed_data:
                for field, value in row_data.items():
                    if field != "row_index" and value is not None:
                        answers.append(ESGAnswer(
                            question_id=field,
                            value=value,
                            is_llm_suggested=False,
                            source="csv_upload"
                        ))
            
            if answers:
                esg_score = calculate_esg_score(answers)
                processing_result.esg_score = esg_score.overall_score
        
        return CSVUploadResponse(
            upload_id=upload_id,
            filename=file.filename,
            processing_result=processing_result,
            download_url=download_url,
            created_at=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )
    finally:
        # Clean up uploaded file
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass


@router.get("/csv-template", response_model=CSVTemplate)
async def get_csv_template():
    """
    Get CSV template with ESG fields and sample data.
    """
    return csv_service.generate_csv_template()


@router.get("/csv-template/download")
async def download_csv_template():
    """
    Download CSV template file.
    """
    try:
        template = csv_service.generate_csv_template()
        
        # Create temporary CSV file
        temp_filename = f"temp_{uuid.uuid4()}.csv"
        temp_path = os.path.join(settings.upload_dir, temp_filename)
        
        # Convert sample data to DataFrame and save
        df = pd.DataFrame(template.sample_data)
        df.to_csv(temp_path, index=False)
        
        return FileResponse(
            path=temp_path,
            filename=template.filename,
            media_type='text/csv',
            background=None  # File will be cleaned up manually
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate template: {str(e)}"
        )


@router.get("/download/{upload_id}")
async def download_processed_file(
    upload_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Download processed CSV file.
    """
    try:
        # Find processed file
        processed_filename = None
        for filename in os.listdir(settings.upload_dir):
            if filename.startswith(f"processed_{upload_id}_"):
                processed_filename = filename
                break
        
        if not processed_filename:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processed file not found"
            )
        
        file_path = os.path.join(settings.upload_dir, processed_filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return FileResponse(
            path=file_path,
            filename=f"processed_esg_data_{upload_id}.csv",
            media_type='text/csv'
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {str(e)}"
        )


@router.get("/column-mappings")
async def get_default_column_mappings():
    """
    Get default column mappings for ESG CSV files.
    """
    try:
        from app.models.csv_data import DEFAULT_CSV_MAPPINGS
    except Exception:
        from csv_data import DEFAULT_CSV_MAPPINGS
    
    mappings = {}
    for mapping in DEFAULT_CSV_MAPPINGS:
        mappings[mapping.csv_column] = {
            "esg_field": mapping.esg_field,
            "data_type": mapping.data_type,
            "required": mapping.required,
            "validation_rules": mapping.validation_rules
        }
    
    return {
        "mappings": mappings,
        "description": "Default column mappings for ESG CSV files",
        "supported_formats": csv_service.supported_formats
    }


@router.post("/validate-csv")
async def validate_csv_structure(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate CSV structure without processing data.
    Returns column information and validation results.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Save temporarily for validation
        temp_filename = f"temp_validate_{uuid.uuid4()}.csv"
        temp_path = os.path.join(settings.upload_dir, temp_filename)
        
        async with aiofiles.open(temp_path, 'wb') as f:
            await f.write(content)
        
        try:
            # Read with pandas
            df = csv_service._read_file(temp_path)
            
            # Analyze structure
            column_info = []
            for col in df.columns:
                col_info = {
                    "name": col,
                    "data_type": str(df[col].dtype),
                    "non_null_count": int(df[col].count()),
                    "null_count": int(df[col].isnull().sum()),
                    "sample_values": df[col].dropna().head(3).tolist()
                }
                column_info.append(col_info)
            
            # Check for potential ESG columns
            from app.models.csv_data import DEFAULT_CSV_MAPPINGS
            esg_fields = [mapping.csv_column for mapping in DEFAULT_CSV_MAPPINGS]
            
            matched_columns = []
            unmatched_columns = []
            
            for col in df.columns:
                if col.lower() in [field.lower() for field in esg_fields]:
                    matched_columns.append(col)
                else:
                    unmatched_columns.append(col)
            
            return {
                "filename": file.filename,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "column_info": column_info,
                "matched_esg_columns": matched_columns,
                "unmatched_columns": unmatched_columns,
                "suggested_mappings": {
                    col: next(
                        (field for field in esg_fields if field.lower() == col.lower()),
                        None
                    )
                    for col in df.columns
                }
            }
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to validate CSV: {str(e)}"
        )

