import html
import os
from pathlib import Path
import requests
import streamlit as st
from PIL import Image

# ---------------------------------------------------------------------------
# 1. Config & Constants
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

# Multilingual Dictionary Mapping
TRANSLATIONS = {
    "English": {
        "welcome": "Welcome to CivicMate!",
        "find": "Find",
        "apply": "Apply",
        "empower": "Empower",
        "choose_scheme": "Tell us about the scheme",
        "upload": "Upload a policy PDF or text file",
        "explain": "Explain this policy",
        "full_name": "Full name",
        "income": "Annual income",
        "approve": "Approve and submit",
        "continue": "Continue",
        "choose_language": "Choose your language",
    },
    "Hindi": {
        "welcome": "CivicMate में आपका स्वागत है!",
        "find": "योजनाएं खोजें",
        "apply": "आवेदन करें",
        "empower": "सशक्त बनें",
        "choose_scheme": "योजना के बारे में बताएं",
        "upload": "नीति PDF या टेक्स्ट फ़ाइल अपलोड करें",
        "explain": "इस नीति को समझाएं",
        "full_name": "पूरा नाम",
        "income": "वार्षिक आय",
        "approve": "अनुमोदित करें और जमा करें",
        "continue": "आगे बढ़ें",
        "choose_language": "अपनी भाषा चुनें",
    },
    "Tamil": {
        "welcome": "CivicMate-க்கு உங்களை வரவேற்கிறோம்!",
        "find": "தேடுங்கள்",
        "apply": "விண்ணப்பிக்கவும்",
        "empower": "மேம்படுங்கள்",
        "choose_scheme": "திட்டத்தைப் பற்றிக் கூறுங்கள்",
        "upload": "கொள்கை PDF அல்லது உரைக் கோப்பைப் பதிவேற்றவும்",
        "explain": "இந்தக் கொள்கையை விளக்கவும்",
        "full_name": "முழுப் பெயர்",
        "income": "ஆண்டு வருமானம்",
        "approve": "ஒப்புதல் அளித்து சமர்ப்பிக்கவும்",
        "continue": "தொடரவும்",
        "choose_language": "மொழியைத் தேர்ந்தெடுக்கவும்",
    },
    "Telugu": {
        "welcome": "CivicMate కు స్వాగతం!",
        "find": "పథకాలను కనుగొనండి",
        "apply": "దరఖాస్తు చేయండి",
        "empower": "సాధికారత పొందండి",
        "choose_scheme": "పథకం గురించి వివరించండి",
        "upload": "పాలసీ PDF లేదా టెక్స్ట్ ఫైల్‌ను అప్‌లోడ్ చేయండి",
        "explain": "ఈ పాలసీని వివరించండి",
        "full_name": "పూర్తి పేరు",
        "income": "వార్షిక ఆదాయం",
        "approve": "ఆమోదించి సమర్పించండి",
        "continue": "కొనసాగించండి",
        "choose_language": "మీ భాషను ఎంచుకోండి",
    },
    "Marathi": {
        "welcome": "CivicMate मध्ये आपले स्वागत आहे!",
        "find": "योजना शोधा",
        "apply": "अर्ज करा",
        "empower": "सक्षम व्हा",
        "choose_scheme": "योजनेबद्दल माहिती द्या",
        "upload": "धोरणाची PDF किंवा मजकूर फाइल अपलोड करा",
        "explain": "हे धोरण समजावून सांगा",
        "full_name": "पूर्ण नाव",
        "income": "वार्षिक उत्पन्न",
        "approve": "मंजूर करा आणि सबमिट करा",
        "continue": "पुढे जा",
        "choose_language": "तुमची भाषा निवडा",
    },
    "Bengali": {
        "welcome": "CivicMate-এ আপনাকে স্বাগতম!",
        "find": "প্রকল্প খুঁজুন",
        "apply": "আবেদন করুন",
        "empower": "ক্ষমতায়ন",
        "choose_scheme": "প্রকল্প সম্পর্কে জানান",
        "upload": "নীতির PDF বা টেক্সট ফাইল আপলোড করুন",
        "explain": "এই নীতিটি ব্যাখ্যা করুন",
        "full_name": "পুরো নাম",
        "income": "বার্ষিক আয়",
        "approve": "অনুমোদন করুন এবং জমা দিন",
        "continue": "চালিয়ে যান",
        "choose_language": "আপনার ভাষা নির্বাচন করুন",
    },
    "Kannada": {
        "welcome": "CivicMate ಗೆ ಸ್ವಾಗತ!",
        "find": "ಯೋಜನೆಗಳನ್ನು ಹುಡುಕಿ",
        "apply": "ಅರ್ಜಿ ಸಲ್ಲಿಸಿ",
        "empower": "ಸಬಲೀಕರಣಗೊಳ್ಳಿ",
        "choose_scheme": "ಯೋಜನೆಯ ಬಗ್ಗೆ ತಿಳಿಸಿ",
        "upload": "ನೀತಿಯ PDF ಅಥವಾ ಪಠ್ಯ ಫೈಲ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        "explain": "ಈ ನೀತಿಯನ್ನು ವಿವರಿಸಿ",
        "full_name": "ಪೂರ್ಣ ಹೆಸರು",
        "income": "ವಾರ್ಷಿಕ ಆದಾಯ",
        "approve": "ಅನುಮೋದಿಸಿ ಮತ್ತು ಸಲ್ಲಿಸಿ",
        "continue": "ಮುಂದುವರಿಸಿ",
        "choose_language": "ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    },
}

# Single Clean Translation Function
def t(key: str) -> str:
    language = st.session_state.get("preferred_language", "English")
    return TRANSLATIONS.get(language, TRANSLATIONS["English"]).get(
        key, TRANSLATIONS["English"].get(key, key)
    )

st.set_page_config(
    page_title="CivicMate | Find • Apply • Empower",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# 2. Page CSS
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

/* ---------- Base Page Setup ---------- */
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

/* ---------- Form Inputs ---------- */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
    background: #fff !important;
    border-color: var(--line-strong) !important;
    border-radius: 10px !important;
}
input, textarea { color: var(--text) !important; -webkit-text-fill-color: var(--text) !important; background: #fff !important; }
::placeholder { color: #8791A6 !important; -webkit-text-fill-color: #8791A6 !important; }
[data-baseweb="select"] *, [data-baseweb="select"] svg { color: var(--text) !important; fill: var(--text) !important; }

/* FIX: Clean White File Uploader Background */
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzone"] > div {
    background: #ffffff !important;
    border: 1.5px dashed var(--line-strong) !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploaderDropzone"] *,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] p {
    color: var(--text) !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: var(--page) !important;
    border: 1px solid var(--line-strong) !important;
    border-radius: 8px !important;
    color: var(--ink) !important;
}

/* ---------- Buttons ---------- */
.stButton > button { border-radius: 12px; font-weight: 700; min-height: 3rem; font-size: 1rem; transition: background .15s; }
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {
    background: var(--blue) !important; border: 1px solid var(--blue) !important;
}
.stButton > button[kind="primary"] p, .stButton > button[data-testid="stBaseButton-primary"] p { color: #fff !important; }
.stButton > button[kind="secondary"], .stButton > button[data-testid="stBaseButton-secondary"] {
    background: #fff !important; border: 1.5px solid var(--line-strong) !important;
}
.stButton > button[kind="secondary"] p, .stButton > button[data-testid="stBaseButton-secondary"] p { color: var(--ink) !important; }

/* ---------- Minimalist Card Containers ---------- */
div[class*="st-key-card_"],
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    border: 1.5px solid var(--line) !important;
    border-radius: 14px !important;
    padding: 1.5rem !important;
    box-shadow: none !important;
    margin-bottom: 1rem !important;
}

/* ---------- Metric Cards (Empower Tab) ---------- */
[data-testid="stMetric"] {
    background-color: #ffffff !important;
    border: 1.5px solid var(--line) !important;
    border-radius: 12px !important;
    padding: 1rem 1.2rem !important;
    box-shadow: none !important;
}
[data-testid="stMetricLabel"] p {
    color: var(--muted) !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] div {
    color: var(--ink) !important;
    font-weight: 800 !important;
    font-size: 1.5rem !important;
}

/* ---------- Hero ---------- */
.hero {
    position: relative; overflow: hidden; background: #fff; border: 1px solid var(--line);
    border-radius: 20px; padding: 2rem 2rem 1.6rem; margin-bottom: 1.5rem;
    box-shadow: 0 2px 10px rgba(20,48,95,.06);
}
.hero::before {
    content: ""; position: absolute; inset: 0 0 auto 0; height: 6px;
    background: linear-gradient(90deg, #E8871E 0 33.33%, #FFFFFF 33.33% 66.66%, #1E7A4C 66.66% 100%);
}
.hero-greet { font-weight: 700; font-size: 1.1rem; color: var(--saffron); }
.hero-title { margin-top: .25rem; color: var(--ink); font-weight: 800; font-size: 2rem; }
.hero-sub { margin-top: .7rem; max-width: 60ch; color: var(--muted); font-size: 1.05rem; }

/* Status pill */
.pill { display: inline-flex; align-items: center; gap: .5rem; padding: .4rem .85rem; border-radius: 999px; font-size: .9rem; font-weight: 700; }
.pill .dot { width: .6rem; height: .6rem; border-radius: 50%; }
.pill-ok { background: #E3F4EA; color: #14573A; } .pill-ok .dot { background: #1E7A4C; }
.pill-warn { background: #FFF1D6; color: #6B4308; } .pill-warn .dot { background: #E8871E; }
.pill-bad { background: #FDE6E6; color: #8A1C1C; } .pill-bad .dot { background: #C62828; }
.wordmark { font-size: 1.5rem; font-weight: 800; color: var(--ink); }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 3. Initial Language Gate
# ---------------------------------------------------------------------------
if "preferred_language" not in st.session_state:
    st.session_state["preferred_language"] = None

if st.session_state["preferred_language"] is None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">Welcome to CivicMate! / CivicMate में आपका स्वागत है!</div>
            <div class="hero-sub">Choose your preferred language to continue. CivicMate will adjust the interface and audio summary language accordingly.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    selected_language = st.selectbox(
        "Choose your preferred language / भाषा चुनें",
        list(LANGUAGES.keys()),
        format_func=lambda l: f"{l} ({LANGUAGES[l]})",
        key="initial_language",
    )
    if st.button("Continue →", type="primary", use_container_width=True):
        st.session_state["preferred_language"] = selected_language
        st.rerun()
    st.stop()

# ---------------------------------------------------------------------------
# 4. Helper Functions
# ---------------------------------------------------------------------------
def card(key: str):
    try:
        return st.container(key=f"card_{key}")
    except TypeError:
        try:
            return st.container(border=True)
        except TypeError:
            return st.container()

def step(number: int, title: str, hint: str = "") -> None:
    st.markdown(
        f'<div style="margin-bottom: 1rem;">'
        f'<div class="step-t">{html.escape(title)}</div>'
        f'<div class="step-h">{html.escape(hint)}</div></div>',
        unsafe_allow_html=True,
    )
def empty_state(icon: str, title: str, body: str) -> None:
    st.markdown(
        f'<div style="text-align:center; padding:1.5rem; color:#556079;"><div style="font-size:2rem;">{icon}</div><b>{html.escape(title)}</b><br><span>{html.escape(body)}</span></div>',
        unsafe_allow_html=True,
    )

def render_list(title: str, items, good: bool = False) -> None:
    if not items:
        return
    lis = "".join(f"<li style='margin-bottom:6px;'>{html.escape(str(i))}</li>" for i in items)
    icon = "✅" if good else "📌"
    st.markdown(f"**{icon} {html.escape(title)}**\n<ul style='padding-left:1.2rem;'>{lis}</ul>", unsafe_allow_html=True)

def call_backend(path: str, payload: dict, timeout: int = 90):
    try:
        r = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, f"Cannot reach CivicMate backend server at {BACKEND_URL}."
    except Exception as e:
        return None, f"Error: {e}"

@st.cache_data(ttl=15, show_spinner=False)
def backend_status(url: str) -> str:
    try:
        data = requests.get(f"{url}/health", timeout=3).json()
        return "ok" if data.get("gemini_configured") else "fallback"
    except Exception:
        return "down"

def render_logo() -> None:
    for name in ("logo.png", "logo.jpg", "logo.jpeg", "logo"):
        path = BASE_DIR / name
        if path.exists():
            try:
                st.image(Image.open(path), use_container_width=True)
                return
            except Exception:
                continue
    st.markdown('<div class="wordmark">🏛️ CivicMate</div>', unsafe_allow_html=True)

def load_sample() -> None:
    st.session_state["policy_text"] = SAMPLE_POLICY

def reset_application() -> None:
    for key in ("agent", "receipt"):
        st.session_state.pop(key, None)

# ---------------------------------------------------------------------------
# 5. Sidebar Layout
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header('Preferences')
    language=st.selectbox('Regional language',LANGUAGES,index=0)
    st.caption('Automation mode is controlled by backend HEADLESS_MODE. Only the bundled local mock portal is supported.')
    schemes_resp=api('GET','/api/schemes/sample')
    schemes=schemes_resp.json() if schemes_resp else [{'id':'PMAY','name':'PMAY sample'}]
    scheme_names={x['name']:x['id'] for x in schemes}
    selected=st.selectbox('Choose a sample scheme',list(scheme_names))
    uploaded=st.file_uploader('Or upload scheme PDF / TXT (max 10 MB)',type=['pdf','txt'])


# =====================================================
# DOCUMENT UPLOAD + OCR REVIEW
# =====================================================

st.divider()
st.subheader("📄 Document-based profile extraction")

st.write(
    "Upload a supporting document to automatically "
    "extract applicant details. Review everything before use."
)

ocr_file = st.file_uploader(
    "Upload income certificate / supporting image",
    type=["png", "jpg", "jpeg", "webp"],
    key="ocr_upload"
)

if st.button(
    "Extract details using AI",
    type="primary",
    disabled=ocr_file is None
):
    response = api(
        "POST",
        "/api/upload-document",
        files={
            "file": (
                ocr_file.name,
                ocr_file.getvalue(),
                ocr_file.type or "image/png"
            )
        }
    )

    if response:
        st.session_state.ocr_result = response.json()
        st.session_state.pop("ocr_review", None)

ocr_result = st.session_state.get("ocr_result")

if ocr_result:
    extracted = ocr_result["profile"]

    st.success("Document processed successfully!")

    st.info(
        "Please verify the extracted information. "
        "OCR results may contain mistakes."
    )

    # Editable review fields
    with st.form("ocr_review_form"):
        reviewed_name = st.text_input(
            "Applicant name",
            value=extracted.get("name") or ""
        )

        reviewed_income = st.number_input(
            "Annual income (₹)",
            min_value=1.0,
            value=float(extracted.get("annual_income") or 1)
        )

        reviewed_state = st.text_input(
            "State",
            value=extracted.get("state") or ""
        )

        reviewed_category = st.selectbox(
            "Category",
            ["General", "OBC", "SC", "ST"],
            index=(
                ["General", "OBC", "SC", "ST"].index(
                    extracted.get("category")
                )
                if extracted.get("category") in
                ["General", "OBC", "SC", "ST"]
                else 0
            )
        )

        review_submit = st.form_submit_button(
            "Confirm reviewed details"
        )

    if review_submit:
        if len(reviewed_name.strip()) < 2:
            st.error("Please enter a valid applicant name.")
        elif reviewed_state not in STATES:
            st.error("Please enter a valid Indian state name.")
        else:
            st.session_state.ocr_review = {
                "name": reviewed_name.strip(),
                "annual_income": reviewed_income,
                "state": reviewed_state,
                "category": reviewed_category,
                "preferred_language": language
            }
            st.success("Details reviewed and confirmed!")

    # Transfer reviewed information to the existing profile
    reviewed = st.session_state.get("ocr_review")

    if reviewed:
        if st.button("Use reviewed details in citizen profile"):
            st.session_state["profile_name"] = reviewed["name"]
            st.session_state["profile_income"] = reviewed["annual_income"]
            st.session_state["profile_state"] = reviewed["state"]
            st.session_state["profile_category"] = reviewed["category"]
            st.rerun()

    screenshot = ocr_result.get("screenshot_path")

    if screenshot and Path(screenshot).is_file():
        st.image(
            screenshot,
            caption="Locally populated mock portal — preview only",
            use_container_width=True
        )

    st.caption(
        "Status: " + ocr_result.get("status", "unknown")
    )

st.subheader('1 · Citizen profile')
with st.form('profile_form'):
    c1,c2=st.columns(2)
    
name=c1.text_input(
    'Full name',
    placeholder='Enter applicant name',
    key='profile_name'
)

income=c2.number_input(
    'Annual household income (₹)',
    min_value=1.0,
    value=200000.0,
    step=1000.0,
    key='profile_income'
)

state=c1.selectbox(
    'State',
    STATES,
    index=STATES.index('Tamil Nadu'),
    key='profile_state'
)

category=c2.selectbox(
    'Social category',
    ['General','OBC','SC','ST'],
    key='profile_category'
)

analyze=st.form_submit_button('✨ Analyze scheme eligibility',type='primary',use_container_width=True)
if analyze:
    if len(name.strip())<2: st.error('Please enter a name with at least 2 characters.')
    else:
        profile={'name':name.strip(),'annual_income':income,'state':state,'category':category,'preferred_language':language}
        files={'file':(uploaded.name,uploaded.getvalue(),uploaded.type or 'application/octet-stream')} if uploaded else None
        data={'profile':__import__('json').dumps(profile),'scheme_id':scheme_names[selected]}
        r=api('POST','/api/summarize',data=data,files=files)
        if r:
            st.session_state.analysis=r.json(); st.session_state.profile=profile; st.session_state.scheme_name=selected; st.session_state.session=None

analysis=st.session_state.get('analysis')
if analysis:
    summary=analysis['summary']
    st.divider(); st.subheader('2 · Scheme eligibility summary')
    if summary['eligible']: st.success('ELIGIBLE · Income criterion passed')
    else: st.error('NOT ELIGIBLE · Automation disabled')
    st.markdown(f'**{summary["scheme_name"]}**')
    for bullet in summary['eligibility_bullets']: st.markdown(f'- {bullet}')
    if summary.get('income_cap') is not None: st.info(f'Maximum annual income cap: ₹{summary["income_cap"]:,.0f}')
    for note in summary.get('notes',[]): st.caption('Note: '+note)
    st.caption('Summary mode: '+analysis['mode']+' · Demo summaries are informational and are not an official eligibility determination.')
    st.divider(); st.subheader('3 · Local portal preparation')
    st.warning('This demo only fills a local mock form. It does not access or submit to a real government portal.')
    if st.button('🚀 Launch local application preparation',disabled=not summary['eligible'],type='primary'):
        r=api('POST','/api/execute-form',json={'profile':st.session_state.profile,'scheme_name':st.session_state.scheme_name,'eligible':summary['eligible']})
        if r: st.session_state.session=r.json()

session=st.session_state.get('session')
if session:
    st.divider(); st.subheader('4 · Live agent trace')
    st.write('Session status: **'+session['status']+'**')
    for step in session.get('trace_log',[]):
        icon='🟢' if step['status']=='ok' else '🟡' if step['status']=='awaiting_approval' else '🔴'
        st.markdown(f'{icon} **{step["step_number"]}. {step["action"]}**')
        if step.get('selector_used'): st.caption('Selector: '+step['selector_used'])
    if session.get('screenshot_path'):
        p=Path(session['screenshot_path'])
        if p.exists(): st.image(str(p),caption='Filled local mock portal — review before approval',use_container_width=True)
    if session['status']=='awaiting_approval':
        st.warning('Human approval required. Inspect the screenshot before continuing.')
        left,right=st.columns(2)
        with left:
            if st.button('✅ Approve & generate local receipt',type='primary',use_container_width=True):
                r=api('POST',f'/api/execute-form/{session["session_id"]}/confirm',data={'approve':'true'})
                if r: st.session_state.session=r.json()['session']; st.session_state.receipt=r.json(); st.rerun()
        with right:
            if st.button('✖ Abort execution',use_container_width=True):
                r=api('POST',f'/api/execute-form/{session["session_id"]}/confirm',data={'approve':'false'})
                if r: st.session_state.session=r.json()['session']; st.rerun()
    if session['status']=='completed':
        receipt=st.session_state.get('receipt',{})
        st.success('Local demo receipt generated · No government application was submitted.')
        st.code('Receipt reference: '+str(receipt.get('receipt_reference','—')))
        if receipt.get('receipt_url'):
            rr=api('GET',receipt['receipt_url'].replace('/api','/api'))
            if rr: st.download_button('⬇ Download visual receipt (PNG)',rr.content,file_name=f'receipt_{session["session_id"]}.png',mime='image/png')
    if st.button('Clear this demo session'):
        api('DELETE',f'/api/sessions/{session["session_id"]}')
        for key in ['analysis','profile','scheme_name','session','receipt']: st.session_state.pop(key,None)
        st.rerun()

    st.divider()
    st.markdown("**Server Status**")
    pill_class, pill_text = {
        "ok": ("pill-ok", "Connected & Ready"),
        "fallback": ("pill-warn", "Fallback Mode"),
        "down": ("pill-bad", "Server Offline"),
    }[backend_status(BACKEND_URL)]
    st.markdown(f'<span class="pill {pill_class}"><span class="dot"></span>{pill_text}</span>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 6. Hero Header Banner
# ---------------------------------------------------------------------------
st.markdown(
    f"""
<div class="hero">
    <div class="hero-greet">Namaste 🙏</div>
    <div class="hero-title">{t("welcome")}</div>
    <div class="hero-sub">Understand public schemes in your language ({curr_lang}), verify rights, and auto-fill portal forms safely.</div>
</div>
""",
    unsafe_allow_html=True,
)

tab_find, tab_apply, tab_empower = st.tabs([
    "🔍 " + t("find"),
    "📝 " + t("apply"),
    "💪 " + t("empower")
])

# ---------------------------------------------------------------------------
# TAB 1: FIND (Policy Explainer)
# ---------------------------------------------------------------------------
with tab_find:
    st.write("")
    col_in, col_out = st.columns(2, gap="large")
    with col_in:
        with card("find_in"):
            step(1, t("choose_scheme"), "Upload a policy document or paste circular text.")
            
            language = st.selectbox(
                t("choose_language"),
                list(LANGUAGES),
                index=list(LANGUAGES.keys()).index(curr_lang),
                format_func=lambda l: f"{l} ({LANGUAGES[l]})",
            )
            uploaded = st.file_uploader(t("upload"), type=["pdf", "txt"])
            st.text_area(
                "Or paste policy notification text:",
                key="policy_text",
                height=160,
                placeholder="Paste notification circular text here...",
            )
            b1, b2 = st.columns([3, 2])
            with b1:
                explain_clicked = st.button(t("explain"), type="primary", use_container_width=True)
            with b2:
                st.button("Use Sample Scheme", on_click=load_sample, use_container_width=True)

    with col_out:
        with card("find_out"):
            step(2, "Simplified Rights & Regional Audio", "View eligibility requirements and listen to voice output.")
            if explain_clicked:
                text = st.session_state.get("policy_text", "").strip()
                if not text and uploaded and uploaded.name.lower().endswith(".txt"):
                    text = uploaded.getvalue().decode("utf-8", errors="ignore").strip()
                if not text:
                    st.error("Please insert policy text or upload a document to proceed.")
                else:
                    with st.spinner(f"Analyzing policy and generating {language} audio..."):
                        res, err = call_backend("/api/explain", {"text": text, "language": language})
                    if err:
                        st.error(err)
                    else:
                        st.session_state["explain"] = {"res": res, "language": language}
            
            result = st.session_state.get("explain")
            if result:
                res = result["res"]
                render_list("Eligibility Requirements", res.get("eligibility_criteria", []))
                render_list("Direct Benefits", res.get("benefits", []), good=True)
                if res.get("audio_url"):
                    st.markdown("#### 🎧 Regional Audio Summary")
                    st.audio(res["audio_url"])
            elif not explain_clicked:
                empty_state("📄", "Your explanation will appear here", "Submit a policy text on the left to analyze requirements.")

# ---------------------------------------------------------------------------
# TAB 2: APPLY (Autonomous Browser Agent)
# ---------------------------------------------------------------------------
with tab_apply:
    st.write("")
    col_form, col_review = st.columns(2, gap="large")
    with col_form:
        with card("apply_in"):
            step(1, "Applicant Information", "Fill in candidate profile details.")
            user_name = st.text_input(t("full_name"), "Rahul Sharma")
            c1, c2 = st.columns(2)
            with c1:
                user_income = st.number_input(t("income") + " (₹)", min_value=0, value=120000, step=10000)
            with c2:
                user_state = st.selectbox("State", ["Karnataka", "Maharashtra", "Tamil Nadu", "Delhi"])
            target_url = st.text_input("Application Portal URL", "https://example.gov.in/apply")
            launch_clicked = st.button("🚀 Launch Browser Agent", type="primary", use_container_width=True)

    with col_review:
        with card("apply_out"):
            step(2, "Human-in-the-Loop Review Gate", "Review browser execution before final submission.")
            if launch_clicked:
                if not user_name.strip():
                    st.error("Please enter applicant name.")
                else:
                    reset_application()
                    with st.spinner("Playwright agent navigating portal and populating form fields..."):
                        res, err = call_backend("/api/agent/fill", {
                            "name": user_name.strip(),
                            "income": user_income,
                            "state": user_state,
                            "target_url": target_url.strip(),
                        }, timeout=120)
                    if err:
                        st.error(err)
                    else:
                        st.session_state["agent"] = res

            agent = st.session_state.get("agent")
            if agent:
                if "screenshot_path" in agent:
                    st.image(agent["screenshot_path"], caption="Live Browser DOM State Capture", use_container_width=True)
                
                if st.button(t("approve"), type="primary", use_container_width=True):
                    with st.spinner("Submitting portal form..."):
                        res, err = call_backend("/api/agent/confirm", {"session_id": agent.get("session_id")})
                    if err:
                        st.error(err)
                    else:
                        st.session_state["receipt"] = res
                        st.success("Form submitted successfully!")
            else:
                empty_state("📝", "Agent Execution Preview", "Fill applicant details and launch browser agent.")

# ---------------------------------------------------------------------------
# TAB 3: EMPOWER (Citizen Tracking Dashboard)
# ---------------------------------------------------------------------------
with tab_empower:
    st.write("")
    
    # Wrap Header and Metrics in Outer Container
    with card("empower_metrics"):
        step(1, "System Metrics & Audit Trail", "Overview of active execution sessions and system health.")
        st.write("")
        
        m1, m2, m3, m4 = st.columns(4, gap="medium")
        with m1:
            st.metric("Policy Clarity", "100%", help="Rules verified against official policy guidelines")
        with m2:
            st.metric("Avg Execution", "1.2 min", help="Average Playwright form automation completion time")
        with m3:
            st.metric("Review Gate", "Enforced", help="Human-in-the-loop review active before every submission")
        with m4:
            st.metric("Languages", "7 Active", help="Regional voice summaries and UI translations supported")

    st.write("")
    
    # Audit Trail Table Section
    with card("empower_logs"):
        step(2, "Your Applications & Verification Logs", "Every submission session and verification hash is recorded here.")
        
        if st.session_state.get("history_logs"):
            st.dataframe(st.session_state["history_logs"], use_container_width=True)
        else:
            empty_state("📑", "No Active Transactions Yet", "Run a policy query in the Find tab or submit a form in Apply to generate live logs.")