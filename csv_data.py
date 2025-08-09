"""
CSV data models for ESG data upload and processing.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class CSVValidationStatus(str, Enum):
    """CSV validation status."""
    VALID = "valid"
    INVALID = "invalid"
    PARTIAL = "partial"
    PROCESSED = "processed"


class CSVColumnMapping(BaseModel):
    """CSV column mapping configuration."""
    csv_column: str
    esg_field: str
    data_type: str  # numeric, percentage, boolean, text
    required: bool = False
    validation_rules: Optional[Dict[str, Any]] = None


class CSVValidationError(BaseModel):
    """CSV validation error model."""
    row: int
    column: str
    value: Any
    error_type: str
    message: str
    suggested_fix: Optional[str] = None


class CSVProcessingResult(BaseModel):
    """CSV processing result model."""
    status: CSVValidationStatus
    total_rows: int
    valid_rows: int
    invalid_rows: int
    errors: List[CSVValidationError]
    warnings: List[str]
    processed_data: List[Dict[str, Any]]
    llm_suggestions: List[Dict[str, Any]]
    esg_score: Optional[float] = None


class CSVUploadRequest(BaseModel):
    """CSV upload request model."""
    use_llm_for_missing: bool = True
    column_mapping: Optional[Dict[str, str]] = None
    industry: str = "retail"
    company_name: Optional[str] = None


class CSVUploadResponse(BaseModel):
    """CSV upload response model."""
    upload_id: str
    filename: str
    processing_result: CSVProcessingResult
    download_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Default CSV column mappings for ESG data
DEFAULT_CSV_MAPPINGS = [
    CSVColumnMapping(
        csv_column="energy_consumption",
        esg_field="annual_energy_consumption",
        data_type="numeric",
        required=False,
        validation_rules={"min": 0, "max": 1000000}
    ),
    CSVColumnMapping(
        csv_column="co2_emissions",
        esg_field="co2_emissions",
        data_type="numeric",
        required=False,
        validation_rules={"min": 0, "max": 10000}
    ),
    CSVColumnMapping(
        csv_column="water_usage",
        esg_field="water_usage",
        data_type="numeric",
        required=False,
        validation_rules={"min": 0}
    ),
    CSVColumnMapping(
        csv_column="waste_generated",
        esg_field="waste_generated",
        data_type="numeric",
        required=False,
        validation_rules={"min": 0}
    ),
    CSVColumnMapping(
        csv_column="recycling_rate",
        esg_field="recycling_rate",
        data_type="percentage",
        required=False,
        validation_rules={"min": 0, "max": 100}
    ),
    CSVColumnMapping(
        csv_column="renewable_energy_percentage",
        esg_field="renewable_energy_percentage",
        data_type="percentage",
        required=False,
        validation_rules={"min": 0, "max": 100}
    ),
    CSVColumnMapping(
        csv_column="packaging_recyclability",
        esg_field="packaging_recyclability",
        data_type="percentage",
        required=False,
        validation_rules={"min": 0, "max": 100}
    ),
    CSVColumnMapping(
        csv_column="employee_count",
        esg_field="employee_count",
        data_type="numeric",
        required=False,
        validation_rules={"min": 1, "max": 10000}
    ),
    CSVColumnMapping(
        csv_column="diversity_percentage",
        esg_field="diversity_percentage",
        data_type="percentage",
        required=False,
        validation_rules={"min": 0, "max": 100}
    ),
    CSVColumnMapping(
        csv_column="female_leadership_percentage",
        esg_field="female_leadership_percentage",
        data_type="percentage",
        required=False,
        validation_rules={"min": 0, "max": 100}
    ),
    CSVColumnMapping(
        csv_column="training_hours_per_employee",
        esg_field="training_hours_per_employee",
        data_type="numeric",
        required=False,
        validation_rules={"min": 0, "max": 200}
    ),
    CSVColumnMapping(
        csv_column="employee_satisfaction_score",
        esg_field="employee_satisfaction_score",
        data_type="numeric",
        required=False,
        validation_rules={"min": 0, "max": 10}
    ),
    CSVColumnMapping(
        csv_column="community_investment",
        esg_field="community_investment",
        data_type="numeric",
        required=False,
        validation_rules={"min": 0}
    ),
    CSVColumnMapping(
        csv_column="board_independence",
        esg_field="board_independence",
        data_type="percentage",
        required=False,
        validation_rules={"min": 0, "max": 100}
    ),
    CSVColumnMapping(
        csv_column="ethics_training_completion",
        esg_field="ethics_training_completion",
        data_type="percentage",
        required=False,
        validation_rules={"min": 0, "max": 100}
    ),
    CSVColumnMapping(
        csv_column="data_privacy_compliance",
        esg_field="data_privacy_compliance",
        data_type="boolean",
        required=False
    ),
    CSVColumnMapping(
        csv_column="supplier_code_of_conduct",
        esg_field="supplier_code_of_conduct",
        data_type="boolean",
        required=False
    ),
    CSVColumnMapping(
        csv_column="transparency_reporting",
        esg_field="transparency_reporting",
        data_type="boolean",
        required=False
    )
]


class CSVTemplate(BaseModel):
    """CSV template model for download."""
    filename: str
    headers: List[str]
    sample_data: List[Dict[str, Any]]
    description: str
    mappings: List[CSVColumnMapping]

