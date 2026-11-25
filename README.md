# 🩻 مُراجِع الجرعة الإشعاعية | RadDose Review

أداة تعليمية: تدخل اسم المريض وعمره ووزنه ونوع الفحص والجرعة وبيانات الجهاز، فتقول لك الجرعة **منخفضة / طبيعية / عالية** وتوصي بإجراء للجهاز (لا تغيير، مراجعة الإعدادات، معايرة وصيانة، أو التفكير في الاستبدال).

> ⚠️ للأغراض التعليمية فقط. البيانات اصطناعية والقيم المرجعية تقريبية.

## محتويات المشروع

| الملف | وظيفته |
|---|---|
| `app.py` | الموقع (Streamlit) |
| `config.py` | حدود التصنيف وقواعد قرار الجهاز |
| `exams.py` | الفحوصات والجرعات المرجعية (عدّلها هنا) |
| `dose_logic.py` | الحسابات والقواعد والتحقق من المدخلات |
| `model_utils.py` | تحميل الموديل (ولو فشل يكمل بالقواعد) |
| `translations.py` | نصوص عربي/إنجليزي |
| `report.py` | تقرير الحالة القابل للتنزيل والطباعة |
| `training/train_model.py` | تدريب الموديل |
| `training/results/` | الدقة، confusion matrix، أهمية المتغيرات (للتقرير) |
| `model/` | الموديل المدرَّب `dose_model.joblib` و `meta.json` |

## الموديل مُدرَّب بالفعل
الموديل جاهز داخل `model/` ودقته على الاختبار مكتوبة في `training/results/results.json`. لو غيّرت الأرقام في `exams.py` أو `config.py` أعد التدريب:
```bash
pip install -r requirements.txt matplotlib
python training/train_model.py
```
(ممكن تشغله في Google Colab: ارفع `exams.py` و `dose_logic.py` و `config.py` و `training/train_model.py` وشغّله.)

## تجربة على جهازك (اختياري)
```bash
pip install -r requirements.txt
streamlit run app.py
```

## الرفع على Streamlit Community Cloud
1. أنشئ حساب GitHub المخصص للمشروع (راجع قسم إخفاء الهوية) وأنشئ Repository **جديد** باسم محايد، مثلاً `dose-review`.
2. من **Add file ← Upload files** ارفع **محتويات** الفولدر (بما فيها `model` و `.streamlit` و `training`). تأكد بعد الرفع إن `.streamlit/config.toml` ظهر في الريبو.
   - الموديل حجمه صغير (أقل من 1MB) فمفيش LFS ولا مشاكل رفع.
3. ادخل https://share.streamlit.io وسجّل بنفس حساب GitHub ← **Create app**.
4. اختر الريبو والفرع `main` والملف `app.py`.
5. **Advanced settings ← Python version: 3.11** ← **Deploy**.
6. اختر Subdomain محايد (مثلاً `dose-review`).

## إخفاء الهوية
- **حساب GitHub:** استخدم حسابًا باسم وصورة محايدين وإيميل مخصص. تنبيه: شروط GitHub بتسمح بحساب مجاني شخصي واحد للشخص، فاعرف الشروط قبل ما تعمل حساب تاني.
- **بيانات الـ commit:** قبل أي رفع بـ git استخدم إيميل الحساب الجديد:
  `git config user.name "اسم محايد"` و `git config user.email "ID+username@users.noreply.github.com"`.
  (لو بترفع من الموقع مباشرة مفيش حاجة تعملها.)
- **على Streamlit:** الإعداد `toolbarMode = "minimal"` موجود في `.streamlit/config.toml` وبيخفي قايمة المطوّر عن الزوار. أظن إن Streamlit ممكن يعرض صاحب التطبيق للزوار، فبعد النشر افتح الرابط من نافذة خاصة (Incognito) وتأكد إن مفيش اسم أو صورة ليك ظاهرة.
- المشروع نفسه ما فيهوش اسمك ولا روابطك في أي ملف.

## مشاكل شائعة
| المشكلة | الحل |
|---|---|
| خطأ في تحميل الموديل | الموقع هيكمل بالقواعد المرجعية وهيكتب ده في النتيجة. تأكد إن `scikit-learn==1.9.1` في `requirements.txt` هو نفسه إصدار `model/meta.json` |
| التنسيق مش ظاهر | تأكد إن `.streamlit/config.toml` اترفع |
| عايز تغيّر الجرعات المرجعية | عدّل `exams.py` ثم أعد التدريب |
