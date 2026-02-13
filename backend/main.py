"""
HealthMate FastAPI Backend - Updated Version
Using Grok AI + Gemini API for Analysis
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json
import uuid

from triage_engine import TriageEngine, PatientProfile
from rag_system import RAGSystem
from risk_scorer import RiskScorer
from llm_integration import TriageAnalysisPipeline
from triage_based_model import TriageBasedAssessment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="HealthMate Advanced - Grok + Gemini",
    description="AI-powered emergency triage with Grok analysis & Gemini reports",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
triage_engine = TriageEngine()
rag_system = RAGSystem()
risk_scorer = RiskScorer()

# Session store
sessions: Dict[str, Dict] = {}


# ============================================================================
# Pydantic Models
# ============================================================================

class ConversationRequest(BaseModel):
    """User message"""
    session_id: str
    user_message: str


class ConversationResponse(BaseModel):
    """Assistant response"""
    session_id: str
    assistant_message: str
    should_continue: bool
    is_emergency: bool


class AdvancedAnalysisResponse(BaseModel):
    """Advanced analysis from Grok + Gemini"""
    session_id: str
    grok_analysis: str
    final_report: str
    urgency_level: str
    model_used: str


class DiagnosticQuestionResponse(BaseModel):
    """Next diagnostic question"""
    session_id: str
    question: str
    question_number: int
    symptom: str


# ============================================================================
# Routes
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "HealthMate Advanced",
        "version": "2.0.0",
        "features": ["Grok Analysis", "Gemini Reports", "Triage-Based Diagnostics"]
    }


@app.post("/api/session/start")
async def start_session():
    """Start new session"""
    session_id = str(uuid.uuid4())
    
    triage_engine.reset()
    
    sessions[session_id] = {
        "created_at": datetime.now().isoformat(),
        "messages": [],
        "completed": False,
        "risk_assessment": None,
        "diagnostic_answers": [],
        "current_symptom": None,
    }
    
    greeting = triage_engine.get_initial_greeting()
    
    logger.info(f"Session started: {session_id}")
    
    return {
        "session_id": session_id,
        "greeting": greeting,
    }


@app.post("/api/conversation", response_model=ConversationResponse)
async def process_conversation(request: ConversationRequest):
    """Process user input"""
    
    session_id = request.session_id
    user_message = request.user_message
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Process through triage engine
    response = triage_engine.process_user_input(user_message)
    
    is_emergency = response.get("emergency_detected", False)
    
    sessions[session_id]["messages"].append(("user", user_message))
    sessions[session_id]["messages"].append(("assistant", response["message"]))
    
    # If triage complete
    should_continue = response.get("should_continue", True)
    if not should_continue and not is_emergency:
        patient_profile = triage_engine.get_patient_profile()
        risk_score_obj = risk_scorer.calculate_risk(patient_profile)
        
        sessions[session_id]["completed"] = True
        sessions[session_id]["risk_assessment"] = risk_score_obj
        sessions[session_id]["current_symptom"] = patient_profile.primary_symptom
        
        logger.info(f"Triage complete: {session_id}")
    
    return ConversationResponse(
        session_id=session_id,
        assistant_message=response["message"],
        should_continue=should_continue,
        is_emergency=is_emergency
    )


@app.post("/api/advanced-analysis/{session_id}", response_model=AdvancedAnalysisResponse)
async def advanced_analysis(session_id: str):
    """
    NEW: Use Grok AI + Gemini for advanced analysis
    """
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not sessions[session_id].get("completed"):
        raise HTTPException(status_code=400, detail="Triage not yet complete")
    
    patient_profile = triage_engine.get_patient_profile()
    risk_score_obj = sessions[session_id]["risk_assessment"]
    
    logger.info(f"Starting advanced analysis: {session_id}")
    
    # Run Grok + Gemini pipeline
    result = TriageAnalysisPipeline.process_patient(
        patient_profile=patient_profile.to_dict(),
        urgency_level=risk_score_obj.urgency_level.value[0]
    )
    
    if not result["success"]:
        logger.error(f"Analysis failed: {result['error']}")
        raise HTTPException(status_code=500, detail=result["error"])
    
    sessions[session_id]["analysis_result"] = result
    
    return AdvancedAnalysisResponse(
        session_id=session_id,
        grok_analysis=result["grok_analysis"],
        final_report=result["final_report"],
        urgency_level=result["urgency_level"],
        model_used="Grok + Gemini"
    )


@app.post("/api/diagnostic-question/{session_id}", response_model=DiagnosticQuestionResponse)
async def get_diagnostic_question(session_id: str):
    """
    NEW: Get next diagnostic question (triage-based)
    """
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    symptom = sessions[session_id].get("current_symptom", "")
    answers = sessions[session_id].get("diagnostic_answers", [])
    
    if not symptom:
        raise HTTPException(status_code=400, detail="No symptom found")
    
    # Get next question
    next_question = TriageBasedAssessment.get_next_diagnostic_question(symptom, answers)
    
    if not next_question:
        # All questions answered - provide assessment
        assessment = TriageBasedAssessment.assess_pattern(symptom, answers)
        sessions[session_id]["diagnostic_assessment"] = assessment
        
        return DiagnosticQuestionResponse(
            session_id=session_id,
            question="[Assessment Complete]",
            question_number=len(answers) + 1,
            symptom=symptom
        )
    
    return DiagnosticQuestionResponse(
        session_id=session_id,
        question=next_question,
        question_number=len(answers) + 1,
        symptom=symptom
    )


@app.post("/api/diagnostic-answer/{session_id}")
async def submit_diagnostic_answer(session_id: str, answer: Dict):
    """
    Submit answer to diagnostic question
    """
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions[session_id]["diagnostic_answers"].append(answer["answer"])
    
    return {
        "success": True,
        "answers_count": len(sessions[session_id]["diagnostic_answers"])
    }


@app.get("/api/triage-result/{session_id}")
async def get_triage_result(session_id: str):
    """Get triage assessment"""
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not sessions[session_id].get("completed"):
        raise HTTPException(status_code=400, detail="Triage not complete")
    
    patient_profile = triage_engine.get_patient_profile()
    risk_score_obj = sessions[session_id]["risk_assessment"]
    
    rag_response = rag_system.generate_grounded_response(
        patient_profile.primary_symptom or ""
    )
    
    return {
        "session_id": session_id,
        "patient_profile": patient_profile.to_dict(),
        "risk_score": risk_score_obj.overall_score,
        "urgency_level": risk_score_obj.urgency_level.value[0],
        "urgency_icon": risk_score_obj.urgency_level.value[2],
        "reasoning": risk_score_obj.reasoning,
        "recommendations": risk_score_obj.recommendations,
        "relevant_guidance": rag_response["guidance"],
    }


@app.get("/api/analysis-report/{session_id}")
async def get_analysis_report(session_id: str):
    """Get Grok + Gemini analysis report"""
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if "analysis_result" not in sessions[session_id]:
        raise HTTPException(status_code=400, detail="Analysis not available")
    
    result = sessions[session_id]["analysis_result"]
    
    return {
        "session_id": session_id,
        "grok_analysis": result["grok_analysis"],
        "final_report": result["final_report"],
        "urgency_level": result["urgency_level"],
        "timestamp": sessions[session_id]["created_at"]
    }


@app.get("/api/diagnostic-assessment/{session_id}")
async def get_diagnostic_assessment(session_id: str):
    """Get diagnostic assessment (triage-based)"""
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if "diagnostic_assessment" not in sessions[session_id]:
        raise HTTPException(status_code=400, detail="Assessment not available")
    
    assessment = sessions[session_id]["diagnostic_assessment"]
    answers = sessions[session_id]["diagnostic_answers"]
    
    return {
        "session_id": session_id,
        "symptom": sessions[session_id].get("current_symptom"),
        "answers": answers,
        "assessment": assessment
    }


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete session"""
    
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session deleted"}
    
    raise HTTPException(status_code=404, detail="Session not found")


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": "Internal server error",
        "status_code": 500
    }


# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("HealthMate Advanced Backend starting...")
    logger.info("Features: Grok AI, Gemini Reports, Triage-Based Diagnostics")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("HealthMate Advanced Backend shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
