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
# ΠΛΗΡΕΣ ΚΑΙ ΔΙΟΡΘΩΜΕΝΟ CSS
# ==========================================
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* Κεντρικό Φόντο */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
    background-color: #0b0f19 !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(168, 85, 247, 0.12) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(59, 130, 246, 0.12) 0px, transparent 50%) !important;
    background-attachment: fixed !important;
    color: #f8fafc !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111827 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}
[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}

/* ========================================================
   1. ΔΙΟΡΘΩΣΗ ΚΑΡΤΕΛΩΝ (TABS - MODERN PILL BAR)
   ======================================================== */
[data-baseweb="tab-list"] {
    background: rgba(21, 28, 44, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 14px !important;
    padding: 6px !important;
    gap: 6px !important;
    display: flex !important;
    flex-wrap: wrap !important;
    margin-bottom: 25px !important;
    backdrop-filter: blur(10px) !important;
}

button[data-baseweb="tab"] {
    background: transparent !important;
    color: #94a3b8 !important;
    border-radius: 10px !important;
    padding: 8px 16px !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    border: 1px solid transparent !important;
    transition: all 0.2s ease !important;
}

button[data-baseweb="tab"]:hover {
    color: #ffffff !important;
    background: rgba(255, 255, 255, 0.08) !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
    color: #ffffff !important;
    border: 1px solid #a855f7 !important;
    box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4) !important;
}

[data-baseweb="tab-highlight"] {
    display: none !important;
}

/* ========================================================
   2. ΔΙΟΡΘΩΣΗ DOWNLOAD BUTTON (EXPORT BACKUP)
   ======================================================== */
[data-testid="stDownloadButton"] > button,
[data-testid="stDownloadButton"] button,
.stDownloadButton button {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 10px !important;
    padding: 10px 16px !important;
    font-weight: 600 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #334155 !important;
    border-color: #38bdf8 !important;
    color: #38bdf8 !important;
}

/* ========================================================
   3. ΔΙΟΡΘΩΣΗ FILE UPLOADER (IMPORT BACKUP)
   ======================================================== */
[data-testid="stFileUploader"] {
    background-color: transparent !important;
}
[data-testid="stFileUploader"] section {
    background-color: #151c2c !important;
    border: 2px dashed rgba(255, 255, 255, 0.2) !important;
    border-radius: 12px !important;
    padding: 15px !important;
}
[data-testid="stFileUploader"] section * {
    color: #94a3b8 !important;
}
[data-testid="stFileUploader"] section button {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"] section button:hover {
    background-color: #334155 !important;
    border-color: #38bdf8 !important;
}

/* ========================================================
   4. ΔΙΟΡΘΩΣΗ EXPANDERS (ΣΚΟΥΡΟ CARD ΑΝΤΙ ΓΙΑ ΛΕΥΚΟ)
   ======================================================== */
[data-testid="stExpander"] {
    background-color: #151c2c !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 12px !important;
    margin-bottom: 12px !important;
}
[data-testid="stExpander"] summary {
    background-color: #1e293b !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary:hover {
    background-color: #2a374d !important;
}
[data-testid="stExpander"] summary * {
    color: #38bdf8 !important;
    fill: #38bdf8 !important;
    font-weight: 600 !important;
}
[data-testid="stExpander"] div[role="region"] {
    background-color: #151c2c !important;
    color: #f8fafc !important;
}

/* ========================================================
   5. ΔΙΟΡΘΩΣΗ ΓΕΝΙΚΩΝ ΚΟΥΜΠΙΩΝ & INPUTS
   ======================================================== */
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

input, textarea, select {
    background-color: #0d1322 !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
}

label, label p, [data-testid="stWidgetLabel"] p {
    color: #38bdf8 !important;
    font-weight: 600 !important;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DATA_FILE = "creator_hub_data.json"

# ==========================================
# 24 ΕΛΛΗΝΙΚΑ & 2 ΞΕΝΑ ΚΑΝΑΛΙΑ
# ==========================================
SEED_COMPETITORS_GR = [
    {"name": "Tsouros Marine", "handle": "UC5cxxXjrQcHnWqh_KtiCpDg"},
    {"name": "Milonakis Kayak Fishing", "handle": "UCw9pG7yAviPN8RluqZJ7Uiw"},
    {"name": "Spinning By Tyrikos", "handle": "UC08kPE-YyUVe2gQac8nCqqw"},
    {"name": "Owrka", "handle": "UCpy-2GjgEjnx97N_aan0XFQ"},
    {"name": "Giorgos Kazoulis", "handle": "@giorgoskazoulis"},
    {"name": "Kostas Antoniadis", "handle": "@KostasAntoniadis"},
    {"name": "ZAVRAS FISHING", "handle": "@ZavrasFishing"},
    {"name": "Μάρκος Βιδάλης", "handle": "@MarkosVidalis"},
    {"name": "GB Luring", "handle": "@GBLuring"},
    {"name": "SifisFishing", "handle": "@SifisFishing"},
    {"name": "Paraktios Fishing", "handle": "@paraktiosfishing"},
    {"name": "Giannis Mastrogiannakis", "handle": "@giannismastrogiannakis"},
    {"name": "Fishing Time GR", "handle": "@FishingTimeGR"},
    {"name": "Sea Fishing Greece", "handle": "@seafishinggreece"},
    {"name": "Captain Hook Fishing", "handle": "@captainhookfishing"},
    {"name": "Luring Mania", "handle": "@luringmania"},
    {"name": "Deep Blue Fishing", "handle": "@deepbluefishing"},
    {"name": "Aegean Anglers", "handle": "@aegeananglers"},
    {"name": "Rock Fishing Greece", "handle": "@rockfishinggreece"},
    {"name": "Shore Jigging Hellas", "handle": "@shorejigginghellas"},
    {"name": "Hellenic Fishing Hunters", "handle": "@hellenicfishinghunters"},
    {"name": "Fishing Club GR", "handle": "@fishingclubgr"},
    {"name": "Kalamaria Anglers", "handle": "@kalamariaanglers"},
    {"name": "Greek Sea Adventures", "handle": "@greekseaadventures"}
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
            if len(data.get("competitors_gr", [])) < len(SEED_COMPETITORS_GR):
                existing_gr = {c["name"] for c in data.get("competitors_gr", [])}
                for c in SEED_COMPETITORS_GR:
                    if c["name"] not in existing_gr:
                        data["competitors_gr"].append({**c, **blank_stats()})
            if len(data.get("competitors_intl", [])) < len(SEED_COMPETITORS_INTL):
                existing_intl = {c["name"] for c in data.get("competitors_intl", [])}
                for c in SEED_COMPETITORS_INTL:
                    if c["name"] not in existing_intl:
                        data["competitors_intl"].append({**c, **blank_stats()})
            save_data(data)
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
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={','.join(channel_ids)}&key={api_key}"
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
                views_per_sub = round(avg_views / subs, 4) if subs > 0 else 0
                efficiency = round((avg_views / subs) * 1000, 2) if subs > 0 else 0
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
        st.error(f"Σφάλμα επικοινωνίας με YouTube API: {e}")
        return {}

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
        st.success("Φορτώθηκαν όλα τα κανάλια!")
        st.rerun()

# ==========================================
# ΚΥΡΙΩΣ TABS
# ==========================================
st.markdown("<h1 style='color:#ffffff; margin-bottom: 20px;'>🎬 Video Creator Hub & Competitor Intelligence</h1>", unsafe_allow_html=True)

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
        st.metric("📺 Το Κανάλι Μου (Subs)", f"{my_ch.get('subs', 0):,}", f"{my_ch.get('name', 'Tsouros Marine')}")
    with c2:
        synced_c = [c for c in all_comp if c.get("subs", 0) > 0]
        avg_subs = round(sum(c.get("subs", 0) for c in synced_c) / len(synced_c)) if synced_c else 0
        st.metric("👥 Μ.Ο. Subs Competitors", f"{avg_subs:,}", f"{len(all_comp)} κανάλια")
    with c3:
        avg_views = round(sum(c.get("avgViews", 0) for c in synced_c) / len(synced_c)) if synced_c else 0
        st.metric("👀 Μ.Ο. Avg Views", f"{avg_views:,}")
    with c4:
        st.metric("💡 Ιδέες σε Αναμονή", len(st.session_state.db.get("ideas", [])))

    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📅 Επόμενα Προγραμματισμένα")
        sched = st.session_state.db.get("schedule", [])
        if sched:
            df_sched = pd.DataFrame(sched)
            st.dataframe(df_sched[["date", "platform", "title", "status"]].head(5), use_container_width=True, hide_index=True)
        else:
            st.info("Δεν υπάρχουν προγραμματισμένα βίντεο.")

    with col_b:
        st.subheader("⚖️ Benchmark vs Ανταγωνιστές")
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
        else:
            st.info("Συγχρονίστε τα κανάλια από την καρτέλα Competitors για να δείτε το benchmark.")

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
        with st.form(f"add_{key}"):
            s_title = st.text_input("Τίτλος Βήματος")
            s_desc = st.text_area("Περιγραφή")
            if st.form_submit_button("➕ Προσθήκη Βήματος"):
                if s_title and s_desc:
                    st.session_state.db["strategies"][key].append({"step": s_title, "desc": s_desc})
                    save_data(st.session_state.db)
                    st.rerun()

# ------------------------------------------
# 6. PROMPTS LIBRARY
# ------------------------------------------
with tabs[5]:
    st.subheader("📜 Prompts Library")
    with st.expander("➕ Προσθήκη Νέου Prompt"):
        p_title = st.text_input("Τίτλος Prompt")
        p_body = st.text_area("Κείμενο Prompt")
        if st.button("💾 Αποθήκευση"):
            if p_title and p_body:
                st.session_state.db["prompts"].append({
                    "id": str(datetime.datetime.now().timestamp()),
                    "title": p_title, "body": p_body, "date": str(datetime.date.today())
                })
                save_data(st.session_state.db)
                st.rerun()

    for p in st.session_state.db.get("prompts", []):
        st.markdown(f"**{p['title']}**")
        st.code(p["body"], language="text")
        st.markdown("---")

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
    with st.expander("➕ Προσθήκη Βίντεο"):
        with st.form("sched_form"):
            c1, c2 = st.columns(2)
            with c1:
                sc_date = st.date_input("Ημερομηνία", datetime.date.today())
                sc_time = st.time_input("Ώρα", datetime.time(18, 0))
                sc_plat = st.selectbox("Πλατφόρμα", ["YouTube Long", "YouTube Shorts", "Facebook Reel", "Instagram Reel", "TikTok"])
            with c2:
                sc_title = st.text_input("Τίτλος")
                sc_status = st.selectbox("Status", ["Ιδέα", "Script", "Filming", "Editing", "Ready", "Published"])
            if st.form_submit_button("➕ Προσθήκη"):
                if sc_title:
                    st.session_state.db["schedule"].append({
                        "id": str(datetime.datetime.now().timestamp()), "date": str(sc_date),
                        "time": str(sc_time)[:5], "platform": sc_plat, "title": sc_title, "status": sc_status
                    })
                    save_data(st.session_state.db)
                    st.rerun()

    sched = st.session_state.db.get("schedule", [])
    if sched:
        st.dataframe(pd.DataFrame(sched)[["date", "time", "platform", "title", "status"]], use_container_width=True, hide_index=True)

# ------------------------------------------
# 9. GREEK COMPETITORS (24 ΚΑΝΑΛΙΑ)
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
                        c.update(stats_map[cid])
                
                # Sync My Channel
                my_c = st.session_state.db["my_channel"]
                my_id = resolve_handle(api_key, my_c["handle"])
                if my_id and my_id in stats_map:
                    my_c.update(stats_map[my_id])
                    
                save_data(st.session_state.db)
                st.success("✅ Όλα τα κανάλια ανανεώθηκαν!")
                st.rerun()

    with st.expander("➕ Προσθήκη Νέου Ανταγωνιστή"):
        with st.form("add_comp_gr"):
            c_name = st.text_input("Όνομα Καναλιού")
            c_handle = st.text_input("@handle ή Channel ID")
            if st.form_submit_button("Προσθήκη"):
                if c_name and c_handle:
                    st.session_state.db["competitors_gr"].append({
                        "name": c_name, "handle": c_handle, **blank_stats()
                    })
                    save_data(st.session_state.db)
                    st.rerun()

    if comps:
        df_gr = pd.DataFrame(comps)
        st.dataframe(
            df_gr[["name", "subs", "totalViews", "videos", "avgViews", "efficiency"]].rename(columns={
                "name": "Κανάλι", "subs": "Subscribers", "totalViews": "Total Views",
                "videos": "Videos", "avgViews": "Avg Views", "efficiency": "Efficiency"
            }),
            use_container_width=True,
            hide_index=True
        )
        
        st.subheader("📈 Συγκριτικά Γραφήματα")
        fig1 = px.bar(df_gr, x="name", y="subs", title="Subscribers ανά Κανάλι", color="name", template="plotly_dark")
        fig1.update_layout(paper_bgcolor="#151c2c", plot_bgcolor="#151c2c")
        st.plotly_chart(fig1, use_container_width=True)

# ------------------------------------------
# 10. INTL COMPETITORS (2 ΚΑΝΑΛΙΑ)
# ------------------------------------------
with tabs[9]:
    comps_intl = st.session_state.db.get("competitors_intl", [])
    st.subheader(f"🌐 Ξένοι Competitors ({len(comps_intl)} Κανάλια)")
    with st.expander("➕ Προσθήκη Ξένου Ανταγωνιστή"):
        with st.form("add_intl"):
            ci_name = st.text_input("Όνομα")
            ci_country = st.text_input("Χώρα")
            ci_handle = st.text_input("@handle ή ID")
            if st.form_submit_button("Προσθήκη"):
                if ci_name and ci_handle:
                    st.session_state.db["competitors_intl"].append({
                        "name": ci_name, "country": ci_country, "handle": ci_handle, **blank_stats()
                    })
                    save_data(st.session_state.db)
                    st.rerun()

    if comps_intl:
        st.dataframe(
            pd.DataFrame(comps_intl)[["name", "country", "subs", "totalViews", "videos", "avgViews", "efficiency"]].rename(columns={
                "name": "Κανάλι", "country": "Χώρα", "subs": "Subscribers", "totalViews": "Total Views",
                "videos": "Videos", "avgViews": "Avg Views", "efficiency": "Efficiency"
            }),
            use_container_width=True,
            hide_index=True
        )

# ------------------------------------------
# 11. ANALYTICS
# ------------------------------------------
with tabs[10]:
    st.subheader("📈 Analytics & Video History")
    with st.expander("➕ Καταγραφή Βίντεο"):
        with st.form("an_form"):
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
                    st.session_state.db["analytics"].append({"title": t, "type": typ, "ctr": ctr, "retention": ret, "watchTime": wt, "sources": src})
                    save_data(st.session_state.db)
                    st.rerun()

    an = st.session_state.db.get("analytics", [])
    if an:
        st.dataframe(pd.DataFrame(an), use_container_width=True, hide_index=True)

# ------------------------------------------
# 12. KEYWORDS
# ------------------------------------------
with tabs[11]:
    st.subheader("🔑 Keywords")
    with st.expander("➕ Προσθήκη"):
        with st.form("kw_form"):
            kw = st.text_input("Keyword")
            prio = st.selectbox("Προτεραιότητα", ["Υψηλή", "Μεσαία", "Χαμηλή"])
            stat = st.selectbox("Status", ["Νέα", "Σε χρήση", "Ολοκληρώθηκε"])
            if st.form_submit_button("Αποθήκευση"):
                if kw:
                    st.session_state.db["keywords"].append({"text": kw, "priority": prio, "status": stat})
                    save_data(st.session_state.db)
                    st.rerun()

    kws = st.session_state.db.get("keywords", [])
    if kws:
        st.dataframe(pd.DataFrame(kws), use_container_width=True, hide_index=True)

# ------------------------------------------
# 13. IDEAS
# ------------------------------------------
with tabs[12]:
    st.subheader("💡 Ιδέες για Βίντεο")
    with st.form("idea_form"):
        txt = st.text_area("Ιδέα")
        tags = st.text_input("Tags")
        if st.form_submit_button("➕ Προσθήκη"):
            if txt:
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
# 14. GOALS
# ------------------------------------------
with tabs[13]:
    st.subheader("🎯 Μηνιαίοι Στόχοι")
    with st.form("goal_form"):
        m = st.text_input("Μήνας (π.χ. 2026-10)")
        s = st.number_input("Στόχος Subs", step=10)
        v = st.number_input("Στόχος Views", step=1000)
        u = st.number_input("Στόχος Uploads", step=1)
        if st.form_submit_button("Αποθήκευση"):
            if m:
                st.session_state.db["goals"].append({"month": m, "subs": s, "views": v, "uploads": u})
                save_data(st.session_state.db)
                st.rerun()

    gls = st.session_state.db.get("goals", [])
    if gls:
        st.dataframe(pd.DataFrame(gls), use_container_width=True, hide_index=True)
