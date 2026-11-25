"""الموقع الرئيسي — شغّله بالأمر:  streamlit run app.py"""
from datetime import datetime
from html import escape

import pandas as pd
import streamlit as st

import config as C
import dose_logic as L
from exams import EXAMS, EXAM_KEYS
from model_utils import classify, model_info
from report import COLORS, build_report
from translations import T

st.set_page_config(page_title="RadDose Review", page_icon="🩻", layout="wide")

# ---------------- اللغة ----------------
_, lang_col = st.columns([5, 2])
with lang_col:
    choice = st.radio("lang", ["العربية", "English"], horizontal=True, label_visibility="collapsed")
lang = "ar" if choice == "العربية" else "en"
t = T[lang]
rtl = lang == "ar"

# ---------------- الشكل ----------------
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap');
html, body, .stApp, .stMarkdown, button, label, p, h1, h2, h3, h4, input, textarea
    {{ font-family: 'IBM Plex Sans Arabic', 'Segoe UI', sans-serif; }}
#MainMenu, footer {{ visibility: hidden; }}
.block-container {{ padding-top: 1.2rem; max-width: 1100px; direction: {'rtl' if rtl else 'ltr'}; text-align: {'right' if rtl else 'left'}; }}
input[type=number] {{ direction: ltr; text-align: {'right' if rtl else 'left'}; }}
.hero {{ background: #0B2545; color: #fff; border-radius: 10px; padding: 1.4rem 1.6rem; margin-bottom: 1rem;
        border-bottom: 4px solid #C9A227; }}
.hero h1 {{ font-size: 1.7rem; margin: 0 0 .3rem; color: #fff; padding: 0; }}
.hero p {{ margin: 0; opacity: .85; font-size: .95rem; }}
.panel-title {{ font-weight: 700; color: #0B2545; border-{'right' if rtl else 'left'}: 4px solid #0F6E8C;
               padding-{'right' if rtl else 'left'}: .6rem; margin: .8rem 0 .5rem; }}
.card {{ background: #fff; border: 1px solid #D5DAE1; border-radius: 10px; padding: 1.1rem 1.3rem; margin: .6rem 0; }}
.badge {{ display: inline-block; padding: .3rem 1rem; border-radius: 6px; color: #fff; font-weight: 700; font-size: 1.1rem; }}
.kv {{ display: flex; justify-content: space-between; border-bottom: 1px solid #EEF1F6; padding: .35rem 0; font-size: .95rem; }}
.kv span:first-child {{ color: #5A6472; }}
.meter {{ direction: ltr; position: relative; margin: 1.6rem 0 .3rem; }}
.meter .bar {{ display: flex; height: 14px; border-radius: 7px; overflow: hidden; }}
.meter .pin {{ position: absolute; top: -12px; width: 0; height: 0; transform: translateX(-50%);
              border-left: 7px solid transparent; border-right: 7px solid transparent; border-top: 11px solid #0B2545; }}
.meter .legend {{ display: flex; font-size: .78rem; color: #5A6472; margin-top: .3rem; }}
.foot {{ text-align: center; color: #7A8493; font-size: .8rem; margin-top: 2rem; }}
</style>
<div class="hero"><h1>🩻 {escape(t['title'])}</h1><p>{escape(t['subtitle'])}</p></div>
""",
    unsafe_allow_html=True,
)

# ---------------- حالة الجلسة ----------------
st.session_state.setdefault("log", [])
st.session_state.setdefault("result", None)


def meter_html(ratio: float) -> str:
    scale = 2.5
    pos = min(ratio, scale) / scale * 100
    w_low, w_norm = C.LOW_RATIO / scale * 100, (C.HIGH_RATIO - C.LOW_RATIO) / scale * 100
    w_high = 100 - w_low - w_norm
    return f"""
<div class="meter">
  <div class="pin" style="left:{pos:.1f}%"></div>
  <div class="bar">
    <div style="width:{w_low:.1f}%;background:{COLORS['low']}"></div>
    <div style="width:{w_norm:.1f}%;background:{COLORS['normal']}"></div>
    <div style="width:{w_high:.1f}%;background:{COLORS['high']}"></div>
  </div>
  <div class="legend">
    <div style="width:{w_low:.1f}%">{escape(t['meter_low'])}</div>
    <div style="width:{w_norm:.1f}%">{escape(t['meter_normal'])}</div>
    <div style="width:{w_high:.1f}%">{escape(t['meter_high'])}</div>
  </div>
</div>"""


def render_result(res: dict):
    exam = EXAMS[res["exam"]]
    color = COLORS[res["label"]]
    st.markdown(f"<div class='panel-title'>{escape(t['result_title'])}</div>", unsafe_allow_html=True)
    kv = [
        (t["patient"], res["name"] or t["unnamed"]),
        (t["exam_l"], exam[lang]),
        (t["device_l"], res["device"] or t["unnamed"]),
        (t["dose_received"], f"{res['dose']:g} mGy"),
        (t["ref_limit"], f"{res['ref']:.3g} mGy"),
        (t["ratio"], f"{res['ratio']:.2f}"),
    ]
    rows = "".join(f"<div class='kv'><span>{escape(a)}</span><b>{escape(str(b))}</b></div>" for a, b in kv)
    st.markdown(
        f"""<div class="card">
<span class="badge" style="background:{color}">{escape(t['label_' + res['label']])}</span>
<p style="margin:.7rem 0 0">{escape(t['desc_' + res['label']])}</p>
{meter_html(res['ratio'])}
{rows}
</div>""",
        unsafe_allow_html=True,
    )
    for w in res["warns"]:
        st.warning(t[w])

    st.markdown(f"<div class='panel-title'>{escape(t['device_decision'])}</div>", unsafe_allow_html=True)
    box = {"keep": st.success, "settings": st.warning, "service": st.error, "replace": st.error}[res["action"]]
    box(t["act_" + res["action"]])
    for n in res["notes"]:
        st.info(t[n])

    st.markdown(f"**{t['probs']}**")
    for k in L.LABELS:
        st.progress(min(max(res["probs"].get(k, 0.0), 0.0), 1.0),
                    text=f"{t['label_' + k]}: {res['probs'].get(k, 0.0) * 100:.1f}%")
    st.caption(t["src_model"] if res["source"] == "model" else t["src_rules"])

    st.download_button(
        t["download"],
        data=build_report(res, t, lang).encode("utf-8"),
        file_name="dose_report.html",
        mime="text/html",
        help=t["download_help"],
    )


tab_check, tab_log, tab_ref, tab_about = st.tabs([t["tab_check"], t["tab_log"], t["tab_ref"], t["tab_about"]])

# ---------------- مراجعة حالة ----------------
with tab_check:
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown(f"<div class='panel-title'>{escape(t['sec_patient'])}</div>", unsafe_allow_html=True)
        name = st.text_input(t["patient_name"], placeholder=t["patient_name_ph"], max_chars=80)
        c1, c2 = st.columns(2)
        age = c1.number_input(t["age"], min_value=0.0, max_value=float(C.MAX_AGE), value=40.0, step=1.0)
        weight = c2.number_input(t["weight"], min_value=0.0, max_value=300.0, value=70.0, step=1.0)

        st.markdown(f"<div class='panel-title'>{escape(t['sec_exam'])}</div>", unsafe_allow_html=True)
        exam = st.selectbox(t["exam"], EXAM_KEYS, format_func=lambda k: EXAMS[k][lang])
        dose = st.number_input(
            f"{t['dose']} — {EXAMS[exam]['qty_' + lang]} (mGy)",
            min_value=0.0, value=None, format="%.3f", placeholder=t["dose_ph"], key="dose",
        )
        st.caption(t["ref_hint"].format(drl=EXAMS[exam]["drl"]))

        st.markdown(f"<div class='panel-title'>{escape(t['sec_device'])}</div>", unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        device = d1.text_input(t["device_name"], placeholder=t["device_name_ph"], max_chars=40)
        device_age = d2.number_input(t["device_age"], min_value=0.0, max_value=60.0, value=5.0, step=1.0)

        analyze = st.button(t["analyze"], type="primary", use_container_width=True)

    if analyze:
        errors, warns = L.validate(exam, age, weight, dose, device_age)
        if errors:
            st.session_state.result = None
            with left:
                for e in errors:
                    st.error(t[e])
        else:
            label, probs, source = classify(exam, weight, dose)
            ratio = L.dose_ratio(exam, dose, weight)
            dev_key = device.strip().lower()
            prev_high = sum(1 for e in st.session_state.log
                            if dev_key and e["device_key"] == dev_key and e["label"] == "high")
            high_count = prev_high + (1 if label == "high" else 0)
            res = {
                "name": name.strip(), "age": age, "weight": weight, "exam": exam, "dose": dose,
                "device": device.strip(), "device_age": device_age, "label": label, "probs": probs,
                "source": source, "ratio": ratio, "ref": L.reference_limit(exam, weight),
                "action": L.device_action(label, ratio, device_age, high_count),
                "notes": L.extra_notes(label, age, high_count), "warns": warns,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            st.session_state.result = res
            st.session_state.log.append({**res, "device_key": dev_key})

    with right:
        if st.session_state.result:
            render_result(st.session_state.result)

    st.warning(t["disclaimer"])
    st.caption(t["privacy"])

# ---------------- سجل الجلسة ----------------
with tab_log:
    st.markdown(f"<div class='panel-title'>{escape(t['log_title'])}</div>", unsafe_allow_html=True)
    log = st.session_state.log
    if not log:
        st.info(t["log_empty"])
    else:
        df = pd.DataFrame({
            t["log_time"]: [e["time"] for e in log],
            t["log_patient"]: [e["name"] or "-" for e in log],
            t["log_exam"]: [EXAMS[e["exam"]][lang] for e in log],
            t["log_device"]: [e["device"] or "-" for e in log],
            t["log_dose"]: [e["dose"] for e in log],
            t["log_ratio"]: [round(e["ratio"], 2) for e in log],
            t["log_result"]: [t["label_" + e["label"]] for e in log],
        })
        st.dataframe(df, use_container_width=True, hide_index=True)
        dev = pd.DataFrame({"d": [e["device"] or "-" for e in log], "h": [e["label"] == "high" for e in log]})
        summ = dev.groupby("d").agg(total=("h", "size"), high=("h", "sum")).reset_index()
        summ.columns = [t["device_l"], t["dev_total"], t["dev_high"]]
        st.markdown(f"**{t['dev_summary']}**")
        st.dataframe(summ, use_container_width=True, hide_index=True)
        if st.button(t["log_clear"]):
            st.session_state.log = []
            st.session_state.result = None
            st.rerun()

# ---------------- المراجع ----------------
with tab_ref:
    st.markdown(f"<div class='panel-title'>{escape(t['ref_title'])}</div>", unsafe_allow_html=True)
    st.caption(t["ref_note"])
    ref = pd.DataFrame({
        t["ref_exam"]: [EXAMS[k][lang] for k in EXAM_KEYS],
        t["ref_qty"]: [EXAMS[k]["qty_" + lang] for k in EXAM_KEYS],
        t["ref_drl"]: [EXAMS[k]["drl"] for k in EXAM_KEYS],
        t["ref_typ"]: [EXAMS[k]["typical"] for k in EXAM_KEYS],
    })
    st.dataframe(ref, use_container_width=True, hide_index=True)
    st.markdown(f"<div class='panel-title'>{escape(t['rules_title'])}</div>", unsafe_allow_html=True)
    st.markdown("\n".join(f"- {r}" for r in t["rules_text"]))

# ---------------- عن المشروع ----------------
with tab_about:
    st.markdown(f"<div class='panel-title'>{escape(t['about_title'])}</div>", unsafe_allow_html=True)
    st.write(t["about_intro"])
    st.subheader(t["about_how_title"])
    st.markdown("\n".join(f"{i}. {s}" for i, s in enumerate(t["about_how"], 1)))
    st.subheader(t["about_data_title"])
    st.write(t["about_data"])
    st.subheader(t["about_model_title"])
    st.write(t["about_model"])
    meta = model_info()
    if meta:
        st.subheader(t["about_results_title"])
        m1, m2 = st.columns(2)
        m1.metric(t["about_acc"], f"{meta.get('test_accuracy', 0) * 100:.1f}%")
        m2.metric(t["about_val"], f"{meta.get('validation_accuracy', 0) * 100:.1f}%")
    st.subheader(t["about_limits_title"])
    st.markdown("\n".join(f"- {s}" for s in t["about_limits"]))

st.markdown(f"<div class='foot'>{escape(t['footer'])}</div>", unsafe_allow_html=True)
