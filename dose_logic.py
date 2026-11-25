"""منطق الجرعات: المرجع، التصنيف بالقواعد، التحقق من المدخلات، توصية الجهاز."""
import config as C
from exams import EXAMS, EXAM_KEYS

LABELS = ["low", "normal", "high"]


def size_factor(weight_kg: float) -> float:
    """الجرعة المقبولة بتزيد مع وزن المريض وبتقل للأطفال والنحاف."""
    return min(max((weight_kg / 70.0) ** 0.6, 0.35), 1.5)


def reference_limit(exam: str, weight: float) -> float:
    return EXAMS[exam]["drl"] * size_factor(weight)


def dose_ratio(exam: str, dose: float, weight: float) -> float:
    return dose / reference_limit(exam, weight)


def rule_label(ratio: float) -> str:
    if ratio < C.LOW_RATIO:
        return "low"
    if ratio <= C.HIGH_RATIO:
        return "normal"
    return "high"


def features(exam: str, weight: float, dose: float):
    """مدخلات الموديل (نفسها في التدريب وفي الموقع)."""
    return [EXAM_KEYS.index(exam), weight, dose, dose / EXAMS[exam]["drl"]]


FEATURE_NAMES = ["exam_idx", "weight", "dose", "dose_over_drl"]


def validate(exam, age, weight, dose, device_age):
    """يرجع (أخطاء تمنع التحليل، تحذيرات)."""
    errors, warns = [], []
    if dose is None or dose <= 0:
        errors.append("err_dose")
    if age is None or not (C.MIN_AGE <= age <= C.MAX_AGE):
        errors.append("err_age")
    if weight is None or not (C.MIN_WEIGHT <= weight <= C.MAX_WEIGHT):
        errors.append("err_weight")
    if device_age is None or device_age < 0:
        errors.append("err_device_age")
    if not errors:
        e = EXAMS[exam]
        if age < e["min_age"]:
            errors.append("err_exam_age")
        elif dose > e["max_valid"]:
            errors.append("err_dose_huge")
        elif dose_ratio(exam, dose, weight) > 5:
            warns.append("warn_unusual")
    return errors, warns


def device_action(label: str, ratio: float, device_age: float, high_count: int) -> str:
    """keep / settings / service / replace"""
    if label != "high":
        return "keep"
    serious = ratio > C.VERY_HIGH_RATIO or high_count >= C.REPEAT_HIGH_COUNT
    if serious and device_age >= C.OLD_DEVICE_YEARS:
        return "replace"
    if serious:
        return "service"
    return "settings"


def extra_notes(label: str, age: float, high_count: int):
    notes = []
    if label == "low":
        notes.append("note_low")
    if high_count >= C.REPEAT_HIGH_COUNT:
        notes.append("note_repeat")
    if age < 15:
        notes.append("note_pediatric")
    return notes
