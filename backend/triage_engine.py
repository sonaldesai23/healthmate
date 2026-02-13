"""
HealthMate Triage Engine
Module 1: Conversational Triage Engine
Handles structured doctor-style questioning with dynamic follow-up logic
Inspired by Health-LLM paper's structured interaction model
"""

import logging
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class UrgencyLevel(Enum):
    """Urgency classification levels"""
    GREEN = "mild"
    YELLOW = "moderate"
    RED = "emergency"


@dataclass
class PatientProfile:
    """Patient information collected during triage"""
    age: Optional[int] = None
    gender: Optional[str] = None
    primary_symptom: Optional[str] = None
    duration: Optional[str] = None
    severity_score: float = 0.0
    medical_history: Dict[str, bool] = None
    current_medications: List[str] = None
    recent_meals: Optional[str] = None
    allergies: List[str] = None
    additional_symptoms: List[str] = None
    
    def __post_init__(self):
        if self.medical_history is None:
            self.medical_history = {
                "diabetes": False,
                "hypertension": False,
                "asthma": False,
                "heart_disease": False,
                "stroke_history": False,
                "kidney_disease": False,
            }
        if self.current_medications is None:
            self.current_medications = []
        if self.allergies is None:
            self.allergies = []
        if self.additional_symptoms is None:
            self.additional_symptoms = []

    def to_dict(self) -> Dict:
        """Convert to dictionary for logging and storage"""
        return {
            "age": self.age,
            "gender": self.gender,
            "primary_symptom": self.primary_symptom,
            "duration": self.duration,
            "severity_score": self.severity_score,
            "medical_history": self.medical_history,
            "current_medications": self.current_medications,
            "recent_meals": self.recent_meals,
            "allergies": self.allergies,
            "additional_symptoms": self.additional_symptoms,
        }


class TriageEngine:
    """
    Structured triage conversation engine
    Mimics doctor's step-by-step questioning pattern
    """
    
    EMERGENCY_TRIGGERS = {
        "chest_pain": [
            "chest pain", "chest tightness", "chest pressure",
            "radiating pain", "shoulder pain with chest",
        ],
        "breathing": [
            "difficulty breathing", "shortness of breath", "gasping",
            "severe breathing", "choking",
        ],
        "consciousness": [
            "unconscious", "fainted", "collapsed", "passed out",
            "unresponsive", "dizzy with vision loss",
        ],
        "seizure": [
            "seizure", "convulsion", "shaking", "losing consciousness and shaking",
        ],
        "bleeding": [
            "heavy bleeding", "severe bleeding", "uncontrolled bleeding",
            "bleeding from", "gushing blood",
        ],
        "stroke": [
            "facial drooping", "arm weakness", "speech difficulty",
            "sudden numbness", "loss of balance",
        ],
        "severe_trauma": [
            "severe burn", "deep cut", "impalement", "severe crush",
            "loss of consciousness from injury",
        ],
    }
    
    SEVERITY_WEIGHTS = {
        "symptom_severity": 0.4,
        "chronic_disease": 0.3,
        "symptom_count": 0.15,
        "duration": 0.15,
    }
    
    CONVERSATION_FLOW = [
        {
            "stage": "greeting",
            "assistant_message": "Hello. I'm HealthMate, your emergency first-aid assistant. I'm here to help you assess your condition. Please know that I'm not a replacement for a doctor. Let me ask you a few quick questions to understand what's happening.",
            "required_info": [],
        },
        {
            "stage": "basic_info",
            "assistant_message": "First, could you please tell me your age and gender?",
            "required_info": ["age", "gender"],
        },
        {
            "stage": "primary_symptom",
            "assistant_message": "What's your main concern or symptom right now?",
            "required_info": ["primary_symptom"],
        },
        {
            "stage": "symptom_duration",
            "assistant_message": "How long have you been experiencing this symptom?",
            "required_info": ["duration"],
        },
        {
            "stage": "severity_assessment",
            "assistant_message": "On a scale of 1 to 10, how severe would you rate your pain or discomfort? 1 being very mild, 10 being the worst possible.",
            "required_info": ["severity_score"],
        },
        {
            "stage": "medical_history",
            "assistant_message": "Do you have any chronic conditions? For example: diabetes, high blood pressure, asthma, or heart disease?",
            "required_info": ["medical_history"],
        },
        {
            "stage": "medications",
            "assistant_message": "Are you currently taking any medications? If yes, please list them.",
            "required_info": ["current_medications"],
        },
        {
            "stage": "allergies",
            "assistant_message": "Do you have any known allergies to medications?",
            "required_info": ["allergies"],
        },
        {
            "stage": "additional_symptoms",
            "assistant_message": "Besides your main symptom, are you experiencing any other symptoms? Such as fever, nausea, dizziness, etc.?",
            "required_info": ["additional_symptoms"],
        },
    ]
    
    def __init__(self):
        self.patient_profile = PatientProfile()
        self.current_stage = 0
        self.conversation_history: List[Tuple[str, str]] = []
        self.emergency_detected = False
        self.triage_complete = False
        
    def get_initial_greeting(self) -> str:
        """Return initial greeting message"""
        return self.CONVERSATION_FLOW[0]["assistant_message"]
    
    def get_next_question(self) -> str:
        """Get next question in conversation flow"""
        if self.current_stage < len(self.CONVERSATION_FLOW):
            message = self.CONVERSATION_FLOW[self.current_stage]["assistant_message"]
            self.current_stage += 1
            return message
        return "Thank you for providing all the information. Let me analyze your situation..."
    
    def process_user_input(self, user_input: str) -> Dict:
        """
        Process user input and extract information
        Returns structured response with extracted data and next question
        """
        self.conversation_history.append(("user", user_input))
        
        # Check for emergency triggers
        if self._check_emergency_triggers(user_input):
            self.emergency_detected = True
            return {
                "emergency_detected": True,
                "message": "EMERGENCY DETECTED - Please call 911 immediately!",
                "should_continue": False,
            }
        
        # Extract information based on current stage
        current_flow = self.CONVERSATION_FLOW[self.current_stage - 1] if self.current_stage > 0 else None
        
        if current_flow:
            self._extract_information(user_input, current_flow["required_info"])
        
        # Get next question
        if self.current_stage < len(self.CONVERSATION_FLOW):
            next_question = self.get_next_question()
            self.conversation_history.append(("assistant", next_question))
            return {
                "emergency_detected": False,
                "message": next_question,
                "should_continue": True,
            }
        else:
            self.triage_complete = True
            return {
                "emergency_detected": False,
                "message": "Thank you for providing all information. Let me analyze your condition now...",
                "should_continue": False,
            }
    
    def _check_emergency_triggers(self, text: str) -> bool:
        """Check if text contains emergency trigger keywords"""
        text_lower = text.lower()
        
        for category, triggers in self.EMERGENCY_TRIGGERS.items():
            for trigger in triggers:
                if trigger in text_lower:
                    logger.warning(f"Emergency trigger detected: {trigger}")
                    return True
        
        return False
    
    def _extract_information(self, user_input: str, required_fields: List[str]) -> None:
        """Extract relevant information from user input"""
        text = user_input.lower().strip()
        
        for field in required_fields:
            if field == "age":
                # Simple age extraction
                import re
                age_match = re.search(r'\b(\d{1,3})\b', user_input)
                if age_match:
                    self.patient_profile.age = int(age_match.group(1))
            
            elif field == "gender":
                if "male" in text or "man" in text or "boy" in text or "m" in text.split():
                    self.patient_profile.gender = "Male"
                elif "female" in text or "woman" in text or "girl" in text or "f" in text.split():
                    self.patient_profile.gender = "Female"
                else:
                    self.patient_profile.gender = "Not specified"
            
            elif field == "primary_symptom":
                self.patient_profile.primary_symptom = user_input
            
            elif field == "duration":
                self.patient_profile.duration = user_input
            
            elif field == "severity_score":
                import re
                score_match = re.search(r'(\d+)', user_input)
                if score_match:
                    score = int(score_match.group(1))
                    self.patient_profile.severity_score = min(10, max(0, score))
            
            elif field == "medical_history":
                conditions = {
                    "diabetes": "diabetes" in text,
                    "hypertension": ("high blood pressure" in text or "hypertension" in text or "bp" in text),
                    "asthma": "asthma" in text,
                    "heart_disease": ("heart" in text or "cardiac" in text),
                    "stroke_history": ("stroke" in text or "tia" in text),
                    "kidney_disease": "kidney" in text,
                }
                self.patient_profile.medical_history.update(conditions)
            
            elif field == "current_medications":
                if "no" not in text and "none" not in text:
                    self.patient_profile.current_medications = [m.strip() for m in user_input.split(",")]
            
            elif field == "allergies":
                if "no" not in text and "none" not in text:
                    self.patient_profile.allergies = [a.strip() for a in user_input.split(",")]
            
            elif field == "additional_symptoms":
                if "no" not in text and "none" not in text:
                    self.patient_profile.additional_symptoms = [s.strip() for s in user_input.split(",")]
    
    def get_patient_profile(self) -> PatientProfile:
        """Return current patient profile"""
        return self.patient_profile
    
    def get_conversation_history(self) -> List[Tuple[str, str]]:
        """Return conversation history"""
        return self.conversation_history
    
    def reset(self) -> None:
        """Reset engine for new conversation"""
        self.patient_profile = PatientProfile()
        self.current_stage = 0
        self.conversation_history = []
        self.emergency_detected = False
        self.triage_complete = False
