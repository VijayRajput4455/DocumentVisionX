"""
Pydantic models for API request/response validation.
Provides automatic validation, type hints, and OpenAPI documentation.
"""

from typing import Literal, Optional, Dict
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ============================================================================
# Common Request / Response Models
# ============================================================================

class ImageMetadata(BaseModel):
    """Image metadata returned after extraction."""
    image_id: str = Field(..., description="Unique image identifier (UUID)")
    image_url: str = Field(..., description="HTTP URL to retrieve the saved image")


class ErrorResponse(BaseModel):
    """Standard error response format."""
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")


# ============================================================================
# AADHAAR Models
# ============================================================================

class AadhaarExtractionRequest(BaseModel):
    """Request model for Aadhaar extraction endpoint."""
    document_type: Literal["aadhar"] = Field(
        ..., 
        description="Must be 'aadhar' for this endpoint"
    )
    image_url: Optional[str] = Field(
        None, 
        description="URL to download image from (alternative to file upload)"
    )

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, v):
        if v.lower() != "aadhar":
            raise ValueError("Expected 'aadhar' for this endpoint")
        return v.lower()


class AadhaarExtractionData(BaseModel):
    """Extracted Aadhaar data fields."""
    model_config = ConfigDict(populate_by_name=True)
    
    user_name: str = Field(..., alias="USER_NAME", description="Cardholder's full name")
    aadhar_number: str = Field(
        ..., 
        alias="AADHAR_NUMBER",
        description="12-digit Aadhaar number",
        pattern=r"^\d{12}$|^NA$"
    )
    father_name: str = Field(..., alias="FATHER_NAME", description="Father's or spouse's name")
    date_of_birth: str = Field(
        ..., 
        alias="DATE_OF_BIRTH",
        description="Date of birth in DD/MM/YYYY format",
        pattern=r"^\d{1,2}/\d{1,2}/\d{4}$|^NA$"
    )
    year_of_birth: str = Field(..., alias="YEAR_OF_BIRTH", description="Year extracted from DOB")
    gender: Literal["MALE", "FEMALE", "OTHER", "NA"] = Field(
        ..., 
        alias="GENDER",
        description="Gender as per Aadhaar"
    )
    mobile_number: str = Field(
        ..., 
        alias="MOBILE_NUMBER",
        description="10-digit mobile number",
        pattern=r"^\d{10}$|^NA$"
    )
    address: str = Field(..., alias="ADDRESS", description="Residential address")


class AadhaarExtractionResponse(BaseModel):
    """Response model for successful Aadhaar extraction."""
    document_type: Literal["aadhar"]
    image: ImageMetadata
    data: AadhaarExtractionData


# ============================================================================
# PAN Models
# ============================================================================

class PANExtractionRequest(BaseModel):
    """Request model for PAN extraction endpoint."""
    document_type: Literal["pancard"] = Field(
        ..., 
        description="Must be 'pancard' for this endpoint"
    )
    image_url: Optional[str] = Field(
        None, 
        description="URL to download image from (alternative to file upload)"
    )

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, v):
        if v.lower() != "pancard":
            raise ValueError("Expected 'pancard' for this endpoint")
        return v.lower()


class PANExtractionData(BaseModel):
    """Extracted PAN data fields."""
    model_config = ConfigDict(populate_by_name=True)
    
    pan_number: str = Field(
        ..., 
        alias="PAN_NUMBER",
        description="10-character PAN number",
        pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]$|^NA$"
    )
    name: str = Field(..., alias="NAME", description="Name as per PAN")
    father_name: str = Field(..., alias="FATHER_NAME", description="Father's name as per PAN")
    date_of_birth: str = Field(
        ..., 
        alias="DATE_OF_BIRTH",
        description="Date of birth if available",
        pattern=r"^\d{1,2}/\d{1,2}/\d{4}$|^NA$"
    )


class PANExtractionResponse(BaseModel):
    """Response model for successful PAN extraction."""
    document_type: Literal["pancard"]
    image: ImageMetadata
    data: PANExtractionData


# ============================================================================
# VOTER ID Models
# ============================================================================

class VoterExtractionRequest(BaseModel):
    """Request model for Voter ID extraction endpoint."""
    document_type: Literal["voter"] = Field(
        ..., 
        description="Must be 'voter' for this endpoint"
    )
    image_url: Optional[str] = Field(
        None, 
        description="URL to download image from (alternative to file upload)"
    )

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, v):
        if v.lower() != "voter":
            raise ValueError("Expected 'voter' for this endpoint")
        return v.lower()


class VoterExtractionData(BaseModel):
    """Extracted Voter ID data fields."""
    model_config = ConfigDict(populate_by_name=True)
    
    name: str = Field(..., alias="NAME", description="Voter's full name")
    voter_id: str = Field(
        ..., 
        alias="EPIC_NUMBER",
        description="Voter ID number (EPIC)",
        min_length=5
    )
    relative_name: str = Field(..., alias="RELATIVE_NAME", description="Relative's name")
    father_name: str = Field(..., alias="FATHER_NAME", description="Father's name")
    date_of_birth: str = Field(
        ..., 
        alias="DATE_OF_BIRTH",
        description="Date of birth",
        pattern=r"^\d{1,2}/\d{1,2}/\d{4}$|^NA$"
    )
    age: str = Field(..., alias="AGE", description="Age of voter")
    gender: Literal["MALE", "FEMALE", "OTHER", "NA"] = Field(..., alias="GENDER")
    address: str = Field(..., alias="ADDRESS", description="Address")


class VoterExtractionResponse(BaseModel):
    """Response model for successful Voter ID extraction."""
    document_type: Literal["voter"]
    image: ImageMetadata
    data: VoterExtractionData


# ============================================================================
# BANK Models
# ============================================================================

class BankExtractionRequest(BaseModel):
    """Request model for Bank document extraction endpoint."""
    document_type: Literal["bank"] = Field(
        ..., 
        description="Must be 'bank' for this endpoint"
    )
    image_url: Optional[str] = Field(
        None, 
        description="URL to download image from (alternative to file upload)"
    )

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, v):
        if v.lower() != "bank":
            raise ValueError("Expected 'bank' for this endpoint")
        return v.lower()


class BankExtractionData(BaseModel):
    """Extracted Bank document data fields."""
    model_config = ConfigDict(populate_by_name=True)
    
    document_subtype: str = Field(
        ..., 
        description="Bank statement, passbook, cheque, etc.",
        examples=["statement", "passbook", "cheque"]
    )
    account_holder_name: str = Field(..., description="Account holder's name")
    account_number: str = Field(
        ..., 
        description="Bank account number",
        min_length=5
    )
    ifsc: str = Field(
        ..., 
        description="IFSC code (11 characters)",
        pattern=r"^[A-Z]{4}0[A-Z0-9]{6}$|^NA$"
    )
    bank_name: str = Field(..., description="Name of the bank")


class BankExtractionResponse(BaseModel):
    """Response model for successful Bank extraction."""
    document_type: Literal["bank"]
    image: ImageMetadata
    data: BankExtractionData


# ============================================================================
# Health Check Models
# ============================================================================

class SemaphoreStatsModel(BaseModel):
    """Stats for a single semaphore (OCR or LLM)."""
    name: str
    limit: int
    in_use: int
    available: int
    utilization: float = Field(..., ge=0.0, le=1.0)


class RateLimitStatsModel(BaseModel):
    """Rate limiting statistics."""
    requests_per_minute: int
    window_seconds: int
    active_keys: int
    requests_in_window: int


class ScalabilityStatsModel(BaseModel):
    """Overall scalability metrics."""
    ocr: SemaphoreStatsModel
    llm: SemaphoreStatsModel
    rate_limit: RateLimitStatsModel


class HealthResponse(BaseModel):
    """Response model for /health endpoint."""
    status: str = Field(..., pattern="^ok$|^error$")
    service: str = Field(default="DocumentVisionX")
    scalability: ScalabilityStatsModel


class ReadyResponse(BaseModel):
    """Response model for /ready endpoint."""
    ready: bool
    reason: Literal["capacity_available", "capacity_saturated"]
    scalability: ScalabilityStatsModel


class OperationMetricsModel(BaseModel):
    """Metrics for a single operation."""
    operation: str
    count: int
    avg_ms: float
    min_ms: float
    max_ms: float
    p50_ms: float
    p95_ms: float


class MetricsResponse(BaseModel):
    """Response model for /metrics endpoint."""
    metrics: Dict[str, OperationMetricsModel] = Field(
        ...,
        description="Performance metrics by operation (OCR, LLM, extraction, etc.)"
    )
    timestamp: str = Field(..., description="Metrics snapshot timestamp")
