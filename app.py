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
# ΡΥΘΜΙΣΕΙΣ ΣΕΛΙΔΑΣ STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Video Creator Hub & Competitor Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "creator_hub_data.json"


# ==========================================
# ΔΙΑΧΕΙΡΙΣΗ ΔΕΔΟΜΕΝΩΝ (PERSISTENCE)
# ==========================================
def get_default_data():
    return {
        "password_hash": hashlib.sha256("1234".encode()).hexdigest(),  # Προεπιλεγμένος κωδικός: 1234
        "api_key": "",
        "my_channel": {
            "name": "Tsouros Marine",
            "handle": "UC5cxxXjrQcHnWqh_KtiCpDg",
            "resolvedId": "UC5cxxXjrQcHnWqh_KtiCpDg",
            "subs": 0,
            "totalViews": 0,
            "videos": 0,
            "avgViews": 0,
            "viewsPerSub": 0.0,
            "efficiency": 0.0,
            "growth": 0.0,
        },
        "competitors_gr": [
            {
                "name": "Tsouros Marine",
                "handle": "UC5cxxXjrQcHnWqh_KtiCpDg",
                "subs": 0,
                "totalViews": 0,
                "videos": 0,
                "avgViews": 0,
                "efficiency": 0.0,
                "growth": 0.0,
            },
            {
                "name": "Milonakis Kayak Fishing",
                "handle": "UCw9pG7yAviPN8RluqZJ7Uiw",
                "subs": 0,
                "totalViews": 0,
                "videos": 0,
                "avgViews": 0,
                "efficiency": 0.0,
                "growth": 0.0,
            },
            {
                "name": "Spinning By Tyrikos",
                "handle": "UC08kPE-YyUVe2gQac8nCqqw",
                "subs": 0,
                "totalViews": 0,
                "videos": 0,
                "avgViews": 0,
                "efficiency": 0.0,
                "growth": 0.0,
            },
            {
                "name": "Owrka",
                "handle": "UCpy-2GjgEjnx97N_aan0XFQ",
                "subs": 0,
                "totalViews": 0,
                "videos": 0,
                "avgViews": 0,
                "efficiency": 0.0,
                "growth": 0.0,
            },
        ],
        "competitors_intl": [],
        "schedule": [],
        "analytics": [],
        "keywords": [],
        "ideas": [],
        "goals": [],
        "prompts": [],
        "strategies": {
            "yt": [
                {
                    "step": "1. Προ-Παραγωγή",
                    "desc": "Έρευνα SEO, Scripting, Thumbnail Concept.",
                },
                {
                    "step": "2. Παραγωγή",
                    "desc": "Οριζόντια εγγραφή (16:9), Ήχος Studio, A-Roll & B-Roll.",
                },
                {
                    "step": "3. Post-Production",
                    "desc": "Montage, Sound Effects, Chapters, Custom Thumbnail.",
                },
            ],
            "shorts": [
                {
                    "step": "1. Hook & Format",
                    "desc": "Hook στα πρώτα 2'', Κάθετο (9:16), διάρκεια < 60 sec.",
                }
            ],
            "meta": [
                {
                    "step": "1. Audio & Visuals",
                    "desc": "Trending Sound, High Contrast Visuals, Safe Zone Text.",
                }
            ],
            "tiktok": [
                {
                    "step": "1. Trends & Style",
                    "desc": "Raw/Authentic aesthetic, Νέα Trends, Fast-paced storytelling.",
                }
            ],
        },
    }


def load_data():
    if not os.path.exists(DATA_FILE):
        data = get_default_data()
        save_data(data)
        return data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
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
                efficiency = (
                    round((avg_views / subs) * 1000, 2) if subs > 0 else 0
                )
                out[item["id"]] = {
                    "subs": subs,
                    "totalViews": views,
                    "videos": videos,
                    "avgViews": avg_views,
                    "viewsPerSub": views_per_sub,
                    "efficiency": efficiency,
                }
        return out
    except Exception as e:
        st.error(f"Σφάλμα επικοινωνίας με YouTube API: {e}")
        return {}


# ==========================================
# ΟΘΟΝΗ ΚΛΕΙΔΩΜΑΤΟΣ (LOGIN / AUTH)
# ==========================================
def check_password():
    if st.session_state.authenticated:
        return True

    st.markdown("<h2 style='text-align: center;'>🔒 Video Creator Hub</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Εισάγετε τον κωδικό πρόσβασης για να ξεκλειδώσετε το εργαλείο.</p>", unsafe_allow_html=True)
    
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
        st.caption("ℹ️ Προεπιλεγμένος κωδικός: `1234` (Μπορείτε να τον αλλάξετε από τις Ρυθμίσεις).")
    return False

if not check_password():
    st.stop()


# ==========================================
# SIDEBAR / BACKUP & ΡΥΘΜΙΣΕΙΣ
# ==========================================
with st.sidebar:
    st.title("🎬 Creator Hub")
    st.markdown("---")
    
    st.subheader("🔑 YouTube API Key")
    api_key_input = st.text_input(
        "API Key (v3)",
        value=st.session_state.db.get("api_key", ""),
        type="password",
        help="Απαιτείται για τον αυτόματο συγχρονισμό στατιστικών.",
    )
    if st.button("💾 Αποθήκευση Key", use_container_width=True):
        st.session_state.db["api_key"] = api_key_input
        save_data(st.session_state.db)
        st.success("Το API Key αποθηκεύτηκε!")

    st.markdown("---")
    st.subheader("💾 Backup & Restore")
    
    # Export JSON
    json_str = json.dumps(st.session_state.db, ensure_ascii=False, indent=2)
    st.download_button(
        label="⬇️ Export Backup (JSON)",
        data=json_str,
        file_name=f"creator_hub_backup_{datetime.date.today()}.json",
        mime="application/json",
        use_container_width=True,
    )
    
    # Import JSON
    uploaded_backup = st.file_uploader("⬆️ Import Backup", type=["json"])
    if uploaded_backup is not None:
        try:
            imported_data = json.load(uploaded_backup)
            st.session_state.db = imported_data
            save_data(st.session_state.db)
            st.success("✅ Το Backup ανακτήθηκε επιτυχώς!")
            st.rerun()
        except Exception as e:
            st.error(f"Σφάλμα ανάγνωσης αρχείου: {e}")

    st.markdown("---")
    st.subheader("🔒 Αλλαγή Κωδικού")
    with st.expander("Αλλαγή κωδικού"):
        new_pw = st.text_input("Νέος Κωδικός", type="password")
        if st.button("Ενημέρωση Κωδικού"):
            if len(new_pw) >= 4:
                st.session_state.db["password_hash"] = hashlib.sha256(new_pw.encode()).hexdigest()
                save_data(st.session_state.db)
                st.success("✅ Ο κωδικός άλλαξε!")
            else:
                st.error("Τουλάχιστον 4 χαρακτήρες.")


# ==========================================
# ΚΥΡΙΩΣ ΠΛΟΗΓΗΣΗ ΜΕ TABS
# ==========================================
tabs = st.tabs([
    "📊 Dashboard",
    "🎬 Στρατηγική",
    "📜 Prompts Library",
    "🖼️ Thumbnail AI",
    "📅 Πρόγραμμα",
    "🇬🇷 Competitors GR",
    "🌐 Competitors Intl",
    "📈 Analytics",
    "🔑 Keywords",
    "💡 Ιδέες",
    "🎯 Στόχοι",
])

# ------------------------------------------
# 1. DASHBOARD
# ------------------------------------------
with tabs[0]:
    st.header("🏠 Επισκόπηση & Performance Hub")
    
    my_ch = st.session_state.db.get("my_channel", {})
    all_comp = st.session_state.db.get("competitors_gr", []) + st.session_state.db.get("competitors_intl", [])
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📺 Το Κανάλι Μου (Subs)", f"{my_ch.get('subs', 0):,}", f"{my_ch.get('name', 'N/A')}")
    with c2:
        avg_subs = round(sum(c.get("subs", 0) for c in all_comp) / len(all_comp)) if all_comp else 0
        st.metric("👥 Μέσος Όρος Subs Ανταγωνιστών", f"{avg_subs:,}")
    with c3:
        avg_views = round(sum(c.get("avgViews", 0) for c in all_comp) / len(all_comp)) if all_comp else 0
        st.metric("👀 Μ.Ο. Avg Views Ανταγωνιστών", f"{avg_views:,}")
    with c4:
        st.metric("💡 Ιδέες σε Αναμονή", len(st.session_state.db.get("ideas", [])))

    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📅 Επόμενα Προγραμματισμένα Βίντεο")
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
            st.write(f"**Τα Avg Views σου vs Μέσος Όρος Ανταγωνιστών:** `{diff_pct:+}%`")
            fig = go.Figure(go.Bar(
                x=["Το Κανάλι Μου", "Μέσος Όρος Ανταγωνισμού"],
                y=[my_avg_v, avg_views],
                marker_color=["#facc15", "#3b82f6"]
            ))
            fig.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Συγχρονίστε τα κανάλια για να δείτε το benchmark.")

# ------------------------------------------
# 2. ΣΤΡΑΤΗΓΙΚΗ (YOUTUBE, SHORTS, REELS, TIKTOK)
# ------------------------------------------
with tabs[1]:
    st.header("🎬 Στρατηγικές Παραγωγής & Formats")
    strat_tabs = st.tabs(["YouTube Long-Form", "YouTube Shorts", "FB & IG Reels", "TikTok"])
    
    formats = [("yt", strat_tabs[0]), ("shorts", strat_tabs[1]), ("meta", strat_tabs[2]), ("tiktok", strat_tabs[3])]
    
    for key, tab_view in formats:
        with tab_view:
            items = st.session_state.db["strategies"].get(key, [])
            for idx, item in enumerate(items):
                with st.expander(f"📌 {item['step']}", expanded=True):
                    st.write(item["desc"])
            
            with st.form(f"add_step_{key}"):
                st.write("➕ **Προσθήκη Νέου Βήματος Στρατηγικής**")
                s_title = st.text_input("Τίτλος Βήματος")
                s_desc = st.text_area("Περιγραφή")
                if st.form_submit_button("Αποθήκευση"):
                    if s_title and s_desc:
                        st.session_state.db["strategies"][key].append({"step": s_title, "desc": s_desc})
                        save_data(st.session_state.db)
                        st.rerun()

# ------------------------------------------
# 3. PROMPTS LIBRARY
# ------------------------------------------
with tabs[2]:
    st.header("📜 Prompts Library (Midjourney, ChatGPT κ.λπ.)")
    
    with st.expander("➕ Προσθήκη Νέου Prompt", expanded=False):
        p_title = st.text_input("Τίτλος Prompt (π.χ. YouTube Thumbnail Action)")
        p_body = st.text_area("Κείμενο Prompt")
        if st.button("💾 Αποθήκευση Prompt"):
            if p_title and p_body:
                st.session_state.db["prompts"].append({
                    "id": str(datetime.datetime.now().timestamp()),
                    "title": p_title,
                    "body": p_body,
                    "date": str(datetime.date.today())
                })
                save_data(st.session_state.db)
                st.success("Το prompt αποθηκεύτηκε!")
                st.rerun()

    prompts = st.session_state.db.get("prompts", [])
    if prompts:
        for p in prompts:
            col_p1, col_p2 = st.columns([5, 1])
            with col_p1:
                st.subheader(p["title"])
                st.code(p["body"], language="text")
                st.caption(f"Ημερομηνία: {p['date']}")
            with col_p2:
                if st.button("🗑️ Διαγραφή", key=f"del_pr_{p['id']}"):
                    st.session_state.db["prompts"] = [x for x in prompts if x["id"] != p["id"]]
                    save_data(st.session_state.db)
                    st.rerun()
            st.markdown("---")
    else:
        st.info("Δεν έχετε αποθηκεύσει prompts ακόμα.")

# ------------------------------------------
# 4. THUMBNAIL AI PROMPT REVERSER
# ------------------------------------------
with tabs[3]:
    st.header("🖼️ Thumbnail AI Prompt Reverser")
    st.write("Ανεβάστε το thumbnail ενός ανταγωνιστή για να λάβετε έτοιμο prompt για Midjourney / DALL-E:")
    
    img_file = st.file_uploader("Επιλέξτε εικόνα Thumbnail", type=["png", "jpg", "jpeg", "webp"])
    if img_file:
        st.image(img_file, caption="Uploaded Competitor Thumbnail", width=420)
        sample_prompt = (
            "High-impact YouTube thumbnail, dramatic lighting, intense action composition, "
            "photorealistic detail, cinematic depth of field, high contrast vivid neon highlights (#facc15, #ef4444), "
            "expressive face, clear text safe zone on left third, professional 8k poster style --ar 16:9 --v 6.0"
        )
        st.subheader("Generated AI Prompt:")
        st.code(sample_prompt, language="text")

# ------------------------------------------
# 5. ΠΡΟΓΡΑΜΜΑ ΔΗΜΟΣΙΕΥΣΕΩΝ (SCHEDULE)
# ------------------------------------------
with tabs[4]:
    st.header("📅 Πρόγραμμα Δημοσιεύσεων")
    
    with st.expander("➕ Προσθήκη Νέου Βίντεο στο Πρόγραμμα"):
        with st.form("new_schedule_form"):
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                sc_date = st.date_input("Ημερομηνία", datetime.date.today())
                sc_time = st.time_input("Ώρα", datetime.time(18, 0))
                sc_plat = st.selectbox("Πλατφόρμα", ["YouTube Long", "YouTube Shorts", "Facebook Reel", "Instagram Reel", "TikTok"])
            with c_d2:
                sc_title = st.text_input("Τίτλος Βίντεο")
                sc_status = st.selectbox("Κατάσταση", ["Ιδέα", "Script", "Filming", "Editing", "Ready", "Published"])
            
            if st.form_submit_button("➕ Προσθήκη"):
                if sc_title:
                    st.session_state.db["schedule"].append({
                        "id": str(datetime.datetime.now().timestamp()),
                        "date": str(sc_date),
                        "time": str(sc_time)[:5],
                        "platform": sc_plat,
                        "title": sc_title,
                        "status": sc_status
                    })
                    save_data(st.session_state.db)
                    st.success("Προστέθηκε!")
                    st.rerun()

    schedule = st.session_state.db.get("schedule", [])
    if schedule:
        df_sc = pd.DataFrame(schedule)
        st.dataframe(df_sc[["date", "time", "platform", "title", "status"]], use_container_width=True, hide_index=True)
    else:
        st.info("Δεν υπάρχουν καταχωρημένα βίντεο στο πρόγραμμα.")

# ------------------------------------------
# 6. GREEK COMPETITORS
# ------------------------------------------
with tabs[5]:
    st.header("🇬🇷 Έλληνες Competitors")
    api_key = st.session_state.db.get("api_key", "")
    
    col_sync1, col_sync2 = st.columns([1, 4])
    with col_sync1:
        if st.button("🔄 Ανανέωση Όλων (API)", use_container_width=True):
            if not api_key:
                st.error("Βάλτε πρώτα το YouTube API Key στη Sidebar.")
            else:
                comps = st.session_state.db["competitors_gr"]
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
                save_data(st.session_state.db)
                st.success("✅ Συγχρονίστηκαν όλα τα κανάλια!")
                st.rerun()

    with st.expander("➕ Προσθήκη Νέου Ανταγωνιστή"):
        with st.form("add_comp_gr"):
            c_name = st.text_input("Όνομα Καναλιού")
            c_handle = st.text_input("@handle ή Channel ID (UC...)")
            if st.form_submit_button("Προσθήκη"):
                if c_name and c_handle:
                    st.session_state.db["competitors_gr"].append({
                        "name": c_name, "handle": c_handle,
                        "subs": 0, "totalViews": 0, "videos": 0, "avgViews": 0, "efficiency": 0.0, "growth": 0.0
                    })
                    save_data(st.session_state.db)
                    st.rerun()

    comps = st.session_state.db.get("competitors_gr", [])
    if comps:
        df_gr = pd.DataFrame(comps)
        st.dataframe(df_gr[["name", "subs", "totalViews", "videos", "avgViews", "efficiency"]], use_container_width=True, hide_index=True)
        
        # Charts
        st.subheader("📈 Συγκριτικά Γραφήματα")
        fig1 = px.bar(df_gr, x="name", y="subs", title="Subscribers ανά Κανάλι", color="name")
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.scatter(df_gr, x="videos", y="avgViews", size="subs", hover_name="name", title="Videos vs Avg Views (Correlation)")
        st.plotly_chart(fig2, use_container_width=True)

# ------------------------------------------
# 7. INTL COMPETITORS
# ------------------------------------------
with tabs[6]:
    st.header("🌐 Ξένοι Competitors")
    with st.expander("➕ Προσθήκη Ξένου Ανταγωνιστή"):
        with st.form("add_comp_intl"):
            ci_name = st.text_input("Όνομα Καναλιού")
            ci_country = st.text_input("Χώρα (π.χ. USA, Japan)")
            ci_handle = st.text_input("@handle ή Channel ID")
            if st.form_submit_button("Προσθήκη"):
                if ci_name and ci_handle:
                    st.session_state.db["competitors_intl"].append({
                        "name": ci_name, "country": ci_country, "handle": ci_handle,
                        "subs": 0, "totalViews": 0, "videos": 0, "avgViews": 0, "efficiency": 0.0, "growth": 0.0
                    })
                    save_data(st.session_state.db)
                    st.rerun()

    comps_intl = st.session_state.db.get("competitors_intl", [])
    if comps_intl:
        df_intl = pd.DataFrame(comps_intl)
        st.dataframe(df_intl[["name", "country", "subs", "totalViews", "videos", "avgViews", "efficiency"]], use_container_width=True, hide_index=True)
    else:
        st.info("Δεν έχετε προσθέσει ξένους ανταγωνιστές.")

# ------------------------------------------
# 8. ANALYTICS & VIDEO HISTORY
# ------------------------------------------
with tabs[7]:
    st.header("📈 Analytics & Video History")
    with st.expander("➕ Καταγραφή Στατιστικών Βίντεο"):
        with st.form("add_analytics_form"):
            an_title = st.text_input("Τίτλος Βίντεο")
            an_type = st.selectbox("Τύπος", ["Long-form (16:9)", "Shorts (9:16)"])
            c_an1, c_an2, c_an3 = st.columns(3)
            with c_an1:
                an_ctr = st.number_input("CTR (%)", min_value=0.0, max_value=100.0, step=0.1)
                an_ret = st.number_input("Avg Viewed (%)", min_value=0.0, max_value=100.0, step=0.1)
            with c_an2:
                an_drop = st.text_input("Drop-off (π.χ. 01:45)")
                an_watch = st.number_input("Watch Time (h)", min_value=0.0, step=0.1)
            with c_an3:
                an_sources = st.text_input("Traffic Sources")
                an_notes = st.text_input("Σημειώσεις")
            if st.form_submit_button("Αποθήκευση"):
                if an_title:
                    st.session_state.db["analytics"].append({
                        "title": an_title, "type": an_type, "ctr": an_ctr,
                        "retention": an_ret, "dropoff": an_drop, "watchTime": an_watch,
                        "sources": an_sources, "notes": an_notes
                    })
                    save_data(st.session_state.db)
                    st.rerun()

    analytics = st.session_state.db.get("analytics", [])
    if analytics:
        st.dataframe(pd.DataFrame(analytics), use_container_width=True, hide_index=True)
    else:
        st.info("Δεν υπάρχουν καταγεγραμμένα analytics.")

# ------------------------------------------
# 9. KEYWORDS
# ------------------------------------------
with tabs[8]:
    st.header("🔑 Keywords & SEO")
    with st.expander("➕ Προσθήκη Keyword"):
        with st.form("add_kw_form"):
            kw_text = st.text_input("Λέξη-κλειδί")
            kw_target = st.text_input("Target Βίντεο")
            kw_priority = st.selectbox("Προτεραιότητα", ["Υψηλή", "Μεσαία", "Χαμηλή"])
            kw_status = st.selectbox("Status", ["Νέα", "Σε χρήση", "Ολοκληρώθηκε"])
            kw_notes = st.text_input("Σημειώσεις")
            if st.form_submit_button("Αποθήκευση"):
                if kw_text:
                    st.session_state.db["keywords"].append({
                        "text": kw_text, "target": kw_target, "priority": kw_priority,
                        "status": kw_status, "notes": kw_notes
                    })
                    save_data(st.session_state.db)
                    st.rerun()

    keywords = st.session_state.db.get("keywords", [])
    if keywords:
        st.dataframe(pd.DataFrame(keywords), use_container_width=True, hide_index=True)

# ------------------------------------------
# 10. ΙΔΕΕΣ
# ------------------------------------------
with tabs[9]:
    st.header("💡 Backlog Ιδεών για Βίντεο")
    with st.form("add_idea_form"):
        id_text = st.text_area("Περιγραφή Ιδέας")
        id_tags = st.text_input("Tags (χωρισμένα με κόμμα)")
        if st.form_submit_button("➕ Προσθήκη Ιδέας"):
            if id_text:
                st.session_state.db["ideas"].append({
                    "id": str(datetime.datetime.now().timestamp()),
                    "text": id_text,
                    "tags": [t.strip() for t in id_tags.split(",") if t.strip()],
                    "date": str(datetime.date.today())
                })
                save_data(st.session_state.db)
                st.rerun()

    ideas = st.session_state.db.get("ideas", [])
    if ideas:
        for i in ideas:
            st.markdown(f"**💡 {i['text']}**")
            st.caption(f"🏷️ Tags: {', '.join(i.get('tags', []))} | 📅 {i.get('date')}")
            st.markdown("---")

# ------------------------------------------
# 11. ΣΤΟΧΟΙ
# ------------------------------------------
with tabs[10]:
    st.header("🎯 Μηνιαίοι Στόχοι")
    with st.form("add_goal_form"):
        g_month = st.text_input("Μήνας (π.χ. 2026-10)")
        g_subs = st.number_input("Στόχος Νέων Subs", min_value=0, step=10)
        g_views = st.number_input("Στόχος Views", min_value=0, step=1000)
        g_uploads = st.number_input("Στόχος Uploads", min_value=0, step=1)
        if st.form_submit_button("Αποθήκευση Στόχου"):
            if g_month:
                st.session_state.db["goals"].append({
                    "month": g_month, "subs": g_subs, "views": g_views, "uploads": g_uploads
                })
                save_data(st.session_state.db)
                st.rerun()

    goals = st.session_state.db.get("goals", [])
    if goals:
        st.dataframe(pd.DataFrame(goals), use_container_width=True, hide_index=True)