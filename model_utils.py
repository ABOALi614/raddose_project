"""تحميل الموديل والتصنيف. لو الموديل مش شغال الموقع يكمل بالقواعد بدل ما يقع."""
import json
from pathlib import Path

import streamlit as st

import dose_logic as L

BASE = Path(__file__).parent
MODEL_PATH = BASE / "model" / "dose_model.joblib"


@st.cache_resource(show_spinner=False)
def load_model():
    """يرجع الموديل أو None لو فيه أي مشكلة (ملف ناقص / اختلاف إصدار المكتبة)."""
    try:
        import joblib

        return joblib.load(MODEL_PATH)
    except Exception:
        return None


def classify(exam: str, weight: float, dose: float):
    """يرجع (التصنيف، قاموس الاحتمالات، المصدر: model أو rules)."""
    model = load_model()
    if model is not None:
        try:
            x = [L.features(exam, weight, dose)]
            probs = model.predict_proba(x)[0]
            probs = {c: float(p) for c, p in zip(model.classes_, probs)}
            top = max(probs, key=probs.get)
            return top, probs, "model"
        except Exception:
            pass
    label = L.rule_label(L.dose_ratio(exam, dose, weight))
    return label, {c: (1.0 if c == label else 0.0) for c in L.LABELS}, "rules"


def model_info() -> dict:
    p = BASE / "model" / "meta.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
