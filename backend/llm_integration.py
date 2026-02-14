"""
LLM Integration: Grok AI + Gemini API
For advanced medical analysis and report generation
"""

import os
import requests
import json
from typing import Dict, Optional
import logging
from config import GROK_API_KEY, GEMINI_API_KEY


logger = logging.getLogger(__name__)

# API Keys from environment
GROK_API_KEY = os.getenv("GROK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class GrokAnalyzer:
    """
    Use Grok AI for detailed symptom analysis
    More advanced than simple heuristics
    """
    
    GROK_API_URL = "https://api.x.ai/v1/chat/completions"
    
    @staticmethod
    def analyze_symptoms(patient_profile: Dict) -> Dict:
        """
        Use Grok to analyze symptoms comprehensively
        """
        
        prompt = f"""
        You are a medical triage specialist. Analyze this patient:
        
        PATIENT INFORMATION:
        Age: {patient_profile.get('age')}
        Gender: {patient_profile.get('gender')}
        Primary Symptom: {patient_profile.get('primary_symptom')}
        Duration: {patient_profile.get('duration')}
        Severity (1-10): {patient_profile.get('severity_score')}
        Medical History: {patient_profile.get('medical_history')}
        Additional Symptoms: {patient_profile.get('additional_symptoms')}
        Current Medications: {patient_profile.get('current_medications')}
        Allergies: {patient_profile.get('allergies')}
        
        IMPORTANT GUIDELINES:
        - This is for TRIAGE ASSESSMENT ONLY, not diagnosis
        - Be conservative in assessment
        - Escalate uncertainty to professional care
        - Do NOT prescribe medications
        - Focus on red flags and urgency
        
        PROVIDE ANALYSIS WITH:
        
        1. SYMPTOM ANALYSIS
           - What could cause these symptoms?
           - How common is each possibility?
           - Pattern analysis
        
        2. RED FLAGS ASSESSMENT
           - Emergency signs present?
           - Serious conditions to rule out?
           - Vital signs concerns?
        
        3. URGENCY DETERMINATION
           - GREEN: Home care sufficient
           - YELLOW: See doctor within 24 hours
           - RED: Immediate emergency care needed
        
        4. RECOMMENDED ACTIONS
           - What to do immediately?
           - When to seek professional help?
           - What to monitor?
           - Self-care suggestions (if appropriate)
        
        5. FOLLOW-UP QUESTIONS
           - Key questions to clarify diagnosis
           - Information for healthcare provider
        
        Format clearly with headers. Be thorough but concise.
        """
        
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "grok-2-1212",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an experienced medical triage specialist. Provide thorough but safe assessment. Always err on side of caution."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            logger.info("Calling Grok API for symptom analysis...")
            response = requests.post(
                GrokAnalyzer.GROK_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            analysis = result['choices'][0]['message']['content']
            
            logger.info("Grok analysis completed successfully")
            
            return {
                "success": True,
                "analysis": analysis,
                "model": "grok-2-1212"
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Grok API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": "API unavailable - using standard assessment"
            }
        except Exception as e:
            logger.error(f"Unexpected error in Grok analysis: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class GeminiReportGenerator:
    """
    Use Gemini AI to generate professional final report
    Formatted for healthcare provider handoff
    """
    
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    
    @staticmethod
    def generate_final_report(
        patient_profile: Dict,
        grok_analysis: str,
        urgency_level: str
    ) -> Dict:
        """
        Use Gemini to create professional triage report
        """
        
        prompt = f"""
        Generate a professional TRIAGE ASSESSMENT REPORT (not a diagnosis):
        
        PATIENT DEMOGRAPHICS:
        - Age: {patient_profile.get('age')}
        - Gender: {patient_profile.get('gender')}
        
        CHIEF COMPLAINT:
        {patient_profile.get('primary_symptom')}
        
        GROK AI ANALYSIS:
        {grok_analysis}
        
        ASSESSED URGENCY LEVEL: {urgency_level.upper()}
        
        ==========================================
        CREATE REPORT WITH EXACT FORMAT:
        ==========================================
        
        HEALTHMATE TRIAGE ASSESSMENT REPORT
        Generated: [DATE]
        
        PATIENT INFORMATION
        - Age: [from data]
        - Gender: [from data]
        
        CHIEF COMPLAINT
        [Primary symptom]
        
        SYMPTOM ASSESSMENT
        [From Grok analysis - symptoms reviewed]
        
        TRIAGE SEVERITY LEVEL
        {urgency_level.upper()}
        [Explanation of why]
        
        CLINICAL OBSERVATIONS
        [Key findings, patterns, red flags]
        
        DIFFERENTIAL CONSIDERATIONS
        [Possible conditions based on symptoms - NOT diagnosis]
        
        IMMEDIATE RECOMMENDATIONS
        [What to do right now]
        - If RED: CALL 911 or go to ER immediately
        - If YELLOW: Schedule doctor visit within 24 hours
        - If GREEN: Supportive home care measures
        
        WHEN TO SEEK EMERGENCY CARE
        [Red flag symptoms that warrant 911]
        - Chest pain
        - Difficulty breathing
        - Loss of consciousness
        - Severe pain
        [Others specific to chief complaint]
        
        HOME CARE SUGGESTIONS
        [If appropriate for severity level]
        - Hydration
        - Rest
        - Over-the-counter options (mentioned as options, not recommendations)
        - Monitoring symptoms
        
        WHAT TO TELL YOUR HEALTHCARE PROVIDER
        [Key information from assessment]
        
        FOLLOW-UP
        [Next steps]
        - Schedule appointment: [timeframe]
        - Monitoring plan
        - When to escalate
        
        IMPORTANT MEDICAL DISCLAIMER
        ===========================
        This assessment is for triage guidance only.
        It is NOT a medical diagnosis.
        It does NOT replace professional medical evaluation.
        Always consult qualified healthcare professionals.
        In emergencies, CALL 911 IMMEDIATELY.
        ===========================
        
        End report with clinical professionalism. Use clear, structured format.
        Make report suitable for patient to share with healthcare provider.
        """
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.5,
                "maxOutputTokens": 2500,
            }
        }
        
        try:
            logger.info("Calling Gemini API for report generation...")
            response = requests.post(
                f"{GeminiReportGenerator.GEMINI_API_URL}?key={GEMINI_API_KEY}",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            report = result['candidates'][0]['content']['parts'][0]['text']
            
            logger.info("Gemini report generated successfully")
            
            return {
                "success": True,
                "report": report,
                "model": "gemini-pro"
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": "Report generation temporarily unavailable"
            }
        except Exception as e:
            logger.error(f"Unexpected error in Gemini report: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class TriageAnalysisPipeline:
    """
    Complete pipeline:
    Triage → Grok Analysis → Gemini Report → Final Output
    """
    
    @staticmethod
    def process_patient(patient_profile: Dict, urgency_level: str) -> Dict:
        """
        Full analysis pipeline with both AI models
        """
        
        logger.info(f"Starting analysis pipeline for patient {patient_profile.get('age')} yo")
        
        # Step 1: Grok Analysis
        logger.info("Step 1: Running Grok analysis...")
        grok_result = GrokAnalyzer.analyze_symptoms(patient_profile)
        
        if not grok_result["success"]:
            logger.error(f"Grok analysis failed: {grok_result.get('error')}")
            return {
                "success": False,
                "error": f"Grok analysis failed: {grok_result.get('error')}"
            }
        
        grok_analysis = grok_result["analysis"]
        logger.info("Grok analysis completed")
        
        # Step 2: Gemini Report
        logger.info("Step 2: Generating Gemini report...")
        gemini_result = GeminiReportGenerator.generate_final_report(
            patient_profile,
            grok_analysis,
            urgency_level
        )
        
        if not gemini_result["success"]:
            logger.error(f"Gemini report failed: {gemini_result.get('error')}")
            return {
                "success": False,
                "error": f"Gemini report failed: {gemini_result.get('error')}"
            }
        
        final_report = gemini_result["report"]
        logger.info("Gemini report completed")
        
        logger.info("Analysis pipeline completed successfully")
        
        return {
            "success": True,
            "grok_analysis": grok_analysis,
            "final_report": final_report,
            "urgency_level": urgency_level,
            "models_used": ["grok-2-1212", "gemini-pro"]
        }
