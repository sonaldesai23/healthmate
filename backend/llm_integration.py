"""
LLM Integration: OpenRouter (Llama 3.3 - Stable)
"""

import os
import requests
import logging
from typing import Dict
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# API Key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def call_llm(prompt: str, model: str = "meta-llama/llama-3.3-70b-instruct") -> str:
    """
    Calls OpenRouter LLM API and returns response text
    """

    if not OPENROUTER_API_KEY:
        raise Exception("OPENROUTER_API_KEY not set in environment variables")

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a medical triage assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.6
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"API Error: {response.text}")

        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        logger.error(f"OpenRouter API error: {e}")
        raise Exception(str(e))


class TriageAnalysisPipeline:

    @staticmethod
    def process_patient(
        patient_profile: Dict,
        urgency_level: str,
        ml_predictions=None
    ) -> Dict:

        logger.info("Running OpenRouter pipeline...")

        # -------------------------
        # 🧠 FINAL PROMPT
        # -------------------------
        prompt = f"""
You are a medical triage assistant. Analyze this patient carefully.

PATIENT DETAILS:
Age: {patient_profile.get('age')}
Gender: {patient_profile.get('gender')}
Primary Symptom: {patient_profile.get('primary_symptom')}
Duration: {patient_profile.get('duration')}
Severity: {patient_profile.get('severity_score')}

Additional Symptoms:
{patient_profile.get('additional_symptoms')}

Medical History:
{patient_profile.get('medical_history')}

ML PREDICTIONS:
{ml_predictions}

URGENCY LEVEL:
{urgency_level}

----------------------------------

PROVIDE STRUCTURED OUTPUT:

1. LIKELY CONDITION
- Based on symptoms + ML predictions

2. REASONING
- Why this condition fits

3. RISK LEVEL EXPLANATION
- Explain urgency level

4. WHAT TO DO NOW
- Immediate actions

5. WHEN TO SEE DOCTOR

6. RED FLAGS
- Emergency symptoms

IMPORTANT:
- Do NOT give diagnosis
- Be cautious
- Keep it clear and structured
"""

        # -------------------------
        # 🔥 CALL LLM
        # -------------------------
        try:
            response_text = call_llm(prompt)

            logger.info("LLM analysis successful")

            return {
                "success": True,
                "analysis": response_text,
                "final_report": response_text,
                "urgency_level": urgency_level,
                "models_used": ["meta-llama/llama-3.3-70b-instruct"]
            }

        except Exception as e:
            logger.error(f"Analysis failed: {e}")

            return {
                "success": False,
                "error": str(e)
            }