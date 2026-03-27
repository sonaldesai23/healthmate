import pandas as pd
import numpy as np
import pickle
import os

from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.utils import resample


# =====================================================
# 📌 CONFIG
# =====================================================
DATA_PATH = "data/imcs21/clean_dataset.csv"
MODEL_PATH = "model.pkl"


# =====================================================
# 🧠 DISEASE PREDICTOR CLASS
# =====================================================
class DiseasePredictor:

    def __init__(self):
        print("🔄 Loading improved multilingual embedding model...")
        self.encoder = SentenceTransformer(
            'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
        )

        self.model = None
        self.label_encoder = None

    # -------------------------------------------------
    # 🧹 TEXT PREPROCESSING (STRUCTURE + AUGMENTATION)
    # -------------------------------------------------
    def preprocess_text(self, symptoms, report):
        base = f"symptoms: {symptoms} | report: {report}"

        augmented = f"patient has {symptoms} and reports {report}"

        return [base, augmented]  # returns 2 samples (augmentation)

    # -------------------------------------------------
    # ⚖️ BALANCE DATASET
    # -------------------------------------------------
    def balance_data(self, df):
        print("⚖️ Balancing dataset...")

        max_size = df['disease'].value_counts().max()

        df_balanced = []

        for disease in df['disease'].unique():
            df_class = df[df['disease'] == disease]

            df_class_upsampled = resample(
                df_class,
                replace=True,
                n_samples=max_size,
                random_state=42
            )

            df_balanced.append(df_class_upsampled)

        return pd.concat(df_balanced)

    # -------------------------------------------------
    # 📊 TRAIN MODEL
    # -------------------------------------------------
    def train(self, csv_path):

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"❌ Dataset not found at: {csv_path}")

        print("📥 Loading dataset...")
        df = pd.read_csv(csv_path)
        df = df.dropna()

        print(f"✅ Original samples: {len(df)}")

        # -------------------------------------------------
        # EXPECTING COLUMNS: symptoms, self_report, disease
        # -------------------------------------------------
        X_text = []
        y = []

        print("🧹 Applying preprocessing + augmentation...")

        for _, row in df.iterrows():
            samples = self.preprocess_text(
                row['symptoms'],
                row['self_report']
            )

            for s in samples:
                X_text.append(s)
                y.append(row['disease'])

        df_aug = pd.DataFrame({"text": X_text, "disease": y})

        print(f"✅ After augmentation: {len(df_aug)} samples")

        # -------------------------------------------------
        # BALANCE DATA
        # -------------------------------------------------
        df_aug = self.balance_data(df_aug)

        print(f"✅ After balancing: {len(df_aug)} samples")

        X_text = df_aug['text'].tolist()
        y = df_aug['disease'].tolist()

        # -------------------------------------------------
        # LABEL ENCODING
        # -------------------------------------------------
        print("🔢 Encoding labels...")
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)

        # -------------------------------------------------
        # EMBEDDINGS
        # -------------------------------------------------
        print("🧠 Generating embeddings...")
        X = self.encoder.encode(X_text, show_progress_bar=True)

        # -------------------------------------------------
        # SPLIT
        # -------------------------------------------------
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )

        # -------------------------------------------------
        # MODEL (LOGISTIC REGRESSION - BEST FOR EMBEDDINGS)
        # -------------------------------------------------
        print("🚀 Training Logistic Regression model...")

        self.model = LogisticRegression(
            max_iter=2000,
            n_jobs=-1
        )

        self.model.fit(X_train, y_train)

        # -------------------------------------------------
        # EVALUATION
        # -------------------------------------------------
        print("\n📊 Evaluating model...")

        y_pred = self.model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        print(f"\n✅ Accuracy: {accuracy:.4f}")

        print("\n📄 Classification Report:")
        print(classification_report(
            y_test,
            y_pred,
            target_names=self.label_encoder.classes_
        ))

        # -------------------------------------------------
        # SAVE MODEL
        # -------------------------------------------------
        print("\n💾 Saving model...")

        with open(MODEL_PATH, "wb") as f:
            pickle.dump({
                "model": self.model,
                "label_encoder": self.label_encoder
            }, f)

        print(f"✅ Model saved at: {MODEL_PATH}")

    # -------------------------------------------------
    # 📂 LOAD MODEL
    # -------------------------------------------------
    def load(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("❌ Model not found. Train first.")

        print("📂 Loading trained model...")

        with open(MODEL_PATH, "rb") as f:
            data = pickle.load(f)

        self.model = data["model"]
        self.label_encoder = data["label_encoder"]

        print("✅ Model loaded successfully")

    # -------------------------------------------------
    # 🔮 PREDICT (TOP-3)
    # -------------------------------------------------
    def predict(self, text):
        if self.model is None:
            raise Exception("❌ Model not loaded")

        emb = self.encoder.encode([text])

        probs = self.model.predict_proba(emb)[0]

        top3_idx = np.argsort(probs)[-3:][::-1]

        diseases = self.label_encoder.inverse_transform(top3_idx)
        confidences = probs[top3_idx]

        return list(zip(diseases, confidences))


# =====================================================
# ▶️ RUN TRAINING
# =====================================================
if __name__ == "__main__":
    predictor = DiseasePredictor()
    predictor.train(DATA_PATH)