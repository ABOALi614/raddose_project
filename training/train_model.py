"""تدريب الموديل. شغّله من فولدر المشروع:   python training/train_model.py
(أو الصق الكود في Colab بعد رفع exams.py و dose_logic.py و config.py)"""
import json
import sys
from pathlib import Path

import joblib
import matplotlib
import numpy as np
import sklearn
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import dose_logic as L  # noqa: E402
from exams import EXAM_KEYS, EXAMS  # noqa: E402

rng = np.random.default_rng(42)
N = 15000


def make_data(n):
    X, y = [], []
    for _ in range(n):
        exam = EXAM_KEYS[rng.integers(len(EXAM_KEYS))]
        age = rng.uniform(EXAMS[exam]["min_age"], 90)
        if age < 18:
            weight = float(np.clip(3.5 + age * 3.0 + rng.normal(0, 3), 3, 90))
        else:
            weight = float(np.clip(rng.normal(75, 16), 40, 150))
        # نسبة الجرعة للمرجع: 25% منخفضة، 50% طبيعية، 25% عالية
        r = rng.random()
        if r < 0.25:
            ratio = rng.uniform(0.05, L.C.LOW_RATIO)
        elif r < 0.75:
            ratio = rng.uniform(L.C.LOW_RATIO, L.C.HIGH_RATIO)
        else:
            ratio = rng.uniform(L.C.HIGH_RATIO, 3.5)
        label = L.rule_label(ratio)
        dose = ratio * L.reference_limit(exam, weight)
        dose *= rng.normal(1.0, 0.03)  # خطأ قياس بسيط عشان الداتا تبقى واقعية
        X.append(L.features(exam, weight, float(dose)))
        y.append(label)
    return np.array(X), np.array(y)


X, y = make_data(N)
X_tr, X_tmp, y_tr, y_tmp = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
X_val, X_te, y_val, y_te = train_test_split(X_tmp, y_tmp, test_size=0.5, random_state=42, stratify=y_tmp)

model = GradientBoostingClassifier(n_estimators=150, max_depth=3, learning_rate=0.1, random_state=42)
model.fit(X_tr, y_tr)

val_acc = float(model.score(X_val, y_val))
test_acc = float(model.score(X_te, y_te))
pred = model.predict(X_te)
report = classification_report(y_te, pred, labels=L.LABELS, output_dict=True)
print(classification_report(y_te, pred, labels=L.LABELS))
print(f"validation accuracy = {val_acc*100:.2f}%   test accuracy = {test_acc*100:.2f}%")

res = ROOT / "training" / "results"
res.mkdir(parents=True, exist_ok=True)
fig, ax = plt.subplots(figsize=(5, 5))
ConfusionMatrixDisplay(confusion_matrix(y_te, pred, labels=L.LABELS), display_labels=L.LABELS).plot(
    ax=ax, cmap="Blues", colorbar=False)
ax.set_title("Confusion matrix (test set)")
plt.tight_layout(); plt.savefig(res / "confusion_matrix.png", dpi=150)

imp = model.feature_importances_
fig, ax = plt.subplots(figsize=(6, 3.2))
ax.barh(L.FEATURE_NAMES, imp, color="#0F6E8C"); ax.set_title("Feature importance")
plt.tight_layout(); plt.savefig(res / "feature_importance.png", dpi=150)

(ROOT / "model").mkdir(exist_ok=True)
joblib.dump(model, ROOT / "model" / "dose_model.joblib", compress=3)
meta = {
    "test_accuracy": test_acc,
    "validation_accuracy": val_acc,
    "samples": {"train": len(y_tr), "validation": len(y_val), "test": len(y_te)},
    "classification_report": report,
    "sklearn_version": sklearn.__version__,
    "algorithm": "GradientBoostingClassifier",
    "data": "synthetic, generated from reference dose levels (educational)",
}
(ROOT / "model" / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
(res / "results.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
print("saved. scikit-learn", sklearn.__version__)
