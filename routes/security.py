"""
Security and Threat Detection API routes
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime

from models.schemas import (
    ThreatDetectionRequest,
    ThreatDetectionResponse,
    RiskLevel
)
from services.ai_service import AIService
from services.security_service import SecurityService

router = APIRouter()
ai_service = AIService()
security_service = SecurityService()

@router.post("/detect-threat", response_model=ThreatDetectionResponse)
async def detect_threat(request: ThreatDetectionRequest):
    """
    Analyze transaction for potential threats before execution
    
    Detects:
    - Phishing attempts
    - Malicious contracts
    - Suspicious transaction patterns
    - Known scam addresses
    - Unusual permission requests
    """
    try:
        # Analyze transaction data
        threat_analysis = await security_service.analyze_transaction(
            request.transaction_data,
            request.wallet_address
        )
        
        # Get AI-powered analysis
        ai_analysis = await ai_service.analyze_transaction_security(
            request.transaction_data,
            threat_analysis
        )
        
        # Calculate risk score
        risk_score = threat_analysis.get("risk_score", 0)
        
        # Determine if transaction should proceed
        should_proceed = risk_score < 0.5 and not threat_analysis.get("critical_threats")
        
        return ThreatDetectionResponse(
            is_safe=should_proceed,
            risk_score=risk_score,
            risk_level=get_risk_level(risk_score),
            threats_detected=threat_analysis.get("threats", []),
            analysis=ai_analysis,
            should_proceed=should_proceed,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Threat detection failed: {str(e)}")

@router.get("/scam-database")
async def get_scam_database():
    """Get list of known scam addresses and patterns"""
    try:
        scam_data = await security_service.get_scam_database()
        return {
            "scam_addresses": scam_data.get("addresses", []),
            "scam_patterns": scam_data.get("patterns", []),
            "last_updated": scam_data.get("last_updated"),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch scam database: {str(e)}")

@router.post("/report-scam")
async def report_scam(address: str, description: str, reporter_wallet: str):
    """Report a suspected scam address"""
    try:
        result = await security_service.report_scam(address, description, reporter_wallet)
        return {
            "success": True,
            "message": "Scam report submitted successfully",
            "report_id": result.get("report_id"),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit report: {str(e)}")

def get_risk_level(risk_score: float) -> RiskLevel:
    """Convert risk score to risk level"""
    if risk_score < 0.25:
        return RiskLevel.LOW
    elif risk_score < 0.5:
        return RiskLevel.MEDIUM
    elif risk_score < 0.75:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL
