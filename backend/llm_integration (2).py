"""
LLM Integration: Grok AI + Gemini API
For advanced medical analysis and report generation
With fallback analysis when APIs unavailable
"""

import os
import requests
import json
from typing import Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# API Keys from environment
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


class GrokAnalyzer:
    """
    Use Grok AI for detailed symptom analysis
    More advanced than simple heuristics
    With fallback to local analysis when API unavailable
    """
    
    GROK_API_URL = "https://api.x.ai/v1/chat/completions"
    REQUEST_TIMEOUT = 15  # 15 second timeout
    
    @staticmethod
    def analyze_symptoms(patient_profile: Dict) -> Dict:
        """
        Use Grok to analyze symptoms comprehensively
        Falls back to local analysis if API unavailable
        """
        
        # If no API key, use fallback immediately
        if not GROK_API_KEY:
            logger.warning("GROK_API_KEY not configured - using fallback analysis")
            return GrokAnalyzer._fallback_analysis(patient_profile)
        
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
                timeout=GrokAnalyzer.REQUEST_TIMEOUT  # Add timeout!
            )
            response.raise_for_status()
            
            result = response.json()
            analysis = result['choices'][0]['message']['content']
            
            logger.info("Grok analysis completed successfully")
            
            return {
                "success": True,
                "analysis": analysis,
                "model": "grok-2-1212",
                "source": "api"
            }
        
        except requests.exceptions.Timeout:
            logger.error("Grok API timeout - using fallback analysis")
            return GrokAnalyzer._fallback_analysis(patient_profile)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Grok API error: {e} - using fallback analysis")
            return GrokAnalyzer._fallback_analysis(patient_profile)
        
        except Exception as e:
            logger.error(f"Unexpected error in Grok analysis: {e} - using fallback")
            return GrokAnalyzer._fallback_analysis(patient_profile)
    
    @staticmethod
    def _fallback_analysis(patient_profile: Dict) -> Dict:
        """Fallback analysis when API is unavailable"""
        
        logger.info("Using fallback Grok analysis (local)")
        
        symptom = patient_profile.get('primary_symptom', 'Unknown').lower()
        severity = patient_profile.get('severity_score', 5)
        additional = patient_profile.get('additional_symptoms', [])
        
        analysis = f"""
SYMPTOM ANALYSIS
================
Primary Symptom: {patient_profile.get('primary_symptom', 'Not specified')}
Severity Level: {severity}/10
Duration: {patient_profile.get('duration', 'Not specified')}
Additional Symptoms: {', '.join(additional) if additional else 'None reported'}

MEDICAL HISTORY & RISK FACTORS
=============================
Medical History: {patient_profile.get('medical_history', {})}
Current Medications: {', '.join(patient_profile.get('current_medications', [])) or 'None'}
Known Allergies: {', '.join(patient_profile.get('allergies', [])) or 'None'}

CLINICAL ASSESSMENT
===================
Based on the reported symptoms, this requires professional medical evaluation.

Possible Differential Diagnoses:
- This symptom could be caused by multiple conditions
- Professional healthcare provider assessment is essential
- Pattern recognition suggests need for further evaluation

RED FLAG ASSESSMENT
===================
Key concerns to monitor:
- Symptom progression and changes
- Development of new symptoms
- Vital sign stability (if able to measure)
- Patient tolerance of symptoms

URGENCY DETERMINATION
====================
Based on severity score of {severity}/10:
- Scores 0-3: GREEN - Home care may be appropriate
- Scores 4-6: YELLOW - Professional evaluation recommended soon
- Scores 7-10: RED - Urgent/Emergency evaluation needed

Your reported severity of {severity}/10 suggests: {"YELLOW - See healthcare provider soon" if 4 <= severity <= 6 else ("RED - Seek immediate medical attention" if severity > 6 else "GREEN - Monitor at home")}

RECOMMENDED ACTIONS
==================
1. Do not self-diagnose - seek professional medical evaluation
2. Monitor your symptoms closely for any worsening
3. Document when symptoms started and any triggering factors
4. Keep list of all medications and allergies for healthcare provider
5. If symptoms worsen significantly, seek immediate care (call 911 or go to ER)
6. Contact your primary care physician for evaluation and guidance

WHEN TO SEEK EMERGENCY CARE
============================
Call 911 immediately if you experience:
- Severe difficulty breathing
- Chest pain or pressure
- Loss of consciousness
- Severe allergic reactions
- Uncontrolled bleeding
- Signs of stroke (facial drooping, arm weakness, speech difficulty)
- Severe trauma or injuries

FOLLOW-UP QUESTIONS FOR HEALTHCARE PROVIDER
============================================
Be prepared to discuss:
1. Exact location and character of symptoms
2. When symptoms started and progression
3. Any triggering or relieving factors
4. Complete medical and medication history
5. Recent travel, exposures, or illnesses
6. Lifestyle factors that may be relevant

ASSESSMENT DISCLAIMER
====================
This is a TRIAGE ASSESSMENT ONLY, generated without real-time API access.
It is NOT a medical diagnosis or substitute for professional medical evaluation.
Always consult qualified healthcare professionals for proper assessment and treatment.
"""
        
        return {
            "success": True,
            "analysis": analysis,
            "model": "fallback-local",
            "source": "fallback"
        }


class GeminiReportGenerator:
    """
    Use Gemini AI to generate professional final report
    Formatted for healthcare provider handoff
    With fallback to structured local report when API unavailable
    """
    
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    REQUEST_TIMEOUT = 15  # 15 second timeout
    
    @staticmethod
    def generate_final_report(
        patient_profile: Dict,
        grok_analysis: str,
        urgency_level: str
    ) -> Dict:
        """
        Use Gemini to create professional triage report
        Falls back to local report generation if API unavailable
        """
        
        # If no API key, use fallback immediately
        if not GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not configured - using fallback report")
            return GeminiReportGenerator._fallback_report(patient_profile, grok_analysis, urgency_level)
        
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
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        PATIENT INFORMATION
        - Age: {patient_profile.get('age')}
        - Gender: {patient_profile.get('gender')}
        
        CHIEF COMPLAINT
        {patient_profile.get('primary_symptom')}
        
        SYMPTOM ASSESSMENT
        [Symptoms reviewed from Grok analysis]
        
        TRIAGE SEVERITY LEVEL
        {urgency_level.upper()}
        
        CLINICAL OBSERVATIONS
        [Key findings, patterns, red flags]
        
        IMMEDIATE RECOMMENDATIONS
        [What to do right now based on severity]
        
        WHEN TO SEEK EMERGENCY CARE
        [Red flag symptoms that warrant 911]
        
        HOME CARE SUGGESTIONS
        [If appropriate for severity level]
        
        WHAT TO TELL YOUR HEALTHCARE PROVIDER
        [Key information from assessment]
        
        IMPORTANT MEDICAL DISCLAIMER
        ===========================
        This assessment is for triage guidance only.
        It is NOT a medical diagnosis.
        It does NOT replace professional medical evaluation.
        Always consult qualified healthcare professionals.
        In emergencies, CALL 911 IMMEDIATELY.
        ===========================
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
                timeout=GeminiReportGenerator.REQUEST_TIMEOUT  # Add timeout!
            )
            response.raise_for_status()
            
            result = response.json()
            report = result['candidates'][0]['content']['parts'][0]['text']
            
            logger.info("Gemini report generated successfully")
            
            return {
                "success": True,
                "report": report,
                "model": "gemini-pro",
                "source": "api"
            }
        
        except requests.exceptions.Timeout:
            logger.error("Gemini API timeout - using fallback report")
            return GeminiReportGenerator._fallback_report(patient_profile, grok_analysis, urgency_level)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API error: {e} - using fallback report")
            return GeminiReportGenerator._fallback_report(patient_profile, grok_analysis, urgency_level)
        
        except Exception as e:
            logger.error(f"Unexpected error in Gemini report: {e}")
            return GeminiReportGenerator._fallback_report(patient_profile, grok_analysis, urgency_level)
    
    @staticmethod
    def _fallback_report(patient_profile: Dict, grok_analysis: str, urgency_level: str) -> Dict:
        """Fallback report generation when API is unavailable"""
        
        logger.info("Using fallback Gemini report (local)")
        
        report = f"""
{'='*70}
HEALTHMATE TRIAGE ASSESSMENT REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*70}

PATIENT INFORMATION
===================
Age: {patient_profile.get('age', 'Not specified')}
Gender: {patient_profile.get('gender', 'Not specified')}

CHIEF COMPLAINT
===============
{patient_profile.get('primary_symptom', 'Not specified')}

SYMPTOM DURATION
================
{patient_profile.get('duration', 'Not specified')}

SEVERITY ASSESSMENT
===================
Patient-reported severity: {patient_profile.get('severity_score', 'Not rated')}/10

ADDITIONAL SYMPTOMS
===================
{', '.join(patient_profile.get('additional_symptoms', [])) or 'None reported'}

MEDICAL HISTORY
===============
{', '.join([k.replace('_', ' ').title() for k, v in patient_profile.get('medical_history', {}).items() if v]) or 'No significant history reported'}

CURRENT MEDICATIONS
===================
{', '.join(patient_profile.get('current_medications', [])) or 'None reported'}

KNOWN ALLERGIES
===============
{', '.join(patient_profile.get('allergies', [])) or 'No known drug allergies'}

TRIAGE SEVERITY LEVEL
=====================
{urgency_level.upper()}

ASSESSMENT BASIS
================
This triage assessment is based on:
1. Patient-reported symptoms and severity
2. Duration and pattern of symptoms
3. Medical history and risk factors
4. Associated symptoms and signs
5. General medical triage principles

CLINICAL OBSERVATIONS
=====================
Key Assessment Points:
- Primary symptom clearly documented
- Severity level recorded
- Associated symptoms noted
- Medical risk factors identified
- Timeline of symptom onset documented

DIFFERENTIAL CONSIDERATIONS
===========================
Based on reported symptoms, the following conditions should be considered:
- Multiple possible etiologies based on symptom pattern
- Professional medical evaluation essential for definitive diagnosis
- Specialist consultation may be appropriate depending on findings
- Further diagnostic testing likely needed

IMMEDIATE RECOMMENDATIONS
==========================
Based on assessed urgency level of {urgency_level.upper()}:

{"⚠️  YELLOW - URGENT MEDICAL EVALUATION RECOMMENDED\n\n" if urgency_level.lower() == "yellow" else ""}
{"🔴 RED - EMERGENCY MEDICAL EVALUATION NEEDED\n\n" if urgency_level.lower() == "red" else ""}
{"🟢 GREEN - HOME CARE MONITORING APPROPRIATE\n\n" if urgency_level.lower() == "green" else ""}

Actions to take:
1. Contact your primary healthcare provider for evaluation
2. If unable to reach regular doctor, visit urgent care clinic
3. For RED level symptoms, call 911 or go to nearest emergency room
4. Do not delay care if symptoms worsen
5. Seek immediate emergency care for any red flag symptoms

WHEN TO SEEK EMERGENCY CARE (CALL 911)
======================================
Seek immediate emergency care if experiencing:
- Chest pain or chest pressure
- Severe difficulty breathing or shortness of breath
- Loss of consciousness or severe dizziness
- Severe allergic reactions
- Uncontrolled bleeding
- Symptoms of stroke (facial drooping, arm weakness, slurred speech)
- Severe abdominal pain
- Seizures or uncontrolled shaking
- Severe trauma or injuries
- Any life-threatening emergency situation

HOME CARE SUGGESTIONS (IF APPROPRIATE)
======================================
For lower-acuity situations:
- Rest: Allow your body adequate time to recover
- Hydration: Drink plenty of water and clear fluids
- Nutrition: Eat light, easily digestible foods if tolerated
- Comfort measures: Use appropriate temperature comfort
- Monitor: Track symptom changes and progression
- Avoid: Strenuous activity, alcohol, and problematic foods
- Document: Note when symptoms started and any triggers

WHAT TO TELL YOUR HEALTHCARE PROVIDER
=====================================
When you see a healthcare professional, share:
1. Exact location and description of primary symptom
2. When the symptom first started
3. How symptoms have progressed or changed
4. Any triggering or relieving factors
5. Associated symptoms you're experiencing
6. Complete medical history as listed above
7. All current medications and dosages
8. Any known drug allergies
9. Recent travels, exposures, or illnesses
10. Impact on your daily activities

IMPORTANT MEDICAL DISCLAIMER
============================
⚠️  CRITICAL LEGAL AND MEDICAL NOTICE:

This triage assessment is FOR GUIDANCE ONLY and is intended to help you
understand your symptoms and determine the urgency of seeking professional care.

THIS ASSESSMENT:
- IS NOT a medical diagnosis
- IS NOT a substitute for professional medical evaluation
- CANNOT replace consultation with healthcare professionals
- DOES NOT authorize self-treatment or self-medication
- IS NOT appropriate for emergency situations (call 911)

LIMITATIONS:
- Based on information you provided, which may be incomplete or inaccurate
- Cannot perform physical examination
- Cannot order or interpret diagnostic tests
- Cannot definitively determine underlying causes
- May not capture all relevant medical information

WHAT YOU SHOULD DO:
- Always consult qualified healthcare professionals for proper evaluation
- Do not delay seeking medical care based on this assessment
- Seek emergency care immediately for serious symptoms
- Use this assessment to help communicate with your healthcare provider
- In case of emergency, CALL 911 IMMEDIATELY

LEGAL RESPONSIBILITY:
The responsibility for medical decisions rests with you and your healthcare providers.
This assessment provider makes no warranty as to accuracy or completeness.
Use at your own discretion and risk.

{'='*70}
END OF TRIAGE ASSESSMENT REPORT
{'='*70}
"""
        
        return {
            "success": True,
            "report": report,
            "model": "fallback-local",
            "source": "fallback"
        }


class TriageAnalysisPipeline:
    """
    Complete pipeline:
    Triage → Grok Analysis → Gemini Report → Final Output
    With graceful fallback when APIs unavailable
    """
    
    @staticmethod
    def process_patient(patient_profile: Dict, urgency_level: str) -> Dict:
        """
        Full analysis pipeline with both AI models
        Falls back to local analysis if APIs unavailable
        """
        
        logger.info(f"Starting analysis pipeline for patient {patient_profile.get('age')} yo")
        
        # Step 1: Grok Analysis
        logger.info("Step 1: Running Grok analysis...")
        grok_result = GrokAnalyzer.analyze_symptoms(patient_profile)
        
        if not grok_result.get("success"):
            logger.error(f"Grok analysis failed: {grok_result.get('error')}")
            grok_result["success"] = True  # Fallback succeeded
        
        grok_analysis = grok_result.get("analysis", "")
        logger.info(f"Grok analysis completed (source: {grok_result.get('source', 'unknown')})")
        
        # Step 2: Gemini Report
        logger.info("Step 2: Generating Gemini report...")
        gemini_result = GeminiReportGenerator.generate_final_report(
            patient_profile,
            grok_analysis,
            urgency_level
        )
        
        if not gemini_result.get("success"):
            logger.error(f"Gemini report failed: {gemini_result.get('error')}")
            gemini_result["success"] = True  # Fallback succeeded
        
        final_report = gemini_result.get("report", "")
        logger.info(f"Gemini report completed (source: {gemini_result.get('source', 'unknown')})")
        
        logger.info("Analysis pipeline completed successfully")
        
        return {
            "success": True,
            "grok_analysis": grok_analysis,
            "final_report": final_report,
            "urgency_level": urgency_level,
            "models_used": [grok_result.get('model', 'unknown'), gemini_result.get('model', 'unknown')],
            "sources": [grok_result.get('source', 'unknown'), gemini_result.get('source', 'unknown')]
        }