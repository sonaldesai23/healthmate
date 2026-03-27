import pickle
import numpy as np
from sentence_transformers import SentenceTransformer


class MLService:

    def __init__(self):
        print("🔄 Loading ML model + embedding...")

        self.encoder = SentenceTransformer(
            'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
        )

        with open("model.pkl", "rb") as f:
            data = pickle.load(f)

        self.model = data["model"]
        self.label_encoder = data["label_encoder"]

        print("✅ ML Service Ready")

    def predict(self, text):
        emb = self.encoder.encode([text])

        probs = self.model.predict_proba(emb)[0]

        top3_idx = np.argsort(probs)[-3:][::-1]

        diseases = self.label_encoder.inverse_transform(top3_idx)
        confidences = probs[top3_idx]

        return [
            {"disease": d, "confidence": float(c)}
            for d, c in zip(diseases, confidences)
        ]