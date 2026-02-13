"""
Triage-Based Diagnostic Model
Mimics professional medical triage (structured questioning)
NOT like WebMD symptom checker (which definitively diagnoses)

Key Difference:
- WebMD: "You have migraine" (definitive)
- HealthMate: "Ask more questions → Could be migraine OR tension OR..." (assessment)
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class TriageBasedAssessment:
    """
    Structured diagnostic questioning for triage
    Gathers information to narrow down urgency level and next steps
    """
    
    # Symptom-specific question trees
    # Each question helps narrow down possibilities
    
    HEADACHE_QUESTIONS = [
        "Where exactly is the headache? (forehead, temples, back of head, all over)",
        "Describe the pain: throbbing/pulsating, dull/aching, sharp/stabbing, pressure?",
        "Any vision changes, nausea, vomiting, or sensitivity to light/sound?",
        "Did it start suddenly (like lightning bolt) or gradually (worsening over hours)?",
        "Any recent head trauma, fever, or neck stiffness?",
        "Any weakness, numbness, difficulty speaking, or loss of balance?",
        "Is this similar to previous headaches you've had?",
        "Any stress, sleep changes, or medication changes recently?"
    ]
    
    CHEST_PAIN_QUESTIONS = [
        "Where exactly? (left side, center, specific point, radiating)",
        "Describe pain: sharp, crushing, pressure, burning, tightness?",
        "Any shortness of breath, sweating, nausea, or dizziness?",
        "Any radiation to arm (which?), jaw, neck, or back?",
        "Did pain start during exercise/exertion or at rest?",
        "Any recent illness, fever, or cough?",
        "Any history of heart problems or risk factors?",
        "Is this new chest pain or similar to previous episodes?"
    ]
    
    ABDOMINAL_PAIN_QUESTIONS = [
        "Which region? (upper left, upper right, lower left, lower right, center, diffuse)",
        "Pain type: sharp/stabbing, dull/cramping, burning, pressure?",
        "Constant or comes and goes (colicky)?",
        "Any vomiting, diarrhea, constipation, or blood?",
        "Any fever, recent illness, or weight loss?",
        "Related to eating, bowel movements, or menstrual cycle?",
        "Any recent abdominal injury or surgery?",
        "Severity worsening or improving?"
    ]
    
    FEVER_QUESTIONS = [
        "What's the highest temperature recorded? (if measured)",
        "How long have you had the fever?",
        "Any chills, sweating, or body aches?",
        "Any cough, sore throat, nasal congestion, or difficulty breathing?",
        "Any rash, neck stiffness, or severe headache?",
        "Any vomiting, diarrhea, or abdominal pain?",
        "Any recent exposure to sick people or travel?",
        "Any chronic conditions or immunosuppression?"
    ]
    
    SHORTNESS_OF_BREATH_QUESTIONS = [
        "Sudden onset or gradual over hours/days?",
        "Worsening with exertion or activity?",
        "Any chest pain, wheezing, or cough?",
        "Any recent illness, travel, or immobilization?",
        "Any swelling in legs or history of blood clots?",
        "Any recent surgery or injury?",
        "Asthma or COPD history?",
        "Any anxiety or panic attacks previously?"
    ]
    
    # Condition patterns (confidence-based assessment)
    ASSESSMENT_PATTERNS = {
        "migraine": {
            "keywords": ["throbbing", "one-sided", "nausea", "sensitivity", "visual"],
            "urgency": "yellow",
            "description": "Likely migraine headache",
            "actions": "See neurologist if frequent. OTC pain relief okay for now.",
            "red_flags": ["sudden worst ever", "fever + stiff neck", "focal neurological signs"],
            "when_to_seek_help": "If worst headache of your life, or with fever/neck stiffness, go to ER"
        },
        
        "tension_headache": {
            "keywords": ["pressure", "both sides", "stress", "neck tension", "dull"],
            "urgency": "green",
            "description": "Likely tension-type headache",
            "actions": "Rest, relax neck muscles, hydration, OTC pain relief",
            "red_flags": ["worsening pattern", "new onset", "with other neurological symptoms"],
            "when_to_seek_help": "If persists >2 weeks or new pattern, see doctor"
        },
        
        "heart_attack": {
            "keywords": ["crushing", "center", "radiation", "shortness", "sweating"],
            "urgency": "red",
            "description": "POSSIBLE ACUTE CORONARY SYNDROME",
            "actions": "CALL 911 IMMEDIATELY - DO NOT DRIVE",
            "red_flags": ["All of the above symptoms"],
            "when_to_seek_help": "EMERGENCY - Call 911 immediately"
        },
        
        "anxiety": {
            "keywords": ["sharp", "localized", "stress", "panic", "breathing"],
            "urgency": "yellow",
            "description": "Possibly anxiety-related",
            "actions": "Breathing exercises, stress management, relaxation",
            "red_flags": ["with actual cardiac symptoms", "persistent despite treatment"],
            "when_to_seek_help": "See doctor to rule out cardiac causes, then mental health support"
        },
        
        "gastroenteritis": {
            "keywords": ["abdominal", "vomiting", "diarrhea", "cramps", "nausea"],
            "urgency": "yellow",
            "description": "Likely viral or bacterial gastroenteritis",
            "actions": "Rest, fluids, bland diet, avoid dairy/fatty foods",
            "red_flags": ["severe pain", "blood in stool", "signs of dehydration", "fever >102"],
            "when_to_seek_help": "If severe dehydration, persistent >3 days, or blood in stool"
        },
        
        "respiratory_infection": {
            "keywords": ["cough", "sore throat", "fever", "congestion", "shortness"],
            "urgency": "yellow",
            "description": "Likely respiratory infection (URI/bronchitis)",
            "actions": "Rest, hydration, cough drops, pain relief for aches",
            "red_flags": ["high fever", "difficulty breathing", "altered consciousness"],
            "when_to_seek_help": "If breathing difficulty, high fever, or symptoms >10 days"
        },
        
        "sepsis": {
            "keywords": ["high fever", "confusion", "rapid heart rate", "difficulty breathing", "shock"],
            "urgency": "red",
            "description": "POSSIBLE SEPSIS - LIFE-THREATENING",
            "actions": "CALL 911 IMMEDIATELY",
            "red_flags": ["Any 2+ of the above"],
            "when_to_seek_help": "EMERGENCY - Call 911"
        }
    }
    
    @staticmethod
    def get_symptom_questions(symptom: str) -> List[str]:
        """Get question tree for a symptom"""
        
        symptom_lower = symptom.lower()
        
        if "headache" in symptom_lower or "head pain" in symptom_lower:
            return TriageBasedAssessment.HEADACHE_QUESTIONS
        elif "chest" in symptom_lower or "heart" in symptom_lower:
            return TriageBasedAssessment.CHEST_PAIN_QUESTIONS
        elif "abdominal" in symptom_lower or "belly" in symptom_lower or "stomach" in symptom_lower:
            return TriageBasedAssessment.ABDOMINAL_PAIN_QUESTIONS
        elif "fever" in symptom_lower or "temperature" in symptom_lower:
            return TriageBasedAssessment.FEVER_QUESTIONS
        elif "breath" in symptom_lower or "shortness" in symptom_lower:
            return TriageBasedAssessment.SHORTNESS_OF_BREATH_QUESTIONS
        else:
            return [f"Describe your {symptom} in more detail",
                    "When did this start?",
                    "Is it getting worse or better?",
                    "What makes it better or worse?",
                    "Any other symptoms?"]
    
    @staticmethod
    def get_next_diagnostic_question(symptom: str, answers: List[str]) -> Optional[str]:
        """
        Get next question based on symptom and previous answers
        Returns None if all questions asked
        """
        
        questions = TriageBasedAssessment.get_symptom_questions(symptom)
        
        if len(answers) < len(questions):
            return questions[len(answers)]
        
        return None
    
    @staticmethod
    def assess_pattern(symptom: str, answers: List[str]) -> Dict:
        """
        Analyze answers and return probability-based assessment
        NOT definitive diagnosis - just possibilities and urgency
        """
        
        answers_combined = " ".join(answers).lower()
        
        assessment = {
            "symptom": symptom,
            "answers_count": len(answers),
            "possible_conditions": [],
            "urgency_level": "green",
            "red_flags_present": [],
            "next_steps": [],
            "disclaimer": "This is an assessment based on your responses, NOT a diagnosis. "
                         "Always consult healthcare professionals for proper diagnosis."
        }
        
        # Pattern matching - calculate confidence for each condition
        condition_scores = {}
        
        for condition, pattern in TriageBasedAssessment.ASSESSMENT_PATTERNS.items():
            # Count keyword matches
            matches = sum(1 for keyword in pattern["keywords"] if keyword in answers_combined)
            if len(pattern["keywords"]) > 0:
                confidence = matches / len(pattern["keywords"])
            else:
                confidence = 0
            
            # Store scores
            if confidence > 0.4:  # Only include if >40% match
                condition_scores[condition] = {
                    "confidence": f"{int(confidence*100)}%",
                    "description": pattern["description"],
                    "actions": pattern["actions"],
                    "urgency": pattern["urgency"]
                }
        
        # Sort by confidence and add to results
        for condition, score in sorted(condition_scores.items(), 
                                      key=lambda x: int(x[1]["confidence"].rstrip("%")), 
                                      reverse=True):
            assessment["possible_conditions"].append({
                "condition": condition,
                "confidence": score["confidence"],
                "description": score["description"],
                "recommended_actions": score["actions"]
            })
            
            # Update urgency to highest (most severe)
            if score["urgency"] == "red":
                assessment["urgency_level"] = "red"
            elif score["urgency"] == "yellow" and assessment["urgency_level"] == "green":
                assessment["urgency_level"] = "yellow"
        
        # Check for red flags
        for condition, pattern in TriageBasedAssessment.ASSESSMENT_PATTERNS.items():
            for red_flag in pattern.get("red_flags", []):
                if red_flag in answers_combined:
                    assessment["red_flags_present"].append(red_flag)
                    if pattern["urgency"] == "red":
                        assessment["urgency_level"] = "red"
        
        # Generate next steps based on urgency
        if assessment["urgency_level"] == "red":
            assessment["next_steps"] = [
                "🚨 EMERGENCY - CALL 911 IMMEDIATELY",
                "Do not drive if symptoms present",
                "Have insurance information ready"
            ]
        elif assessment["urgency_level"] == "yellow":
            assessment["next_steps"] = [
                "🟡 Schedule doctor appointment within 24 hours",
                "Visit urgent care clinic if cannot see regular doctor",
                "Monitor symptoms for any worsening",
                "Stay home if contagious symptoms present"
            ]
        else:
            assessment["next_steps"] = [
                "🟢 Home care measures appropriate",
                "Rest, hydration, basic comfort measures",
                "Monitor symptoms - see doctor if worsening or persistent",
                "Schedule regular appointment if symptoms continue >48 hours"
            ]
        
        return assessment
    
    @staticmethod
    def get_summary(assessment: Dict) -> str:
        """
        Generate readable summary of assessment
        """
        
        summary = f"\n{'='*60}\n"
        summary += "TRIAGE ASSESSMENT SUMMARY\n"
        summary += f"{'='*60}\n\n"
        
        summary += f"Symptom: {assessment['symptom']}\n"
        summary += f"Urgency Level: {assessment['urgency_level'].upper()}\n\n"
        
        if assessment["possible_conditions"]:
            summary += "Possible Conditions:\n"
            for i, cond in enumerate(assessment["possible_conditions"], 1):
                summary += f"  {i}. {cond['condition'].title()} ({cond['confidence']} confidence)\n"
                summary += f"     {cond['description']}\n\n"
        
        if assessment["red_flags_present"]:
            summary += "🚨 Red Flags Identified:\n"
            for flag in assessment["red_flags_present"]:
                summary += f"  - {flag}\n"
            summary += "\n"
        
        summary += "Recommended Actions:\n"
        for action in assessment["next_steps"]:
            summary += f"  {action}\n"
        
        summary += f"\n{assessment['disclaimer']}\n"
        summary += f"{'='*60}\n"
        
        return summary
