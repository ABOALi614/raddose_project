"""تقرير الحالة كملف HTML (بيفتح وبيتطبع أو يتحفظ PDF من المتصفح)."""
from html import escape

from exams import EXAMS

COLORS = {"low": "#1D6FB8", "normal": "#1E8449", "high": "#B03A2E"}


def build_report(res: dict, t: dict, lang: str) -> str:
    rtl = lang == "ar"
    exam = EXAMS[res["exam"]]
    rows = [
        (t["patient"], res["name"] or t["unnamed"]),
        (t["age"], f"{res['age']:g}"),
        (t["weight"], f"{res['weight']:g}"),
        (t["exam_l"], exam[lang]),
        (t["device_l"], f"{res['device'] or t['unnamed']} ({res['device_age']:g})"),
        (exam["qty_" + lang], f"{res['dose']:g} mGy"),
        (t["ref_limit"], f"{res['ref']:.3g} mGy"),
        (t["ratio"], f"{res['ratio']:.2f}"),
    ]
    tr = "".join(f"<tr><th>{escape(str(a))}</th><td>{escape(str(b))}</td></tr>" for a, b in rows)
    notes = "".join(f"<li>{escape(t[n])}</li>" for n in res["notes"])
    color = COLORS[res["label"]]
    return f"""<!doctype html>
<html lang="{lang}" dir="{'rtl' if rtl else 'ltr'}"><head><meta charset="utf-8">
<title>{escape(t['report_title'])}</title>
<style>
body{{font-family:'Segoe UI',Tahoma,Arial,sans-serif;max-width:760px;margin:30px auto;padding:0 20px;color:#1B2430}}
h1{{font-size:22px;border-bottom:3px solid #0B2545;padding-bottom:8px;color:#0B2545}}
table{{width:100%;border-collapse:collapse;margin:16px 0}}
th,td{{border:1px solid #D5DAE1;padding:8px 10px;text-align:{'right' if rtl else 'left'}}}
th{{background:#EEF1F6;width:42%}}
.badge{{display:inline-block;padding:6px 16px;border-radius:6px;color:#fff;font-weight:700;background:{color}}}
.box{{border:1px solid #D5DAE1;border-radius:8px;padding:12px 16px;margin:14px 0}}
.dis{{font-size:12px;color:#5A6472;margin-top:26px}}
button{{padding:8px 18px;margin-top:10px}}
@media print{{button{{display:none}}}}
</style></head><body>
<h1>{escape(t['report_title'])}</h1>
<div>{escape(t['report_date'])}: {escape(res['time'])}</div>
<table>{tr}</table>
<div class="box"><span class="badge">{escape(t['label_' + res['label']])}</span>
<p>{escape(t['desc_' + res['label']])}</p>
<p><b>{escape(t['device_decision'])}:</b> {escape(t['act_' + res['action']])}</p>
{('<ul>' + notes + '</ul>') if notes else ''}</div>
<p class="dis">{escape(t['disclaimer'])}</p>
<button onclick="window.print()">{escape(t['print'])}</button>
</body></html>"""
