"""
CSV processing service for ESG data upload and validation.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import uuid
import os
from datetime import datetime
import json

try:
    from app.models.csv_data import (
        CSVProcessingResult, CSVValidationError, CSVValidationStatus,
        CSVColumnMapping, DEFAULT_CSV_MAPPINGS, CSVTemplate
    )
    from app.services.llm_service import llm_service
    from app.core.config import settings
except Exception:
    from csv_data import (
        CSVProcessingResult, CSVValidationError, CSVValidationStatus,
        CSVColumnMapping, DEFAULT_CSV_MAPPINGS, CSVTemplate
    )
    from llm_service import llm_service
    from config import settings


class CSVProcessingService:
    """Service for processing ESG CSV uploads."""
    
    def __init__(self):
        self.upload_dir = settings.upload_dir
        self.max_file_size = settings.max_file_size
        self.supported_formats = ['.csv', '.xlsx', '.xls']
    
    async def process_csv_file(
        self, 
        file_path: str, 
        use_llm_for_missing: bool = True,
        column_mapping: Optional[Dict[str, str]] = None,
        industry: str = "retail"
    ) -> CSVProcessingResult:
        """
        Process uploaded CSV file with ESG data.
        """
        try:
            # Read the file
            df = self._read_file(file_path)
            
            # Apply column mapping
            if column_mapping:
                df = self._apply_column_mapping(df, column_mapping)
            
            # Validate data
            validation_result = self._validate_data(df)
            
            # Process missing values with LLM if requested
            llm_suggestions = []
            if use_llm_for_missing and validation_result["missing_values"]:
                llm_suggestions = await self._process_missing_values_with_llm(
                    df, validation_result["missing_values"], industry
                )
                
                # Apply LLM suggestions to dataframe
                df = self._apply_llm_suggestions(df, llm_suggestions)
            
            # Convert to processed data format
            processed_data = self._convert_to_esg_format(df)
            
            # Calculate basic statistics
            total_rows = len(df)
            valid_rows = len(df.dropna())
            invalid_rows = total_rows - valid_rows
            
            # Determine status
            if invalid_rows == 0:
                status = CSVValidationStatus.VALID
            elif valid_rows > 0:
                status = CSVValidationStatus.PARTIAL
            else:
                status = CSVValidationStatus.INVALID
            
            return CSVProcessingResult(
                status=status,
                total_rows=total_rows,
                valid_rows=valid_rows,
                invalid_rows=invalid_rows,
                errors=validation_result["errors"],
                warnings=validation_result["warnings"],
                processed_data=processed_data,
                llm_suggestions=llm_suggestions
            )
        
        except Exception as e:
            return CSVProcessingResult(
                status=CSVValidationStatus.INVALID,
                total_rows=0,
                valid_rows=0,
                invalid_rows=0,
                errors=[CSVValidationError(
                    row=0,
                    column="file",
                    value="",
                    error_type="processing_error",
                    message=f"Failed to process file: {str(e)}"
                )],
                warnings=[],
                processed_data=[],
                llm_suggestions=[]
            )
    
    def _read_file(self, file_path: str) -> pd.DataFrame:
        """Read CSV or Excel file into pandas DataFrame."""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.csv':
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    return pd.read_csv(file_path, encoding=encoding)
                except UnicodeDecodeError:
                    continue
            raise ValueError("Could not read CSV file with any supported encoding")
        
        elif file_ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _apply_column_mapping(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
        """Apply custom column mapping to DataFrame."""
        # Rename columns based on mapping
        df_mapped = df.rename(columns=column_mapping)
        
        # Keep only mapped columns that exist in our ESG schema
        esg_columns = [mapping.esg_field for mapping in DEFAULT_CSV_MAPPINGS]
        existing_columns = [col for col in df_mapped.columns if col in esg_columns]
        
        return df_mapped[existing_columns]
    
    def _validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate DataFrame against ESG schema."""
        errors = []
        warnings = []
        missing_values = []
        
        # Create mapping lookup
        mapping_lookup = {mapping.esg_field: mapping for mapping in DEFAULT_CSV_MAPPINGS}
        
        for col in df.columns:
            if col not in mapping_lookup:
                warnings.append(f"Unknown column '{col}' will be ignored")
                continue
            
            mapping = mapping_lookup[col]
            
            for idx, value in df[col].items():
                if pd.isna(value) or value == '':
                    missing_values.append({
                        "row": idx,
                        "column": col,
                        "mapping": mapping
                    })
                    continue
                
                # Validate based on data type
                validation_error = self._validate_value(value, mapping, idx)
                if validation_error:
                    errors.append(validation_error)
        
        return {
            "errors": errors,
            "warnings": warnings,
            "missing_values": missing_values
        }
    
    def _validate_value(self, value: Any, mapping: CSVColumnMapping, row_idx: int) -> Optional[CSVValidationError]:
        """Validate a single value against its mapping rules."""
        try:
            if mapping.data_type == "numeric":
                float_val = float(value)
                if mapping.validation_rules:
                    min_val = mapping.validation_rules.get("min")
                    max_val = mapping.validation_rules.get("max")
                    
                    if min_val is not None and float_val < min_val:
                        return CSVValidationError(
                            row=row_idx,
                            column=mapping.csv_column,
                            value=value,
                            error_type="range_error",
                            message=f"Value {float_val} is below minimum {min_val}",
                            suggested_fix=f"Use value >= {min_val}"
                        )
                    
                    if max_val is not None and float_val > max_val:
                        return CSVValidationError(
                            row=row_idx,
                            column=mapping.csv_column,
                            value=value,
                            error_type="range_error",
                            message=f"Value {float_val} is above maximum {max_val}",
                            suggested_fix=f"Use value <= {max_val}"
                        )
            
            elif mapping.data_type == "percentage":
                float_val = float(value)
                if not 0 <= float_val <= 100:
                    return CSVValidationError(
                        row=row_idx,
                        column=mapping.csv_column,
                        value=value,
                        error_type="range_error",
                        message=f"Percentage value {float_val} must be between 0 and 100",
                        suggested_fix="Use value between 0 and 100"
                    )
            
            elif mapping.data_type == "boolean":
                if str(value).lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                    return CSVValidationError(
                        row=row_idx,
                        column=mapping.csv_column,
                        value=value,
                        error_type="type_error",
                        message=f"Boolean value '{value}' not recognized",
                        suggested_fix="Use true/false, yes/no, or 1/0"
                    )
        
        except (ValueError, TypeError):
            return CSVValidationError(
                row=row_idx,
                column=mapping.csv_column,
                value=value,
                error_type="type_error",
                message=f"Cannot convert '{value}' to {mapping.data_type}",
                suggested_fix=f"Provide valid {mapping.data_type} value"
            )
        
        return None
    
    async def _process_missing_values_with_llm(
        self, 
        df: pd.DataFrame, 
        missing_values: List[Dict], 
        industry: str
    ) -> List[Dict[str, Any]]:
        """Process missing values using LLM suggestions."""
        suggestions = []
        
        # Group missing values by column for batch processing
        missing_by_column = {}
        for missing in missing_values:
            col = missing["column"]
            if col not in missing_by_column:
                missing_by_column[col] = []
            missing_by_column[col].append(missing)
        
        for column, missing_list in missing_by_column.items():
            try:
                mapping = missing_list[0]["mapping"]
                
                # Generate suggestion for this column
                suggestion_result = await llm_service.generate_esg_suggestion(
                    question=f"Default value for {column} in {industry} industry",
                    industry=industry,
                    question_type=mapping.data_type
                )
                
                # Apply suggestion to all missing values in this column
                for missing in missing_list:
                    suggestions.append({
                        "row": missing["row"],
                        "column": column,
                        "suggested_value": suggestion_result.get("suggested_value"),
                        "confidence": suggestion_result.get("confidence", 0.5),
                        "explanation": suggestion_result.get("explanation", "LLM suggestion"),
                        "source": "llm_suggestion"
                    })
            
            except Exception as e:
                # Fallback to default values
                for missing in missing_list:
                    suggestions.append({
                        "row": missing["row"],
                        "column": column,
                        "suggested_value": self._get_fallback_value(mapping),
                        "confidence": 0.3,
                        "explanation": f"Fallback value due to LLM error: {str(e)}",
                        "source": "fallback"
                    })
        
        return suggestions
    
    def _apply_llm_suggestions(self, df: pd.DataFrame, suggestions: List[Dict[str, Any]]) -> pd.DataFrame:
        """Apply LLM suggestions to fill missing values in DataFrame."""
        df_copy = df.copy()
        
        for suggestion in suggestions:
            row = suggestion["row"]
            column = suggestion["column"]
            value = suggestion["suggested_value"]
            
            if column in df_copy.columns:
                df_copy.at[row, column] = value
        
        return df_copy
    
    def _get_fallback_value(self, mapping: CSVColumnMapping) -> Any:
        """Get fallback value for a mapping."""
        if mapping.data_type == "numeric":
            return 0
        elif mapping.data_type == "percentage":
            return 50.0
        elif mapping.data_type == "boolean":
            return False
        else:
            return "Not specified"
    
    def _convert_to_esg_format(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert DataFrame to ESG format for API response."""
        processed_data = []
        
        for idx, row in df.iterrows():
            row_data = {"row_index": idx}
            
            for col, value in row.items():
                if not pd.isna(value):
                    # Convert pandas types to Python types
                    if isinstance(value, (np.integer, np.floating)):
                        value = value.item()
                    elif isinstance(value, np.bool_):
                        value = bool(value)
                    
                    row_data[col] = value
            
            processed_data.append(row_data)
        
        return processed_data
    
    def generate_csv_template(self) -> CSVTemplate:
        """Generate CSV template for download."""
        headers = [mapping.csv_column for mapping in DEFAULT_CSV_MAPPINGS]
        
        # Create sample data
        sample_data = [
            {
                "energy_consumption": 45000,
                "co2_emissions": 8.5,
                "water_usage": 12000,
                "waste_generated": 2500,
                "recycling_rate": 65,
                "renewable_energy_percentage": 25,
                "packaging_recyclability": 70,
                "employee_count": 25,
                "diversity_percentage": 40,
                "female_leadership_percentage": 35,
                "training_hours_per_employee": 20,
                "employee_satisfaction_score": 7.8,
                "community_investment": 5000,
                "board_independence": 60,
                "ethics_training_completion": 90,
                "data_privacy_compliance": True,
                "supplier_code_of_conduct": False,
                "transparency_reporting": False
            }
        ]
        
        return CSVTemplate(
            filename="esg_data_template.csv",
            headers=headers,
            sample_data=sample_data,
            description="ESG data template for retail SMBs",
            mappings=DEFAULT_CSV_MAPPINGS
        )
    
    def save_processed_data(self, data: List[Dict[str, Any]], filename: str) -> str:
        """Save processed data to file and return file path."""
        output_path = os.path.join(self.upload_dir, f"processed_{filename}")
        
        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        
        return output_path


# Global CSV service instance
csv_service = CSVProcessingService()

