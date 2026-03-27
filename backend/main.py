"""
Advanced analysis using OpenRouter LLM
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json
import uuid

from ml_service import MLService  # ✅ ADDED
from triage_engine import TriageEngine, PatientProfile
from rag_system import RAGSystem
from risk_scorer import RiskScorer
from llm_integration import TriageAnalysisPipeline
from triage_based_model import TriageBasedAssessment
from dotenv import load_dotenv
import os

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="HealthMate Advanced - OpenRouter LLM",
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

# ✅ LOAD ML MODEL GLOBALLY
ml_service = MLService()

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
    session_id: str
    analysis: str
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
        "features": ["OpenRouter LLM", "Triage-Based Diagnostics"]
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
        "ml_predictions": []  # ✅ ADDED
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

        # =========================================
        # 🧠 ML PREDICTION STEP (ADDED)
        # =========================================
        user_summary = json.dumps(patient_profile.to_dict(), ensure_ascii=False)
        predictions = ml_service.predict(user_summary)
        sessions[session_id]["ml_predictions"] = predictions

        logger.info(f"ML Predictions: {predictions}")
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
    ml_predictions = sessions[session_id].get("ml_predictions", [])  # ✅ ADDED
    
    logger.info(f"Starting advanced analysis: {session_id}")
    
    # Run Grok + Gemini pipeline
    result = TriageAnalysisPipeline.process_patient(
        patient_profile=patient_profile.to_dict(),
        urgency_level=risk_score_obj.urgency_level.value[0],
        ml_predictions=ml_predictions  # ✅ ADDED
    )
    
    if not result["success"]:
        logger.error(f"Analysis failed: {result['error']}")
        raise HTTPException(status_code=500, detail=result["error"])
    
    sessions[session_id]["analysis_result"] = result
    
    return AdvancedAnalysisResponse(
        session_id=session_id,
        analysis=result["analysis"],
        final_report=result["final_report"],
        urgency_level=result["urgency_level"],
        model_used="OpenRouter Llama 3.3"
    )


@app.get("/api/triage-result/{session_id}")
async def get_triage_result(session_id: str):
    """Get triage assessment"""
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not sessions[session_id].get("completed"):
        raise HTTPException(status_code=400, detail="Triage not complete")
    
    patient_profile = triage_engine.get_patient_profile()
    risk_score_obj = sessions[session_id]["risk_assessment"]
    ml_predictions = sessions[session_id].get("ml_predictions", [])  # ✅ ADDED
    
    # =========================================
    # 🧠 RAG QUERY (FINAL)
    # =========================================
    rag_query = f"{patient_profile.primary_symptom} {ml_predictions}"

    rag_response = rag_system.generate_grounded_response(rag_query)
    
    
    return {
        "session_id": session_id,
        "patient_profile": patient_profile.to_dict(),
        "risk_score": risk_score_obj.overall_score,
        "urgency_level": risk_score_obj.urgency_level.value[0],
        "urgency_icon": risk_score_obj.urgency_level.value[2],
        "reasoning": risk_score_obj.reasoning,
        "recommendations": risk_score_obj.recommendations,
        "relevant_guidance": rag_response["guidance"],
        "ml_predictions": ml_predictions  # ✅ ADDED
    }