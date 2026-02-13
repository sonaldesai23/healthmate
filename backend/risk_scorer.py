"""
Module 4: Risk Scoring and Urgency Classification
Calculates severity scores and maps to urgency levels
Inspired by Health-LLM's confidence scoring mechanism
"""

import logging
import math
from typing import Dict, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class UrgencyLevel(Enum):
    """Urgency classification"""
    GREEN = ("mild", 0.33, "🟢")
    YELLOW = ("moderate", 0.66, "🟡")
    RED = ("emergency", 1.0, "🔴")


@dataclass
class RiskScore:
    """Risk assessment result"""
    overall_score: float  # 0-1
    symptom_severity_score: float  # 0-1
    chronic_disease_score: float  # 0-1
    symptom_count_score: float  # 0-1
    duration_score: float  # 0-1
    urgency_level: UrgencyLevel
    reasoning: str
    recommendations: list
    

class RiskScorer:
    """
    Calculates risk scores based on patient profile
    Maps scores to urgency levels
    Provides reasoning and recommendations
    """
    
    # Score weights (from SEVERITY_WEIGHTS in triage_engine)
    WEIGHTS = {
        "symptom_severity": 0.4,
        "chronic_disease": 0.3,
        "symptom_count": 0.15,
        "duration": 0.15,
    }
    
    # Severity scoring thresholds
    SEVERITY_THRESHOLDS = {
        "low_risk": 0.33,
        "moderate_risk": 0.66,
        "high_risk": 1.0,
    }
    
    # Symptoms that increase urgency
    HIGH_URGENCY_SYMPTOMS = {
        "chest_pain", "difficulty_breathing", "unconscious", "seizure",
        "heavy_bleeding", "stroke_symptoms", "severe_trauma", "poisoning",
        "anaphylaxis", "severe_allergic_reaction", "choking", "cardiac_symptoms",
    }
    
    MODERATE_URGENCY_SYMPTOMS = {
        "high_fever", "severe_vomiting", "severe_diarrhea", "severe_dehydration",
        "severe_abdominal_pain", "severe_head_pain", "severe_injury",
        "uncontrolled_bleeding", "severe_breathing_difficulty",
    }
    
    # Chronic conditions that increase risk
    CHRONIC_CONDITIONS_RISK = {
        "diabetes": 0.15,
        "hypertension": 0.12,
        "heart_disease": 0.25,
        "stroke_history": 0.20,
        "asthma": 0.10,
        "kidney_disease": 0.18,
    }
    
    def calculate_risk(self, patient_profile) -> RiskScore:
        """
        Calculate overall risk score from patient profile
        Returns RiskScore with breakdown and urgency level
        """
        
        # Component scores
        symptom_severity_score = self._calculate_symptom_severity(patient_profile)
        chronic_disease_score = self._calculate_chronic_disease_score(patient_profile)
        symptom_count_score = self._calculate_symptom_count_score(patient_profile)
        duration_score = self._calculate_duration_score(patient_profile)
        
        # Weighted overall score
        overall_score = (
            self.WEIGHTS["symptom_severity"] * symptom_severity_score +
            self.WEIGHTS["chronic_disease"] * chronic_disease_score +
            self.WEIGHTS["symptom_count"] * symptom_count_score +
            self.WEIGHTS["duration"] * duration_score
        )
        
        # Clamp to 0-1
        overall_score = min(1.0, max(0.0, overall_score))
        
        # Determine urgency level
        if overall_score >= self.SEVERITY_THRESHOLDS["high_risk"]:
            urgency_level = UrgencyLevel.RED
        elif overall_score >= self.SEVERITY_THRESHOLDS["moderate_risk"]:
            urgency_level = UrgencyLevel.YELLOW
        else:
            urgency_level = UrgencyLevel.GREEN
        
        # Generate reasoning and recommendations
        reasoning = self._generate_reasoning(
            overall_score, symptom_severity_score, chronic_disease_score,
            symptom_count_score, duration_score, patient_profile
        )
        
        recommendations = self._generate_recommendations(
            urgency_level, patient_profile, overall_score
        )
        
        return RiskScore(
            overall_score=overall_score,
            symptom_severity_score=symptom_severity_score,
            chronic_disease_score=chronic_disease_score,
            symptom_count_score=symptom_count_score,
            duration_score=duration_score,
            urgency_level=urgency_level,
            reasoning=reasoning,
            recommendations=recommendations,
        )
    
    def _calculate_symptom_severity(self, patient_profile) -> float:
        """
        Calculate severity score based on:
        1. Self-reported severity (0-10 scale)
        2. Symptom type classification
        """
        base_score = patient_profile.severity_score / 10.0
        
        # Check for high-urgency symptoms
        symptoms_text = (
            (patient_profile.primary_symptom or "").lower() +
            " " +
            " ".join(patient_profile.additional_symptoms or []).lower()
        ).lower()
        
        symptom_multiplier = 1.0
        
        for symptom in self.HIGH_URGENCY_SYMPTOMS:
            if symptom.replace("_", " ") in symptoms_text:
                symptom_multiplier = 1.5
                break
        
        if symptom_multiplier == 1.0:
            for symptom in self.MODERATE_URGENCY_SYMPTOMS:
                if symptom.replace("_", " ") in symptoms_text:
                    symptom_multiplier = 1.2
                    break
        
        severity_score = min(1.0, base_score * symptom_multiplier)
        return severity_score
    
    def _calculate_chronic_disease_score(self, patient_profile) -> float:
        """
        Calculate risk increase from chronic conditions
        Multiple conditions increase risk exponentially
        """
        if not patient_profile.medical_history:
            return 0.0
        
        total_risk = 0.0
        for condition, has_condition in patient_profile.medical_history.items():
            if has_condition and condition in self.CHRONIC_CONDITIONS_RISK:
                total_risk += self.CHRONIC_CONDITIONS_RISK[condition]
        
        # Cap at 1.0, but allow stacking of conditions
        return min(1.0, total_risk)
    
    def _calculate_symptom_count_score(self, patient_profile) -> float:
        """
        Calculate score based on number of symptoms
        Multiple symptoms increase risk
        """
        symptom_count = len(patient_profile.additional_symptoms or [])
        
        # Non-linear increase: 0 symptoms = 0, 1 = 0.1, 2-3 = 0.3, 4+ = 0.7
        if symptom_count == 0:
            return 0.0
        elif symptom_count == 1:
            return 0.1
        elif symptom_count <= 3:
            return 0.3
        else:
            return min(1.0, 0.7 + (symptom_count - 3) * 0.1)
    
    def _calculate_duration_score(self, patient_profile) -> float:
        """
        Calculate score based on symptom duration
        Longer duration = higher risk of serious condition
        """
        duration_text = (patient_profile.duration or "").lower()
        
        # Parsing duration
        if "minutes" in duration_text or "hour" in duration_text and "hours" not in duration_text:
            return 0.1  # Recent onset, low risk
        elif "hours" in duration_text:
            return 0.2  # Several hours
        elif "day" in duration_text:
            # Parse number of days
            import re
            match = re.search(r'(\d+)', duration_text)
            if match:
                days = int(match.group(1))
                if days <= 3:
                    return 0.3
                elif days <= 7:
                    return 0.5
                else:
                    return 0.7
            return 0.4
        elif "week" in duration_text:
            return 0.8
        elif "month" in duration_text or "months" in duration_text:
            return 0.9
        else:
            return 0.2  # Unknown duration, assume recent
    
    def _generate_reasoning(
        self, overall_score, symptom_score, disease_score,
        count_score, duration_score, patient_profile
    ) -> str:
        """Generate human-readable reasoning for risk score"""
        
        reasons = []
        
        # Symptom severity
        if symptom_score >= 0.7:
            reasons.append(f"High symptom severity (score: {symptom_score:.2f}) - symptoms are severe")
        elif symptom_score >= 0.4:
            reasons.append(f"Moderate symptom severity (score: {symptom_score:.2f})")
        
        # Chronic diseases
        if disease_score > 0:
            active_conditions = [
                cond.replace("_", " ").title()
                for cond, has_cond in patient_profile.medical_history.items()
                if has_cond
            ]
            reasons.append(f"Chronic conditions increase risk: {', '.join(active_conditions)} (score: {disease_score:.2f})")
        
        # Multiple symptoms
        if count_score >= 0.3:
            reasons.append(f"Multiple symptoms present ({len(patient_profile.additional_symptoms)} additional symptoms)")
        
        # Duration
        if duration_score >= 0.5:
            reasons.append(f"Extended symptom duration increases concern")
        
        reasoning = "Risk Assessment: " + "; ".join(reasons) if reasons else "Risk Assessment: Mild symptoms, recent onset"
        return reasoning
    
    def _generate_recommendations(
        self, urgency_level: UrgencyLevel, patient_profile, overall_score
    ) -> list:
        """Generate action recommendations based on risk level"""
        
        recommendations = []
        
        if urgency_level == UrgencyLevel.RED:
            recommendations = [
                "🚨 EMERGENCY - CALL 911 IMMEDIATELY",
                "Do not drive to the hospital - call an ambulance",
                "Have insurance information and medication list ready",
                "If possible, have someone stay with you",
                "Keep this assessment record for paramedics",
            ]
        
        elif urgency_level == UrgencyLevel.YELLOW:
            recommendations = [
                "🟡 Moderate Urgency - Visit doctor or urgent care soon",
                "Schedule appointment or visit walk-in clinic today/tomorrow",
                "Monitor your condition closely for any worsening",
                "Keep hydrated and rest",
                "Avoid driving if dizzy or impaired",
                "Have your medical history and medications available",
            ]
        
        else:  # GREEN
            recommendations = [
                "🟢 Mild - Home care may be sufficient",
                "Rest, hydration, and over-the-counter care if needed",
                "Monitor symptoms - seek care if worsening",
                "Contact primary care doctor if symptoms persist >48 hours",
                "Avoid self-medication without consulting pharmacist",
                "Stay home if fever/infectious symptoms to prevent spread",
            ]
        
        return recommendations


class SeverityAnalyzer:
    """
    Additional analyzer for complex severity assessments
    Used for edge cases and multi-symptom evaluation
    """
    
    @staticmethod
    def is_potentially_serious(primary_symptom: str, additional_symptoms: list) -> bool:
        """Quick check if combination seems serious"""
        
        serious_combinations = {
            ("chest pain", ["difficulty breathing", "dizziness"]),
            ("difficulty breathing", ["chest pain", "dizziness"]),
            ("severe headache", ["fever", "stiff neck"]),
            ("confusion", ["high fever", "difficulty breathing"]),
        }
        
        symptom_set = set([s.lower() for s in [primary_symptom] + (additional_symptoms or [])])
        
        for combo in serious_combinations:
            if all(s.lower() in " ".join(symptom_set) for s in combo):
                return True
        
        return False
    
    @staticmethod
    def assess_dehydration_risk(symptoms: list, duration_hours: float) -> float:
        """Assess dehydration risk from vomiting/diarrhea"""
        
        diarrhea_vomit_count = sum(
            1 for s in symptoms
            if any(x in s.lower() for x in ["diarrhea", "vomit", "vomiting"])
        )
        
        risk = min(1.0, (diarrhea_vomit_count / 2.0) * (duration_hours / 24.0))
        return risk
