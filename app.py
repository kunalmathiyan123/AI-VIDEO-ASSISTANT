import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VisiScope - AI Meeting Intelligence Platform",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS (Premium SaaS Interface Theme) ──────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

:root {
    --bg: #09090b;
    --card-bg: rgba(18, 18, 24, 0.7);
    --border-color: rgba(255, 255, 255, 0.08);
    --border-hover: rgba(124, 58, 237, 0.4);
    --primary: #7C3AED;
    --primary-glow: rgba(124, 58, 237, 0.2);
    --secondary: #06B6D4;
    --secondary-glow: rgba(6, 182, 212, 0.2);
    --text-primary: #f8fafc;
    --text-muted: #94a3b8;
    --success: #22c55e;
    --warning: #f59e0b;
    --danger: #ef4444;
}

/* Global resets & typography */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: var(--bg) !important;
    color: var(--text-primary) !important;
}

.stApp {
    background: var(--bg) !important;
}

/* Custom radial backdrop stars and gradients */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image: 
        radial-gradient(circle at 12% 18%, rgba(124, 58, 237, 0.04) 0%, transparent 40%),
        radial-gradient(circle at 88% 82%, rgba(6, 182, 212, 0.04) 0%, transparent 40%),
        radial-gradient(rgba(255, 255, 255, 0.012) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 36px 36px;
    pointer-events: none;
    z-index: 0;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: #0c0c0e !important;
    border-right: 1px solid var(--border-color) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

/* Saas Text Gradient */
.saas-heading {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #a78bfa 50%, #22d3ee 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.03em;
}

/* Premium Glassmorphic Cards */
.premium-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.premium-card:hover {
    border-color: var(--border-hover);
    box-shadow: 0 10px 40px rgba(124, 58, 237, 0.12);
    transform: translateY(-2px);
}
.premium-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 3px;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    opacity: 0.8;
}

/* Card titles */
.premium-card-title {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-muted);
    margin-bottom: 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Badges */
.premium-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    border: 1px solid transparent;
}
.badge-purple {
    background: rgba(124, 58, 237, 0.15);
    color: #c084fc;
    border-color: rgba(124, 58, 237, 0.3);
}
.badge-cyan {
    background: rgba(6, 182, 212, 0.15);
    color: #22d3ee;
    border-color: rgba(6, 182, 212, 0.3);
}
.badge-green {
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border-color: rgba(34, 197, 94, 0.3);
}

/* Premium Button with hover glow */
.stButton > button {
    background: linear-gradient(135deg, var(--primary) 0%, #6d28d9 100%) !important;
    color: #ffffff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 15px rgba(124, 58, 237, 0.25) !important;
    cursor: pointer;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.45) !important;
    border-color: rgba(255, 255, 255, 0.18) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* Secondary/Action inputs */
div[data-baseweb="input"],
div[data-baseweb="select"] > div {
    background: rgba(18, 18, 24, 0.85) !important;
    background-color: rgba(18, 18, 24, 0.85) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    transition: all 0.2s ease !important;
}
div[data-baseweb="input"]:focus-within,
div[data-baseweb="select"] > div:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px var(--primary-glow) !important;
}
.stTextInput input {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.85rem !important;
}
.stSelectbox div[data-baseweb="select"] * {
    background: transparent !important;
    background-color: transparent !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.85rem !important;
}
/* Style the dropdown list items */
ul[data-testid="stSelectboxVirtualDropdown"] {
    background-color: #121218 !important;
    border: 1px solid var(--border-color) !important;
}
ul[data-testid="stSelectboxVirtualDropdown"] li {
    background-color: #121218 !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.85rem !important;
}
ul[data-testid="stSelectboxVirtualDropdown"] li:hover {
    background-color: var(--primary) !important;
    color: #ffffff !important;
}

/* Pipeline timeline layout */
.pipeline-timeline {
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
    margin-top: 1.25rem;
    padding-left: 0.25rem;
    position: relative;
}
.pipeline-timeline::before {
    content: '';
    position: absolute;
    left: 8px;
    top: 12px;
    bottom: 12px;
    width: 2px;
    background: rgba(255, 255, 255, 0.05);
    z-index: 0;
}
.timeline-item {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    font-size: 0.8rem;
    position: relative;
    z-index: 1;
}
.timeline-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #18181b;
    border: 2px solid #27272a;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.dot-active {
    background: var(--secondary) !important;
    border-color: var(--secondary) !important;
    box-shadow: 0 0 8px var(--secondary) !important;
    transform: scale(1.25);
}
.dot-done {
    background: var(--success) !important;
    border-color: var(--success) !important;
}
.timeline-text {
    color: var(--text-muted);
}
.timeline-text-active {
    color: var(--text-primary) !important;
    font-weight: 600;
}

/* Claude / ChatGPT styled Chat UI */
.chat-container {
    background: rgba(18, 18, 24, 0.4);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.25rem;
    max-height: 480px;
    overflow-y: auto;
    margin-bottom: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    backdrop-filter: blur(8px);
}
.chat-msg {
    display: flex;
    gap: 0.85rem;
    max-width: 85%;
}
.chat-msg-user {
    align-self: flex-end;
    flex-direction: row-reverse;
}
.chat-msg-bot {
    align-self: flex-start;
}
.chat-avatar {
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
    flex-shrink: 0;
}
.avatar-user {
    background: linear-gradient(135deg, var(--primary), #c084fc);
    color: white;
}
.avatar-bot {
    background: linear-gradient(135deg, var(--secondary), #22d3ee);
    color: #09090b;
}
.chat-bubble {
    padding: 0.75rem 1.1rem;
    border-radius: 14px;
    font-size: 0.85rem;
    line-height: 1.6;
    word-break: break-word;
    border: 1px solid transparent;
}
.bubble-user {
    background: rgba(124, 58, 237, 0.08);
    border-color: rgba(124, 58, 237, 0.16);
    color: #e2e8f0;
}
.bubble-bot {
    background: rgba(255, 255, 255, 0.03);
    border-color: var(--border-color);
    color: #f1f5f9;
}

/* Transcript viewer container */
.transcript-box {
    background: #0c0c0f;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.25rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.8;
    max-height: 320px;
    overflow-y: auto;
    color: #e2e8f0;
    white-space: pre-wrap;
    word-break: break-word;
}

/* Custom scrollbars */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.08); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* Progress loader overrides */
.stProgress > div > div > div { background: var(--primary) !important; }
.stSpinner > div { border-top-color: var(--secondary) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text-primary) !important; }
label { color: var(--text-muted) !important; font-size: 0.8rem !important; font-weight: 500 !important; }
hr { border-top: 1px solid var(--border-color) !important; margin: 1.75rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Language Mapping (Whisper-supported Languages) ───────────────────────────
WHISPER_LANGUAGES = {
    "Auto Detect": "auto",
    "English": "en",
    "Hinglish": "hinglish",
    "Chinese": "zh",
    "German": "de",
    "Spanish": "es",
    "Russian": "ru",
    "Korean": "ko",
    "French": "fr",
    "Japanese": "ja",
    "Portuguese": "pt",
    "Turkish": "tr",
    "Polish": "pl",
    "Catalan": "ca",
    "Dutch": "nl",
    "Arabic": "ar",
    "Swedish": "sv",
    "Italian": "it",
    "Indonesian": "id",
    "Hindi": "hi",
    "Finnish": "fi",
    "Vietnamese": "vi",
    "Hebrew": "he",
    "Ukrainian": "uk",
    "Greek": "el",
    "Malay": "ms",
    "Czech": "cs",
    "Romanian": "ro",
    "Danish": "da",
    "Hungarian": "hu",
    "Tamil": "ta",
    "Norwegian": "no",
    "Thai": "th",
    "Urdu": "ur",
    "Croatian": "hr",
    "Bulgarian": "bg",
    "Lithuanian": "lt",
    "Latin": "la",
    "Maori": "mi",
    "Malayalam": "ml",
    "Welsh": "cy",
    "Slovak": "sk",
    "Telugu": "te",
    "Persian": "fa",
    "Latvian": "lv",
    "Bengali": "bn",
    "Serbian": "sr",
    "Azerbaijani": "az",
    "Slovenian": "sl",
    "Kannada": "kn",
    "Estonian": "et",
    "Macedonian": "mk",
    "Breton": "br",
    "Basque": "eu",
    "Icelandic": "is",
    "Armenian": "hy",
    "Nepali": "ne",
    "Mongolian": "mn",
    "Bosnian": "bs",
    "Kazakh": "kk",
    "Albanian": "sq",
    "Swahili": "sw",
    "Galician": "gl",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Sinhala": "si",
    "Khmer": "km",
    "Shona": "sn",
    "Yoruba": "yo",
    "Somali": "so",
    "Afrikaans": "af",
    "Occitan": "oc",
    "Georgian": "ka",
    "Belarusian": "be",
    "Tajik": "tg",
    "Sindhi": "sd",
    "Gujarati": "gu",
    "Amharic": "am",
    "Yiddish": "yi",
    "Lao": "lo",
    "Uzbek": "uz",
    "Faroese": "fo",
    "Haitian Creole": "ht",
    "Pashto": "ps",
    "Turkmen": "tk",
    "Nynorsk": "nn",
    "Maltese": "mt",
    "Sanskrit": "sa",
    "Luxembourgish": "lb",
    "Myanmar": "my",
    "Tibetan": "bo",
    "Tagalog": "tl",
    "Malagasy": "mg",
    "Assamese": "as",
    "Tatar": "tt",
    "Hawaiian": "haw",
    "Lingala": "ln",
    "Hausa": "ha",
    "Bashkir": "ba",
    "Javanese": "jw",
    "Sundanese": "su"
}

# Alphabetically sort all options, keeping "Auto Detect" first
_sorted_langs = sorted([lang for lang in WHISPER_LANGUAGES.keys() if lang != "Auto Detect"])
WHISPER_SORTED_OPTIONS = ["Auto Detect"] + _sorted_langs

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
    "selected_language": "Auto Detect",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
def render_timeline(steps: dict):
    html = '<div class="pipeline-timeline">'
    for step, icon, label in [
        ("audio",      "🔊", "Audio Processing"),
        ("transcript", "📝", "Whisper Transcription"),
        ("title",      "🏷️", "Title Generation"),
        ("summary",    "📋", "Meeting Summarisation"),
        ("extract",    "🔍", "Action/Decision Extraction"),
        ("rag",        "🧠", "RAG Engine Build"),
    ]:
        status = steps.get(step, "pending")
        dot_css = "dot-active" if status == "active" else ("dot-done" if status == "done" else "")
        text_css = "timeline-text-active" if status in ["active", "done"] else "timeline-text"
        
        status_icon = "⏳" if status == "active" else ("✓" if status == "done" else "○")
        color_css = "color:var(--secondary);" if status == "active" else ("color:var(--success);" if status == "done" else "color:var(--text-muted);")
        
        html += f"""
        <div class="timeline-item">
            <div class="timeline-dot {dot_css}"></div>
            <div class="{text_css}" style="display:flex; justify-content:space-between; width:100%;">
                <span>{icon} {label}</span>
                <span style="font-size:0.7rem; font-weight:700; {color_css}">{status_icon}</span>
            </div>
        </div>
        """
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# ─── Sidebar (VS Code/Cursor Inspired Layout) ──────────────────────────────────
with st.sidebar:
    # Branding header
    st.markdown("""
    <div style="display:flex; align-items:center; gap:0.75rem; margin-top:0.5rem; margin-bottom:1.5rem;">
        <span style="font-size:2.25rem; filter: drop-shadow(0 0 10px rgba(124,58,237,0.5))">🎬</span>
        <div>
            <h1 class="saas-heading" style="font-size:1.45rem; margin:0; line-height:1.1;">VisiScope</h1>
            <p style="font-size:0.65rem; color:var(--text-muted); margin:0; letter-spacing:0.12em; text-transform:uppercase;">Meeting Intelligence</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<span class="premium-badge badge-purple" style="margin-bottom:0.6rem;">📁 Upload Panel</span>', unsafe_allow_html=True)
    source = st.text_input("YouTube URL or File Path", placeholder="Paste URL or absolute file path...", label_visibility="collapsed")

    st.markdown('<span class="premium-badge badge-cyan" style="margin-top:0.8rem; margin-bottom:0.6rem;">🌐 Language Model</span>', unsafe_allow_html=True)
    
    try:
        default_lang_idx = WHISPER_SORTED_OPTIONS.index(st.session_state.selected_language)
    except ValueError:
        default_lang_idx = 0
        
    selected_display = st.selectbox(
        "Language",
        WHISPER_SORTED_OPTIONS,
        index=default_lang_idx,
        label_visibility="collapsed",
        key="lang_selectbox_key"
    )
    st.session_state.selected_language = selected_display
    language = WHISPER_LANGUAGES[selected_display]

    st.markdown('<div style="margin-top:0.75rem;"></div>', unsafe_allow_html=True)
    run_btn = st.button("⚡ Analyse Session", use_container_width=True)

    # Render pipeline timeline status when running or done
    if st.session_state.pipeline_done or st.session_state.processing:
        st.markdown("---")
        st.markdown('<span class="premium-badge badge-purple" style="margin-bottom:0.5rem;">Pipeline Status</span>', unsafe_allow_html=True)
        render_timeline(st.session_state.pipeline_steps)

# ─── Main Area Dashboard Layout ────────────────────────────────────────────────
st.markdown('<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;"><h1 class="saas-heading" style="font-size:2rem; margin:0;">AI Video Assistant</h1><span class="premium-badge badge-cyan">Platform v1.2</span></div>', unsafe_allow_html=True)
st.markdown('<div style="color:var(--text-muted); font-size:0.85rem; letter-spacing:0.02em; margin-bottom:1rem;">Transcribe · Summarise · Extract Action Items · Chat with your Meetings</div>', unsafe_allow_html=True)
st.markdown("---")

# ── Run Pipeline Action Loop ──────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("Please enter a YouTube URL or file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}
        st.session_state.processing = True

        progress_placeholder = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state
            # Render a premium loader visual in the main workspace
            with progress_placeholder.container():
                st.markdown("""
                <div class="premium-card" style="padding: 2.5rem; text-align: center; margin-bottom:1.5rem;">
                    <div style="display: flex; justify-content: center; margin-bottom: 1rem;">
                        <div class="stSpinner" style="width: 36px; height: 36px; border-top-color: var(--primary) !important;"></div>
                    </div>
                    <h3 style="margin: 0 0 0.5rem 0; font-size: 1.2rem;">⚙️ VisiScope Pipeline Active</h3>
                    <p style="color: var(--text-muted); font-size: 0.82rem; max-width: 400px; margin: 0 auto 1.5rem auto;">
                        Executing meeting analysis stages. Whisper speech transcription and vector database syncing can take a minute.
                    </p>
                    <div style="display: flex; gap: 0.5rem; justify-content: center;">
                        <span class="premium-badge badge-cyan">GPU Enabled</span>
                        <span class="premium-badge badge-purple">ChromaDB Sync</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        try:
            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items  = extract_action_items(transcript)
            decisions     = extract_key_decisions(transcript)
            questions     = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            st.session_state.processing = False
            progress_placeholder.success("✅ Analysis complete!")
            time.sleep(0.5)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            st.session_state.processing = False
            import traceback
            import logging
            logging.error(f"Pipeline failed: {e}")
            logging.error(traceback.format_exc())

            for k in ["audio","transcript","title","summary","extract","rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            
            err_msg = str(e)
            if "FFmpeg" in err_msg or "ffmpeg" in err_msg or "WinError 2" in err_msg:
                friendly_error = "❌ FFmpeg Error: Could not locate FFmpeg on your system. Please ensure FFmpeg is installed and added to PATH."
            elif "API_KEY" in err_msg or "api_key" in err_msg or "Unauthorized" in err_msg or "Mistral" in err_msg:
                friendly_error = "❌ API Key / Client Error: Please check your API keys (MISTRAL_API_KEY, SARVAM_API_KEY) in the environment (.env) file."
            elif "yt-dlp" in err_msg or "youtube" in err_msg.lower() or "download" in err_msg:
                friendly_error = "❌ YouTube Download Error: Failed to download the video. It may be restricted, private, or unavailable."
            else:
                friendly_error = f"❌ Pipeline failed at active stage. Error details: {err_msg}"
                
            progress_placeholder.error(friendly_error)

# ── Results Dashboard Rendering ────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # Title Card
    st.markdown(f"""
    <div class="premium-card" style="padding: 1.5rem; margin-bottom: 1.5rem;">
        <div class="premium-card-title">📌 Session Title</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:1.6rem; font-weight:800; color:var(--text-primary); letter-spacing:-0.02em;">
            {r['title']}
        </div>
        <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
            <span class="premium-badge badge-purple">Language: {language.upper()}</span>
            <span class="premium-badge badge-cyan">Status: ANALYSED</span>
        </div>
    </div>""", unsafe_allow_html=True)

    # Top Row: Summary & Transcript Columns
    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.markdown(f"""
        <div class="premium-card" style="margin-bottom: 0.5rem;">
            <div class="premium-card-title">📋 Executive Summary</div>
            <div style="font-size:0.875rem; line-height:1.7; color:var(--text-primary);">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)
        
        # Download action for Summary
        st.download_button(
            label="📥 Export Summary (Markdown)",
            data=r['summary'],
            file_name="meeting_summary.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col2:
        st.markdown("""
        <div class="premium-card" style="margin-bottom: 0.5rem;">
            <div class="premium-card-title">📝 Meeting Transcript</div>
        </div>""", unsafe_allow_html=True)
        
        with st.expander("🔍 View Full Transcript", expanded=True):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)
            
        st.download_button(
            label="📥 Export Transcript (Text)",
            data=r['transcript'],
            file_name="meeting_transcript.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # Second Row: Action Items | Decisions | Questions Dashboard
    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        st.markdown(f"""
        <div class="premium-card">
            <div class="premium-card-title">✅ Action Items</div>
            <div style="font-size:0.85rem; line-height:1.6; color:var(--text-primary);">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="premium-card">
            <div class="premium-card-title">🔑 Key Decisions</div>
            <div style="font-size:0.85rem; line-height:1.6; color:var(--text-primary);">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="premium-card">
            <div class="premium-card-title">❓ Open Questions</div>
            <div style="font-size:0.85rem; line-height:1.6; color:var(--text-primary);">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── RAG Chat Interface Redesign (Claude / ChatGPT style) ──────────────────────
    st.markdown('<div style="font-family:\'Plus Jakarta Sans\',sans-serif; font-size:1.3rem; font-weight:800; margin-top:2rem; margin-bottom:1rem; display:flex; align-items:center; gap:0.5rem;">💬 Chat with your Meeting Knowledge Base</div>', unsafe_allow_html=True)

    # Chat history display
    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            is_user = msg["role"] == "user"
            msg_class = "chat-msg-user" if is_user else "chat-msg-bot"
            avatar_class = "avatar-user" if is_user else "avatar-bot"
            bubble_class = "bubble-user" if is_user else "bubble-bot"
            avatar_label = "U" if is_user else "AI"
            
            chat_html += f"""
            <div class="chat-msg {msg_class}">
                <div class="chat-avatar {avatar_class}">{avatar_label}</div>
                <div class="chat-bubble {bubble_class}">{msg['content']}</div>
            </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="premium-card" style="text-align:center; padding:2.5rem; background:rgba(255,255,255,0.015);">
            <div style="font-size:2rem; margin-bottom:0.5rem;">💬</div>
            <div style="font-weight:700; font-size:0.95rem; margin-bottom:0.25rem;">Knowledge Base Ready</div>
            <div style="color:var(--text-muted); font-size:0.8rem;">Ask follow-up questions, request lists, or seek deep analysis from this meeting session.</div>
        </div>""", unsafe_allow_html=True)

    # Chat input and actions
    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input("Your question", placeholder="Ask a question about the meeting context...", label_visibility="collapsed", key="chat_input_val")
    with chat_col2:
        send_btn = st.button("Send ➔", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user",      "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    # Clear Chat control
    if st.session_state.chat_history:
        clear_col1, clear_col2 = st.columns([5, 1])
        with clear_col2:
            if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

else:
    # Empty State (SaaS Hero landing)
    st.markdown("""
    <div style="text-align: center; padding: 2.5rem 1.5rem; max-width: 800px; margin: 0 auto;">
        <span class="premium-badge badge-purple" style="font-size: 0.75rem; padding: 0.4rem 1rem; margin-bottom: 1.5rem;">🎬 VisiScope AI Assistant</span>
        <h1 class="saas-heading" style="font-size: 3rem; margin-bottom: 0.6rem; line-height: 1.2;">
            Zero-friction meeting intelligence.
        </h1>
        <p style="color: var(--text-muted); font-size: 1.05rem; line-height: 1.6; margin-bottom: 2rem;">
            Turn any video, call recording, or YouTube link into structured summaries, key decisions, action items, and an interactive RAG knowledge base in seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        st.markdown("""
        <div class="premium-card" style="text-align: center; padding: 1.25rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔊</div>
            <div style="font-weight: 700; font-size: 0.85rem; margin-bottom: 0.25rem;">Audio Pipeline</div>
            <div style="color: var(--text-muted); font-size: 0.72rem; line-height: 1.4;">16 kHz WAV normalization and smart chunking.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="premium-card" style="text-align: center; padding: 1.25rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📝</div>
            <div style="font-weight: 700; font-size: 0.85rem; margin-bottom: 0.25rem;">AI Transcription</div>
            <div style="color: var(--text-muted); font-size: 0.72rem; line-height: 1.4;">Whisper-powered speech-to-text.</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="premium-card" style="text-align: center; padding: 1.25rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
            <div style="font-weight: 700; font-size: 0.85rem; margin-bottom: 0.25rem;">Meeting Intel</div>
            <div style="color: var(--text-muted); font-size: 0.72rem; line-height: 1.4;">Action items, questions, and decisions extraction.</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="premium-card" style="text-align: center; padding: 1.25rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💬</div>
            <div style="font-weight: 700; font-size: 0.85rem; margin-bottom: 0.25rem;">RAG Chat</div>
            <div style="color: var(--text-muted); font-size: 0.72rem; line-height: 1.4;">Interactive contextual chatbot for follow-ups.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="premium-card" style="margin-top: 2rem; padding: 1.5rem;">
        <div class="premium-card-title">💡 Quick Start Guide</div>
        <div style="font-size: 0.82rem; line-height: 1.6; color: var(--text-muted);">
            1. Paste a <strong>YouTube URL</strong> or specify an <strong>absolute local file path</strong> (mp3, wav, mp4, mkv, etc.) in the sidebar.<br>
            2. Choose the audio language (Whisper for English, Sarvam for Hinglish/Hindi translations).<br>
            3. Hit <strong>Analyse</strong> and watch the pipeline run live.<br><br>
            <strong>Sample URL to try:</strong> <code style="background: #18181b; padding: 0.2rem 0.4rem; border-radius: 4px; color: var(--secondary); font-family: monospace;">https://www.youtube.com/watch?v=dQw4w9WgXcQ</code> (Creative Commons / Public testing video)
        </div>
    </div>
    """, unsafe_allow_html=True)