"""
Module 3: RAG Knowledge System
Retrieval-Augmented Generation for medical knowledge grounding
Uses sentence-transformers embeddings and FAISS for efficient retrieval
Prevents hallucination by grounding responses in curated medical documents
"""

import logging
import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS not available - using basic retrieval fallback")


class MedicalKnowledgeBase:
    """
    Medical knowledge base with curated first-aid and emergency protocols
    Stored as embeddings indexed by FAISS
    """
    
    KNOWLEDGE_DOCUMENTS = [
        {
            "id": "chest_pain_001",
            "title": "Chest Pain - Initial Assessment",
            "category": "Emergency",
            "content": """
            CHEST PAIN ASSESSMENT:
            - If accompanied by shortness of breath, radiating to arm/jaw, dizziness: CALL 911 IMMEDIATELY
            - Do not delay seeking medical help for chest pain
            - Symptoms of heart attack: crushing pressure, cold sweats, nausea
            - First aid: Have patient sit/lie down, loosen tight clothing
            - If prescribed nitroglycerin available and patient is conscious, may take it
            - Monitor vital signs if possible
            - Keep patient calm and reassured
            - Never drive to hospital if having chest pain - call ambulance
            """,
        },
        {
            "id": "breathing_001",
            "title": "Severe Breathing Difficulty",
            "category": "Emergency",
            "content": """
            BREATHING DIFFICULTY - EMERGENCY PROTOCOL:
            - Signs requiring immediate 911: gasping, can't complete sentences, turning blue
            - Asthma attack: Look for wheezing, use rescue inhaler if available
            - Choking: Use Heimlich maneuver if object visible and accessible
            - Anaphylaxis: If known severe allergy, use epinephrine auto-injector if available
            - Position: Sit upright, lean forward slightly
            - Remove tight clothing from neck/chest
            - Stay calm - anxiety worsens breathing
            - Have patient breathe slowly - in for 4 counts, out for 4 counts
            - Do not leave patient alone
            - Call 911 for any severe or persistent breathing difficulty
            """,
        },
        {
            "id": "unconsciousness_001",
            "title": "Unconsciousness and Loss of Consciousness",
            "category": "Emergency",
            "content": """
            UNCONSCIOUSNESS RESPONSE - IMMEDIATE ACTION:
            - CHECK: Is patient breathing? Check for responsiveness
            - If unconscious and breathing: Recovery position (on side)
            - If unconscious and NOT breathing: CPR needed (chest compressions 100-120/min)
            - CALL 911 IMMEDIATELY
            - Do not move patient unnecessarily unless in danger
            - Clear airway if possible
            - Monitor breathing and pulse continuously
            - Be ready to perform CPR
            - Do not give food or drink to unconscious person
            - Keep patient warm with blankets
            - Do not leave patient unattended
            - If seizure activity: Protect head, do not restrain
            """,
        },
        {
            "id": "hemorrhage_001",
            "title": "Severe Bleeding Management",
            "category": "Emergency",
            "content": """
            SEVERE BLEEDING CONTROL:
            - CALL 911 for heavy, uncontrolled bleeding
            - Apply direct pressure with clean cloth - DO NOT REMOVE CLOTH
            - If cloth soaks through, add more cloth on top (don't remove first)
            - Maintain pressure for 10-15 minutes minimum
            - Elevate injured area above heart if possible (no fracture suspected)
            - Apply pressure to arterial pressure points if available:
              * Inner arm (brachial artery) for arm bleeding
              * Groin (femoral artery) for leg bleeding
            - Use tourniquet above wound if leg/arm bleeding uncontrolled (last resort)
            - Do not use tourniquet on neck, torso, or head
            - Do not probe wound or remove embedded objects
            - Keep patient lying down
            - Do not give anything to eat or drink
            - Monitor for shock: pale, cold, weak pulse, rapid breathing
            - Reassure patient and keep warm
            """,
        },
        {
            "id": "seizure_001",
            "title": "Seizure First Aid",
            "category": "Emergency",
            "content": """
            SEIZURE MANAGEMENT:
            - CALL 911 if first seizure or seizure lasting >5 minutes
            - During seizure:
              * Do NOT restrain patient
              * Do NOT put anything in mouth
              * Protect head with cushion if available
              * Move dangerous objects away
              * Clear space around patient
              * Note time seizure started
            - Position patient on side after seizure stops
            - Do not give food/water until fully conscious
            - Stay with patient - confusion may persist after seizure
            - Check for injuries after seizure ends
            - If known epilepsy and rescue medication available (Diastat), follow instructions
            - After seizure: Recovery position, monitor breathing, reassure patient
            - Patient may be confused - speak calmly and slowly
            - Do not drive after seizure
            """,
        },
        {
            "id": "stroke_001",
            "title": "Stroke Recognition - FAST Assessment",
            "category": "Emergency",
            "content": """
            STROKE ASSESSMENT - FAST TEST (Time Critical):
            F - FACE: Ask to smile. Facial drooping on one side?
            A - ARMS: Raise both arms. Drift downward on one side?
            S - SPEECH: Repeat simple phrase. Slurred or difficult?
            T - TIME: Note exact time symptoms started
            
            IF ANY POSITIVE: CALL 911 IMMEDIATELY
            
            Stroke symptoms:
            - Sudden weakness or numbness (one side)
            - Sudden vision problems
            - Sudden loss of balance/coordination
            - Sudden severe headache with no known cause
            - Sudden trouble understanding others
            
            First aid:
            - DO NOT DRIVE - call 911
            - Note exact time of symptom onset
            - Keep airway clear
            - Do not give food/drink
            - Reassure patient
            - Loosen tight clothing
            - Keep patient calm
            - Have medication list/allergies ready for paramedics
            - STROKE IS TIME-CRITICAL: Get to hospital within 3 hours if possible
            """,
        },
        {
            "id": "anaphylaxis_001",
            "title": "Anaphylaxis and Severe Allergic Reaction",
            "category": "Emergency",
            "content": """
            ANAPHYLAXIS - LIFE-THREATENING EMERGENCY:
            Signs and symptoms:
            - Difficulty breathing, throat tightness
            - Swelling of lips, face, throat
            - Hives, severe itching, red rash
            - Rapid weak pulse
            - Dizziness, fainting
            - Severe abdominal pain, diarrhea
            
            IMMEDIATE ACTION:
            1. CALL 911 IMMEDIATELY
            2. If epinephrine auto-injector (EpiPen) available:
               - Follow injection instructions immediately
               - Inject into outer thigh (can inject through clothing)
               - Keep pressure on injector as directed
               - May need second dose after 5-15 minutes
            3. Position patient: Lying flat, legs elevated (unless vomiting)
            4. Loosen clothing
            5. Do not leave patient alone
            6. Have medication list ready
            7. If patient unconscious and breathing: Recovery position
            8. If not breathing: Be prepared for CPR
            
            Even if symptoms improve after epinephrine, MUST go to hospital
            """,
        },
        {
            "id": "diarrhea_001",
            "title": "Acute Diarrhea and Dehydration",
            "category": "Non-Emergency",
            "content": """
            DIARRHEA MANAGEMENT:
            Mild diarrhea (non-emergency):
            - Most acute diarrhea resolves within 24-48 hours
            - Causes: viral, bacterial, food intolerance, antibiotics
            
            Home care:
            - REST: Reduce activity, avoid strenuous exercise
            - FLUIDS: Drink electrolyte solutions (oral rehydration salts)
            - Clear broths, sports drinks, water acceptable
            - DIET: Start with bland foods (rice, bananas, crackers, toast)
            - Avoid dairy, fatty, spicy foods for 24-48 hours
            - Medications: Loperamide if no fever or blood
            
            Seek immediate care if:
            - Severe abdominal pain
            - Blood or black stools
            - Signs of severe dehydration (dizziness, no urination >6 hours)
            - High fever (>103°F)
            - Diarrhea lasting >48 hours
            - Signs of sepsis (extreme weakness, altered mental status)
            
            Dehydration signs:
            - Dry mouth, thirst
            - Dark urine
            - Dizziness
            - Decreased urination
            - Weakness
            """,
        },
        {
            "id": "fever_001",
            "title": "Fever Management",
            "category": "Non-Emergency",
            "content": """
            FEVER MANAGEMENT (>100.4°F / 38°C):
            Home treatment for mild fever:
            - Rest: Get adequate sleep
            - Hydration: Drink fluids, water, warm liquids
            - Temperature reduction:
              * Cool compress on forehead/wrists
              * Light clothing and blankets
              * Lukewarm sponging (avoid cold water - may cause chills)
            - Medications (acetaminophen, ibuprofen) if discomfort
            - Avoid ice baths - counterproductive
            
            Seek medical care if:
            - High fever (>103°F / 39.4°C) in adults
            - Fever >104°F (40°C)
            - Fever lasting >48-72 hours
            - Fever with severe headache, stiff neck, confusion
            - Fever with difficulty breathing
            - Fever with unresponsiveness
            - Any fever in infants <3 months old (call pediatrician)
            
            Fever fact: Fever is body's defense mechanism - not harmful by itself
            """,
        },
        {
            "id": "wounds_001",
            "title": "Wound Care and Minor Injury Management",
            "category": "Non-Emergency",
            "content": """
            MINOR WOUND CARE:
            Clean wound (minor cut/scrape):
            1. Stop bleeding: Apply direct pressure for 5-10 minutes
            2. Clean: Wash with soap and clean water
            3. Remove debris: Use clean cloth to gently remove dirt
            4. Dry: Pat dry with clean cloth
            5. Disinfect: Apply antibiotic ointment if available
            6. Cover: Use sterile bandage if needed
            7. Change bandage: Daily or when wet/dirty
            
            Wound care tips:
            - Keep wound clean and dry
            - Elevate if possible to reduce swelling
            - Change dressing if bleeding continues
            - Watch for signs of infection
            
            Seek medical care if:
            - Bleeding doesn't stop after 15 minutes pressure
            - Wound is deep (more than ¼ inch)
            - Edges wide open or gaping
            - Severe pain
            - Wound is dirty or rusty object (tetanus risk)
            - Wound on face/hand needs better cosmetic closure
            
            Signs of wound infection:
            - Increasing redness, warmth, swelling
            - Pus or discharge
            - Red streaks extending from wound
            - Fever
            """,
        },
        {
            "id": "shock_001",
            "title": "Shock - Acute Emergency",
            "category": "Emergency",
            "content": """
            SHOCK RECOGNITION AND FIRST AID:
            Shock signs (multiple or all present):
            - Pale, cold, clammy skin
            - Rapid weak pulse (>100/min)
            - Rapid shallow breathing
            - Confusion, anxiety, reduced consciousness
            - Weakness, fainting
            - Low blood pressure (if measured)
            
            Causes: Severe bleeding, severe infection, allergic reaction, trauma
            
            IMMEDIATE ACTION:
            1. CALL 911 IMMEDIATELY
            2. Lay patient flat
            3. Elevate legs 12 inches (unless head/neck/spinal injury suspected)
            4. Do NOT give food/water
            5. Keep patient warm with blankets
            6. Do not move unnecessarily
            7. Loosen tight clothing
            8. Monitor breathing
            9. Be ready for CPR
            10. Stay calm and reassure patient
            
            Do not:
            - Give anything by mouth
            - Move patient unless in danger
            - Leave patient alone
            - Elevate legs if spinal injury suspected
            """,
        },
    ]
    
    def __init__(self):
        self.documents = self.KNOWLEDGE_DOCUMENTS
        self.embeddings = None
        self.index = None
        self.model = None
        self.document_texts = None
        self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """Initialize embedding model and FAISS index"""
        try:
            if FAISS_AVAILABLE:
                self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                self.document_texts = [doc["content"] for doc in self.documents]
                self.embeddings = self.model.encode(self.document_texts, convert_to_numpy=True)
                self.embeddings = np.asarray(self.embeddings).astype('float32')
                
                # Create FAISS index
                self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
                self.index.add(self.embeddings)
                logger.info(f"RAG Knowledge Base initialized with {len(self.documents)} documents")
            else:
                logger.warning("FAISS not available - using basic keyword matching")
        except Exception as e:
            logger.error(f"Error initializing embeddings: {e}")
            self.embeddings = None
    
    def retrieve_relevant_documents(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve top-k most relevant documents for a query
        Uses FAISS if available, falls back to keyword matching
        """
        if self.model and self.index:
            return self._retrieve_with_faiss(query, top_k)
        else:
            return self._retrieve_with_keywords(query, top_k)
    
    def _retrieve_with_faiss(self, query: str, top_k: int) -> List[Dict]:
        """Retrieve using FAISS embeddings"""
        try:
            query_embedding = self.model.encode([query], convert_to_numpy=True)
            query_embedding = np.asarray(query_embedding).astype('float32')
            
            distances, indices = self.index.search(query_embedding, top_k)
            
            results = []
            for idx in indices[0]:
                if idx < len(self.documents):
                    results.append({
                        "document": self.documents[idx],
                        "relevance_score": float(1 / (1 + distances[0][len(results)])),
                    })
            
            return results
        except Exception as e:
            logger.error(f"FAISS retrieval error: {e}")
            return self._retrieve_with_keywords(query, top_k)
    
    def _retrieve_with_keywords(self, query: str, top_k: int) -> List[Dict]:
        """Fallback keyword-based retrieval"""
        query_words = set(query.lower().split())
        
        scores = []
        for i, doc in enumerate(self.documents):
            doc_text = (doc["title"] + " " + doc["content"]).lower()
            doc_words = set(doc_text.split())
            
            # Calculate Jaccard similarity
            if doc_words:
                intersection = len(query_words & doc_words)
                union = len(query_words | doc_words)
                score = intersection / union if union > 0 else 0
                scores.append((score, i))
        
        scores.sort(reverse=True)
        results = []
        for score, idx in scores[:top_k]:
            results.append({
                "document": self.documents[idx],
                "relevance_score": score,
            })
        
        return results
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict]:
        """Retrieve specific document by ID"""
        for doc in self.documents:
            if doc["id"] == doc_id:
                return doc
        return None
    
    def get_documents_by_category(self, category: str) -> List[Dict]:
        """Get all documents in a category"""
        return [doc for doc in self.documents if doc["category"] == category]


class RAGSystem:
    """
    Retrieval-Augmented Generation wrapper
    Grounds medical responses in curated knowledge base
    """
    
    def __init__(self):
        self.knowledge_base = MedicalKnowledgeBase()
    
    def generate_grounded_response(self, query: str, context: Optional[str] = None) -> Dict:
        """
        Generate response grounded in retrieved knowledge
        Returns retrieved documents and guidance text
        """
        # Retrieve relevant documents
        retrieved_docs = self.knowledge_base.retrieve_relevant_documents(query, top_k=3)
        
        response = {
            "query": query,
            "retrieved_documents": retrieved_docs,
            "guidance": self._compile_guidance(retrieved_docs),
            "sources": [doc["document"]["id"] for doc in retrieved_docs],
        }
        
        return response
    
    def _compile_guidance(self, retrieved_docs: List[Dict]) -> str:
        """Compile guidance from retrieved documents"""
        if not retrieved_docs:
            return "No specific guidance found for this query."
        
        guidance_parts = []
        for doc_info in retrieved_docs:
            doc = doc_info["document"]
            guidance_parts.append(f"\n### {doc['title']}")
            guidance_parts.append(doc["content"])
        
        return "".join(guidance_parts)
    
    def get_emergency_protocols(self) -> Dict:
        """Get all emergency protocols"""
        emergency_docs = self.knowledge_base.get_documents_by_category("Emergency")
        return {
            "emergency_protocols": emergency_docs,
            "count": len(emergency_docs),
        }
    
    def get_first_aid_guidance(self, symptom: str) -> Dict:
        """Get first aid guidance for a symptom"""
        return self.generate_grounded_response(symptom)
