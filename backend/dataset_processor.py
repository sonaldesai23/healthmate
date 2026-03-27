import json
import pandas as pd
import os


# =====================================================
# 📌 CONFIGURATION
# =====================================================
INPUT_PATH = "data/imcs21/train.json"
OUTPUT_PATH = "data/imcs21/clean_dataset.csv"


# =====================================================
# 🧠 LOAD DATASET
# =====================================================
def load_dataset(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Dataset not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"✅ Loaded dataset with {len(data)} cases")
    return data


# =====================================================
# 🔍 EXTRACT & PROCESS EACH CASE
# =====================================================
def process_case(case):
    # --------------------------
    # 1. Extract fields
    # --------------------------
    self_report = case.get("self_report", "")
    diagnosis = case.get("diagnosis", "")

    # Extract symptoms
    symptoms = case.get("explicit_info", {}).get("Symptom", [])
    symptoms_text = " ".join(symptoms)

    # Extract dialogue (kept but NOT used)
    dialogue_list = case.get("dialogue", [])
    dialogue_text = " ".join([
        d.get("sentence", "") for d in dialogue_list
    ])

    # --------------------------
    # 2. Return structured fields
    # --------------------------
    return symptoms_text.strip(), self_report.strip(), diagnosis


# =====================================================
# 🚀 MAIN PROCESS FUNCTION
# =====================================================
def process_dataset(input_path, output_path):
    data = load_dataset(input_path)

    rows = []

    for idx, case in enumerate(data.values(), start=1):
        try:
            symptoms, self_report, label = process_case(case)

            if symptoms and self_report and label:
                rows.append({
                    "symptoms": symptoms,
                    "self_report": self_report,
                    "disease": label
                })

            if idx % 100 == 0:
                print(f"Processed {idx} cases...")

        except Exception as e:
            print(f"⚠️ Error processing case {idx}: {e}")

    # Convert to DataFrame
    df = pd.DataFrame(rows)

    # Remove empty rows
    df = df.dropna()

    # Save CSV
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("\n🎉 DATASET PROCESSING COMPLETE")
    print(f"✅ Total processed samples: {len(df)}")
    print(f"📁 Saved to: {output_path}")


# =====================================================
# ▶️ RUN SCRIPT
# =====================================================
if __name__ == "__main__":
    process_dataset(INPUT_PATH, OUTPUT_PATH)