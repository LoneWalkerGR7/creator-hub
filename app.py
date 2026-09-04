import datetime
import hashlib
import json
import os
import urllib.parse
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# ==========================================
# ΕΝΣΩΜΑΤΩΜΕΝΟ YOUTUBE DATA API KEY
# ==========================================
YOUTUBE_API_KEY = "AIzaSyCf5YtVQBxrBAU1If2N2CJATtvOAjXk8PY"

# ==========================================
# ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ
# ==========================================
st.set_page_config(
    page_title="Video Creator Hub & Competitor Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# ULTRA HIGH CONTRAST & BOLD CSS
# ==========================================
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
    background-color: #0b0f19 !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(168, 85, 247, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(59, 130, 246, 0.15) 0px, transparent 50%) !important;
    background-attachment: fixed !important;
    color: #ffffff !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111827 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* ========================================================
   1. ΜΕΝΟΥ ΚΑΡΤΕΛΩΝ: ΦΩΤΕΙΝΟ ΘΑΛΑΣΣΙ & BOLD
   ======================================================== */
[data-testid="stTabs"] [data-baseweb="tab-list"],
div[role="tablist"] {
    display: flex !important;
    flex-wrap: wrap !important;
    overflow: visible !important;
    overflow-x: visible !important;
    white-space: normal !important;
    justify-content: center !important;
    gap: 8px !important;
    background: rgba(21, 28, 44, 0.85) !important;
    padding: 12px !important;
    border-radius: 16px !important;
    border: 1px solid rgba(56, 189, 248, 0.25) !important;
    backdrop-filter: blur(14px) !important;
    width: 100% !important;
    margin-bottom: 25px !important;
}

[data-testid="stTabs"] button[aria-label="Scroll right"],
[data-testid="stTabs"] button[aria-label="Scroll left"],
[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"] {
    display: none !important;
}

/* Έντονα Θαλασσί Γράμματα (Bold 700) */
button[data-baseweb="tab"] {
    background: rgba(13, 19, 34, 0.6) !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
    padding: 10px 16px !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    flex: 0 1 auto !important;
    transition: all 0.2s ease !important;
}

button[data-baseweb="tab"] p, 
button[data-baseweb="tab"] span, 
button[data-baseweb="tab"] div,
button[data-baseweb="tab"] {
    color: #38bdf8 !important; /* ΦΩΤΕΙΝΟ ΘΑΛΑΣΣΙ */
    font-weight: 700 !important;
    opacity: 1 !important;
    text-shadow: 0 1px 3px rgba(0,0,0,0.8) !important;
}

button[data-baseweb="tab"]:hover {
    background: rgba(56, 189, 248, 0.2) !important;
    border-color: #38bdf8 !important;
    transform: translateY(-1px) !important;
}
button[data-baseweb="tab"]:hover p {
    color: #ffffff !important;
}

/* Χρώματα Active Tabs */
button[data-baseweb="tab"]:nth-of-type(1)[aria-selected="true"] { background: linear-gradient(135deg, #2e1065 0%, #a855f7 100%) !important; border-color: #c084fc !important; box-shadow: 0 4px 14px rgba(168, 85, 247, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(2)[aria-selected="true"] { background: linear-gradient(135deg, #450a0a 0%, #ef4444 100%) !important; border-color: #fca5a5 !important; box-shadow: 0 4px 14px rgba(239, 68, 68, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(3)[aria-selected="true"] { background: linear-gradient(135deg, #4c0519 0%, #f43f5e 100%) !important; border-color: #fecdd3 !important; box-shadow: 0 4px 14px rgba(244, 63, 94, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(4)[aria-selected="true"] { background: linear-gradient(135deg, #500724 0%, #ec4899 100%) !important; border-color: #fbcfe8 !important; box-shadow: 0 4px 14px rgba(236, 72, 153, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(5)[aria-selected="true"] { background: linear-gradient(135deg, #083344 0%, #06b6d4 100%) !important; border-color: #a5f3fc !important; box-shadow: 0 4px 14px rgba(6, 182, 212, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(6)[aria-selected="true"] { background: linear-gradient(135deg, #172554 0%, #3b82f6 100%) !important; border-color: #bfdbfe !important; box-shadow: 0 4px 14px rgba(59, 130, 246, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(7)[aria-selected="true"] { background: linear-gradient(135deg, #022c22 0%, #10b981 100%) !important; border-color: #a7f3d0 !important; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(8)[aria-selected="true"] { background: linear-gradient(135deg, #431407 0%, #f97316 100%) !important; border-color: #fed7aa !important; box-shadow: 0 4px 14px rgba(249, 115, 22, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(9)[aria-selected="true"] { background: linear-gradient(135deg, #1e1b4b 0%, #6366f1 100%) !important; border-color: #c7d2fe !important; box-shadow: 0 4px 14px rgba(99, 102, 241, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(10)[aria-selected="true"] { background: linear-gradient(135deg, #083344 0%, #22d3ee 100%) !important; border-color: #a5f3fc !important; box-shadow: 0 4px 14px rgba(34, 211, 238, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(11)[aria-selected="true"] { background: linear-gradient(135deg, #422006 0%, #ca8a04 100%) !important; border-color: #fef08a !important; box-shadow: 0 4px 14px rgba(202, 138, 4, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(12)[aria-selected="true"] { background: linear-gradient(135deg, #4c0519 0%, #e11d48 100%) !important; border-color: #fecdd3 !important; box-shadow: 0 4px 14px rgba(225, 29, 72, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(13)[aria-selected="true"] { background: linear-gradient(135deg, #312e81 0%, #4f46e5 100%) !important; border-color: #818cf8 !important; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(14)[aria-selected="true"] { background: linear-gradient(135deg, #831843 0%, #db2777 100%) !important; border-color: #f472b6 !important; box-shadow: 0 4px 14px rgba(219, 39, 119, 0.6) !important; }

button[data-baseweb="tab"][aria-selected="true"] p,
button[data-baseweb="tab"][aria-selected="true"] span {
    color: #ffffff !important;
    font-weight: 800 !important;
}

/* ========================================================
   2. METRICS DASHBOARD: ΚΑΤΑΛΕΥΚΟΙ ΑΡΙΘΜΟΙ & ΘΑΛΑΣΣΙ ΤΙΤΛΟΙ
   ======================================================== */
[data-testid="stMetric"] {
    background: #151c2c !important;
    border: 1px solid rgba(56, 189, 248, 0.25) !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {
    color: #38bdf8 !important; /* ΘΑΛΑΣΣΙ ΤΙΤΛΟΣ */
    font-weight: 700 !important;
    font-size: 0.95rem !important;
}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: #ffffff !important; /* ΚΑΤΑΛΕΥΚΟΣ ΜΕΓΑΛΟΣ ΑΡΙΘΜΟΣ */
    font-weight: 800 !important;
    font-size: 2.3rem !important;
    text-shadow: 0 2px 10px rgba(255,255,255,0.2) !important;
}

[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] * {
    font-weight: 700 !important;
    font-size: 0.9rem !important;
}

/* ========================================================
   3. EXPANDERS & ΚΟΥΜΠΙΑ
   ======================================================== */
[data-testid="stExpander"], div[data-testid="stExpander"] {
    background-color: #151c2c !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 12px !important;
    margin-bottom: 12px !important;
}

[data-testid="stExpander"] details, [data-testid="stExpander"] summary {
    background-color: #1e293b !important;
    background: #1e293b !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] summary * {
    color: #38bdf8 !important;
    fill: #38bdf8 !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
}

[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    background-color: #151c2c !important;
    color: #ffffff !important;
    padding: 14px !important;
}

div.stButton > button, button[kind="secondary"], .stButton button {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}

div.stButton > button:hover {
    background-color: #334155 !important;
    border-color: #38bdf8 !important;
    color: #38bdf8 !important;
}

button[kind="primary"] {
    background-color: #dc2626 !important;
    border-color: #ef4444 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
}

.stForm button {
    background-color: #16a34a !important;
    border: 1px solid #22c55e !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
}

input, textarea, select {
    background-color: #0d1322 !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
input::placeholder, textarea::placeholder {
    color: #cbd5e1 !important;
    opacity: 0.9 !important;
}

/* ========================================================
   4. DATA TABLE STYLING
   ======================================================== */
.data-table-container {
    background: #151c2c;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    margin-top: 15px;
    margin-bottom: 30px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);
    overflow-x: auto;
    width: 100%;
}
.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.92rem;
    text-align: left;
}
.custom-table th {
    background: rgba(13, 19, 34, 0.95);
    color: #38bdf8; /* ΘΑΛΑΣΣΙ HEADERS */
    font-weight: 700;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 16px 18px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}
.custom-table td {
    padding: 14px 18px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    color: #ffffff;
    font-weight: 600;
}
.custom-table tr:hover {
    background-color: rgba(255, 255, 255, 0.05);
}
.custom-table tr.my-row {
    background: linear-gradient(90deg, rgba(168, 85, 247, 0.22) 0%, transparent 100%) !important;
    border-left: 4px solid #facc15 !important;
}
.badge-you {
    background: #facc15;
    color: #000;
    font-size: 0.72rem;
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 800;
    margin-left: 6px;
}
.growth-up { color: #10b981; font-weight: 700; }
.growth-down { color: #ef4444; font-weight: 700; }
.growth-flat { color: #94a3b8; font-weight: 600; }

.prompt-card-box {
    background: #151c2c;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 14px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DATA_FILE = "creator_hub_data.json"

# ==========================================
# SEED DATA
# ==========================================
SEED_COMPETITORS_GR = [
    {"name": "ZAVRAS FISHING", "handle": "@ZavrasFishing"},
    {"name": "sotosvasi", "handle": "@sotosvasi"},
    {"name": "Μάρκος Βιδάλης", "handle": "@MarkosVidalis"},
    {"name": "Giannis Mastrogiannakis", "handle": "@giannismastrogiannakis"},
    {"name": "Kostas Antoniadis", "handle": "@TheKwstasantoniadis"},
    {"name": "michael trifo", "handle": "@michaeltrifo6610"},
    {"name": "Milonakis Kayak Fishing", "handle": "UCw9pG7yAviPN8RluqZJ7Uiw"},
    {"name": "Giorgos Kazoulis", "handle": "@giorgoskazoulis4928"},
    {"name": "Spinning By Tyrikos", "handle": "UC08kPE-YyUVe2gQac8nCqqw"},
    {"name": "SifisFishing", "handle": "@SifisFishing"},
    {"name": "Tsouros Marine", "handle": "UC5cxxXjrQcHnWqh_KtiCpDg"},
    {"name": "Owrka", "handle": "UCpy-2GjgEjnx97N_aan0XFQ"},
    {"name": "GB Luring", "handle": "@GBLuring"},
    {"name": "Paraktios Fishing", "handle": "@paraktiosfishing"},
    {"name": "Fishing Time GR", "handle": "@FishingTimeGR"},
    {"name": "Sea Fishing Greece", "handle": "@seafishinggreece"},
    {"name": "Captain Hook Fishing", "handle": "@captainhookfishing"},
    {"name": "Luring Mania", "handle": "@luringmania"},
    {"name": "Deep Blue Fishing", "handle": "@deepbluefishing"},
    {"name": "Aegean Anglers", "handle": "@aegeananglers"},
    {"name": "Rock Fishing Greece", "handle": "@rockfishinggreece"},
    {"name": "Shore Jigging Hellas", "handle": "@shorejigginghellas"},
    {"name": "Hellenic Fishing Hunters", "handle": "@hellenicfishinghunters"},
    {"name": "Fishing Club GR", "handle": "@fishingclubgr"}
]

SEED_COMPETITORS_INTL = [
    {"name": "Salt Strong", "country": "USA", "handle": "@SaltStrong"},
    {"name": "BlacktipH", "country": "USA", "handle": "@BlacktipH"}
]

def blank_stats():
    return {"subs": 0, "totalViews": 0, "videos": 0, "avgViews": 0, "viewsPerSub": 0.0, "efficiency": 0.0, "growth": 0.0}

def get_default_data():
    return {
        "password_hash": hashlib.sha256("1234".encode()).hexdigest(),
        "my_channel": {
            "name": "Tsouros Marine",
            "handle": "UC5cxxXjrQcHnWqh_KtiCpDg",
            "resolvedId": "UC5cxxXjrQcHnWqh_KtiCpDg",
            **blank_stats()
        },
        "competitors_gr": [{**c, **blank_stats()} for c in SEED_COMPETITORS_GR],
        "competitors_intl": [{**c, **blank_stats()} for c in SEED_COMPETITORS_INTL],
        "schedule": [],
        "analytics": [],
        "keywords": [],
        "ideas": [],
        "goals": [],
        "prompts": [],
        "strategies": {
            "yt": [
                {"step": "1. Προ-Παραγωγή", "desc": "Έρευνα SEO, Scripting, Thumbnail Concept."},
                {"step": "2. Παραγωγή", "desc": "Οριζόντια εγγραφή (16:9), Ήχος Studio, A-Roll & B-Roll."},
                {"step": "3. Post-Production", "desc": "Montage, Sound Effects, Chapters, Custom Thumbnail."}
            ],
            "shorts": [
                {"step": "1. Hook & Format", "desc": "Hook στα πρώτα 2'', Κάθετο (9:16), διάρκεια < 60 sec."}
            ],
            "meta": [
                {"step": "1. Audio & Visuals", "desc": "Trending Sound, High Contrast Visuals, Safe Zone Text."}
            ],
            "tiktok": [
                {"step": "1. Trends & Style", "desc": "Raw/Authentic aesthetic, Νέα Trends, Fast-paced storytelling."}
            ]
        }
    }

def load_data():
    if not os.path.exists(DATA_FILE):
        data = get_default_data()
        save_data(data)
        return data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "prompts" not in data: data["prompts"] = []
            if "strategies" not in data: data["strategies"] = get_default_data()["strategies"]
            if "competitors_intl" not in data: data["competitors_intl"] = [{**c, **blank_stats()} for c in SEED_COMPETITORS_INTL]
            return data
    except Exception:
        return get_default_data()

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "db" not in st.session_state:
    st.session_state.db = load_data()
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ==========================================
# YOUTUBE API HELPER
# ==========================================
def resolve_handle(api_key, handle):
    if not handle or not api_key:
        return None
    if handle.startswith("UC"):
        return handle
    clean_handle = handle if handle.startswith("@") else f"@{handle}"
    url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forHandle={urllib.parse.quote(clean_handle)}&key={api_key}"
    try:
        res = requests.get(url, timeout=10).json()
        if "items" in res and len(res["items"]) > 0:
            return res["items"][0]["id"]
    except Exception:
        pass
    return None

def fetch_channel_stats(api_key, channel_ids):
    if not api_key or not channel_ids:
        return {}
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={','.join(channel_ids)}&key={api_key}"
    try:
        res = requests.get(url, timeout=10).json()
        out = {}
        if "items" in res:
            for item in res["items"]:
                stats = item["statistics"]
                subs = int(stats.get("subscriberCount", 0))
                views = int(stats.get("viewCount", 0))
                videos = int(stats.get("videoCount", 0))
                avg_views = round(views / videos) if videos > 0 else 0
                views_per_sub = round(avg_views / subs, 2) if subs > 0 else 0
                efficiency = round((avg_views / subs) * 1000, 1) if subs > 0 else 0
                out[item["id"]] = {
                    "subs": subs, "totalViews": views, "videos": videos,
                    "avgViews": avg_views, "viewsPerSub": views_per_sub, "efficiency": efficiency
                }
        return out
    except Exception as e:
        st.error(f"Σφάλμα API: {e}")
        return {}

def fmt(n):
    return "—" if not n else f"{n:,}".replace(",", ".")

def sort_channels(channels, sort_by, sort_dir):
    is_desc = "Φθίνουσα" in sort_dir
    if sort_by == "Subscribers":
        return sorted(channels, key=lambda x: x.get("subs", 0), reverse=is_desc)
    elif sort_by == "Total Views":
        return sorted(channels, key=lambda x: x.get("totalViews", 0), reverse=is_desc)
    elif sort_by == "Videos":
        return sorted(channels, key=lambda x: x.get("videos", 0), reverse=is_desc)
    elif sort_by == "Avg Views":
        return sorted(channels, key=lambda x: x.get("avgViews", 0), reverse=is_desc)
    elif sort_by == "Views/Sub":
        return sorted(channels, key=lambda x: x.get("viewsPerSub", 0.0), reverse=is_desc)
    elif sort_by == "Efficiency":
        return sorted(channels, key=lambda x: x.get("efficiency", 0.0), reverse=is_desc)
    elif sort_by == "Growth":
        return sorted(channels, key=lambda x: x.get("growth", 0.0), reverse=is_desc)
    elif "Όνομα" in sort_by:
        return sorted(channels, key=lambda x: x.get("name", "").lower(), reverse=not is_desc)
    return channels

# ==========================================
# LOGIN SCREEN
# ==========================================
def check_password():
    if st.session_state.authenticated:
        return True

    st.markdown("<h2 style='text-align: center; margin-top:50px; color:#ffffff; font-weight:800;'>🔒 Video Creator Hub</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #38bdf8; font-weight:700;'>Βάλτε τον κωδικό πρόσβασης για να ξεκλειδώσετε το εργαλείο.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        pw_input = st.text_input("Κωδικός", type="password", key="login_pw")
        if st.button("🔓 Είσοδος", use_container_width=True):
            entered_hash = hashlib.sha256(pw_input.encode()).hexdigest()
            stored_hash = st.session_state.db.get("password_hash")
            if entered_hash == stored_hash:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Λάθος κωδικός πρόσβασης! (Προεπιλεγμένος: 1234)")
        st.caption("ℹ️ Προεπιλεγμένος κωδικός: `1234`")
    return False

if not check_password():
    st.stop()

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#38bdf8; font-weight:800;'>🎬 Creator Hub</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("<h4 style='color:#38bdf8; font-weight:700;'>💾 Backup & Επαναφορά</h4>", unsafe_allow_html=True)
    
    json_str = json.dumps(st.session_state.db, ensure_ascii=False, indent=2)
    st.download_button(
        label="⬇️ Export Backup (JSON)",
        data=json_str,
        file_name=f"creator_hub_backup_{datetime.date.today()}.json",
        mime="application/json",
        use_container_width=True
    )
    
    uploaded_backup = st.file_uploader("⬆️ Import Backup", type=["json"])
    if uploaded_backup is not None:
        try:
            imported_data = json.load(uploaded_backup)
            st.session_state.db = imported_data
            save_data(st.session_state.db)
            st.success("✅ Το Backup ανακτήθηκε!")
            st.rerun()
        except Exception as e:
            st.error(f"Σφάλμα αρχείου: {e}")

    st.markdown("---")
    if st.button("🔄 Επαναφορά 24 GR + 2 Intl", use_container_width=True):
        st.session_state.db["competitors_gr"] = [{**c, **blank_stats()} for c in SEED_COMPETITORS_GR]
        st.session_state.db["competitors_intl"] = [{**c, **blank_stats()} for c in SEED_COMPETITORS_INTL]
        save_data(st.session_state.db)
        st.success("Φορτώθηκαν όλα τα κανάλια!")
        st.rerun()

# ==========================================
# ΚΥΡΙΩΣ TABS
# ==========================================
st.markdown("<h1 style='text-align: center; color:#ffffff; font-weight:800; margin-bottom: 25px;'>🎬 Video Creator Hub & Competitor Intelligence</h1>", unsafe_allow_html=True)

tabs = st.tabs([
    "📊 Dashboard",
    "🎬 YouTube Long-Form",
    "📱 YouTube Shorts",
    "📸 FB & IG Reels",
    "🎵 TikTok",
    "📅 Πρόγραμμα",
    "🇬🇷 Έλληνες Competitors",
    "🌐 Ξένοι Competitors",
    "📈 Ιστορικό & Analytics",
    "🔑 Keywords",
    "💡 Ιδέες",
    "🎯 Στόχοι",
    "📜 Prompts Library",
    "🖼️ Thumbnail AI Editor"
])

# ------------------------------------------
# 1. DASHBOARD
# ------------------------------------------
with tabs[0]:
    st.markdown("<h3 style='color:#38bdf8; font-weight:800;'>🏠 Επισκόπηση Καναλιού & Ανταγωνισμού</h3>", unsafe_allow_html=True)
    my_ch = st.session_state.db.get("my_channel", {})
    all_comp = st.session_state.db.get("competitors_gr", []) + st.session_state.db.get("competitors_intl", [])
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📺 Το Κανάλι Μου", fmt(my_ch.get('subs', 0)), f"{my_ch.get('name', 'Tsouros Marine')}")
    with c2:
        synced_c = [c for c in all_comp if c.get("subs", 0) > 0]
        avg_subs = round(sum(c.get("subs", 0) for c in synced_c) / len(synced_c)) if synced_c else 0
        st.metric("👥 Μ.Ο. Subs Competitors", fmt(avg_subs), f"{len(all_comp)} κανάλια")
    with c3:
        avg_views = round(sum(c.get("avgViews", 0) for c in synced_c) / len(synced_c)) if synced_c else 0
        st.metric("👀 Μ.Ο. Avg Views", fmt(avg_views))
    with c4:
        st.metric("💡 Ιδέες σε Αναμονή", len(st.session_state.db.get("ideas", [])))

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<h4 style='color:#38bdf8; font-weight:700;'>📅 Επόμενα Προγραμματισμένα</h4>", unsafe_allow_html=True)
        sched = st.session_state.db.get("schedule", [])
        if sched:
            df_sched = pd.DataFrame(sched)
            st.dataframe(df_sched[["date", "platform", "title", "status"]].head(5), use_container_width=True, hide_index=True)
        else:
            st.info("Δεν υπάρχουν προγραμματισμένα βίντεο.")

    with col_b:
        st.markdown("<h4 style='color:#38bdf8; font-weight:700;'>⚖️ Benchmark vs Ανταγωνιστές</h4>", unsafe_allow_html=True)
        my_avg_v = my_ch.get("avgViews", 0)
        if avg_views > 0:
            diff_pct = round(((my_avg_v - avg_views) / avg_views) * 100, 1)
            st.write(f"**Τα Avg Views σου vs Μέσος Όρος Ανταγωνισμού:** `{diff_pct:+}%`")
            fig = go.Figure(go.Bar(
                x=["Το Κανάλι Μου", "Μέσος Όρος Ανταγωνισμού"],
                y=[my_avg_v, avg_views],
                marker_color=["#facc15", "#3b82f6"]
            ))
            fig.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="#151c2c", plot_bgcolor="#151c2c", font=dict(color="#fff"))
            st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------
# 2-5. STRATEGY TABS
# ------------------------------------------
strat_map = [("yt", tabs[1], "🎬 YouTube Long-Form"), ("shorts", tabs[2], "📱 YouTube Shorts"), ("meta", tabs[3], "📸 FB & IG Reels"), ("tiktok", tabs[4], "🎵 TikTok")]
for key, t_view, t_title in strat_map:
    with t_view:
        st.markdown(f"<h3 style='color:#38bdf8; font-weight:800;'>{t_title} Strategy</h3>", unsafe_allow_html=True)
        
        items = st.session_state.db.get("strategies", {}).get(key, [])
        for idx, item in enumerate(items):
            col_s1, col_s2 = st.columns([5.5, 1])
            with col_s1:
                with st.expander(f"📌 {item['step']}", expanded=True):
                    st.write(item["desc"])
            with col_s2:
                if st.button("🗑️ Διαγραφή", key=f"del_step_{key}_{idx}", type="primary"):
                    st.session_state.db["strategies"][key].pop(idx)
                    save_data(st.session_state.db)
                    st.rerun()

        with st.form(f"add_step_form_{key}", clear_on_submit=True):
            st.markdown("<h4 style='color:#38bdf8; font-weight:700;'>➕ Προσθήκη Νέου Βήματος</h4>", unsafe_allow_html=True)
            s_title = st.text_input("Τίτλος Βήματος (π.χ. 4. SEO & Distribution)", key=f"inp_t_{key}")
            s_desc = st.text_area("Περιγραφή Βήματος", height=100, key=f"inp_d_{key}")
            if st.form_submit_button("➕ Προσθήκη Βήματος", use_container_width=True):
                if s_title and s_desc:
                    if "strategies" not in st.session_state.db:
                        st.session_state.db["strategies"] = {}
                    if key not in st.session_state.db["strategies"]:
                        st.session_state.db["strategies"][key] = []
                    st.session_state.db["strategies"][key].append({"step": s_title, "desc": s_desc})
                    save_data(st.session_state.db)
                    st.success("Το βήμα προστέθηκε επιτυχώς!")
                    st.rerun()
                else:
                    st.warning("⚠️ Συμπληρώστε τίτλο και περιγραφή.")

# ------------------------------------------
# 6. SCHEDULE
# ------------------------------------------
with tabs[5]:
    st.markdown("<h3 style='color:#38bdf8; font-weight:800;'>📅 Πρόγραμμα Δημοσιεύσεων</h3>", unsafe_allow_html=True)
    with st.expander("➕ Προσθήκη Νέου Βίντεο"):
        with st.form("sched_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                sc_date = st.date_input("Ημερομηνία", datetime.date.today())
                sc_time = st.time_input("Ώρα", datetime.time(18, 0))
                sc_plat = st.selectbox("Πλατφόρμα", ["YouTube Long", "YouTube Shorts", "Facebook Reel", "Instagram Reel", "TikTok"])
            with c2:
                sc_title = st.text_input("Τίτλος Βίντεο")
                sc_status = st.selectbox("Status", ["Ιδέα", "Script", "Filming", "Editing", "Ready", "Published"])
            if st.form_submit_button("➕ Προσθήκη Βίντεο"):
                if sc_title:
                    if "schedule" not in st.session_state.db:
                        st.session_state.db["schedule"] = []
                    st.session_state.db["schedule"].append({
                        "id": str(datetime.datetime.now().timestamp()), "date": str(sc_date),
                        "time": str(sc_time)[:5], "platform": sc_plat, "title": sc_title, "status": sc_status
                    })
                    save_data(st.session_state.db)
                    st.success("Το βίντεο προστέθηκε!")
                    st.rerun()

    sched = st.session_state.db.get("schedule", [])
    if sched:
        st.dataframe(pd.DataFrame(sched)[["date", "time", "platform", "title", "status"]], use_container_width=True, hide_index=True)
    else:
        st.info("Δεν υπάρχουν προγραμματισμένα βίντεο.")

# ------------------------------------------
# 7. GREEK COMPETITORS
# ------------------------------------------
with tabs[6]:
    comps = st.session_state.db.get("competitors_gr", [])
    st.markdown(f"<h3 style='color:#38bdf8; font-weight:800;'>🇬🇷 Έλληνες Competitors ({len(comps)} Κανάλια)</h3>", unsafe_allow_html=True)
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🔄 Ανανέωση Όλων (Sync API)", key="sync_gr_btn", use_container_width=True):
            ids = []
            for c in comps:
                cid = resolve_handle(YOUTUBE_API_KEY, c["handle"])
                c["resolvedId"] = cid
                if cid: ids.append(cid)
            
            stats_map = fetch_channel_stats(YOUTUBE_API_KEY, ids)
            for c in comps:
                cid = c.get("resolvedId")
                if cid and cid in stats_map:
                    old_subs = c.get("subs", 0)
                    c.update(stats_map[cid])
                    new_subs = c.get("subs", 0)
                    c["growth"] = round(((new_subs - old_subs) / old_subs) * 100, 2) if old_subs > 0 else 0.0
            
            my_c = st.session_state.db["my_channel"]
            my_id = resolve_handle(YOUTUBE_API_KEY, my_c["handle"])
            if my_id and my_id in stats_map:
                my_c.update(stats_map[my_id])
                
            save_data(st.session_state.db)
            st.success("✅ Όλα τα κανάλια ανανεώθηκαν!")
            st.rerun()

    col_add, col_del = st.columns(2)
    with col_add:
        with st.expander("➕ Προσθήκη Νέου Καναλιού"):
            with st.form("add_comp_gr", clear_on_submit=True):
                c_name = st.text_input("Όνομα Καναλιού")
                c_handle = st.text_input("@handle ή Channel ID (UC...)")
                if st.form_submit_button("➕ Προσθήκη"):
                    if c_name and c_handle:
                        st.session_state.db["competitors_gr"].append({"name": c_name, "handle": c_handle, **blank_stats()})
                        save_data(st.session_state.db)
                        st.rerun()

    with col_del:
        with st.expander("🗑️ Διαγραφή Καναλιού"):
            comp_names = [c["name"] for c in comps]
            if comp_names:
                selected_del = st.selectbox("Επιλέξτε κανάλι για διαγραφή:", comp_names, key="sel_del_gr")
                if st.button("🗑️ Διαγραφή Επιλεγμένου", key="btn_del_gr", type="primary"):
                    st.session_state.db["competitors_gr"] = [c for c in comps if c["name"] != selected_del]
                    save_data(st.session_state.db)
                    st.success(f"Το κανάλι '{selected_del}' διαγράφηκε!")
                    st.rerun()

    col_sort1, col_sort2, _ = st.columns([2, 1.8, 1.5])
    with col_sort1:
        sort_by_gr = st.selectbox(
            "📊 Ταξινόμηση κατά:",
            ["Subscribers", "Total Views", "Videos", "Avg Views", "Views/Sub", "Efficiency", "Growth", "Όνομα (Α-Ω)"],
            key="sort_by_gr"
        )
    with col_sort2:
        sort_dir_gr = st.radio("Σειρά:", ["Φθίνουσα ⬇️", "Αύξουσα ⬆️"], horizontal=True, key="sort_dir_gr")

    sorted_comps = sort_channels(comps, sort_by_gr, sort_dir_gr)

    rows_list = []
    for c in sorted_comps:
        is_my = "tsouros" in c["name"].lower()
        row_cls = "my-row" if is_my else ""
        badge = '<span class="badge-you">Εσύ</span>' if is_my else ""
        
        growth = c.get("growth", 0.0)
        growth_html = f'<span class="growth-up">+{growth}%</span>' if growth > 0 else (f'<span class="growth-down">{growth}%</span>' if growth < 0 else '<span class="growth-flat">0%</span>')

        row = (
            f'<tr class="{row_cls}">'
            f'<td style="font-weight:700;">{c["name"]} {badge}</td>'
            f'<td style="text-align:right; font-weight:800; color:#ffffff;">{fmt(c.get("subs", 0))}</td>'
            f'<td style="text-align:right;">{fmt(c.get("totalViews", 0))}</td>'
            f'<td style="text-align:right;">{fmt(c.get("videos", 0))}</td>'
            f'<td style="text-align:right;">{fmt(c.get("avgViews", 0))}</td>'
            f'<td style="text-align:right;">{c.get("viewsPerSub", 0.0)}</td>'
            f'<td style="text-align:right;">{c.get("efficiency", 0.0)}</td>'
            f'<td style="text-align:center;">{growth_html}</td>'
            f'</tr>'
        )
        rows_list.append(row)

    table_html = (
        '<div class="data-table-container">'
        '<table class="custom-table">'
        '<thead><tr>'
        '<th style="text-align:left;">CHANNEL</th>'
        '<th style="text-align:right;">SUBSCRIBERS (ΑΚΡΙΒΗΣ)</th>'
        '<th style="text-align:right;">TOTAL VIEWS</th>'
        '<th style="text-align:right;">VIDEOS</th>'
        '<th style="text-align:right;">AVG VIEWS</th>'
        '<th style="text-align:right;">VIEWS/SUB</th>'
        '<th style="text-align:right;">EFFICIENCY</th>'
        '<th style="text-align:center;">GROWTH</th>'
        '</tr></thead>'
        '<tbody>' + "".join(rows_list) + '</tbody>'
        '</table>'
        '</div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)

# ------------------------------------------
# 8. INTL COMPETITORS
# ------------------------------------------
with tabs[7]:
    comps_intl = st.session_state.db.get("competitors_intl", [])
    st.markdown(f"<h3 style='color:#38bdf8; font-weight:800;'>🌐 Ξένοι Competitors ({len(comps_intl)} Κανάλια)</h3>", unsafe_allow_html=True)
    
    col_ibtn1, col_ibtn2 = st.columns([1, 4])
    with col_ibtn1:
        if st.button("🔄 Ανανέωση Όλων (Sync API)", key="sync_intl_btn", use_container_width=True):
            ids = []
            for c in comps_intl:
                cid = resolve_handle(YOUTUBE_API_KEY, c["handle"])
                c["resolvedId"] = cid
                if cid: ids.append(cid)
            
            stats_map = fetch_channel_stats(YOUTUBE_API_KEY, ids)
            for c in comps_intl:
                cid = c.get("resolvedId")
                if cid and cid in stats_map:
                    old_subs = c.get("subs", 0)
                    c.update(stats_map[cid])
                    new_subs = c.get("subs", 0)
                    c["growth"] = round(((new_subs - old_subs) / old_subs) * 100, 2) if old_subs > 0 else 0.0
            
            save_data(st.session_state.db)
            st.success("✅ Όλοι οι ξένοι competitors ανανεώθηκαν!")
            st.rerun()

    col_iadd, col_idel = st.columns(2)
    with col_iadd:
        with st.expander("➕ Προσθήκη Ξένου Καναλιού"):
            with st.form("add_comp_intl", clear_on_submit=True):
                ci_name = st.text_input("Όνομα Καναλιού")
                ci_country = st.text_input("Χώρα (π.χ. USA, Japan)")
                ci_handle = st.text_input("@handle ή Channel ID")
                if st.form_submit_button("➕ Προσθήκη"):
                    if ci_name and ci_handle:
                        st.session_state.db["competitors_intl"].append({
                            "name": ci_name, "country": ci_country, "handle": ci_handle, **blank_stats()
                        })
                        save_data(st.session_state.db)
                        st.rerun()

    with col_idel:
        with st.expander("🗑️ Διαγραφή Ξένου Καναλιού"):
            comp_intl_names = [c["name"] for c in comps_intl]
            if comp_intl_names:
                selected_del_intl = st.selectbox("Επιλέξτε κανάλι για διαγραφή:", comp_intl_names, key="sel_del_intl")
                if st.button("🗑️ Διαγραφή Επιλεγμένου", key="btn_del_intl", type="primary"):
                    st.session_state.db["competitors_intl"] = [c for c in comps_intl if c["name"] != selected_del_intl]
                    save_data(st.session_state.db)
                    st.success(f"Το κανάλι '{selected_del_intl}' διαγράφηκε!")
                    st.rerun()

    col_isort1, col_isort2, _ = st.columns([2, 1.8, 1.5])
    with col_isort1:
        sort_by_intl = st.selectbox(
            "📊 Ταξινόμηση κατά:",
            ["Subscribers", "Total Views", "Videos", "Avg Views", "Views/Sub", "Efficiency", "Growth", "Όνομα (Α-Ω)"],
            key="sort_by_intl"
        )
    with col_isort2:
        sort_dir_intl = st.radio("Σειρά:", ["Φθίνουσα ⬇️", "Αύξουσα ⬆️"], horizontal=True, key="sort_dir_intl")

    sorted_intl = sort_channels(comps_intl, sort_by_intl, sort_dir_intl)

    rows_intl_list = []
    for c in sorted_intl:
        growth = c.get("growth", 0.0)
        growth_html = f'<span class="growth-up">+{growth}%</span>' if growth > 0 else (f'<span class="growth-down">{growth}%</span>' if growth < 0 else '<span class="growth-flat">0%</span>')

        row_intl = (
            f'<tr>'
            f'<td style="font-weight:700;">{c["name"]}</td>'
            f'<td>{c.get("country", "—")}</td>'
            f'<td style="text-align:right; font-weight:800; color:#ffffff;">{fmt(c.get("subs", 0))}</td>'
            f'<td style="text-align:right;">{fmt(c.get("totalViews", 0))}</td>'
            f'<td style="text-align:right;">{fmt(c.get("videos", 0))}</td>'
            f'<td style="text-align:right;">{fmt(c.get("avgViews", 0))}</td>'
            f'<td style="text-align:right;">{c.get("viewsPerSub", 0.0)}</td>'
            f'<td style="text-align:right;">{c.get("efficiency", 0.0)}</td>'
            f'<td style="text-align:center;">{growth_html}</td>'
            f'</tr>'
        )
        rows_intl_list.append(row_intl)

    table_intl_html = (
        '<div class="data-table-container">'
        '<table class="custom-table">'
        '<thead><tr>'
        '<th style="text-align:left;">CHANNEL</th>'
        '<th style="text-align:left;">ΧΩΡΑ</th>'
        '<th style="text-align:right;">SUBSCRIBERS (ΑΚΡΙΒΗΣ)</th>'
        '<th style="text-align:right;">TOTAL VIEWS</th>'
        '<th style="text-align:right;">VIDEOS</th>'
        '<th style="text-align:right;">AVG VIEWS</th>'
        '<th style="text-align:right;">VIEWS/SUB</th>'
        '<th style="text-align:right;">EFFICIENCY</th>'
        '<th style="text-align:center;">GROWTH</th>'
        '</tr></thead>'
        '<tbody>' + "".join(rows_intl_list) + '</tbody>'
        '</table>'
        '</div>'
    )
    st.markdown(table_intl_html, unsafe_allow_html=True)

# ------------------------------------------
# 9. ANALYTICS
# ------------------------------------------
with tabs[8]:
    st.markdown("<h3 style='color:#38bdf8; font-weight:800;'>📈 Analytics & Video History</h3>", unsafe_allow_html=True)
    with st.expander("➕ Καταγραφή Στατιστικών Βίντεο"):
        with st.form("an_form_add", clear_on_submit=True):
            t = st.text_input("Τίτλος Βίντεο")
            typ = st.selectbox("Τύπος", ["Long-form", "Shorts"])
            c1, c2 = st.columns(2)
            with c1:
                ctr = st.number_input("CTR (%)", step=0.1)
                ret = st.number_input("Retention (%)", step=0.1)
            with c2:
                wt = st.number_input("Watch Time (h)", step=0.1)
                src = st.text_input("Traffic Sources")
            if st.form_submit_button("Αποθήκευση"):
                if t:
                    if "analytics" not in st.session_state.db:
                        st.session_state.db["analytics"] = []
                    st.session_state.db["analytics"].append({"title": t, "type": typ, "ctr": ctr, "retention": ret, "watchTime": wt, "sources": src})
                    save_data(st.session_state.db)
                    st.rerun()

    an = st.session_state.db.get("analytics", [])
    if an:
        st.dataframe(pd.DataFrame(an), use_container_width=True, hide_index=True)

# ------------------------------------------
# 10. KEYWORDS
# ------------------------------------------
with tabs[9]:
    st.markdown("<h3 style='color:#38bdf8; font-weight:800;'>🔑 Keywords</h3>", unsafe_allow_html=True)
    with st.expander("➕ Προσθήκη Keyword"):
        with st.form("kw_form_add", clear_on_submit=True):
            kw = st.text_input("Keyword")
            prio = st.selectbox("Προτεραιότητα", ["Υψηλή", "Μεσαία", "Χαμηλή"])
            stat = st.selectbox("Status", ["Νέα", "Σε χρήση", "Ολοκληρώθηκε"])
            if st.form_submit_button("Αποθήκευση"):
                if kw:
                    if "keywords" not in st.session_state.db:
                        st.session_state.db["keywords"] = []
                    st.session_state.db["keywords"].append({"text": kw, "priority": prio, "status": stat})
                    save_data(st.session_state.db)
                    st.rerun()

    kws = st.session_state.db.get("keywords", [])
    if kws:
        st.dataframe(pd.DataFrame(kws), use_container_width=True, hide_index=True)

# ------------------------------------------
# 11. IDEAS
# ------------------------------------------
with tabs[10]:
    st.markdown("<h3 style='color:#38bdf8; font-weight:800;'>💡 Ιδέες για Βίντεο</h3>", unsafe_allow_html=True)
    with st.form("idea_form_add", clear_on_submit=True):
        txt = st.text_area("Ιδέα", height=90)
        tags = st.text_input("Tags")
        if st.form_submit_button("➕ Προσθήκη"):
            if txt:
                if "ideas" not in st.session_state.db:
                    st.session_state.db["ideas"] = []
                st.session_state.db["ideas"].append({
                    "id": str(datetime.datetime.now().timestamp()),
                    "text": txt, "tags": [t.strip() for t in tags.split(",") if t.strip()],
                    "date": str(datetime.date.today())
                })
                save_data(st.session_state.db)
                st.rerun()

    for i in st.session_state.db.get("ideas", []):
        st.markdown(f"**💡 {i['text']}**")
        st.caption(f"🏷️ {', '.join(i.get('tags', []))} | 📅 {i.get('date')}")
        st.markdown("---")

# ------------------------------------------
# 12. GOALS
# ------------------------------------------
with tabs[11]:
    st.markdown("<h3 style='color:#38bdf8; font-weight:800;'>🎯 Μηνιαίοι Στόχοι</h3>", unsafe_allow_html=True)
    with st.form("goal_form_add", clear_on_submit=True):
        m = st.text_input("Μήνας (π.χ. 2026-10)")
        s = st.number_input("Στόχος Subs", step=10)
        v = st.number_input("Στόχος Views", step=1000)
        u = st.number_input("Στόχος Uploads", step=1)
        if st.form_submit_button("Αποθήκευση"):
            if m:
                if "goals" not in st.session_state.db:
                    st.session_state.db["goals"] = []
                st.session_state.db["goals"].append({"month": m, "subs": s, "views": v, "uploads": u})
                save_data(st.session_state.db)
                st.rerun()

    gls = st.session_state.db.get("goals", [])
    if gls:
        st.dataframe(pd.DataFrame(gls), use_container_width=True, hide_index=True)

# ------------------------------------------
# 13. PROMPTS LIBRARY
# ------------------------------------------
with tabs[12]:
    st.markdown("<h3 style='color:#38bdf8; font-weight:800;'>📜 Prompts Library</h3>", unsafe_allow_html=True)
    
    with st.form("add_prompt_main_form", clear_on_submit=True):
        p_title = st.text_input("Τίτλος Prompt", placeholder="Τίτλος Prompt (π.χ. Midjourney Fishing Action)", label_visibility="collapsed")
        p_body = st.text_area("Κείμενο Prompt", placeholder="Επικολλήστε το prompt εδώ...", height=120, label_visibility="collapsed")
        submitted = st.form_submit_button("➕ Προσθήκη Prompt", use_container_width=True)
        if submitted:
            if p_title and p_body:
                if "prompts" not in st.session_state.db:
                    st.session_state.db["prompts"] = []
                st.session_state.db["prompts"].append({
                    "id": str(datetime.datetime.now().timestamp()),
                    "title": p_title, "body": p_body, "date": str(datetime.date.today())
                })
                save_data(st.session_state.db)
                st.success("✅ Το Prompt προστέθηκε επιτυχώς!")
                st.rerun()
            else:
                st.warning("⚠️ Συμπληρώστε τίτλο και κείμενο!")

    st.markdown("<br>", unsafe_allow_html=True)
    prompts = st.session_state.db.get("prompts", [])
    if prompts:
        for p in prompts:
            col_pr1, col_pr2 = st.columns([5.5, 1])
            with col_pr1:
                st.markdown(f"<div class='prompt-card-box'><h4>{p['title']}</h4><p style='font-family:monospace; color:#38bdf8;'>{p['body']}</p><small style='color:#94a3b8;'>📅 {p.get('date', '')}</small></div>", unsafe_allow_html=True)
            with col_pr2:
                if st.button("🗑️ Διαγραφή", key=f"del_pr_{p['id']}", type="primary"):
                    st.session_state.db["prompts"] = [x for x in prompts if x["id"] != p["id"]]
                    save_data(st.session_state.db)
                    st.rerun()
    else:
        st.markdown("<div style='text-align: center; color: #38bdf8; font-weight:700; padding: 40px 0;'>Δεν υπάρχουν αποθηκευμένα prompts. Πρόσθεσε ένα παραπάνω.</div>", unsafe_allow_html=True)

# ------------------------------------------
# 14. THUMBNAIL AI EDITOR
# ------------------------------------------
with tabs[13]:
    st.markdown("<h3 style='color:#38bdf8; font-weight:800;'>🖼️ Thumbnail AI Editor</h3>", unsafe_allow_html=True)
    img_file = st.file_uploader("Ανεβάστε thumbnail ανταγωνιστή", type=["png", "jpg", "jpeg", "webp"])
    if img_file:
        st.image(img_file, caption="Competitor Thumbnail", width=400)
        st.code("High-impact YouTube thumbnail, dramatic lighting, intense composition, vivid neon highlights (#facc15, #ef4444), photorealistic detail, 8k resolution, cinematic depth of field, bold text safe zone on left third --ar 16:9 --v 6.0", language="text")
