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
# ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ
# ==========================================
st.set_page_config(
    page_title="Video Creator Hub & Competitor Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# ΑΥΘΕΝΤΙΚΟ DARK THEME & TABS CSS
# ==========================================
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
    background-color: #0b0f19 !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(168, 85, 247, 0.12) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(59, 130, 246, 0.12) 0px, transparent 50%) !important;
    background-attachment: fixed !important;
    color: #f8fafc !important;
}

[data-testid="stSidebar"] {
    background-color: #111827 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}
[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}

/* ========================================================
   TABS BAR (ΜΕΝΟΥ ΚΑΡΤΕΛΩΝ ΜΕ ΧΡΩΜΑΤΑ ΑΝΑ ΚΑΡΤΕΛΑ)
   ======================================================== */
[data-baseweb="tab-list"] {
    display: flex !important;
    gap: 8px !important;
    margin-bottom: 25px !important;
    flex-wrap: wrap !important;
    justify-content: center !important;
    background: rgba(21, 28, 44, 0.6) !important;
    padding: 8px !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(12px) !important;
    width: 100% !important;
}

button[data-baseweb="tab"] {
    background: transparent !important;
    color: #94a3b8 !important;
    border: 1px solid transparent !important;
    padding: 10px 18px !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

button[data-baseweb="tab"]:hover {
    color: #ffffff !important;
    background: rgba(255, 255, 255, 0.05) !important;
}

[data-baseweb="tab-highlight"] {
    display: none !important;
}

/* Χρώματα Active Tabs */
button[data-baseweb="tab"]:nth-of-type(1)[aria-selected="true"] { background: linear-gradient(135deg, #2e1065 0%, #a855f7 100%) !important; border-color: #c084fc !important; color:#fff !important; box-shadow: 0 4px 14px rgba(168, 85, 247, 0.4) !important; }
button[data-baseweb="tab"]:nth-of-type(2)[aria-selected="true"] { background: linear-gradient(135deg, #450a0a 0%, #ef4444 100%) !important; border-color: #fca5a5 !important; color:#fff !important; }
button[data-baseweb="tab"]:nth-of-type(3)[aria-selected="true"] { background: linear-gradient(135deg, #4c0519 0%, #f43f5e 100%) !important; border-color: #fecdd3 !important; color:#fff !important; }
button[data-baseweb="tab"]:nth-of-type(4)[aria-selected="true"] { background: linear-gradient(135deg, #500724 0%, #ec4899 100%) !important; border-color: #fbcfe8 !important; color:#fff !important; }
button[data-baseweb="tab"]:nth-of-type(5)[aria-selected="true"] { background: linear-gradient(135deg, #083344 0%, #06b6d4 100%) !important; border-color: #a5f3fc !important; color:#fff !important; }
button[data-baseweb="tab"]:nth-of-type(6)[aria-selected="true"] { background: linear-gradient(135deg, #312e81 0%, #4f46e5 100%) !important; border-color: #818cf8 !important; color:#fff !important; }
button[data-baseweb="tab"]:nth-of-type(7)[aria-selected="true"] { background: linear-gradient(135deg, #831843 0%, #db2777 100%) !important; border-color: #f472b6 !important; color:#fff !important; }
button[data-baseweb="tab"]:nth-of-type(8)[aria-selected="true"] { background: linear-gradient(135deg, #172554 0%, #3b82f6 100%) !important; border-color: #bfdbfe !important; color:#fff !important; }
button[data-baseweb="tab"]:nth-of-type(9)[aria-selected="true"] { background: linear-gradient(135deg, #022c22 0%, #10b981 100%) !important; border-color: #a7f3d0 !important; color:#fff !important; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4) !important; }
button[data-baseweb="tab"]:nth-of-type(10)[aria-selected="true"] { background: linear-gradient(135deg, #431407 0%, #f97316 100%) !important; border-color: #fed7aa !important; color:#fff !important; }
button[data-baseweb="tab"]:nth-of-type(11)[aria-selected="true"] { background: linear-gradient(135deg, #1e1b4b 0%, #6366f1 100%) !important; border-color: #c7d2fe !important; color:#fff !important; }
button[data-baseweb="tab"]:nth-of-type(12)[aria-selected="true"] { background: linear-gradient(135deg, #083344 0%, #22d3ee 100%) !important; border-color: #a5f3fc !important; color:#fff !important; }
button[data-baseweb="tab"]:nth-of-type(13)[aria-selected="true"] { background: linear-gradient(135deg, #422006 0%, #ca8a04 100%) !important; border-color: #fef08a !important; color:#fff !important; }
button[data-baseweb="tab"]:nth-of-type(14)[aria-selected="true"] { background: linear-gradient(135deg, #4c0519 0%, #e11d48 100%) !important; border-color: #fecdd3 !important; color:#fff !important; }

/* ========================================================
   ΠΙΝΑΚΑΣ COMPETITORS (INDEX.HTML STYLE)
   ======================================================== */
.data-table-container {
    background: #151c2c;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 30px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.35);
    overflow-x: auto;
    width: 100%;
}

.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
    text-align: left;
}

.custom-table th {
    background: rgba(13, 19, 34, 0.95);
    color: #94a3b8;
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 16px 18px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.custom-table td {
    padding: 14px 18px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    color: #f8fafc;
}

.custom-table tr:hover {
    background-color: rgba(255, 255, 255, 0.03);
}

.custom-table tr.my-row {
    background: linear-gradient(90deg, rgba(168, 85, 247, 0.18) 0%, transparent 100%) !important;
    border-left: 4px solid #facc15 !important;
}

.badge-you {
    background: #facc15;
    color: #000;
    font-size: 0.7rem;
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 700;
    margin-left: 6px;
}

.growth-up { color: #10b981; font-weight: 600; }
.growth-down { color: #ef4444; font-weight: 600; }
.growth-flat { color: #94a3b8; }

/* Buttons & Inputs */
[data-testid="stDownloadButton"] > button {
    background-color: #7c3aed !important;
    border: 1px solid #8b5cf6 !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
[data-testid="stFileUploader"] section {
    background-color: #151c2c !important;
    border: 2px dashed rgba(255, 255, 255, 0.15) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] {
    background-color: #151c2c !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    margin-bottom: 15px !important;
}
[data-testid="stExpander"] summary {
    background-color: #1e293b !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary * {
    color: #38bdf8 !important;
    font-weight: 600 !important;
}
div.stButton > button {
    background-color: #1e293b !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
div.stButton > button:hover {
    background-color: #334155 !important;
    border-color: #38bdf8 !important;
    color: #38bdf8 !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DATA_FILE = "creator_hub_data.json"

# ==========================================
# 24 ΕΛΛΗΝΙΚΑ ΚΑΝΑΛΙΑ (ΜΕ ΣΩΣΤΑ HANDLES)
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
        "api_key": "",
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
                    "subs": subs,
                    "totalViews": views,
                    "videos": videos,
                    "avgViews": avg_views,
                    "viewsPerSub": views_per_sub,
                    "efficiency": efficiency
                }
        return out
    except Exception as e:
        st.error(f"Σφάλμα API: {e}")
        return {}

def fmt(n):
    return "—" if not n else f"{n:,}".replace(",", ".")

# ==========================================
# LOGIN SCREEN
# ==========================================
def check_password():
    if st.session_state.authenticated:
        return True

    st.markdown("<h2 style='text-align: center; margin-top:50px; color:#ffffff;'>🔒 Video Creator Hub</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Βάλτε τον κωδικό πρόσβασης για να ξεκλειδώσετε το εργαλείο.</p>", unsafe_allow_html=True)
    
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
    st.markdown("<h2 style='color:#38bdf8;'>🎬 Creator Hub</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("🔑 YouTube Data API Key")
    api_key_input = st.text_input(
        "API Key (v3)",
        value=st.session_state.db.get("api_key", ""),
        type="password",
        help="Απαιτείται για τον συγχρονισμό στατιστικών."
    )
    if st.button("💾 Αποθήκευση Key", use_container_width=True):
        st.session_state.db["api_key"] = api_key_input
        save_data(st.session_state.db)
        st.success("Το API Key αποθηκεύτηκε!")

    st.markdown("---")
    st.subheader("💾 Backup & Επαναφορά")
    
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
        st.success("Φορτώθηκαν όλα τα 24 κανάλια!")
        st.rerun()

# ==========================================
# ΚΥΡΙΩΣ TABS
# ==========================================
st.markdown("<h1 style='text-align: center; color:#ffffff; margin-bottom: 25px;'>🎬 Video Creator Hub & Competitor Intelligence</h1>", unsafe_allow_html=True)

tabs = st.tabs([
    "📊 Dashboard",
    "🎬 Long-Form",
    "📱 Shorts",
    "📸 Reels",
    "🎵 TikTok",
    "📜 Prompts",
    "🖼️ Thumbnail AI",
    "📅 Πρόγραμμα",
    "🇬🇷 Competitors GR",
    "🌐 Competitors Intl",
    "📈 Analytics",
    "🔑 Keywords",
    "💡 Ιδέες",
    "🎯 Στόχοι"
])

# ------------------------------------------
# 1. DASHBOARD
# ------------------------------------------
with tabs[0]:
    st.subheader("🏠 Επισκόπηση Καναλιού & Ανταγωνισμού")
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

# ------------------------------------------
# 2-5. STRATEGY TABS
# ------------------------------------------
strat_map = [("yt", tabs[1], "🎬 Long-Form"), ("shorts", tabs[2], "⚡ Shorts"), ("meta", tabs[3], "📸 FB & IG Reels"), ("tiktok", tabs[4], "🎵 TikTok")]
for key, t_view, t_title in strat_map:
    with t_view:
        st.subheader(f"{t_title} Strategy")
        items = st.session_state.db["strategies"].get(key, [])
        for idx, item in enumerate(items):
            with st.expander(f"📌 {item['step']}", expanded=True):
                st.write(item["desc"])

# ------------------------------------------
# 6. PROMPTS LIBRARY
# ------------------------------------------
with tabs[5]:
    st.subheader("📜 Prompts Library")
    for p in st.session_state.db.get("prompts", []):
        st.markdown(f"**{p['title']}**")
        st.code(p["body"], language="text")

# ------------------------------------------
# 7. THUMBNAIL AI
# ------------------------------------------
with tabs[6]:
    st.subheader("🖼️ Thumbnail AI Prompt Reverser")
    img_file = st.file_uploader("Ανεβάστε εικόνα thumbnail", type=["png", "jpg", "jpeg", "webp"])
    if img_file:
        st.image(img_file, caption="Competitor Thumbnail", width=400)
        st.code("High-impact YouTube thumbnail, dramatic lighting, intense composition, vivid neon highlights (#facc15, #ef4444), photorealistic detail, 8k resolution, cinematic depth of field, bold text safe zone on left third --ar 16:9 --v 6.0", language="text")

# ------------------------------------------
# 8. SCHEDULE
# ------------------------------------------
with tabs[7]:
    st.subheader("📅 Πρόγραμμα Δημοσιεύσεων")
    sched = st.session_state.db.get("schedule", [])
    if sched:
        st.dataframe(pd.DataFrame(sched)[["date", "time", "platform", "title", "status"]], use_container_width=True, hide_index=True)

# ------------------------------------------
# 9. GREEK COMPETITORS (FULL HTML TABLE - EXACT INDEX.HTML)
# ------------------------------------------
with tabs[8]:
    comps = st.session_state.db.get("competitors_gr", [])
    st.subheader(f"🇬🇷 Έλληνες Competitors ({len(comps)} Κανάλια)")
    api_key = st.session_state.db.get("api_key", "")
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🔄 Ανανέωση Όλων (Sync API)", use_container_width=True):
            if not api_key:
                st.error("Βάλτε πρώτα το YouTube API Key στη Sidebar!")
            else:
                ids = []
                for c in comps:
                    cid = resolve_handle(api_key, c["handle"])
                    c["resolvedId"] = cid
                    if cid:
                        ids.append(cid)
                
                stats_map = fetch_channel_stats(api_key, ids)
                for c in comps:
                    cid = c.get("resolvedId")
                    if cid and cid in stats_map:
                        old_subs = c.get("subs", 0)
                        c.update(stats_map[cid])
                        new_subs = c.get("subs", 0)
                        if old_subs > 0:
                            c["growth"] = round(((new_subs - old_subs) / old_subs) * 100, 2)
                        else:
                            c["growth"] = 0.0
                
                # Sync My Channel
                my_c = st.session_state.db["my_channel"]
                my_id = resolve_handle(api_key, my_c["handle"])
                if my_id and my_id in stats_map:
                    my_c.update(stats_map[my_id])
                    
                save_data(st.session_state.db)
                st.success("✅ Όλα τα κανάλια ανανεώθηκαν!")
                st.rerun()

    # ΠΡΟΣΘΗΚΗ & ΔΙΑΓΡΑΦΗ ΚΑΝΑΛΙΩΝ
    col_add, col_del = st.columns(2)
    with col_add:
        with st.expander("➕ Προσθήκη Νέου Καναλιού"):
            with st.form("add_comp_gr"):
                c_name = st.text_input("Όνομα Καναλιού")
                c_handle = st.text_input("@handle ή Channel ID (UC...)")
                if st.form_submit_button("➕ Προσθήκη"):
                    if c_name and c_handle:
                        st.session_state.db["competitors_gr"].append({
                            "name": c_name, "handle": c_handle, **blank_stats()
                        })
                        save_data(st.session_state.db)
                        st.rerun()

    with col_del:
        with st.expander("🗑️ Διαγραφή Καναλιού"):
            comp_names = [c["name"] for c in comps]
            if comp_names:
                selected_del = st.selectbox("Επιλέξτε κανάλι για διαγραφή:", comp_names)
                if st.button("🗑️ Διαγραφή Επιλεγμένου", type="primary"):
                    st.session_state.db["competitors_gr"] = [c for c in comps if c["name"] != selected_del]
                    save_data(st.session_state.db)
                    st.success(f"Το κανάλι '{selected_del}' διαγράφηκε!")
                    st.rerun()

    # ΤΑΞΙΝΟΜΗΣΗ ΚΑΤΑ SUBSCRIBERS
    sorted_comps = sorted(comps, key=lambda x: x.get("subs", 0), reverse=True)

    # ΚΑΤΑΣΚΕΥΗ ΑΥΘΕΝΤΙΚΟΥ HTML ΠΙΝΑΚΑ
    rows_html = ""
    for c in sorted_comps:
        is_my = "tsouros" in c["name"].lower()
        row_cls = "my-row" if is_my else ""
        badge = '<span class="badge-you">Εσύ</span>' if is_my else ""
        
        growth = c.get("growth", 0.0)
        if growth > 0:
            growth_html = f'<span class="growth-up">+{growth}%</span>'
        elif growth < 0:
            growth_html = f'<span class="growth-down">{growth}%</span>'
        else:
            growth_html = '<span class="growth-flat">0%</span>'

        rows_html += f"""
        <tr class="{row_cls}">
            <td style="font-weight:600;">{c['name']} {badge}</td>
            <td style="text-align:right; font-weight:700; color:#ffffff;">{fmt(c.get('subs', 0))}</td>
            <td style="text-align:right;">{fmt(c.get('totalViews', 0))}</td>
            <td style="text-align:right;">{fmt(c.get('videos', 0))}</td>
            <td style="text-align:right;">{fmt(c.get('avgViews', 0))}</td>
            <td style="text-align:right;">{c.get('viewsPerSub', 0.0)}</td>
            <td style="text-align:right;">{c.get('efficiency', 0.0)}</td>
            <td style="text-align:center;">{growth_html}</td>
        </tr>
        """

    table_html = f"""
    <div class="data-table-container">
        <table class="custom-table">
            <thead>
                <tr>
                    <th style="text-align:left;">CHANNEL</th>
                    <th style="text-align:right;">SUBSCRIBERS (ΑΚΡΙΒΗΣ)</th>
                    <th style="text-align:right;">TOTAL VIEWS</th>
                    <th style="text-align:right;">VIDEOS</th>
                    <th style="text-align:right;">AVG VIEWS</th>
                    <th style="text-align:right;">VIEWS/SUB</th>
                    <th style="text-align:right;">EFFICIENCY</th>
                    <th style="text-align:center;">GROWTH</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

# ------------------------------------------
# 10. INTL COMPETITORS
# ------------------------------------------
with tabs[9]:
    comps_intl = st.session_state.db.get("competitors_intl", [])
    st.subheader(f"🌐 Ξένοι Competitors ({len(comps_intl)} Κανάλια)")
    sorted_intl = sorted(comps_intl, key=lambda x: x.get("subs", 0), reverse=True)
    rows_intl_html = ""
    for c in sorted_intl:
        rows_intl_html += f"""
        <tr>
            <td style="font-weight:600;">{c['name']}</td>
            <td>{c.get('country', '—')}</td>
            <td style="text-align:right; font-weight:700;">{fmt(c.get('subs', 0))}</td>
            <td style="text-align:right;">{fmt(c.get('totalViews', 0))}</td>
            <td style="text-align:right;">{fmt(c.get('videos', 0))}</td>
            <td style="text-align:right;">{fmt(c.get('avgViews', 0))}</td>
            <td style="text-align:right;">{c.get('efficiency', 0.0)}</td>
        </tr>
        """
    table_intl_html = f"""
    <div class="data-table-container">
        <table class="custom-table">
            <thead>
                <tr>
                    <th>CHANNEL</th>
                    <th>ΧΩΡΑ</th>
                    <th style="text-align:right;">SUBSCRIBERS</th>
                    <th style="text-align:right;">TOTAL VIEWS</th>
                    <th style="text-align:right;">VIDEOS</th>
                    <th style="text-align:right;">AVG VIEWS</th>
                    <th style="text-align:right;">EFFICIENCY</th>
                </tr>
            </thead>
            <tbody>
                {rows_intl_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(table_intl_html, unsafe_allow_html=True)

# ------------------------------------------
# 11. ANALYTICS
# ------------------------------------------
with tabs[10]:
    st.subheader("📈 Analytics & Video History")
    an = st.session_state.db.get("analytics", [])
    if an:
        st.dataframe(pd.DataFrame(an), use_container_width=True, hide_index=True)

# ------------------------------------------
# 12. KEYWORDS
# ------------------------------------------
with tabs[11]:
    st.subheader("🔑 Keywords")
    kws = st.session_state.db.get("keywords", [])
    if kws:
        st.dataframe(pd.DataFrame(kws), use_container_width=True, hide_index=True)

# ------------------------------------------
# 13. IDEAS
# ------------------------------------------
with tabs[12]:
    st.subheader("💡 Ιδέες για Βίντεο")
    for i in st.session_state.db.get("ideas", []):
        st.markdown(f"**💡 {i['text']}**")
        st.caption(f"🏷️ {', '.join(i.get('tags', []))} | 📅 {i.get('date')}")
        st.markdown("---")

# ------------------------------------------
# 14. GOALS
# ------------------------------------------
with tabs[13]:
    st.subheader("🎯 Μηνιαίοι Στόχοι")
    gls = st.session_state.db.get("goals", [])
    if gls:
        st.dataframe(pd.DataFrame(gls), use_container_width=True, hide_index=True)
