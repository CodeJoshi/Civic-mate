import html
import os
from pathlib import Path

import requests
import streamlit as st
from PIL import Image

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BASE_DIR = Path(__file__).resolve().parent

LANGUAGES = {
    "Hindi": "हिन्दी",
    "Tamil": "தமிழ்",
    "Telugu": "తెలుగు",
    "Marathi": "मराठी",
    "Bengali": "বাংলা",
    "Kannada": "ಕನ್ನಡ",
    "English": "English",
}

SAMPLE_POLICY = """PM-KISAN (Pradhan Mantri Kisan Samman Nidhi), simplified sample

Income support of ₹6,000 per year is given to eligible landholding farmer families. It is paid in three equal instalments of ₹2,000 directly into the beneficiary's bank account.

Eligible: farmer families who own cultivable land and have an Aadhaar-linked bank account.

Not eligible: institutional landholders, current or former holders of constitutional posts, income tax payers, and registered professionals such as doctors, engineers and lawyers."""

SAMPLE_LOG = [
    ("cm-8921", "PM Kisan Samman Nidhi", "done", "2026-10-31 16:40"),
    ("cm-8922", "State Higher Ed Scholarship", "wait", "2026-10-31 16:52"),
]

st.set_page_config(
    page_title="CivicMate | Find • Apply • Empower",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Styles. The page forces its own light, friendly look so it reads the same
# whether the visitor's Streamlit theme is light or dark.
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;600;700&family=Noto+Sans+Tamil:wght@400;600;700&family=Noto+Sans+Telugu:wght@400;600;700&family=Noto+Sans+Bengali:wght@400;600;700&family=Noto+Sans+Kannada:wght@400;600;700&display=swap');

:root {
    --ink: #14305F;
    --blue: #1F4C9A;
    --blue-dark: #183F80;
    --saffron: #E8871E;
    --green: #1E7A4C;
    --page: #F3F7FC;
    --text: #1B2330;
    --muted: #556079;
    --line: #DAE2EF;
    --line-strong: #B6C3DA;
}

/* ---------- Base: force a light page ---------- */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: var(--page) !important;
    color: var(--text) !important;
}
html, body, .stApp, .stButton button, [data-baseweb="tab"], label, input, textarea,
[data-baseweb="select"], [data-testid="stMarkdownContainer"] {
    font-family: 'Public Sans', 'Noto Sans Devanagari', 'Noto Sans Tamil', 'Noto Sans Telugu',
                 'Noto Sans Bengali', 'Noto Sans Kannada', system-ui, sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stHeader"] *, [data-testid="stToolbar"] * { color: var(--muted) !important; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2.2rem; max-width: 1180px; }

[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
    background: #fff !important;
    border-right: 1px solid var(--line);
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp li, .stApp label { color: var(--text) !important; }
[data-testid="stMarkdownContainer"] p { font-size: 1.04rem; line-height: 1.6; }
[data-testid="stWidgetLabel"] p { font-weight: 600; font-size: 1rem; }
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] * { color: var(--muted) !important; }
hr { border-color: var(--line) !important; }

/* ---------- Inputs ---------- */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
    background: #fff !important;
    border-color: var(--line-strong) !important;
    border-radius: 10px !important;
}
input, textarea { color: var(--text) !important; -webkit-text-fill-color: var(--text) !important; background: #fff !important; }
::placeholder { color: #8791A6 !important; -webkit-text-fill-color: #8791A6 !important; }
[data-baseweb="select"] *, [data-baseweb="select"] svg { color: var(--text) !important; fill: var(--text) !important; }
[data-baseweb="popover"], [data-baseweb="popover"] ul, [data-baseweb="menu"] { background: #fff !important; }
[data-baseweb="popover"] li, [data-baseweb="popover"] li * { color: var(--text) !important; }
[data-testid="stNumberInput"] button { background: var(--page) !important; color: var(--text) !important; }
[data-testid="stFileUploaderDropzone"] {
    background: var(--page) !important;
    border: 1.5px dashed #8FA6CC !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploaderDropzone"] *, [data-testid="stFileUploaderDropzone"] small { color: var(--text) !important; }
[data-testid="stFileUploaderDropzone"] button { background: #fff !important; border: 1px solid var(--line-strong) !important; border-radius: 10px !important; }

/* ---------- Buttons ---------- */
.stButton > button { border-radius: 12px; font-weight: 700; min-height: 3rem; font-size: 1rem; transition: background .15s; }
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {
    background: var(--blue) !important; border: 1px solid var(--blue) !important;
}
.stButton > button[kind="primary"] p, .stButton > button[data-testid="stBaseButton-primary"] p { color: #fff !important; }
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover { background: var(--blue-dark) !important; }
.stButton > button[kind="secondary"], .stButton > button[data-testid="stBaseButton-secondary"] {
    background: #fff !important; border: 1.5px solid var(--line-strong) !important;
}
.stButton > button[kind="secondary"] p, .stButton > button[data-testid="stBaseButton-secondary"] p { color: var(--ink) !important; }
.stButton > button[kind="secondary"]:hover, .stButton > button[data-testid="stBaseButton-secondary"]:hover { background: var(--page) !important; }
.stButton > button:disabled { opacity: .5; }
button:focus-visible, [role="tab"]:focus-visible { outline: 3px solid var(--saffron) !important; outline-offset: 2px; }

/* ---------- Alerts ---------- */
[data-testid^="stAlert"] { background: #fff !important; border-radius: 12px !important; }
[data-testid="stAlert"] { border: 1px solid var(--line); }
[data-testid^="stAlert"] *, [data-testid^="stAlert"] p { color: var(--text) !important; }

/* ---------- Hero ---------- */
.hero {
    position: relative; overflow: hidden;
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 2rem 2rem 1.6rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 10px rgba(20,48,95,.06);
}
.hero::before {
    content: ""; position: absolute; inset: 0 0 auto 0; height: 6px;
    background: linear-gradient(90deg, #E8871E 0 33.33%, #FFFFFF 33.33% 66.66%, #1E7A4C 66.66% 100%);
    border-bottom: 1px solid var(--line);
}
.hero-greet { font-weight: 700; font-size: 1.1rem; color: var(--saffron); }
.hero-title {
    margin-top: .25rem; color: var(--ink); font-weight: 800;
    font-size: clamp(1.7rem, 3.6vw, 2.35rem); line-height: 1.2; letter-spacing: -0.015em; max-width: 24ch;
}
.hero-sub { margin-top: .7rem; max-width: 60ch; line-height: 1.6; color: var(--muted); font-size: 1.05rem; }
.flow { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1.5rem; }
.flow-item {
    display: flex; gap: .8rem; align-items: flex-start;
    background: var(--page); border: 1px solid var(--line); border-radius: 14px; padding: .9rem 1rem;
}
.flow-n {
    flex: 0 0 2rem; height: 2rem; border-radius: 50%; display: grid; place-items: center;
    font-weight: 800; font-size: .95rem;
}
.flow-item:nth-child(1) .flow-n { background: #FFE6C2; color: #7A4300; }
.flow-item:nth-child(2) .flow-n { background: #D6E4FA; color: var(--ink); }
.flow-item:nth-child(3) .flow-n { background: #D3EEDF; color: #14573A; }
.flow-item b { display: block; color: var(--ink); font-size: 1.05rem; }
.flow-item .d { display: block; color: var(--muted); font-size: .92rem; line-height: 1.45; margin-top: .1rem; }
@media (max-width: 760px) { .flow { grid-template-columns: 1fr; } .hero { padding: 1.5rem 1.2rem 1.2rem; } }

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--line-strong); }
.stTabs [data-baseweb="tab"] { height: auto; padding: .8rem 1.3rem; background: transparent !important; }
.stTabs [data-baseweb="tab"] p { font-size: 1.1rem !important; font-weight: 700 !important; color: var(--muted) !important; }
.stTabs [aria-selected="true"] p { color: var(--ink) !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color: var(--saffron) !important; height: 4px; border-radius: 4px 4px 0 0; }
.stTabs [data-baseweb="tab-border"] { display: none; }

/* ---------- Cards ---------- */
[class*="st-key-card_"] {
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 1.5rem 1.5rem 1.3rem;
    box-shadow: 0 2px 8px rgba(20,48,95,.05);
}
.step { display: flex; gap: .8rem; align-items: flex-start; margin: 0 0 1.1rem; }
.step-n {
    flex: 0 0 2rem; height: 2rem; border-radius: 50%;
    background: var(--ink); color: #fff !important; font-weight: 800; font-size: .95rem;
    display: grid; place-items: center;
}
.step-t { font-weight: 800; font-size: 1.2rem; color: var(--ink); line-height: 1.3; }
.step-h { color: var(--muted); font-size: .95rem; margin-top: .15rem; line-height: 1.45; }

/* Results */
.res-title { font-weight: 800; font-size: 1.05rem; margin: .5rem 0 .55rem; color: var(--ink); }
.res-list { list-style: none; padding: 0; margin: 0 0 1.1rem; }
.res-list li {
    position: relative; padding: .7rem .9rem .7rem 2.4rem; margin-bottom: .45rem;
    border: 1px solid var(--line); border-radius: 12px; background: var(--page);
    color: var(--text); line-height: 1.55;
}
.res-list li::before {
    content: ""; position: absolute; left: .95rem; top: 1.15rem;
    width: .55rem; height: .55rem; border-radius: 50%; background: var(--blue);
}
.res-list.good li { background: #EEF8F2; border-color: #CBE8D8; }
.res-list.good li::before {
    content: "✓"; width: auto; height: auto; top: .65rem; left: .9rem;
    background: none; color: var(--green); font-weight: 800;
}

/* Empty state */
.empty { text-align: center; padding: 1.8rem 1rem 1.6rem; color: var(--muted); line-height: 1.55; }
.empty .ico { font-size: 2.4rem; line-height: 1; margin-bottom: .6rem; }
.empty b { display: block; color: var(--ink); font-size: 1.1rem; margin-bottom: .25rem; }
.empty span { display: block; max-width: 34ch; margin: 0 auto; }

/* Approval gate */
.gate {
    border: 1px solid #F0C98A; border-left: 6px solid var(--saffron);
    background: #FFF7E8; color: #5A3A07;
    border-radius: 12px; padding: .9rem 1.1rem; margin: .9rem 0; line-height: 1.55;
}
.gate b { color: #3F2704; }

/* Status pill and badges */
.pill { display: inline-flex; align-items: center; gap: .5rem; padding: .4rem .85rem; border-radius: 999px; font-size: .9rem; font-weight: 700; }
.pill .dot { width: .6rem; height: .6rem; border-radius: 50%; }
.pill-ok   { background: #E3F4EA; color: #14573A; } .pill-ok .dot   { background: #1E7A4C; }
.pill-warn { background: #FFF1D6; color: #6B4308; } .pill-warn .dot { background: #E8871E; }
.pill-bad  { background: #FDE6E6; color: #8A1C1C; } .pill-bad .dot  { background: #C62828; }
.wordmark { font-size: 1.5rem; font-weight: 800; color: var(--ink); }

/* Metrics */
[data-testid="stMetric"] { background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 1rem 1.1rem; }
[data-testid="stMetric"] * { color: var(--text) !important; }
[data-testid="stMetricLabel"] * { color: var(--muted) !important; }
[data-testid="stMetricValue"] * { color: var(--ink) !important; font-weight: 800; }

/* Log table */
.log-wrap { overflow-x: auto; }
.log { width: 100%; border-collapse: separate; border-spacing: 0; background: #fff; border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }
.log th { text-align: left; font-size: .88rem; font-weight: 700; color: var(--muted); background: var(--page); padding: .75rem 1rem; border: 0; }
.log td { padding: .85rem 1rem; border: 0; border-top: 1px solid var(--line); color: var(--text); }
.badge { display: inline-block; padding: .2rem .65rem; border-radius: 999px; font-size: .85rem; font-weight: 700; }
.badge-done { background: #E3F4EA; color: #14573A; }
.badge-wait { background: #FFF1D6; color: #6B4308; }
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def card(key: str):
    """A white rounded card. Falls back to a bordered container on older Streamlit."""
    try:
        return st.container(key=f"card_{key}")
    except TypeError:
        return st.container(border=True)


def step(number: int, title: str, hint: str = "") -> None:
    st.markdown(
        f'<div class="step"><div class="step-n">{number}</div>'
        f'<div><div class="step-t">{html.escape(title)}</div>'
        f'<div class="step-h">{html.escape(hint)}</div></div></div>',
        unsafe_allow_html=True,
    )


def empty_state(icon: str, title: str, body: str) -> None:
    st.markdown(
        f'<div class="empty"><div class="ico">{icon}</div><b>{html.escape(title)}</b>'
        f"<span>{html.escape(body)}</span></div>",
        unsafe_allow_html=True,
    )


def render_list(title: str, items, good: bool = False) -> None:
    if not items:
        return
    lis = "".join(f"<li>{html.escape(str(i))}</li>" for i in items)
    cls = "res-list good" if good else "res-list"
    st.markdown(
        f'<div class="res-title">{html.escape(title)}</div><ul class="{cls}">{lis}</ul>',
        unsafe_allow_html=True,
    )


def log_table(rows) -> None:
    labels = {"done": ("badge-done", "Completed"), "wait": ("badge-wait", "Waiting for approval")}
    head = "".join(f"<th>{h}</th>" for h in ("Session", "Scheme", "Status", "Time"))
    body = ""
    for session, scheme, status, ts in rows:
        cls, label = labels[status]
        body += (
            f"<tr><td>{html.escape(session)}</td><td>{html.escape(scheme)}</td>"
            f'<td><span class="badge {cls}">{label}</span></td><td>{html.escape(ts)}</td></tr>'
        )
    st.markdown(
        f'<div class="log-wrap"><table class="log"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def call_backend(path: str, payload: dict, timeout: int = 90):
    """POST to the backend. Returns (data, error_message)."""
    try:
        r = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, f"We can’t reach the CivicMate server at {BACKEND_URL}. Start the backend and try again."
    except requests.exceptions.Timeout:
        return None, "The server took too long to respond. Please try again in a moment."
    except Exception as e:  # noqa: BLE001
        return None, f"Something went wrong: {e}"


@st.cache_data(ttl=15, show_spinner=False)
def backend_status(url: str) -> str:
    try:
        data = requests.get(f"{url}/health", timeout=3).json()
        return "ok" if data.get("gemini_configured") else "fallback"
    except Exception:  # noqa: BLE001
        return "down"


def render_logo() -> None:
    for name in ("logo.png", "logo.jpg", "logo.jpeg", "logo"):
        path = BASE_DIR / name
        if path.exists():
            try:
                st.image(Image.open(path), use_container_width=True)
                return
            except Exception:  # noqa: BLE001
                continue
    st.markdown('<div class="wordmark">🏛️ CivicMate</div>', unsafe_allow_html=True)


def load_sample() -> None:
    st.session_state["policy_text"] = SAMPLE_POLICY


def reset_application() -> None:
    for key in ("agent", "receipt"):
        st.session_state.pop(key, None)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    render_logo()
    st.caption("")
    st.divider()

    st.markdown("**Server status**")
    pill_class, pill_text = {
        "ok": ("pill-ok", "Connected and ready"),
        "fallback": ("pill-warn", "Offline fallback mode"),
        "down": ("pill-bad", "Server offline"),
    }[backend_status(BACKEND_URL)]
    st.markdown(
        f'<span class="pill {pill_class}"><span class="dot"></span>{pill_text}</span>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.caption(
        "New here? Open the Find tab and choose “Use sample scheme” to see how an "
        "explanation looks, or paste text from an official notification."
    )

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown(
    """
<div class="hero">
    <div class="hero-greet">Namaste </div>
    <div class="hero-title">Get the government benefits you’re entitled to</div>
    <div class="hero-sub">Understand any scheme in your own language, then let CivicMate fill in the application for you. Nothing is submitted until you approve it.</div>
    <div class="flow">
        <div class="flow-item"><div class="flow-n">1</div><div><b>Find</b><span class="d">Read a scheme in plain language, with audio</span></div></div>
        <div class="flow-item"><div class="flow-n">2</div><div><b>Apply</b><span class="d">We fill in the portal form, you check it</span></div></div>
        <div class="flow-item"><div class="flow-n">3</div><div><b>Empower</b><span class="d">Approve, then keep your receipts</span></div></div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

tab_find, tab_apply, tab_empower = st.tabs(["🔍 Find", "📝 Apply", "💪 Empower"])

# ---------------------------------------------------------------------------
# FIND
# ---------------------------------------------------------------------------
with tab_find:
    st.write("")
    col_in, col_out = st.columns(2, gap="large")

    with col_in:
        with card("find_in"):
            step(1, "Tell us about the scheme", "Upload a document or paste its text.")

            language = st.selectbox(
                "Choose Language:",
                list(LANGUAGES),
                format_func=lambda l: l if l == "English" else f"{l} ({LANGUAGES[l]})",
            )
            uploaded = st.file_uploader("Upload a policy PDF or text file", type=["pdf", "txt"])
            st.text_area(
                "Or paste the notification text",
                key="policy_text",
                height=170,
                placeholder="Paste the text of a government notification or circular here…",
            )

            b1, b2 = st.columns([3, 2])
            with b1:
                explain_clicked = st.button("Explain this policy", type="primary", use_container_width=True)
            with b2:
                st.button("Use sample scheme", on_click=load_sample, use_container_width=True)

    with col_out:
        with card("find_out"):
            step(2, "Here’s what it means for you", "Who can apply, what you receive, and an audio summary.")

            if explain_clicked:
                text = st.session_state.get("policy_text", "").strip()
                if not text and uploaded and uploaded.name.lower().endswith(".txt"):
                    text = uploaded.getvalue().decode("utf-8", errors="ignore").strip()

                if not text and uploaded:
                    st.error("We can’t read PDFs yet. Copy the text from the PDF and paste it on the left.")
                elif not text:
                    st.error("Add a policy document or paste its text first.")
                else:
                    with st.spinner(f"Reading the policy and preparing the {language} audio…"):
                        res, err = call_backend("/api/explain", {"text": text, "language": language})
                    if err:
                        st.error(err)
                    else:
                        st.session_state["explain"] = {"res": res, "language": language}

            result = st.session_state.get("explain")
            if result:
                res = result["res"]
                st.caption(f"Explained in {result['language']}")
                criteria = res.get("eligibility_criteria", [])
                benefits = res.get("benefits", [])
                render_list("Who can apply", criteria)
                render_list("What you receive", benefits, good=True)
                if not criteria and not benefits:
                    st.info("We didn’t find eligibility or benefit details in this text. Try a longer excerpt.")
                if res.get("audio_url"):
                    st.markdown('<div class="res-title">Listen to the summary</div>', unsafe_allow_html=True)
                    st.audio(res["audio_url"])
            elif not explain_clicked:
                empty_state(
                    "📄",
                    "Your explanation will appear here",
                    "Add a scheme on the left, or try the sample scheme to see how it works.",
                )

# ---------------------------------------------------------------------------
# APPLY
# ---------------------------------------------------------------------------
with tab_apply:
    st.write("")
    col_form, col_review = st.columns(2, gap="large")

    with col_form:
        with card("apply_in"):
            step(1, "Who is applying?", "We’ll enter these details on the portal for you.")

            st.file_uploader(
                "Upload a document to read details from (optional)",
                type=["png", "jpg", "pdf"],
            )
            user_name = st.text_input("Full name", "Rahul Sharma")
            c1, c2 = st.columns(2)
            with c1:
                user_income = st.number_input("Annual income (₹)", min_value=0, value=120000, step=10000)
            with c2:
                user_state = st.selectbox("State", ["Karnataka", "Maharashtra", "Tamil Nadu", "Delhi"])
            target_url = st.text_input("Application portal address", "https://example.com/demo-portal")

            launch_clicked = st.button("Fill in the application form", type="primary", use_container_width=True)

    with col_review:
        with card("apply_out"):
            step(2, "Check the form, then approve", "Nothing is sent until you say so.")

            if launch_clicked:
                if not user_name.strip():
                    st.error("Enter the applicant’s full name.")
                elif not target_url.strip().lower().startswith(("http://", "https://")):
                    st.error("Enter the portal address starting with http:// or https://.")
                else:
                    reset_application()
                    with st.spinner("Opening the portal and filling in your details. This can take a minute…"):
                        res, err = call_backend(
                            "/api/agent/fill",
                            {
                                "name": user_name.strip(),
                                "income": user_income,
                                "state": user_state,
                                "target_url": target_url.strip(),
                            },
                            timeout=180,
                        )
                    if err:
                        st.error(err)
                    elif "screenshot_path" not in res:
                        st.warning("We finished, but couldn’t show a preview of the form. Please try again.")
                    else:
                        st.session_state["agent"] = res

            agent = st.session_state.get("agent")
            receipt = st.session_state.get("receipt")

            if not agent:
                empty_state(
                    "📝",
                    "Your filled-in form will appear here",
                    "Enter the details on the left and we’ll show you the completed form to check.",
                )
            else:
                st.image(
                    agent["screenshot_path"],
                    caption="The portal form as we filled it in",
                    use_container_width=True,
                )

                if receipt is None:
                    st.markdown(
                        '<div class="gate"><b>Please check before you approve.</b> '
                        "Read every field in the preview. Your application is only submitted when you "
                        "choose Approve and submit.</div>",
                        unsafe_allow_html=True,
                    )
                    a1, a2 = st.columns(2)
                    with a1:
                        approve = st.button(
                            "Approve and submit",
                            type="primary",
                            use_container_width=True,
                            disabled=not agent.get("session_id"),
                        )
                    with a2:
                        discard = st.button("Discard", use_container_width=True)

                    if approve:
                        with st.spinner("Submitting your application…"):
                            res, err = call_backend(
                                "/api/agent/confirm", {"session_id": agent["session_id"]}, timeout=120
                            )
                        if err:
                            st.error(err)
                        else:
                            st.session_state["receipt"] = res or {}
                            st.rerun()
                    if discard:
                        reset_application()
                        st.rerun()
                else:
                    st.success("Your application has been submitted. Keep the receipt below.")
                    if receipt.get("receipt_url"):
                        st.image(receipt["receipt_url"], caption="Submission receipt", use_container_width=True)
                    st.button("Start a new application", on_click=reset_application, use_container_width=True)

# ---------------------------------------------------------------------------
# EMPOWER
# ---------------------------------------------------------------------------
with tab_empower:
    st.write("")
    step(1, "How CivicMate is helping", "A quick summary of the assistant’s work.")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Schemes processed", "100%")
        st.caption("Rules verified")
    with m2:
        st.metric("Average run time", "1.4 min")
        st.caption("Per application")
    with m3:
        st.metric("Your approval", "Always asked")
        st.caption("Before every submission")
    with m4:
        st.metric("Languages", "6")
        st.caption("With audio summaries")

    st.write("")
    step(2, "Your applications and receipts", "Every submission is logged here.")
    log_table(SAMPLE_LOG)
    st.caption("Sample data shown for demonstration.")  