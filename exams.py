"""بيانات الفحوصات المرجعية (تقريبية وللأغراض التعليمية فقط).

القيم مبنية على نطاق مستويات الجرعة المرجعية (DRL) المنشورة في الأدلة الأوروبية
والأمريكية. لو القسم عندكم بيستخدم أرقام محلية، عدّلها هنا فقط ثم أعد التدريب:
    python training/train_model.py
كل الجرعات بوحدة mGy لكن الكمية المقاسة بتختلف من فحص لفحص.
"""

EXAMS = {
    "chest_xray": {
        "ar": "أشعة سينية على الصدر (PA)",
        "en": "Chest X-ray (PA)",
        "qty_ar": "الجرعة السطحية عند الدخول (ESD)",
        "qty_en": "Entrance surface dose (ESD)",
        "drl": 0.30,       # الجرعة المرجعية mGy
        "typical": 0.12,
        "max_valid": 5.0,  # أي قيمة أكبر منها غالبًا خطأ في الإدخال
        "min_age": 0,
    },
    "mammography": {
        "ar": "تصوير الثدي بالأشعة (ماموجرافي)",
        "en": "Mammography",
        "qty_ar": "متوسط جرعة الغدة الثديية لكل مسقط (AGD)",
        "qty_en": "Average glandular dose per view (AGD)",
        "drl": 2.5,
        "typical": 1.4,
        "max_valid": 25.0,
        "min_age": 18,
    },
    "ct_head": {
        "ar": "أشعة مقطعية على الرأس",
        "en": "CT Head",
        "qty_ar": "مؤشر جرعة الأشعة المقطعية (CTDIvol)",
        "qty_en": "CT dose index (CTDIvol)",
        "drl": 60.0,
        "typical": 42.0,
        "max_valid": 400.0,
        "min_age": 0,
    },
    "ct_chest": {
        "ar": "أشعة مقطعية على الصدر",
        "en": "CT Chest",
        "qty_ar": "مؤشر جرعة الأشعة المقطعية (CTDIvol)",
        "qty_en": "CT dose index (CTDIvol)",
        "drl": 15.0,
        "typical": 9.0,
        "max_valid": 150.0,
        "min_age": 0,
    },
    "ct_abdomen": {
        "ar": "أشعة مقطعية على البطن والحوض",
        "en": "CT Abdomen & Pelvis",
        "qty_ar": "مؤشر جرعة الأشعة المقطعية (CTDIvol)",
        "qty_en": "CT dose index (CTDIvol)",
        "drl": 20.0,
        "typical": 12.0,
        "max_valid": 200.0,
        "min_age": 0,
    },
}

EXAM_KEYS = list(EXAMS)
