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
# ΑΣΦΑΛΗΣ ΑΝΑΚΤΗΣΗ YOUTUBE API KEY
# ==========================================

YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]

# ==========================================
# ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ
# ==========================================
st.set_page_config(
    page_title="Video Creator Hub & Competitor Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "creator_hub_data.json"

# ==========================================
# ΕΠΙΛΟΓΕΣ ΠΗΓΩΝ ΕΠΙΣΚΕΨΙΜΟΤΗΤΑΣ YOUTUBE
# ==========================================
TRAFFIC_SOURCE_OPTIONS = [
    "Λειτουργίες περιήγησης",
    "Αναζήτηση YouTube",
    "Προτεινόμενα βίντεο",
    "Σελίδες καναλιών",
    "Εξωτερικές",
    "Απευθείας πληκτρολόγηση ή άγνωστη πηγή",
    "Ειδοποιήσεις",
    "Διαφημίσεις YouTube",
    "Άλλες λειτουργίες του YouTube",
    "Τελικές οθόνες",
    "Σχετικά Short",
    "Λίστα αναπαραγωγής",
    "Σελίδες hashtag (#)"
]

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

# ==========================================
# ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ & BADGES
# ==========================================
def blank_stats():
    return {"subs": 0, "totalViews": 0, "videos": 0, "avgViews": 0, "viewsPerSub": 0.0, "efficiency": 0.0, "growth": 0.0}

def fmt(n):
    return "—" if (n is None or n == "") else f"{n:,}".replace(",", ".")

def score_badge(score):
    if score is None or score == "" or score == 0:
        return '<span style="color:#94a3b8;">—</span>'
    try:
        val = int(score)
        if val >= 65:
            color, bg = "#10b981", "rgba(16, 185, 129, 0.2)"
        elif val >= 45:
            color, bg = "#facc15", "rgba(250, 204, 21, 0.2)"
        else:
            color, bg = "#ef4444", "rgba(239, 68, 68, 0.2)"
        return f'<span style="background:{bg}; color:{color}; padding:3px 10px; border-radius:12px; font-weight:800; border:1px solid {color}50;">📊 {val}/100</span>'
    except Exception:
        return str(score)

def rank_badge(rank, is_my=True):
    if not rank or str(rank).strip() in ["", "0", "—", "-", "None"]:
        return '<span style="color:#94a3b8;">—</span>'
    r_str = str(rank).strip()
    if not r_str.startswith("#"):
        r_str = f"#{r_str}"
    if is_my:
        return f'<span style="background:rgba(16, 185, 129, 0.25); color:#10b981; padding:3px 9px; border-radius:12px; font-weight:800; border:1px solid rgba(16, 185, 129, 0.5);">🟢 {r_str}</span>'
    else:
        return f'<span style="background:rgba(59, 130, 246, 0.25); color:#60a5fa; padding:3px 9px; border-radius:12px; font-weight:800; border:1px solid rgba(59, 130, 246, 0.5);">🔵 {r_str}</span>'

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
            if "keywords" not in data: data["keywords"] = []
            if "analytics" not in data: data["analytics"] = []
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
# ΕΠΑΓΓΕΛΜΑΤΙΚΟ DARK THEME CSS
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

[data-testid="stSidebar"] {
    background-color: #111827 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* ========================================================
   1. ΑΝΑΚΑΤΑΣΚΕΥΗ ΜΕΝΟΥ: ΚΑΤΑΛΕΥΚΑ PILLS & 2 ΣΕΙΡΕΣ
   ======================================================== */
[data-testid="stTabs"] [data-baseweb="tab-list"],
div[role="tablist"] {
    display: flex !important;
    flex-wrap: wrap !important;
    overflow: visible !important;
    overflow-x: visible !important;
    white-space: normal !important;
    justify-content: center !important;
    align-items: center !important;
    gap: 8px !important;
    background: #151c2c !important;
    padding: 14px !important;
    border-radius: 18px !important;
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.5) !important;
    width: 100% !important;
    margin-bottom: 25px !important;
}

[data-testid="stTabs"] button[aria-label*="Scroll"],
[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none !important;
}

/* Κάθε Tab ως ξεχωριστό φωτεινό κουμπί */
[data-testid="stTabs"] button[data-baseweb="tab"],
button[data-baseweb="tab"] {
    background-color: #1e293b !important;
    background: #1e293b !important;
    border: 1px solid rgba(255, 255, 255, 0.22) !important;
    padding: 10px 18px !important;
    border-radius: 12px !important;
    margin: 2px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.35) !important;
    transition: all 0.2s ease !important;
}

/* ΕΠΙΒΟΛΗ ΚΑΤΑΛΕΥΚΟΥ BOLD ΧΡΩΜΑΤΟΣ ΣΕ ΟΛΑ ΤΑ ΓΡΑΜΜΑΤΑ ΤΟΥ ΜΕΝΟΥ */
[data-testid="stTabs"] button[data-baseweb="tab"] *,
[data-testid="stTabs"] button[data-baseweb="tab"] p,
[data-testid="stTabs"] button[data-baseweb="tab"] span,
[data-testid="stTabs"] button[data-baseweb="tab"] div,
button[data-baseweb="tab"] p,
button[data-baseweb="tab"] span,
button[data-baseweb="tab"] div,
button[data-baseweb="tab"] {
    color: #ffffff !important; /* ΚΑΤΑΛΕΥΚΟ */
    font-weight: 800 !important; /* BOLD */
    font-size: 0.95rem !important;
    opacity: 1 !important;
    text-shadow: 0 1px 4px rgba(0,0,0,0.9) !important;
}

[data-testid="stTabs"] button[data-baseweb="tab"]:hover,
button[data-baseweb="tab"]:hover {
    background-color: #334155 !important;
    border-color: #38bdf8 !important;
    transform: translateY(-2px) !important;
}
[data-testid="stTabs"] button[data-baseweb="tab"]:hover * {
    color: #38bdf8 !important;
}

/* Χρώματα Active Tabs */
button[data-baseweb="tab"]:nth-of-type(1)[aria-selected="true"] { background: linear-gradient(135deg, #2e1065 0%, #a855f7 100%) !important; border: 2px solid #c084fc !important; box-shadow: 0 4px 14px rgba(168, 85, 247, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(2)[aria-selected="true"] { background: linear-gradient(135deg, #450a0a 0%, #ef4444 100%) !important; border: 2px solid #fca5a5 !important; box-shadow: 0 4px 14px rgba(239, 68, 68, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(3)[aria-selected="true"] { background: linear-gradient(135deg, #4c0519 0%, #f43f5e 100%) !important; border: 2px solid #fecdd3 !important; box-shadow: 0 4px 14px rgba(244, 63, 94, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(4)[aria-selected="true"] { background: linear-gradient(135deg, #500724 0%, #ec4899 100%) !important; border: 2px solid #fbcfe8 !important; box-shadow: 0 4px 14px rgba(236, 72, 153, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(5)[aria-selected="true"] { background: linear-gradient(135deg, #083344 0%, #06b6d4 100%) !important; border: 2px solid #a5f3fc !important; box-shadow: 0 4px 14px rgba(6, 182, 212, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(6)[aria-selected="true"] { background: linear-gradient(135deg, #172554 0%, #3b82f6 100%) !important; border: 2px solid #bfdbfe !important; box-shadow: 0 4px 14px rgba(59, 130, 246, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(7)[aria-selected="true"] { background: linear-gradient(135deg, #022c22 0%, #10b981 100%) !important; border: 2px solid #a7f3d0 !important; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(8)[aria-selected="true"] { background: linear-gradient(135deg, #431407 0%, #f97316 100%) !important; border: 2px solid #fed7aa !important; box-shadow: 0 4px 14px rgba(249, 115, 22, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(9)[aria-selected="true"] { background: linear-gradient(135deg, #1e1b4b 0%, #6366f1 100%) !important; border: 2px solid #c7d2fe !important; box-shadow: 0 4px 14px rgba(99, 102, 241, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(10)[aria-selected="true"] { background: linear-gradient(135deg, #083344 0%, #22d3ee 100%) !important; border: 2px solid #a5f3fc !important; box-shadow: 0 4px 14px rgba(34, 211, 238, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(11)[aria-selected="true"] { background: linear-gradient(135deg, #422006 0%, #ca8a04 100%) !important; border: 2px solid #fef08a !important; box-shadow: 0 4px 14px rgba(202, 138, 4, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(12)[aria-selected="true"] { background: linear-gradient(135deg, #4c0519 0%, #e11d48 100%) !important; border: 2px solid #fecdd3 !important; box-shadow: 0 4px 14px rgba(225, 29, 72, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(13)[aria-selected="true"] { background: linear-gradient(135deg, #312e81 0%, #4f46e5 100%) !important; border: 2px solid #818cf8 !important; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.6) !important; }
button[data-baseweb="tab"]:nth-of-type(14)[aria-selected="true"] { background: linear-gradient(135deg, #831843 0%, #db2777 100%) !important; border: 2px solid #f472b6 !important; box-shadow: 0 4px 14px rgba(219, 39, 119, 0.6) !important; }

button[data-baseweb="tab"][aria-selected="true"] * {
    color: #ffffff !important;
    font-weight: 800 !important;
    text-shadow: 0 0 10px rgba(255,255,255,0.7) !important;
}

/* ========================================================
   2. LABELS & INPUTS
   ======================================================== */
label, label p, [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p {
    color: #38bdf8 !important;
    font-weight: 800 !important;
    font-size: 0.96rem !important;
    opacity: 1 !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.6) !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] label * {
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
}

input, textarea, select, [data-baseweb="select"] {
    background-color: #0d1322 !important;
    color: #ffffff !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}
input:focus, textarea:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 8px rgba(56, 189, 248, 0.4) !important;
}
input::placeholder, textarea::placeholder {
    color: #cbd5e1 !important;
    opacity: 0.9 !important;
    font-weight: 500 !important;
}

/* METRICS */
[data-testid="stMetric"] {
    background: #151c2c !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
    color: #38bdf8 !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
    color: #ffffff !important;
    font-weight: 800 !important;
    font-size: 2.3rem !important;
    text-shadow: 0 2px 10px rgba(255,255,255,0.2) !important;
}

/* EXPANDERS & BUTTONS */
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
    font-weight: 800 !important;
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
    font-weight: 800 !important;
    transition: all 0.2s ease !important;
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
    font-weight: 800 !important;
}
.stForm button {
    background-color: #16a34a !important;
    border: 1px solid #22c55e !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
}

/* TABLE */
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
    color: #38bdf8;
    font-weight: 800;
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
.growth-up { color: #10b981; font-weight: 800; }
.growth-down { color: #ef4444; font-weight: 800; }
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

# ==========================================
# LOGIN SCREEN
# ==========================================
def check_password():
    if st.session_state.authenticated:
        return True

    st.markdown("<h2 style='text-align: center; margin-top:50px; color:#ffffff; font-weight:800;'>🔒 Video Creator Hub</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #38bdf8; font-weight:800;'>Βάλτε τον κωδικό πρόσβασης για να ξεκλειδώσετε το εργαλείο.</p>", unsafe_allow_html=True)
    
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
    
    st.markdown("<h4 style='color:#38bdf8; font-weight:800;'>💾 Backup & Επαναφορά</h4>", unsafe_allow_html=True)
    
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
# ΚΥΡΙΩΣ TABS (14 TABS)
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
        st.markdown("<h4 style='color:#38bdf8; font-weight:800;'>📅 Επόμενα Προγραμματισμένα</h4>", unsafe_allow_html=True)
        sched = st.session_state.db.get("schedule", [])
        if sched:
            df_sched = pd.DataFrame(sched)
            st.dataframe(df_sched[["date", "platform", "title", "status"]].head(5), use_container_width=True, hide_index=True)
        else:
            st.info("Δεν υπάρχουν προγραμματισμένα βίντεο.")

    with col_b:
        st.markdown("<h4 style='color:#38bdf8; font-weight:800;'>⚖️ Benchmark vs Ανταγωνιστές</h4>", unsafe_allow_html=True)
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
            st.markdown("<h4 style='color:#38bdf8; font-weight:800;'>➕ Προσθήκη Νέου Βήματος</h4>", unsafe_allow_html=True)
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
# 9. ANALYTICS & VIDEO HISTORY
# ------------------------------------------
with tabs[8]:
    st.markdown("<h3 style='color:#38bdf8; font-weight:800;'>📈 Analytics & Video History</h3>", unsafe_allow_html=True)
    
    with st.expander("➕ Καταγραφή Στατιστικών Βίντεο"):
        with st.form("an_form_add", clear_on_submit=True):
            a_c1, a_c2, a_c3 = st.columns(3)
            with a_c1:
                t = st.text_input("Τίτλος Βίντεο")
                typ = st.selectbox("Τύπος Βίντεο", ["Long-form (16:9)", "Shorts (9:16)"])
                views = st.number_input("👁️ Προβολές (Views)", min_value=0, step=100)
                unique_viewers = st.number_input("👥 Μοναδικοί Θεατές", min_value=0, step=50)

            with a_c2:
                ctr = st.number_input("CTR (%)", min_value=0.0, max_value=100.0, step=0.1)
                ret = st.number_input("Retention / Avg Viewed (%)", min_value=0.0, max_value=100.0, step=0.1)
                avd = st.text_input("⏱️ Μέση Διάρκεια (AVD)", placeholder="π.χ. 03:45")
                new_subs = st.number_input("➕ New Subs", step=1)

            with a_c3:
                wt = st.number_input("Συνολικό Watch Time (Ώρες)", min_value=0.0, step=0.1)
                st.markdown("<p style='color:#38bdf8; font-weight:800; margin-bottom:4px;'>📊 Πηγές Επισκεψιμότητας & Ώρες</p>", unsafe_allow_html=True)
                src_1 = st.selectbox("1η Κύρια Πηγή:", ["— Καμία —"] + TRAFFIC_SOURCE_OPTIONS, key="an_src1")
                hours_1 = st.number_input("Ώρες 1ης Πηγής (h)", min_value=0.0, step=0.1, key="an_h1")
                src_2 = st.selectbox("2η Πηγή (προαιρετικά):", ["— Καμία —"] + TRAFFIC_SOURCE_OPTIONS, key="an_src2")
                hours_2 = st.number_input("Ώρες 2ης Πηγής (h)", min_value=0.0, step=0.1, key="an_h2")

            if st.form_submit_button("➕ Αποθήκευση Analytics Βίντεο", use_container_width=True):
                if t:
                    if "analytics" not in st.session_state.db:
                        st.session_state.db["analytics"] = []
                    
                    sources_list = []
                    if wt > 0:
                        if src_1 != "— Καμία —" and hours_1 > 0:
                            pct_1 = round((hours_1 / wt) * 100, 1)
                            sources_list.append(f"{src_1}: {hours_1}h ({pct_1}%)")
                        elif src_1 != "— Καμία —":
                            sources_list.append(src_1)
                        
                        if src_2 != "— Καμία —" and hours_2 > 0:
                            pct_2 = round((hours_2 / wt) * 100, 1)
                            sources_list.append(f"{src_2}: {hours_2}h ({pct_2}%)")
                        elif src_2 != "— Καμία —":
                            sources_list.append(src_2)
                    else:
                        if src_1 != "— Καμία —": sources_list.append(src_1)
                        if src_2 != "— Καμία —": sources_list.append(src_2)
                    
                    sources_str = ", ".join(sources_list) if sources_list else "—"

                    st.session_state.db["analytics"].append({
                        "id": str(datetime.datetime.now().timestamp()),
                        "title": t,
                        "type": typ,
                        "views": int(views),
                        "unique_viewers": int(unique_viewers),
                        "ctr": float(ctr),
                        "retention": float(ret),
                        "avd": avd or "—",
                        "new_subs": int(new_subs),
                        "watchTime": float(wt),
                        "sources": sources_str,
                        "date": str(datetime.date.today())
                    })
                    save_data(st.session_state.db)
                    st.success("✅ Τα αναλυτικά στατιστικά του βίντεο αποθηκεύτηκαν!")
                    st.rerun()
                else:
                    st.warning("⚠️ Συμπληρώστε τον τίτλο του βίντεο.")

    analytics_list = st.session_state.db.get("analytics", [])
    if analytics_list:
        with st.expander("🗑️ Διαγραφή Εγγραφής Analytics"):
            an_titles = [a.get("title", "Βίντεο") for a in analytics_list]
            selected_an_del = st.selectbox("Επιλέξτε βίντεο για διαγραφή:", an_titles, key="sel_del_an")
            if st.button("🗑️ Διαγραφή Επιλεγμένου Βίντεο", key="btn_del_an", type="primary"):
                st.session_state.db["analytics"] = [a for a in analytics_list if a.get("title") != selected_an_del]
                save_data(st.session_state.db)
                st.success(f"Η εγγραφή '{selected_an_del}' διαγράφηκε!")
                st.rerun()

    col_asort1, col_asort2, _ = st.columns([2, 1.8, 1.5])
    with col_asort1:
        sort_by_an = st.selectbox("📊 Ταξινόμηση κατά:", ["Προβολές (Views)", "Watch Time", "CTR (%)", "Retention (%)", "New Subs", "Μοναδικοί Θεατές", "Τίτλος (Α-Ω)", "Ημερομηνία"], key="sort_by_an")
    with col_asort2:
        sort_dir_an = st.radio("Σειρά:", ["Φθίνουσα ⬇️", "Αύξουσα ⬆️"], horizontal=True, key="sort_dir_an")

    is_a_desc = "Φθίνουσα" in sort_dir_an
    sorted_analytics = list(analytics_list)
    if "Προβολές" in sort_by_an:
        sorted_analytics = sorted(sorted_analytics, key=lambda x: x.get("views", 0), reverse=is_a_desc)
    elif "Watch Time" in sort_by_an:
        sorted_analytics = sorted(sorted_analytics, key=lambda x: x.get("watchTime", 0.0), reverse=is_a_desc)
    elif "CTR" in sort_by_an:
        sorted_analytics = sorted(sorted_analytics, key=lambda x: x.get("ctr", 0.0), reverse=is_a_desc)
    elif "Retention" in sort_by_an:
        sorted_analytics = sorted(sorted_analytics, key=lambda x: x.get("retention", 0.0), reverse=is_a_desc)
    elif "New Subs" in sort_by_an:
        sorted_analytics = sorted(sorted_analytics, key=lambda x: x.get("new_subs", 0), reverse=is_a_desc)
    elif "Μοναδικοί" in sort_by_an:
        sorted_analytics = sorted(sorted_analytics, key=lambda x: x.get("unique_viewers", 0), reverse=is_a_desc)
    elif "Τίτλος" in sort_by_an:
        sorted_analytics = sorted(sorted_analytics, key=lambda x: x.get("title", "").lower(), reverse=not is_a_desc)
    elif "Ημερομηνία" in sort_by_an:
        sorted_analytics = sorted(sorted_analytics, key=lambda x: x.get("date", ""), reverse=is_a_desc)

    if sorted_analytics:
        rows_an_list = []
        for a in sorted_analytics:
            typ_label = a.get("type", "Long-form")
            typ_badge = '<span style="background:rgba(244,63,94,0.25); color:#f43f5e; padding:3px 9px; border-radius:12px; font-weight:800;">Shorts</span>' if "Shorts" in typ_label else '<span style="background:rgba(59,130,246,0.25); color:#60a5fa; padding:3px 9px; border-radius:12px; font-weight:800;">Long-form</span>'
            
            ctr_val = a.get("ctr", 0.0)
            ctr_badge = f'<span style="background:rgba(16,185,129,0.2); color:#10b981; padding:3px 8px; border-radius:8px; font-weight:800;">{ctr_val}%</span>' if ctr_val >= 5.0 else f'<span style="background:rgba(234,179,8,0.2); color:#fde047; padding:3px 8px; border-radius:8px; font-weight:800;">{ctr_val}%</span>'

            ret_val = a.get("retention", 0.0)
            ret_badge = f'<span style="background:rgba(16,185,129,0.2); color:#10b981; padding:3px 8px; border-radius:8px; font-weight:800;">{ret_val}%</span>' if ret_val >= 40.0 else f'<span style="background:rgba(234,179,8,0.2); color:#fde047; padding:3px 8px; border-radius:8px; font-weight:800;">{ret_val}%</span>'

            subs_count = a.get("new_subs", 0)
            subs_badge = f'<span style="background:rgba(16,185,129,0.2); color:#10b981; padding:3px 8px; border-radius:8px; font-weight:800;">+{subs_count}</span>' if subs_count > 0 else f'<span style="color:#94a3b8;">{subs_count}</span>'

            src_str = a.get("sources", "—")
            src_html = f'<span style="background:rgba(56,189,248,0.15); color:#38bdf8; padding:3px 10px; border-radius:8px; font-weight:700;">{src_str}</span>' if src_str != "—" else '<span style="color:#94a3b8;">—</span>'

            row_an = (
                f'<tr>'
                f'<td style="font-weight:700; color:#ffffff; font-size:0.95rem;">{a.get("title", "—")}</td>'
                f'<td style="text-align:center;">{typ_badge}</td>'
                f'<td style="text-align:right; font-weight:800; color:#ffffff;">{fmt(a.get("views", 0))}</td>'
                f'<td style="text-align:right; font-weight:700; color:#cbd5e1;">{fmt(a.get("unique_viewers", 0))}</td>'
                f'<td style="text-align:center;">{ctr_badge}</td>'
                f'<td style="text-align:center;">{ret_badge}</td>'
                f'<td style="text-align:center; font-weight:700; color:#38bdf8;">{a.get("avd", "—")}</td>'
                f'<td style="text-align:center;">{subs_badge}</td>'
                f'<td style="text-align:right; font-weight:800; color:#38bdf8;">{a.get("watchTime", 0.0)} h</td>'
                f'<td>{src_html}</td>'
                f'</tr>'
            )
            rows_an_list.append(row_an)

        table_an_html = (
            '<div class="data-table-container">'
            '<table class="custom-table">'
            '<thead><tr>'
            '<th style="text-align:left;">ΤΙΤΛΟΣ ΒΙΝΤΕΟ</th>'
            '<th style="text-align:center;">ΤΥΠΟΣ</th>'
            '<th style="text-align:right;">ΠΡΟΒΟΛΕΣ</th>'
            '<th style="text-align:right;">ΜΟΝ. ΘΕΑΤΕΣ</th>'
            '<th style="text-align:center;">CTR (%)</th>'
            '<th style="text-align:center;">RETENTION (%)</th>'
            '<th style="text-align:center;">ΜΕΣΗ ΔΙΑΡΚΕΙΑ (AVD)</th>'
            '<th style="text-align:center;">NEW SUBS</th>'
            '<th style="text-align:right;">WATCH TIME</th>'
            '<th style="text-align:left;">ΠΗΓΕΣ (ΩΡΕΣ & %)</th>'
            '</tr></thead>'
            '<tbody>' + "".join(rows_an_list) + '</tbody>'
            '</table>'
            '</div>'
        )
        st.markdown(table_an_html, unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: center; color: #38bdf8; font-weight:800; padding: 40px 0;'>Δεν έχετε καταχωρήσει στατιστικά βίντεο ακόμα. Προσθέστε ένα παραπάνω!</div>", unsafe_allow_html=True)

# ------------------------------------------
# 10. KEYWORDS & TAG SCORE INTELLIGENCE
# ------------------------------------------
with tabs[9]:
    st.markdown("<h3 style='color:#38bdf8; font-weight:800;'>🔑 YouTube Keywords & Tag Score Intelligence</h3>", unsafe_allow_html=True)
    
    col_q1, col_q2, col_q3 = st.columns([2.5, 1.2, 1.2])
    with col_q1:
        quick_kw = st.text_input("🔎 Γρήγορη Έρευνα Tag / Keyword:", placeholder="π.χ. Spinning για Λαβράκια...")
    with col_q2:
        st.write("")
        st.write("")
        if st.button("🔴 YouTube Search", use_container_width=True):
            if quick_kw:
                st.markdown(f'<a href="https://www.youtube.com/results?search_query={urllib.parse.quote(quick_kw)}" target="_blank"><button style="width:100%; padding:10px; background:#ef4444; color:#fff; border-radius:8px; border:none; font-weight:700;">Άνοιγμα στο YouTube ↗</button></a>', unsafe_allow_html=True)
            else:
                st.warning("Γράψτε πρώτα μια λέξη.")
    with col_q3:
        st.write("")
        st.write("")
        if st.button("📈 Google Trends", use_container_width=True):
            if quick_kw:
                st.markdown(f'<a href="https://trends.google.com/trends/explore?q={urllib.parse.quote(quick_kw)}&geo=GR" target="_blank"><button style="width:100%; padding:10px; background:#3b82f6; color:#fff; border-radius:8px; border:none; font-weight:700;">Άνοιγμα στο Trends ↗</button></a>', unsafe_allow_html=True)
            else:
                st.warning("Γράψτε πρώτα μια λέξη.")

    with st.expander("➕ Προσθήκη Νέου Tag με Σκορ & Κατάταξη (TubeBuddy / SEO)"):
        with st.form("kw_advanced_form", clear_on_submit=True):
            k_c1, k_c2 = st.columns(2)
            with k_c1:
                kw_tag = st.text_input("Λέξη-Κλειδί / Tag (π.χ. LRF τεχνική)")
                kw_target = st.text_input("Target Βίντεο (προαιρετικό)")
                kw_my_rank = st.text_input("🟢 Θέση Κατάταξής μου στο YouTube (π.χ. #3)")
                kw_tb_rank = st.text_input("🔵 TubeBuddy Trending Rank (π.χ. #1)")
            with k_c2:
                kw_overall_score = st.number_input("📊 Overall Keyword Score (0 - 100)", min_value=0, max_value=100, value=60, step=1)
                kw_volume = st.selectbox("📊 Search Volume (Όγκος Αναζήτησης)", ["Πολύ Υψηλός", "Υψηλός", "Μέτριος", "Χαμηλός"])
                kw_comp = st.selectbox("⚔️ Competition (Ανταγωνισμός)", ["Πολύ Χαμηλός", "Χαμηλός", "Μέτριος", "Υψηλός", "Πολύ Υψηλός"])
                kw_opt = st.selectbox("🎯 Optimization Strength", ["Εξαιρετική (90-100%)", "Καλή (70-89%)", "Μέτρια (50-69%)", "Χαμηλή (<50%)"])

            k_c3, k_c4 = st.columns(2)
            with k_c3:
                kw_priority = st.selectbox("Προτεραιότητα", ["Υψηλή", "Μεσαία", "Χαμηλή"])
            with k_c4:
                kw_status = st.selectbox("Status", ["Νέα", "Σε χρήση", "Ολοκληρώθηκε"])

            if st.form_submit_button("➕ Αποθήκευση Tag & Σκορ", use_container_width=True):
                if kw_tag:
                    if "keywords" not in st.session_state.db:
                        st.session_state.db["keywords"] = []
                    st.session_state.db["keywords"].append({
                        "id": str(datetime.datetime.now().timestamp()),
                        "tag": kw_tag,
                        "target": kw_target or "—",
                        "my_rank": kw_my_rank or "—",
                        "tb_rank": kw_tb_rank or "—",
                        "score": int(kw_overall_score),
                        "volume": kw_volume,
                        "competition": kw_comp,
                        "optimization": kw_opt,
                        "priority": kw_priority,
                        "status": kw_status,
                        "date": str(datetime.date.today())
                    })
                    save_data(st.session_state.db)
                    st.success("✅ Το Tag και τα στατιστικά του αποθηκεύτηκαν!")
                    st.rerun()
                else:
                    st.warning("⚠️ Συμπληρώστε τη λέξη-κλειδί.")

    keywords_list = st.session_state.db.get("keywords", [])
    if keywords_list:
        with st.expander("🗑️ Διαγραφή Tag / Keyword"):
            kw_names = [k.get("tag", "Tag") for k in keywords_list]
            selected_kw_del = st.selectbox("Επιλέξτε Tag για διαγραφή:", kw_names, key="sel_del_kw")
            if st.button("🗑️ Διαγραφή Επιλεγμένου Tag", key="btn_del_kw", type="primary"):
                st.session_state.db["keywords"] = [k for k in keywords_list if k.get("tag") != selected_kw_del]
                save_data(st.session_state.db)
                st.success(f"Το Tag '{selected_kw_del}' διαγράφηκε!")
                st.rerun()

    col_ksort1, col_ksort2, _ = st.columns([2, 1.8, 1.5])
    with col_ksort1:
        sort_by_kw = st.selectbox(
            "📊 Ταξινόμηση κατά:",
            ["Overall Score", "🟢 Θέση μου", "🔵 TubeBuddy #", "Tag (Α-Ω)", "Προτεραιότητα", "Status"],
            key="sort_by_kw"
        )
    with col_ksort2:
        sort_dir_kw = st.radio("Σειρά:", ["Φθίνουσα ⬇️", "Αύξουσα ⬆️"], horizontal=True, key="sort_dir_kw")

    is_k_desc = "Φθίνουσα" in sort_dir_kw
    sorted_keywords = list(keywords_list)
    if sort_by_kw == "Overall Score":
        sorted_keywords = sorted(sorted_keywords, key=lambda x: x.get("score", 0), reverse=is_k_desc)
    elif "🟢" in sort_by_kw:
        sorted_keywords = sorted(sorted_keywords, key=lambda x: str(x.get("my_rank", "")), reverse=not is_k_desc)
    elif "🔵" in sort_by_kw:
        sorted_keywords = sorted(sorted_keywords, key=lambda x: str(x.get("tb_rank", "")), reverse=not is_k_desc)
    elif "Tag" in sort_by_kw:
        sorted_keywords = sorted(sorted_keywords, key=lambda x: x.get("tag", "").lower(), reverse=not is_k_desc)
    elif "Προτεραιότητα" in sort_by_kw:
        sorted_keywords = sorted(sorted_keywords, key=lambda x: x.get("priority", ""), reverse=is_k_desc)
    elif "Status" in sort_by_kw:
        sorted_keywords = sorted(sorted_keywords, key=lambda x: x.get("status", ""), reverse=is_k_desc)

    if sorted_keywords:
        rows_kw_list = []
        for k in sorted_keywords:
            prio = k.get("priority", "Μεσαία")
            if prio == "Υψηλή":
                prio_html = '<span style="background:rgba(239,68,68,0.25); color:#fca5a5; padding:3px 9px; border-radius:12px; font-weight:800;">Υψηλή</span>'
            elif prio == "Μεσαία":
                prio_html = '<span style="background:rgba(234,179,8,0.25); color:#fde047; padding:3px 9px; border-radius:12px; font-weight:800;">Μεσαία</span>'
            else:
                prio_html = '<span style="background:rgba(59,130,246,0.25); color:#93c5fd; padding:3px 9px; border-radius:12px; font-weight:800;">Χαμηλή</span>'

            row_kw = (
                f'<tr>'
                f'<td style="font-weight:800; color:#38bdf8; font-size:1rem;">{k.get("tag", "—")}</td>'
                f'<td style="text-align:center;">{rank_badge(k.get("my_rank"), is_my=True)}</td>'
                f'<td style="text-align:center;">{rank_badge(k.get("tb_rank"), is_my=False)}</td>'
                f'<td style="text-align:center;">{score_badge(k.get("score"))}</td>'
                f'<td style="text-align:center; font-weight:700;">{k.get("volume", "—")}</td>'
                f'<td style="text-align:center; font-weight:700;">{k.get("competition", "—")}</td>'
                f'<td style="text-align:center; font-weight:700;">{k.get("optimization", "—")}</td>'
                f'<td style="font-weight:600; color:#cbd5e1;">{k.get("target", "—")}</td>'
                f'<td style="text-align:center;">{prio_html}</td>'
                f'<td style="text-align:center; font-weight:700; color:#ffffff;">{k.get("status", "Νέα")}</td>'
                f'</tr>'
            )
            rows_kw_list.append(row_kw)

        table_kw_html = (
            '<div class="data-table-container">'
            '<table class="custom-table">'
            '<thead><tr>'
            '<th style="text-align:left;">TAG / KEYWORD</th>'
            '<th style="text-align:center;">🟢 ΘΕΣΗ ΜΟΥ</th>'
            '<th style="text-align:center;">🔵 TUBEBUDDY #</th>'
            '<th style="text-align:center;">📊 OVERALL SCORE</th>'
            '<th style="text-align:center;">📈 SEARCH VOL.</th>'
            '<th style="text-align:center;">⚔️ COMPETITION</th>'
            '<th style="text-align:center;">🎯 OPTIMIZATION</th>'
            '<th style="text-align:left;">TARGET ΒΙΝΤΕΟ</th>'
            '<th style="text-align:center;">ΠΡΟΤΕΡΑΙΟΤΗΤΑ</th>'
            '<th style="text-align:center;">STATUS</th>'
            '</tr></thead>'
            '<tbody>' + "".join(rows_kw_list) + '</tbody>'
            '</table>'
            '</div>'
        )
        st.markdown(table_kw_html, unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: center; color: #38bdf8; font-weight:800; padding: 40px 0;'>Δεν έχετε καταχωρήσει Tags / Keywords ακόμα. Προσθέστε ένα παραπάνω!</div>", unsafe_allow_html=True)

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
        st.markdown("<div style='text-align: center; color: #38bdf8; font-weight:800; padding: 40px 0;'>Δεν υπάρχουν αποθηκευμένα prompts. Πρόσθεσε ένα παραπάνω.</div>", unsafe_allow_html=True)

# ------------------------------------------
# 14. THUMBNAIL AI EDITOR
# ------------------------------------------
with tabs[13]:
    st.markdown("<h3 style='color:#38bdf8; font-weight:800;'>🖼️ Thumbnail AI Editor</h3>", unsafe_allow_html=True)
    img_file = st.file_uploader("Ανεβάστε thumbnail ανταγωνιστή", type=["png", "jpg", "jpeg", "webp"])
    if img_file:
        st.image(img_file, caption="Competitor Thumbnail", width=400)
        st.code("High-impact YouTube thumbnail, dramatic lighting, intense composition, vivid neon highlights (#facc15, #ef4444), photorealistic detail, 8k resolution, cinematic depth of field, bold text safe zone on left third --ar 16:9 --v 6.0", language="text")
