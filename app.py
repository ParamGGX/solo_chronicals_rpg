import os
import re
import random
import json
import time
import requests
from urllib.parse import quote

os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"

import streamlit as st

def load_api_key():
    # Try multiple path strategies so it works regardless of cwd
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_key.txt"),
        os.path.expanduser("~/storage/shared/dnd_app/api_key.txt"),
        os.path.expanduser("~/dnd_app/api_key.txt"),
        "api_key.txt",
    ]
    for path in candidates:
        try:
            with open(path, "r") as f:
                key = f.read().strip()
            if key:
                return key
        except Exception:
            continue
    return ""

GEMINI_API_KEY = load_api_key()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="⚔️ Chronicles RPG",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Gemini setup ──────────────────────────────────────────────────────────────
GEMINI_AVAILABLE = True

def generate_dm_response(prompt_text, history_context=""):
    if not GEMINI_API_KEY:
        return "⚠️ Gemini API Key is missing. Please check your setup."

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key=" + str(GEMINI_API_KEY)

    # Safely combine strings cleanly without triggering f-string or command-line parser errors
    full_prompt = str(DM_SYSTEM_PROMPT) + "\n\n[Campaign History]\n" + str(history_context) + "\n\n[Player Action]\n" + str(prompt_text) + "\n\nDM:"

    payload = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }]
    }

    for attempt in range(3):
        try:
            response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
            if response.status_code == 503 and attempt < 2:
                time.sleep(4)
                continue
            if response.status_code != 200:
                try:
                    err = response.json()
                    return "❌ API Error: " + str(err.get("error", {}).get("message", response.text))
                except Exception:
                    return "❌ API Error " + str(response.status_code) + ": " + response.text[:200]
            res_json = response.json()
            if "candidates" in res_json:
                return res_json["candidates"][0]["content"]["parts"][0]["text"]
            elif "error" in res_json:
                return "❌ API Error: " + str(res_json["error"]["message"])
            return "❌ Error: Unexpected response format from Google."
        except Exception as e:
            if attempt < 2:
                time.sleep(4)
                continue
            return "❌ Connection Error: " + str(e)
    return "❌ API Error: High demand — please try again in a moment." 



# ── Custom CSS — Old World Royal Tabletop Theme ───────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0E0B08 !important;
    color: #F2EFE9 !important;
    font-family: 'EB Garamond', Georgia, serif !important;
    font-size: 17px !important;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #1A1410; }
::-webkit-scrollbar-thumb { background: #6B4A2A; border-radius: 2px; }

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

.main .block-container {
    padding: 0.5rem 0.75rem 2rem !important;
    max-width: 100% !important;
}

/* ── Title & subtitle ── */
.dnd-title {
    text-align: center;
    font-family: 'Cinzel Decorative', serif;
    font-size: clamp(1.1rem, 4vw, 1.85rem);
    font-weight: 700;
    color: #E6C280;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.9), 0 0 18px rgba(180,130,40,0.3);
    letter-spacing: 0.04em;
    margin: 0.3rem 0 0.1rem;
    line-height: 1.3;
}
.dnd-subtitle {
    text-align: center;
    font-family: 'EB Garamond', serif;
    font-size: 0.92rem;
    color: #8A7355;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    font-style: italic;
}
.dnd-divider {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, #6B3A1A, #8A7355, #6B3A1A, transparent);
    margin: 0.35rem 0 0.65rem;
}

/* ── Tabs ── */
[data-testid="stTabs"] > div:first-child {
    background: linear-gradient(180deg, #2C251E 0%, #1F1A15 100%);
    border-bottom: 2px solid #8A7355;
    border-radius: 0;
    padding: 0 0.25rem;
    gap: 0;
    box-shadow: 0 4px 14px rgba(0,0,0,0.7);
}
[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Cinzel Decorative', serif !important;
    font-size: clamp(0.5rem, 1.6vw, 0.65rem) !important;
    font-weight: 700 !important;
    color: #8A7355 !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    border-radius: 0 !important;
    padding: 0.5rem 0.5rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
}
[data-testid="stTabs"] button[role="tab"]:hover {
    color: #E6C280 !important;
    background: rgba(138,115,85,0.08) !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #E6C280 !important;
    border-bottom-color: #901A1E !important;
    background: rgba(144,26,30,0.12) !important;
}
[data-testid="stTabsContent"] { padding-top: 0.5rem !important; }

/* ── Chat — ancient manuscript fragments ── */
[data-testid="stChatMessage"] {
    background: linear-gradient(135deg, #2C251E 0%, #221C16 100%) !important;
    border: 1px solid #8A7355 !important;
    border-radius: 2px !important;
    padding: 0.75rem 0.9rem !important;
    margin-bottom: 0.5rem !important;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.8), 0 8px 20px rgba(0,0,0,0.5) !important;
}
[data-testid="stChatMessage"][data-testid*="assistant"] {
    border-left: 3px solid #901A1E !important;
    background: linear-gradient(135deg, #211912 0%, #291F18 100%) !important;
}
[data-testid="stChatMessage"][data-testid*="user"] {
    border-left: 3px solid #8A7355 !important;
    background: linear-gradient(135deg, #2A2218 0%, #1E1A12 100%) !important;
}
.stChatMessage p, [data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li, [data-testid="stChatMessage"] td {
    font-family: 'EB Garamond', serif !important;
    font-size: clamp(1.05rem, 3vw, 1.2rem) !important;
    line-height: 1.75 !important;
    color: #F2EFE9 !important;
}
[data-testid="stChatMessage"] strong {
    color: #E6C280 !important;
    font-weight: 600 !important;
}
[data-testid="stChatMessage"] em { color: #C8A87A !important; }
[data-testid="stChatInput"] {
    background: linear-gradient(135deg, #2C251E 0%, #1F1A15 100%) !important;
    border: 1px solid #8A7355 !important;
    border-radius: 2px !important;
    box-shadow: inset 0 0 14px rgba(0,0,0,0.6) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #F2EFE9 !important;
    font-family: 'EB Garamond', serif !important;
    font-size: 1.05rem !important;
}
[data-testid="stChatInput"] button {
    background: #901A1E !important;
    color: #E6C280 !important;
    border-radius: 2px !important;
}

/* ── Buttons — iron/stone blocks ── */
.stButton > button {
    font-family: 'Cinzel Decorative', serif !important;
    font-size: clamp(0.52rem, 1.6vw, 0.65rem) !important;
    font-weight: 700 !important;
    background: linear-gradient(180deg, #3A2E22 0%, #26201A 100%) !important;
    color: #E6C280 !important;
    border: 1px solid #8A7355 !important;
    border-bottom: 3px solid #4A3820 !important;
    border-radius: 2px !important;
    padding: 0.4rem 0.45rem !important;
    transition: all 0.15s ease !important;
    letter-spacing: 0.03em !important;
    width: 100% !important;
    white-space: nowrap !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 4px 10px rgba(0,0,0,0.5) !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.9) !important;
}
.stButton > button:hover {
    background: linear-gradient(180deg, #4A3A2A 0%, #3A2A1A 100%) !important;
    border-color: #E6C280 !important;
    color: #FFF0B0 !important;
    box-shadow: inset 0 0 14px rgba(0,0,0,0.5), 0 0 12px rgba(144,26,30,0.4) !important;
}
.stButton > button:active {
    transform: translateY(2px) !important;
    border-bottom-width: 1px !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.8) !important;
}

/* ── Description Box ── */
.desc-box {
    background: linear-gradient(135deg, #0E0B08 0%, #1A1410 100%);
    border-left: 3px solid #6B5430;
    border-radius: 0 2px 2px 0;
    padding: 0.38rem 0.7rem;
    margin: -0.15rem 0 0.55rem 0;
    font-family: 'EB Garamond', serif;
    font-size: 1.02rem;
    color: #C8A87A;
    line-height: 1.6;
    font-style: italic;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
}
.desc-box.species  { border-left-color: #2E6B3E; color: #90C878; }
.desc-box.cls      { border-left-color: #901A1E; color: #D4907A; }
.desc-box.subcls   { border-left-color: #6A3090; color: #C09AE0; }
.desc-box.bg       { border-left-color: #1A5A6A; color: #7AC8D8; }
.desc-box.spell    { border-left-color: #1A3A8B; color: #88AADE; }
.desc-box.equip    { border-left-color: #7A5A00; color: #D4B860; }

/* ── Dice roller ── */
.dice-header {
    font-family: 'Cinzel Decorative', serif;
    font-size: 0.63rem;
    color: #8A7355;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.3rem;
    text-align: center;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.9);
}

/* ── Suggested actions ── */
.suggestions-box {
    background: linear-gradient(135deg, #221A0E 0%, #2A2010 100%);
    border: 1px solid #8A7355;
    border-left: 3px solid #E6C280;
    border-radius: 2px;
    padding: 0.65rem 0.8rem;
    margin-top: 0.5rem;
    box-shadow: inset 0 0 18px rgba(0,0,0,0.7), 0 6px 16px rgba(0,0,0,0.5);
}
.suggestions-title {
    font-family: 'Cinzel Decorative', serif;
    font-size: 0.63rem;
    color: #E6C280;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.4rem;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.9);
}

/* ── Scene view ── */
.scene-header {
    font-family: 'Cinzel Decorative', serif;
    font-size: 0.65rem;
    color: #8A7355;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    text-align: center;
    margin-bottom: 0.4rem;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.9);
}
.scene-caption {
    font-family: 'EB Garamond', serif;
    font-style: italic;
    font-size: 1.02rem;
    color: #8A7355;
    text-align: center;
    margin-top: 0.4rem;
    padding: 0.3rem;
    border-top: 1px solid #3A2A1A;
}
.scene-placeholder {
    background: linear-gradient(135deg, #1A1208 0%, #0E0B08 50%, #1A1210 100%);
    border: 2px solid #8A7355;
    border-radius: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    min-height: 250px;
    color: #5A4A30;
    font-family: 'EB Garamond', serif;
    font-size: 1rem;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
}

/* ── Sheet & Loadout sections ── */
.sheet-section {
    background: linear-gradient(135deg, #2C251E 0%, #1F1A15 100%);
    border: 1px solid #8A7355;
    border-radius: 2px;
    padding: 0.8rem;
    margin-bottom: 0.65rem;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.8), 0 8px 18px rgba(0,0,0,0.5);
}
.sheet-section-title {
    font-family: 'Cinzel Decorative', serif;
    font-size: 0.63rem;
    color: #901A1E;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
    padding-bottom: 0.28rem;
    border-bottom: 1px solid #3A1A1A;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.9);
}
.loadout-item {
    background: linear-gradient(135deg, #1A1410 0%, #0E0B08 100%);
    border: 1px solid #8A7355;
    border-radius: 2px;
    padding: 0.35rem 0.55rem;
    margin: 0.2rem 0;
    font-family: 'EB Garamond', serif;
    font-size: 1rem;
    color: #E6C280;
}
.loadout-item::before { content: "✦ "; color: #8A7355; }
.loadout-tag {
    display: inline-block;
    background: linear-gradient(135deg, #221A0A 0%, #1A1408 100%);
    border: 1px solid #8A7355;
    border-radius: 1px;
    padding: 0.1rem 0.45rem;
    font-family: 'Cinzel Decorative', serif;
    font-size: 0.52rem;
    color: #E6C280;
    margin: 0.1rem;
    letter-spacing: 0.05em;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.9);
}
.slots-badge {
    display: inline-block;
    background: linear-gradient(135deg, #1A0A1A 0%, #0E0810 100%);
    border: 1px solid #6A3A8A;
    border-radius: 1px;
    padding: 0.15rem 0.5rem;
    font-family: 'Cinzel Decorative', serif;
    font-size: 0.54rem;
    color: #C09AE0;
    margin-bottom: 0.4rem;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.9);
}

/* ── Inputs ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: linear-gradient(135deg, #2C251E 0%, #1F1A15 100%) !important;
    border: 1px solid #8A7355 !important;
    color: #F2EFE9 !important;
    border-radius: 2px !important;
    font-family: 'EB Garamond', serif !important;
    font-size: 1rem !important;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.5) !important;
}
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background: linear-gradient(135deg, #1F1A15 0%, #161210 100%) !important;
    border: 1px solid #8A7355 !important;
    color: #F2EFE9 !important;
    border-radius: 2px !important;
    font-family: 'EB Garamond', serif !important;
    font-size: 1rem !important;
    box-shadow: inset 0 0 8px rgba(0,0,0,0.5) !important;
}
label, [data-testid="stWidgetLabel"] p {
    font-family: 'Cinzel Decorative', serif !important;
    font-size: 0.58rem !important;
    color: #8A7355 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
}

/* ── HP bar ── */
.hp-bar-container {
    background: #0E0B08;
    border: 1px solid #8A7355;
    border-radius: 2px;
    height: 14px;
    overflow: hidden;
    margin-top: 0.3rem;
    box-shadow: inset 0 0 8px rgba(0,0,0,0.7);
}
.hp-bar-fill { height: 100%; border-radius: 1px; transition: width 0.3s ease; }

/* ── Roll result ── */
.roll-result {
    background: linear-gradient(135deg, #2C251E 0%, #1F1A15 100%);
    border: 1px solid #8A7355;
    border-radius: 2px;
    padding: 0.45rem 0.7rem;
    font-family: 'Cinzel Decorative', serif;
    font-size: 0.82rem;
    color: #E6C280;
    text-align: center;
    margin: 0.3rem 0;
    box-shadow: inset 0 0 14px rgba(0,0,0,0.7), 0 4px 12px rgba(0,0,0,0.4);
    text-shadow: 1px 1px 3px rgba(0,0,0,0.9);
}

/* ── Scene image ── */
[data-testid="stImage"] img {
    border-radius: 2px;
    border: 2px solid #8A7355;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.8), 0 10px 24px rgba(0,0,0,0.6);
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: linear-gradient(135deg, #2C251E 0%, #1F1A15 100%) !important;
    border: 1px solid #8A7355 !important;
    border-radius: 2px !important;
    box-shadow: inset 0 0 16px rgba(0,0,0,0.7) !important;
}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] > div > div > p {
    font-family: 'Cinzel Decorative', serif !important;
    font-size: 0.65rem !important;
    color: #8A7355 !important;
    letter-spacing: 0.08em !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
    text-transform: uppercase !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: linear-gradient(135deg, #2C251E 0%, #1F1A15 100%) !important;
    border: 1px solid #8A7355 !important;
    border-radius: 2px !important;
    font-family: 'EB Garamond', serif !important;
    color: #F2EFE9 !important;
    font-size: 1rem !important;
}

/* ── Download buttons ── */
[data-testid="stDownloadButton"] > button {
    font-family: 'Cinzel Decorative', serif !important;
    font-size: 0.6rem !important;
    font-weight: 700 !important;
    background: linear-gradient(180deg, #3A2E22 0%, #26201A 100%) !important;
    color: #E6C280 !important;
    border: 1px solid #8A7355 !important;
    border-bottom: 3px solid #4A3820 !important;
    border-radius: 2px !important;
    box-shadow: 0 3px 8px rgba(0,0,0,0.5) !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.9) !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
}
[data-testid="stDownloadButton"] > button:hover {
    border-color: #E6C280 !important;
    color: #FFF0B0 !important;
    box-shadow: 0 0 10px rgba(144,26,30,0.35) !important;
}
[data-testid="stDownloadButton"] > button:active {
    transform: translateY(2px) !important;
    border-bottom-width: 1px !important;
}

/* ── Markdown text throughout ── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    font-family: 'EB Garamond', serif !important;
    font-size: 1rem !important;
    color: #F2EFE9 !important;
    line-height: 1.7 !important;
}

/* ── Dice animation states ── */
@keyframes diceFlash {
    0%   { opacity:0; transform:scale(0.75) rotate(-8deg); }
    40%  { opacity:1; transform:scale(1.08) rotate(3deg); }
    100% { opacity:1; transform:scale(1) rotate(0deg); }
}
@keyframes goldPulse {
    0%   { box-shadow:inset 0 0 14px rgba(0,0,0,0.7), 0 0  4px rgba(230,194,128,0.2); }
    50%  { box-shadow:inset 0 0 14px rgba(0,0,0,0.7), 0 0 22px rgba(230,194,128,0.65); }
    100% { box-shadow:inset 0 0 14px rgba(0,0,0,0.7), 0 4px 12px rgba(0,0,0,0.4); }
}
.roll-animating {
    background: linear-gradient(135deg, #2C251E 0%, #1F1A15 100%);
    border: 1px solid #6A5535;
    border-radius: 2px; padding: 0.45rem 0.7rem;
    font-family: 'Cinzel Decorative', serif; font-size: 1.05rem;
    color: #C8A840; text-align: center; margin: 0.3rem 0;
    opacity: 0.75;
}
.roll-final-glow {
    background: linear-gradient(135deg, #2C251E 0%, #1F1A15 100%);
    border: 1px solid #E6C280; border-radius: 2px;
    padding: 0.45rem 0.7rem;
    font-family: 'Cinzel Decorative', serif; font-size: 1.1rem;
    color: #FFE08A; text-align: center; margin: 0.3rem 0;
    animation: diceFlash 0.45s ease-out, goldPulse 0.9s ease-out 0.1s;
    text-shadow: 0 0 10px rgba(230,194,128,0.6), 1px 1px 3px rgba(0,0,0,0.9);
}
/* ── NPC portrait cameo ── */
.npc-cameo {
    display: inline-block;
    width: 36px; height: 36px;
    border-radius: 50%;
    border: 2px solid #8A7355;
    object-fit: cover;
    vertical-align: middle;
    margin-right: 0.35rem;
    box-shadow: 0 0 6px rgba(0,0,0,0.6);
}
/* ── Mobile ── */
@media (max-width: 640px) {
    .main .block-container { padding: 0.25rem 0.4rem 4rem !important; }
    [data-testid="stTabs"] button[role="tab"] {
        padding: 0.4rem 0.25rem !important;
        font-size: 0.48rem !important;
    }
    .dnd-title { font-size: clamp(0.95rem, 5vw, 1.4rem) !important; }
}
</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# DATA DICTIONARIES
# ═════════════════════════════════════════════════════════════════════════════

SUBCLASSES = {
    "Barbarian": ["Path of the Berserker","Wild Heart","Zealot","World Tree","Ancestral Guardian","Beast","Storm Herald","Wild Magic","Giant"],
    "Bard":      ["College of Lore","Valor","Glamour","Swords","Whispers","Eloquence","Creation","Spirits","Dance"],
    "Cleric":    ["Life","Light","Tempest","War","Trickery","Knowledge","Nature","Death","Arcana","Forge","Grave","Order","Peace","Twilight"],
    "Druid":     ["Circle of the Land","Moon","Dreams","Shepherd","Spores","Stars","Wildfire","Sea"],
    "Fighter":   ["Champion","Battle Master","Eldritch Knight","Cavalier","Samurai","Arcane Archer","Psi Warrior","Rune Knight","Echo Knight"],
    "Monk":      ["Way of the Open Hand","Shadow","Four Elements","Long Death","Sun Soul","Drunken Master","Kensei","Mercy","Astral Self","Ascendant Dragon"],
    "Paladin":   ["Oath of Devotion","Ancients","Vengeance","Crown","Conquest","Redemption","Glory","Watchers","Oathbreaker"],
    "Ranger":    ["Hunter","Beast Master","Gloom Stalker","Horizon Walker","Monster Slayer","Fey Wanderer","Swarmkeeper","Drakewarden"],
    "Rogue":     ["Thief","Assassin","Arcane Trickster","Inquisitive","Mastermind","Scout","Swashbuckler","Phantom","Soulknife"],
    "Sorcerer":  ["Draconic Bloodline","Wild Magic","Divine Soul","Shadow Magic","Storm Sorcery","Aberrant Mind","Clockwork Soul","Lunar Sorcery"],
    "Warlock":   ["The Archfey","The Fiend","The Great Old One","The Undying","The Celestial","The Hexblade","The Fathomless","The Genie","The Undead"],
    "Wizard":    ["School of Abjuration","Conjuration","Divination","Enchantment","Evocation","Illusion","Necromancy","Transmutation","War Magic","Bladesinging","Chronurgy","Graviturgy"],
    "Artificer": ["Alchemist","Armorer","Artillerist","Battle Smith"],
}

SPECIES = ["Human","Elf","Dwarf","Halfling","Dragonborn","Gnome","Half-Elf","Half-Orc",
           "Tiefling","Giff","Goliath","Orc","Goblin","Kobold","Tabaxi","Tortle","Harengon",
           "Owlin","Aasimar","Changeling"]

CLASSES = list(SUBCLASSES.keys())

BACKGROUNDS = ["Acolyte","Criminal","Folk Hero","Noble","Sage","Soldier","Entertainer",
               "Artisan","Hermit","Charlatan","Outlander","Sailor","Urchin"]

SKILLS_LIST = ["Acrobatics","Animal Handling","Arcana","Athletics","Deception","History",
               "Insight","Intimidation","Investigation","Medicine","Nature","Perception",
               "Performance","Persuasion","Religion","Sleight of Hand","Stealth","Survival"]

DICE = {"d4":4,"d6":6,"d8":8,"d10":10,"d12":12,"d20":20}

HIT_DICE = {
    "Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10,
    "Bard": 8, "Cleric": 8, "Druid": 8, "Monk": 8, "Rogue": 8, "Warlock": 8, "Artificer": 8,
    "Sorcerer": 6, "Wizard": 6,
}

SAVE_DIR = os.path.expanduser("~/storage/shared/dnd_app/saves")

CONDITIONS_LIST = [
    "Blinded", "Charmed", "Deafened", "Frightened", "Grappled",
    "Incapacitated", "Invisible", "Paralyzed", "Petrified", "Poisoned",
    "Prone", "Restrained", "Stunned", "Unconscious",
]

CONDITIONS_RULES = {
    "Blinded":       "⚠️ BLINDED: Automatically fail sight-based checks. Attacks against you have advantage; your attacks have disadvantage.",
    "Charmed":       "⚠️ CHARMED: Cannot attack the charmer. The charmer has advantage on all social checks against you.",
    "Deafened":      "⚠️ DEAFENED: Automatically fail hearing-based checks. Immune to effects that require hearing.",
    "Frightened":    "⚠️ FRIGHTENED: Disadvantage on attack rolls and ability checks while source is in sight. Cannot willingly move closer to source.",
    "Grappled":      "⚠️ GRAPPLED: Speed becomes 0. Ends if grappler is incapacitated or you are moved out of reach.",
    "Incapacitated": "⚠️ INCAPACITATED: Cannot take actions or reactions.",
    "Invisible":     "🌟 INVISIBLE: Cannot be seen without special senses. Attacks against you have disadvantage; your attacks have advantage.",
    "Paralyzed":     "⚠️ PARALYZED: Incapacitated, cannot move or speak. Attack rolls against you have advantage; hits within 5 ft. are critical hits. Fail STR and DEX saves.",
    "Petrified":     "⚠️ PETRIFIED: Transformed to stone. Incapacitated, unaware of surroundings. Resistance to all damage; immune to poison and disease.",
    "Poisoned":      "⚠️ POISONED: Disadvantage on attack rolls and ability checks.",
    "Prone":         "⚠️ PRONE: Only move option is crawl (half speed). Melee attacks against you have advantage; ranged attacks have disadvantage. Your attacks have disadvantage.",
    "Restrained":    "⚠️ RESTRAINED: Speed becomes 0. Attacks against you have advantage; your attacks have disadvantage. Disadvantage on DEX saves.",
    "Stunned":       "⚠️ STUNNED: Incapacitated, cannot move, can only speak falteringly. Attacks against you have advantage. Fail STR and DEX saves.",
    "Unconscious":   "⚠️ UNCONSCIOUS: Incapacitated, cannot move or speak. Drop everything, fall prone. All attacks have advantage; hits within 5 ft. are critical.",
}

CLASS_PORTRAITS = {
    "Barbarian": "⚔️", "Bard": "🎵", "Cleric": "✝️", "Druid": "🌿",
    "Fighter": "🛡️", "Monk": "👊", "Paladin": "⚜️", "Ranger": "🏹",
    "Rogue": "🗡️", "Sorcerer": "✨", "Warlock": "🔮", "Wizard": "📖", "Artificer": "⚙️",
}

CLASS_PACKS = {
    "Explorer's Pack": [
        "Backpack", "Bedroll", "Mess Kit", "Tinderbox",
        "10 Torches", "10 days' Rations", "Waterskin", "50 ft. Hempen Rope",
    ],
    "Dungeoneer's Pack": [
        "Backpack", "Crowbar", "Hammer", "10 Pitons",
        "10 Torches", "Tinderbox", "10 days' Rations", "Waterskin", "50 ft. Hempen Rope",
    ],
    "Scholar's Pack": [
        "Backpack", "Book of Lore", "Bottle of Ink", "Ink Pen",
        "10 Sheets of Parchment", "Bag of Sand", "Small Knife",
    ],
    "Priest's Pack": [
        "Backpack", "Blanket", "10 Candles", "Tinderbox", "Alms Box",
        "2 Blocks Incense", "Censer", "Holy Vestments", "2 days' Rations", "Waterskin",
    ],
    "Burglar's Pack": [
        "Backpack", "1,000 Ball Bearings", "10 ft. String", "Bell",
        "5 Candles", "Crowbar", "Hammer", "10 Pitons",
        "Hooded Lantern", "2 Flasks Oil", "5 days' Rations",
        "Tinderbox", "Waterskin", "50 ft. Hempen Rope",
    ],
    "Diplomat's Pack": [
        "Chest", "2 Map/Scroll Cases", "Fine Clothes", "Bottle of Ink",
        "Ink Pen", "Lamp", "2 Flasks Oil", "5 Sheets Paper",
        "Vial of Perfume", "Sealing Wax", "Soap",
    ],
    "Entertainer's Pack": [
        "Backpack", "Bedroll", "2 Costumes", "5 Candles",
        "5 days' Rations", "Waterskin", "Disguise Kit",
    ],
}

# ── Species Descriptions ──────────────────────────────────────────────────────
SPECIES_DESC = {
    "Human":      "Versatile and adaptable. Choose Variant for +1 to two scores, a bonus Feat, and an extra skill. Bonus language of choice.",
    "Elf":        "Keen senses, Darkvision 60 ft., immunity to magical sleep, proficiency in Perception. High Elves add a Wizard cantrip.",
    "Dwarf":      "+2 CON, Darkvision 60 ft., resistance to poison, battleaxe/handaxe/warhammer proficiency. Stone Cunning for stonework.",
    "Halfling":   "+2 DEX, Lucky (reroll 1s on any d20 roll), Brave (advantage vs. fear), Naturally Stealthy (hide behind larger creatures).",
    "Dragonborn": "+2 STR, +1 CHA. Dragon Ancestry grants a Breath Weapon attack and damage resistance matching your draconic lineage.",
    "Gnome":      "+2 INT, Darkvision 60 ft., Gnome Cunning (advantage on INT/WIS/CHA saves vs. magic). Forest Gnomes gain Minor Illusion.",
    "Half-Elf":   "+2 CHA, +1 to any two other scores, Darkvision 60 ft., Fey Ancestry, two bonus skill proficiencies of your choice.",
    "Half-Orc":   "+2 STR, +1 CON, Darkvision 60 ft., Intimidation proficiency, Relentless Endurance (survive 0 HP once/long rest), Savage Attacks.",
    "Tiefling":   "+2 CHA, +1 INT, Darkvision 60 ft., fire resistance. Infernal Legacy: Thaumaturgy, Hellish Rebuke, Darkness spell progression.",
    "Giff":       "Astral hippo-folk with firearms proficiency and Hippogriff Charge (bonus action shove). Advantage on all Strength checks.",
    "Goliath":    "+2 STR, +1 CON. Stone's Endurance: reduce damage by 1d12+CON mod once/short rest. Powerful Build, Mountain Born cold resist.",
    "Orc":        "+2 STR, +1 CON, Darkvision 60 ft., Aggressive (bonus action move toward enemy), Powerful Build, Intimidation proficiency.",
    "Goblin":     "+2 DEX, +1 CON, Darkvision 60 ft., Nimble Escape (Disengage or Hide as bonus action), Fury of the Small (bonus damage).",
    "Kobold":     "Pack Tactics: advantage on attacks when an ally is adjacent to target. Grovel, Cower, Beg as group distraction action.",
    "Tabaxi":     "+2 DEX, +1 CHA, Cat's Claws (climb 20 ft., 1d4 slashing), Cat's Talent (Perception + Stealth proficiency), Feline Agility.",
    "Tortle":     "+2 STR, +1 WIS, Natural Armor (base AC 17—no other armor needed), Claws (1d4 slashing), Hold Breath 1 hr, Shell Defense.",
    "Harengon":   "Rabbit-folk. Lucky Footwork (add PB to DEX saves once/short rest), Rabbit Hop bonus movement, Hare-Trigger initiative boost.",
    "Owlin":      "+2/+1 flexible scores, Darkvision 120 ft., fly speed equal to walk speed (silent flight), Stealth proficiency.",
    "Aasimar":    "+2 CHA, +1 WIS, Darkvision 60 ft., celestial resistance (necrotic & radiant), Healing Hands, Light cantrip from Light Bearer.",
    "Changeling": "+2 CHA, +1 to one score. Shapechanger: alter size, features, and voice at will. Two bonus social skill proficiencies.",
}

# ── Class Descriptions ────────────────────────────────────────────────────────
CLASS_DESC = {
    "Barbarian": "Primal warrior fueled by Rage: advantage on STR checks/saves, bonus damage, resistance to B/P/S. d12 Hit Die, no spells.",
    "Bard":      "Versatile performer-mage with Bardic Inspiration (d6→d12), Jack of All Trades, and access to any spell list via Magical Secrets.",
    "Cleric":    "Divine conduit channeling a deity's power. Prepares from the full Cleric list each day. Channel Divinity, d8 Hit Die.",
    "Druid":     "Nature-bound caster who Wild Shapes into beasts. Prepares from the full Druid list. Cannot wear metal armor. d8 Hit Die.",
    "Fighter":   "Martial master with Second Wind, Action Surge (bonus action), and up to 4 attacks at level 20. d10 Hit Die, all armor.",
    "Monk":      "Disciplined martial artist using Ki: Flurry of Blows, Patient Defense, Step of the Wind. No armor, d8 Hit Die.",
    "Paladin":   "Holy warrior combining martial might with Divine Smite (spend spell slots for radiant burst on hit). d10 Hit Die.",
    "Ranger":    "Wilderness predator with Favored Enemy, Hunter's Mark, and spellcasting (level 1 in Chronicles RPG rules). d10 Hit Die.",
    "Rogue":     "Cunning expert: Sneak Attack bonus damage, Cunning Action (BA Dash/Disengage/Hide), Expertise in chosen skills. d8 Hit Die.",
    "Sorcerer":  "Innate spellcaster with Sorcery Points and Metamagic to reshape spells. Fewer spells known, maximum impact. d6 Hit Die.",
    "Warlock":   "Pact-bound caster: short-rest spell slots, Eldritch Blast, and Invocations for customized power. d8 Hit Die.",
    "Wizard":    "Scholarly arcanist with the broadest spell list. Spellbook, Arcane Recovery, and unmatched magical versatility. d6 Hit Die.",
    "Artificer": "Magical inventor who infuses items with power. Tool proficiencies, Infusions, and INT-based spellcasting. d8 Hit Die.",
}

# ── Subclass Descriptions ─────────────────────────────────────────────────────
SUBCLASS_DESC = {
    # Barbarian
    "Path of the Berserker":  "Go berserk during Rage for bonus weapon attacks. Mindless Rage prevents charm/fright. Retaliation attacks on damage.",
    "Wild Heart":             "Bond with a beast totem (Bear, Eagle, Wolf) for supernatural powers: endurance, mobility, or pack-hunt synergy.",
    "Zealot":                 "Warrior of the gods. Divine Fury adds radiant/necrotic damage on hits. Can be resurrected at no material cost.",
    "World Tree":             "Channel Yggdrasil's power. Gain temp HP in Rage, teleport allies through Branches of the World Tree.",
    "Ancestral Guardian":     "Spectral ancestors mark enemies: imposing disadvantage on attacks against anyone but you. Strong tank subclass.",
    "Beast":                  "Manifest bestial features: claws, a bite with life-drain, or a tail for reach. Natural weapons scale with level.",
    "Storm Herald":           "Radiate an elemental aura: Arctic (cold), Desert (fire), or Sea (lightning) zone deals damage to nearby foes.",
    "Wild Magic":             "Each Rage may unleash a random Wild Magic surge. Unstable but potent—effects range from teleport to healing.",
    "Giant":                  "Channel giant power. Elemental Cleaver adds damage type of choice; grow to Large size and throw creatures.",
    # Bard
    "College of Lore":        "Master of secrets. Cutting Words reaction imposes disadvantage; Bonus Magical Secrets unlocks any spell list early.",
    "Valor":                  "Warrior-poet. Gains martial weapons and medium armor. Combat Inspiration boosts AC or weapon damage rolls.",
    "Glamour":                "Fey magic of enthrallment. Mantle of Inspiration grants temp HP + movement; Enthralling Performance charms crowds.",
    "Swords":                 "Blade Flourish mid-performance: Defensive Flourish adds AC, Slashing Flourish hits adjacent enemies, Mobile Flourish pushes.",
    "Whispers":               "Infiltrator who steals secrets. Psychic Blades add psychic Sneak Attack–style damage once per turn.",
    "Eloquence":              "Master orator. Bardic Inspiration never fails on a 1; Unsettling Words forces WIS save vs. disadvantage.",
    "Creation":               "Animate matter through song. Animating Performance creates a dancing item that distracts and fights for you.",
    "Spirits":                "Channel ancestral spirits via a deck of cards. Each spirit grants a different narrative and mechanical boon.",
    "Dance":                  "Graceful combat performance. Dazzling Footwork boosts AC while unarmored; movement-based inspiration bonuses.",
    # Cleric
    "Life":                   "Supreme healer. Disciple of Life adds CON mod to all healing. Bonus spells: Cure Wounds, Mass Cure Wounds, etc.",
    "Light":                  "Radiance and revelation. Warding Flare (reaction) imposes disadvantage on an attack. Fireball on spell list.",
    "Tempest":                "Storm and sea. Wrath of the Storm deals lightning/thunder on hit (reaction). Thunderwave, Call Lightning added.",
    "War":                    "Battle priest. War Priest grants bonus weapon attacks. Guided Strike adds +10 to a roll. Heavy armor, martial weapons.",
    "Trickery":               "Deceptive agent. Invoke Duplicity summons an illusion to distract; Cloak of Shadows. Charm Person on list.",
    "Knowledge":              "Loremaster. Visions of the Past; Channel Divinity grants temporary proficiency in any skill. All languages.",
    "Nature":                 "Druidic divinity. Acolyte of Nature grants a Druid cantrip and nature skill; Channel Divinity charms plants/animals.",
    "Death":                  "Forbidden necromancy. Reaper targets two creatures with necromancy cantrips. Animate Dead, Inflict Wounds added.",
    "Arcana":                 "Blends divinity with arcana. Arcane Initiate grants 2 Wizard cantrips; Arcane Abjuration banishes extraplanar foes.",
    "Forge":                  "Smith of divine craft. Blessing of the Forge grants +1 to a weapon or armor each long rest. Turns constructs.",
    "Grave":                  "Guardian of death's threshold. Circle of Mortality maximizes healing at 0 HP. Sentinel at Death's Door negates crits.",
    "Order":                  "Lawful enforcer. Voice of Authority lets an ally make a weapon attack after you cast a spell on them.",
    "Peace":                  "Healer of discord. Emboldening Bond links allies for rerolls. Channel Divinity creates a protective sphere.",
    "Twilight":               "Shepherd of the night. Eyes of Night grants Darkvision 300 ft. to allies; Vigilant Blessing prevents surprise.",
    # Druid
    "Circle of the Land":     "Terrain-specialist caster. Bonus Nature/Survival; extra spells based on terrain (Arctic, Forest, Desert, etc.).",
    "Moon":                   "Master shape-shifter. Wild Shape into CR 1 beasts at level 2 (scales). Combat Wild Shape as bonus action.",
    "Dreams":                 "Fey connection. Balm of the Summer Court heals allies with Wild Shape charges; Hearth of Moonlight teleports.",
    "Shepherd":               "Beast summoner. Speech of the Woods communicates with animals. Faithful Summons auto-summons creatures when downed.",
    "Spores":                 "Fungal growth and decay. Halo of Spores deals necrotic on reaction. Symbiotic Entity supercharges Wild Shape as HP.",
    "Stars":                  "Celestial magic. Starry Form grants constellation bonuses (Archer, Chalice, or Dragon) when Wild Shape activates.",
    "Wildfire":               "Flame and rebirth. Wildfire Spirit summon deals fire damage and teleports allies between bonded flame points.",
    "Sea":                    "Ocean druid. Wrath of the Sea creates a water aura; Channel Divinity calls squalls and controls sea currents.",
    # Fighter
    "Champion":               "Straightforward excellence. Improved Critical (crits on 19–20), Remarkable Athlete adds PB to STR/DEX/CON checks.",
    "Battle Master":          "Tactical genius. Superiority Dice (d8s) fuel maneuvers: Riposte, Trip Attack, Precision Attack, and more.",
    "Eldritch Knight":        "Spell-and-sword hybrid. Learns Abjuration/Evocation spells; War Magic lets you attack after casting a cantrip.",
    "Cavalier":               "Mounted warrior. Born to the Saddle; Unwavering Mark forces an enemy to attack you instead of your allies.",
    "Samurai":                "Disciplined warrior. Fighting Spirit grants temp HP + advantage 3/day. Elegant Courtier adds WIS to Persuasion.",
    "Arcane Archer":          "Magic-imbued archer. Arcane Shots deal special effects on hits: seeking arrows, bursting shadow, gravity well, etc.",
    "Psi Warrior":            "Telekinetic fighter. Psionic Power dice enhance attacks, create damage shields, or move objects remotely.",
    "Rune Knight":            "Giant rune master. Runes inscribed on gear grant powers; grow Large size; deal bonus damage when enlarged.",
    "Echo Knight":            "Manifest a shadowy echo of yourself. Echo can take your place, make opportunity attacks, or serve as your origin.",
    # Monk
    "Way of the Open Hand":   "Pure martial arts mastery. Flurry of Blows extras: push, knock prone, or prevent reactions. Wholeness of Body heals.",
    "Shadow":                 "Ninja-style. Shadow Arts grants darkness-themed spells; Shadow Step teleports between dim-light zones.",
    "Four Elements":          "Elemental ki powers. Spend ki to cast themed spells: Fireball, Water Whip, Fangs of the Fire Snake, and more.",
    "Long Death":             "Death cultist. Touch of Death siphons temp HP from kills; Hour of Reaping frightens all nearby creatures.",
    "Sun Soul":               "Radiant ki blasts as ranged attacks. Searing Arc Strike unleashes a Burning Hands cone fueled by ki.",
    "Drunken Master":         "Unpredictable stagger style. Tipsy Sway: redirect missed attacks to another creature; Drunkard's Luck rerolls with ki.",
    "Kensei":                 "Weapon artisan monk. Kensei Weapons gain finesse/range; Deft Strike adds 1d4 to an unarmed combo hit.",
    "Mercy":                  "Healer monk. Hands of Healing removes conditions or heals; Hands of Harm applies necrotic damage and a condition.",
    "Astral Self":            "Project a translucent astral form. Arms of the Astral Self replace unarmed strikes with WIS-based force damage + reach.",
    "Ascendant Dragon":       "Dragon-disciple. Breath of the Dragon replaces unarmed with elemental breath; Wings Unfurled grants fly speed.",
    # Paladin
    "Oath of Devotion":       "Classic holy warrior. Sacred Weapon adds CHA to attack rolls. Aura of Devotion prevents charm. Holy Nimbus at 20.",
    "Ancients":               "Nature's guardian. Aura of Warding grants resistance to spell damage. Abjure the Extraplanar banishes outsiders.",
    "Vengeance":              "Relentless avenger. Vow of Enmity grants advantage on attacks vs. one target. Relentless Avenger pursues fleers.",
    "Crown":                  "Sovereign of law. Champion Challenge keeps enemies engaged; Warding Bond transfers damage from an ally to you.",
    "Conquest":               "Tyrant paladin. Conquering Presence causes wide fear. Aura of Conquest deals psychic damage to frightened foes.",
    "Redemption":             "Pacifist guardian. Aura of the Guardian transfers damage from allies to you. Emissary of Peace boosts Persuasion.",
    "Glory":                  "Champion of legend. Peerless Athlete supercharges athletic checks; Aura of Alacrity boosts allies' move speed.",
    "Watchers":               "Sentinel vs. extraplanar threats. Watcher's Will grants advantage on saves vs. aberrations, celestials, and fiends.",
    "Oathbreaker":            "Fallen paladin turned dark. Animate Dead for free; Control Undead; Aura of Hate adds CHA bonus to evil attacks.",
    # Ranger
    "Hunter":                 "Classic predator. Colossus Slayer/Horde Breaker/Giant Killer for offense; Uncanny Dodge and MultiAttack Defense.",
    "Beast Master":           "Animal companion forms a fighting bond. Beast's Defense, Share Spells, and coordinated attack synergy.",
    "Gloom Stalker":          "Darkness hunter. Umbral Sight: invisible to darkvision in dark. Dread Ambusher adds an extra attack on round 1.",
    "Horizon Walker":         "Planar wanderer. Planar Warrior adds force damage; Ethereal Step briefly plane-shifts you. Detect Portal.",
    "Monster Slayer":         "Expert hunter of the supernatural. Hunter's Sense reveals vulnerabilities; Slayer's Counter negates enemy spells.",
    "Fey Wanderer":           "Fey-touched wanderer. Dreadful Strikes add psychic damage. Otherworldly Glamour adds WIS to Charisma checks.",
    "Swarmkeeper":            "Commands a swarm of spirit insects. Gathered Swarm deals extra damage, repositions you, or pushes a foe.",
    "Drakewarden":            "Bond with a drake companion that grows with you. Eventually ride it and channel its elemental breath attacks.",
    # Rogue
    "Thief":                  "Versatile burglar. Fast Hands (BA Use Object), Second-Story Work (climb speed), Use Magic Device at level 13.",
    "Assassin":               "Assassinate: advantage on surprised targets, auto-crit if they haven't acted. Infiltration Expertise for disguise.",
    "Arcane Trickster":       "Spellcasting rogue. Enchantment/Illusion wizard spells; Mage Hand Legerdemain for remote pickpocketing.",
    "Inquisitive":            "Detective rogue. Ear for Deceit (never roll below 8 on Insight); Eye for Detail (BA Investigation/Perception).",
    "Mastermind":             "Social manipulator. Master of Tactics: Help from 30 ft. Misdirection redirects enemy attention via Deception.",
    "Scout":                  "Wilderness expert. Skirmisher: move without OA when targeted. Superior Mobility and improved stealth in nature.",
    "Swashbuckler":           "Fencing duelist. Fancy Footwork prevents OA after melee attacks; Rakish Audacity Sneak Attacks without an ally.",
    "Phantom":                "Death-touched. Whispers of the Dead grants a skill/tool proficiency; Tokens of the Departed steal soul power.",
    "Soulknife":              "Psionic blade manifestor. Psychic Blades: finesse energy daggers appear from thin air; reroll skill checks via ki.",
    # Sorcerer
    "Draconic Bloodline":     "Dragon ancestor grants Draconic Resilience (AC 13+DEX, bonus max HP) and damage affinity bonus at level 6.",
    "Wild Magic":             "Unstable arcane conduit. Wild Magic Surge table triggers randomly on spells. Tides of Chaos grants temporary advantage.",
    "Divine Soul":            "Celestial or infernal patron. Access to full Cleric spell list. Empowered Healing enhances healing dice.",
    "Shadow Magic":           "Born of shadow-magic. Eyes of the Dark grants Darkness; Strength of the Grave delays death at 0 HP once/day.",
    "Storm Sorcery":          "Tempest bloodline. Tempestuous Magic fly 10 ft. after casting; Heart of the Storm deals AoE lightning/thunder.",
    "Aberrant Mind":          "Psionic corruption. Telepathic Speech, bonus Enchantment/Divination spells; Mind Link and telepathic communication.",
    "Clockwork Soul":         "Mechanus order. Restore Balance cancels advantage/disadvantage. Bonus abjuration/transmutation spells.",
    "Lunar Sorcery":          "Moon-phase magic. Lunar Embodiment changes bonus spells by moon phase; Moon Fire channels Sacred Flame at range.",
    # Warlock
    "The Archfey":            "Capricious fey lord. Fey Presence: charm or frighten in 10 ft. (WIS save). Misty Escape: teleport + invisible on damage.",
    "The Fiend":              "Devil's bargain. Dark One's Blessing: gain temp HP on kill. Dark One's Own Luck adds d10 to a check/save.",
    "The Great Old One":      "Alien cosmic entity. Telepathy 30 ft. Entropic Ward imposes disadvantage, then grants advantage if the attack missed.",
    "The Undying":            "Immortal patron. Among the Dead: undead ignore you. Defy Death: stabilize at 0 HP and regain HP once/short rest.",
    "The Celestial":          "Angelic patron. Healing Light pool (d6s) heals freely. Radiant Soul adds CHA bonus to one radiant/fire damage roll.",
    "The Hexblade":           "Weapon-spirit patron. Hexblade's Curse adds PB to damage and crit range. Hex Warrior uses CHA for one weapon.",
    "The Fathomless":         "Deep ocean entity. Tentacle of the Deeps summoned for attacks and grappling. Gift of the Sea: swim + water breath.",
    "The Genie":              "Noble Genie patron. Genie's Vessel: rest inside a bottle + choose elemental damage affinity. Elemental Gift buffs.",
    "The Undead":             "Power of undeath. Form of Dread: bonus temp HP, cause fear, ignore fear immunity; reroll one damage die per turn.",
    # Wizard
    "School of Abjuration":  "Protective specialist. Arcane Ward: HP pool fueled by Abjuration spell casting absorbs incoming damage.",
    "Conjuration":            "Summoner. Minor Conjuration creates small objects. Focused Conjuration: concentration can't break from damage.",
    "Divination":             "Oracle. Portent: roll 2d20 at dawn, replace any d20 result with your portent dice. Enormously powerful.",
    "Enchantment":            "Mind-bender. Hypnotic Gaze entrances a creature; Instinctive Charm redirects attacks to another target.",
    "Evocation":              "Blast specialist. Sculpt Spells protects allies inside AoE; Potent Cantrip still deals half damage on a save.",
    "Illusion":               "Master of deception. Improved Minor Illusion adds sound to image. Illusory Self creates a phantasmal duplicate.",
    "Necromancy":             "Death magic. Grim Harvest heals you when your spells kill. Undead Thralls animate extra corpses as minions.",
    "Transmutation":          "Shape-changer. Transmuter's Stone grants a persistent buff. Master Transmuter can swap stone for major effects.",
    "War Magic":              "Battle wizard. Arcane Deflection (reaction): +2 AC or +4 save. Tactical Wit adds INT to initiative rolls.",
    "Bladesinging":           "Elf martial-arcane tradition. Bladesong adds INT to AC and movement speed. Extra Attack at level 6.",
    "Chronurgy":              "Time manipulation. Chronal Shift rerolls any creature's d20 twice per day. Momentary Stasis briefly paralyzes.",
    "Graviturgy":             "Gravity control. Adjust Density makes targets heavy or light. Event Horizon pulls nearby creatures inward.",
    # Artificer
    "Alchemist":              "Potion-brewer. Experimental Elixir provides random magical benefits each long rest. Bonus healing formula spells.",
    "Armorer":                "Living suit of armor. Arcane Armor integrates into your body. Guardian or Infiltrator model defines combat role.",
    "Artillerist":            "Turret specialist. Eldritch Cannon (flamethrower, force ballista, or protector) deployed as a construct.",
    "Battle Smith":           "Defender with a steel guardian construct. Steel Defender fights alongside you. Battle-ready uses INT for attacks.",
}

# ── Background Descriptions ───────────────────────────────────────────────────
BACKGROUND_DESC = {
    "Acolyte":    "Devoted temple servant. Proficiencies: Insight, Religion. Two bonus languages. Feature: Shelter of the Faithful.",
    "Criminal":   "Life of crime. Proficiencies: Deception, Stealth. Tools: gaming set, thieves' tools. Feature: Criminal Contact.",
    "Folk Hero":  "Champion of the common people. Proficiencies: Animal Handling, Survival. Tools: artisan's tools, land vehicles.",
    "Noble":      "Privileged upbringing. Proficiencies: History, Persuasion. Tools: gaming set. Language: one. Feature: Position of Privilege.",
    "Sage":       "Scholarly researcher. Proficiencies: Arcana, History. Two bonus languages. Feature: Researcher (know where to find any lore).",
    "Soldier":    "Military veteran. Proficiencies: Athletics, Intimidation. Tools: gaming set, land vehicles. Feature: Military Rank.",
    "Entertainer":"Performer and showperson. Proficiencies: Acrobatics, Performance. Tools: disguise kit, musical instrument of choice.",
    "Artisan":    "Skilled craftsperson. Proficiencies: History, Persuasion. Tools: artisan's tools of choice. Feature: Guild Membership.",
    "Hermit":     "Reclusive contemplative. Proficiencies: Medicine, Religion. Tools: herbalism kit. Language: one. Feature: Discovery.",
    "Charlatan":  "Con artist. Proficiencies: Deception, Sleight of Hand. Tools: disguise kit, forgery kit. Feature: False Identity.",
    "Outlander":  "Wilderness wanderer. Proficiencies: Athletics, Survival. Tools: musical instrument. Language: one. Feature: Wanderer.",
    "Sailor":     "Sea-faring veteran. Proficiencies: Athletics, Perception. Tools: navigator's tools, water vehicles. Feature: Ship's Passage.",
    "Urchin":     "Street-raised survivor. Proficiencies: Sleight of Hand, Stealth. Tools: disguise kit, thieves' tools. Feature: City Secrets.",
}

# ── Equipment Descriptions ────────────────────────────────────────────────────
EQUIPMENT_DESC = {
    "Greataxe":              "Barbarian's iconic weapon. Heavy, Two-Handed, d12. Brutal with Reckless Attack—consistent crits in rage.",
    "Rapier":                "Elegant dueling blade. Finesse (DEX or STR), d8 damage. Best one-handed finesse weapon for light builds.",
    "Longsword":             "Versatile knight's weapon. d8 one-handed or d10 two-handed. Pairs well with a shield or two-handed style.",
    "Quarterstaff":          "Simple staff, d6 or d8 versatile. Druid/Wizard staple. Shillelagh makes it WIS-based for Druids.",
    "Shortsword":            "Light finesse blade, d6 piercing. Ideal for two-weapon fighting or as a Monk's chosen weapon.",
    "Mace":                  "Cleric staple. d6 bludgeoning—bypasses B/P/S resistance splits on some creatures. No STR minimum.",
    "Warhammer":             "d8 bludgeoning, Versatile. Martial proficiency required. War/Forge Clerics wield this effectively.",
    "Scimitar":              "d6 slashing, Finesse and Light. Ideal Druid weapon—pairs with shield or off-hand for two-weapon fighting.",
    "Handaxe":               "d6 slashing, Light, Thrown 20/60 ft. Barbarian utility—throw before closing into melee or use off-hand.",
    "Dagger":                "d4 piercing, Finesse, Light, Thrown 20/60 ft. Fallback for casters. Off-hand bonus attack option.",
    "Javelin":               "d6 piercing, Thrown 30/120 ft. Barbarian's disposable ranged opener before closing into melee.",
    "Light Crossbow":        "d8 piercing, Loading, range 80/320 ft. Best simple ranged weapon—no STR requirement.",
    "Shortbow":              "d6 piercing, range 80/320 ft. No loading. Reliable ranged Sneak Attack delivery for Rogues.",
    "Longbow":               "d8 piercing, Heavy, Two-Handed, range 150/600 ft. Ranger's signature ranged weapon. Pairs with Hunter's Mark.",
    "Chain Mail":            "AC 16, Heavy, Stealth disadvantage, requires STR 13. Strong flat AC with no DEX cap. Classic knight armor.",
    "Scale Mail":            "AC 14 + DEX mod (max +2). Medium armor with Stealth disadvantage. Solid mid-tier before better armor.",
    "Leather Armor":         "AC 11 + DEX mod. Light armor, no Stealth penalty. Ideal for high-DEX and stealthy characters.",
    "Shield":                "+2 AC, requires one free hand. Cannot combine with two-weapon fighting or two-handed weapons.",
    "Explorer's Pack":       "Bedroll, mess kit, tinderbox, 10 torches, 10 rations, waterskin, 50 ft. rope. General all-purpose kit.",
    "Dungeoneer's Pack":     "Crowbar, hammer, 10 pitons, 10 torches, tinderbox, 10 rations, waterskin, 50 ft. rope. Dungeon-focused.",
    "Priest's Pack":         "Blanket, candles, tinderbox, alms box, incense, censer, vestments, 2 rations, waterskin. Cleric standard.",
    "Scholar's Pack":        "Book of lore, ink, ink pen, 10 parchment sheets, bag of sand, small knife. Essential for Wizards.",
    "Burglar's Pack":        "1000 ball bearings, string, bell, candles, crowbar, hammer, pitons, bullseye lantern. Rogue essentials.",
    "Diplomat's Pack":       "Chest, scroll cases, fine clothes, ink, lamp, oil, paper. Formal social interactions and negotiation.",
    "Entertainer's Pack":    "Bedroll, 2 costumes, candles, 5 rations, waterskin, disguise kit. For performers on the road.",
    "Holy Symbol":           "Divine focus for Cleric/Paladin spells. Worn, emblazoned on shield, or held—no hands needed if worn.",
    "Druidic Focus":         "Mistletoe sprig, totem, wooden staff, or yew wand. Required to cast Druid spells with material components.",
    "Component Pouch":       "All non-costly spell material components. Replaces tracking most per-spell material requirements.",
    "Arcane Focus":          "Crystal, orb, rod, staff, or wand. Replaces non-costly materials for Wizard/Sorcerer/Warlock spells.",
    "Thieves' Tools":        "Lockpicks for disabling devices and locks. Core Rogue tool. Also Artificers' default proficiency tool.",
    "Spellbook":             "Wizard's tome. Starts with 6 1st-level spells + INT mod bonus. Copy more spells from scrolls or tomes.",
    "Lute":                  "Bard's signature stringed instrument. Resonant and complex—doubles as spellcasting focus.",
    "Lyre":                  "Compact plucked string instrument. Elegant and portable. Serves as a Bard's spellcasting focus.",
    "Drum":                  "Percussive instrument—loud and driving. Can signal allies from a distance in the field.",
    "Flute":                 "Lightweight woodwind. Ideal for stealthy bards and wilderness travel. Easy to carry.",
    "Viol":                  "Bowed string instrument with rich resonance. Favored by College of Eloquence and Whispers bards.",
    "Pan Flute":             "Multi-pipe reed instrument. Associated with Fey music. Favored by nature and Glamour bards.",
    "Shawm":                 "Double-reed woodwind—loud and piercing. Excellent for outdoor performances and battlefield morale.",
    "Unarmored Defense":     "Barbarians: AC = 10 + DEX mod + CON mod. Monks: AC = 10 + DEX mod + WIS mod. No armor required.",
    "Two Daggers":           "Dual finesse light blades (d4 each). Fallback melee + off-hand bonus attack. Rogues' close-quarters tools.",
    "Five Javelins":         "Five Thrown javelins (d6 each, 30/120 ft.). Paladin ranged option before closing into melee.",
    "Ten Darts":             "10 darts (d4 each, Finesse, Thrown 20/60 ft.). Monk's ranged fallback paired with Flurry of Blows.",
}

# ── Spell Descriptions ────────────────────────────────────────────────────────
SPELL_DESC = {
    # Cantrips
    "Acid Splash":         "Range 60 ft. One or two creatures within 5 ft. of each other take 1d6 acid (DEX save). Scales at Lv5/11/17.",
    "Blade Ward":          "Reaction. Gain resistance to B/P/S damage from weapon attacks until end of your next turn. No damage output.",
    "Booming Blade":       "Melee weapon attack: weapon damage + 1d8 thunder if target moves voluntarily. Scales at Lv5/11/17.",
    "Chill Touch":         "Range 120 ft. 1d8 necrotic on hit; target can't regain HP until next turn. Undead have attack disadvantage.",
    "Control Flames":      "Manipulate nonmagical flames within 60 ft.: expand, extinguish, shape, or change color. Pure utility.",
    "Create Bonfire":      "Range 60 ft. Conjure a bonfire in a 5 ft. space. Creatures inside take 1d8 fire (DEX save). Concentration.",
    "Dancing Lights":      "Range 120 ft. Create 4 hovering lights for 1 minute. Concentration. Illumination and distraction utility.",
    "Druidcraft":          "Minor nature effects: predict weather, bloom flowers, create tiny sensory effects. Pure roleplay utility.",
    "Eldritch Blast":      "Range 120 ft. 1d10 force damage per beam. Multi-beam at higher levels. The Warlock's primary attack cantrip.",
    "Fire Bolt":           "Range 120 ft. 1d10 fire damage—highest single-target cantrip damage. Scales at Lv5/11/17.",
    "Friends":             "Concentration, 1 min. One non-hostile creature has advantage on CHA checks toward you. They know afterward.",
    "Green-Flame Blade":   "Melee weapon attack: weapon damage + 1d8 fire that leaps to a second creature within 5 ft.",
    "Guidance":            "Touch. Concentration, 1 min. Target adds 1d4 to one ability check. Most useful non-combat cantrip.",
    "Gust":                "Range 30 ft. Push a creature 5 ft. (STR save), push an object, or create a window-rattling gust. Minor utility.",
    "Infestation":         "Range 30 ft. 1d6 poison (CON save) and the target moves 5 ft. in a random direction on a failed save.",
    "Light":               "Touch. Object sheds bright light 20 ft., dim 40 ft. for 1 hr. Hostile creature holding it gets CHA save.",
    "Mage Hand":           "Range 30 ft. Spectral hand manipulates objects, opens doors, retrieves items within 60 ft. Cannot attack.",
    "Mending":             "Touch. Repair a single break or tear in an object up to 1 ft. long over 1 minute. Fixes gear.",
    "Message":             "Range 120 ft. Whisper to one creature; they can whisper a reply only you hear. Discreet communication.",
    "Minor Illusion":      "Range 30 ft. Create a sound or image (not both). Concentration-free for 1 min. Versatile deception tool.",
    "Mold Earth":          "Range 30 ft. Move 5 ft. of loose earth, create difficult terrain, or dig. Utility cantrip.",
    "Poison Spray":        "Range 10 ft. CON save or take 1d12 poison damage—highest single-cantrip damage but very short range.",
    "Prestidigitation":    "Range 10 ft. Minor magical trick: clean, soil, chill, warm, flavor, or make a small sensory mark. Pure utility.",
    "Produce Flame":       "Hold a harmless flame for light, or hurl it 30 ft. for 1d8 fire damage. Combines utility and offense.",
    "Ray of Frost":        "Range 60 ft. 1d8 cold damage and target's speed reduced by 10 ft. until your next turn. Battlefield control.",
    "Resistance":          "Touch. Concentration, 1 min. Target adds 1d4 to one saving throw. Best used before a known dangerous save.",
    "Sacred Flame":        "Range 60 ft. DEX save (ignores cover) or 1d8 radiant. Useful against prone or heavily shielded enemies.",
    "Shape Water":         "Range 30 ft. Move, freeze, or animate up to 5 ft. cube of water. Utility only.",
    "Shillelagh":          "Bonus action. Club/quarterstaff becomes magical: use WIS for attack and damage rolls. Perfect WIS-Druid weapon.",
    "Shocking Grasp":      "Melee spell attack. 1d8 lightning; target can't take reactions until next turn. Escape melee cleanly.",
    "Spare the Dying":     "Touch. Stabilize a creature at 0 HP instantly. No healing, no resource—stops death saves. Unlimited use.",
    "Sword Burst":         "Self 5-ft. radius. DEX save or 1d6 force damage to all within range. Area denial when surrounded.",
    "Thaumaturgy":         "Range 30 ft. Minor divine miracles: loud voice, flickering flames, tremors, eye color change. Roleplay utility.",
    "Thunderclap":         "Self 5-ft. radius. CON save or 1d6 thunder—audible 100 ft. away. Short-range crowd control starter.",
    "Toll the Dead":       "Range 60 ft. WIS save or 1d8 necrotic (1d12 if missing HP). Strongest damage cantrip vs. wounded foes.",
    "True Strike":         "Range 30 ft. Concentration. Advantage on next attack vs. target. Often too slow—costs your action first.",
    "Vicious Mockery":     "Range 60 ft. WIS save or 1d4 psychic + disadvantage on next attack roll. Reliable Bard control cantrip.",
    "Virtue":              "Touch. Concentration, 1 min. Target gains 1 temporary HP. Minimal combat value; mostly symbolic.",
    "Word of Radiance":    "Self 5-ft. radius. CON save or 1d6 radiant. Like Thunderclap but radiant damage. Cleric melee splash.",
    # 1st-level spells
    "Absorb Elements":     "Reaction. Resist triggering elemental damage type; next melee attack deals +1d6 of that type. No concentration.",
    "Alarm":               "Ritual. Set a mental or audible alarm on an area for 8 hours. Concentration-free anti-stealth utility.",
    "Animal Friendship":   "Range 30 ft. Charm a Beast for 24 hours (WIS save). Only works if the creature's INT is 3 or lower.",
    "Armor of Agathys":    "Self. Gain 5 temp HP; any melee attacker takes 5 cold damage. Scales with slot level. No concentration.",
    "Arms of Hadar":       "10-ft. radius self. STR save or 2d6 necrotic + lose reactions until next turn. Short range AoE.",
    "Bane":                "Range 30 ft. Concentration 1 min. Up to 3 creatures subtract 1d4 from attack rolls and saving throws.",
    "Bless":               "Range 30 ft. Concentration 1 min. Up to 3 creatures add 1d4 to attack rolls and saving throws. Elite support.",
    "Burning Hands":       "15-ft. cone. DEX save or 3d6 fire, half on save. Classic AoE opener for Sorcerers and Wizards.",
    "Catapult":            "Range 60 ft. Hurl an object 1–5 lbs. DEX save or 3d8 bludgeoning. Creative environmental damage.",
    "Cause Fear":          "Range 60 ft. WIS save or one creature is frightened for 1 min (concentration). Disables enemy aggression.",
    "Charm Person":        "Range 30 ft. WIS save. Target is charmed (treats you as friendly) for 1 hr or until harmed. Social tool.",
    "Chromatic Orb":       "Range 90 ft. Ranged spell attack: 3d8 of chosen element. Requires a 50gp diamond. Versatile damage.",
    "Color Spray":         "15-ft. cone. Blind creatures totaling 6d10 HP (lowest HP first). Powerful opening crowd control.",
    "Command":             "Range 60 ft. WIS save. One-word command (Flee, Drop, Halt, Grovel) obeyed on their next turn.",
    "Compelled Duel":      "Range 30 ft. WIS save. Target has disadvantage attacking others and must move toward you. Paladin taunt.",
    "Comprehend Languages":"Ritual, 1 hr. Understand any spoken and written language. Doesn't grant speaking ability. Utility.",
    "Create or Destroy Water":"Range 30 ft. Create 10 gallons of water or destroy fog/rain in a 30 ft. cube. Environmental utility.",
    "Cure Wounds":         "Touch. Restore 1d8 + spellcasting mod HP. No concentration. Good healing but weaker action cost than Healing Word.",
    "Defense of the Faithful":"Bonus action, Range 30 ft. Grant an ally +1d4 to their next saving throw. Paladin support.",
    "Detect Evil and Good":"Self, 30 ft. Concentration 10 min. Sense aberrations, celestials, elementals, fey, fiends, undead nearby.",
    "Detect Magic":        "Ritual, Self, 30 ft. Concentration 10 min. Sense and identify magic auras. Essential dungeon exploration tool.",
    "Detect Poison and Disease":"Ritual, Self, 30 ft. Concentration 10 min. Sense all poisons, diseases, and their sources.",
    "Disguise Self":       "Self. Change your appearance (height ±1 ft., different clothes/features). Illusion only—no touch verification.",
    "Dissonant Whispers":  "Range 60 ft. WIS save or 3d6 psychic damage + flee immediately (provoking OA). Half damage on save.",
    "Divine Favor":        "Self. Bonus action. Concentration 1 min. Weapon attacks deal +1d4 radiant damage. Paladin smite enabler.",
    "Earth Tremor":        "5-ft. radius self. DEX save or 1d6 bludgeoning + knocked prone. Creates difficult terrain. Area control.",
    "Entangle":            "Range 90 ft. 20-ft. square. STR save or restrained (STR check to escape each turn). Concentration 1 min.",
    "Ensnaring Strike":    "Self. Concentration 1 min. Next ranged hit: STR save or restrained, taking 1d6 piercing/turn.",
    "Expeditious Retreat": "Self. Bonus action Dash each turn for 10 min (concentration). Closing distance or escaping combat fast.",
    "Faerie Fire":         "Range 60 ft. 20-ft. cube. DEX save or outlined: attacks vs. outlined creatures have advantage. Concentration.",
    "False Life":          "Self. Gain 1d4+4 temporary HP for 1 hr. No concentration. Cheap buffer for squishy spellcasters.",
    "Feather Fall":        "Reaction, Range 60 ft. Up to 5 creatures fall at 60 ft/round and take no fall damage. Critical safety reaction.",
    "Find Familiar":       "Ritual. Summon a magical familiar (cat, owl, raven, etc.). Deliver touch spells, scout ahead. Permanent.",
    "Fog Cloud":           "Range 120 ft. 20-ft. radius sphere, heavily obscured for 1 hr (concentration). Total vision block.",
    "Goodberry":           "Touch. Up to 10 berries created. Each heals 1 HP and provides a day of nourishment. Excellent rationing.",
    "Grease":              "Range 60 ft. 10-ft. square. DEX save or fall prone. Difficult terrain. Concentration-free for 1 min.",
    "Guiding Bolt":        "Range 120 ft. Ranged spell attack: 4d6 radiant, next attack roll vs. target has advantage. Strong opener.",
    "Hail of Thorns":      "Self. Bonus action. Next ranged attack also hits all within 5 ft. of target for 1d10 piercing (DEX save).",
    "Healing Word":        "Bonus action, Range 60 ft. 1d4 + mod HP. Bonus action and range make this superior to Cure Wounds in combat.",
    "Hellish Rebuke":      "Reaction, Range 60 ft. When damaged, deal 2d10 fire (DEX save, half). Powerful Warlock reaction.",
    "Heroism":             "Touch. Concentration 1 min. Target immune to fright and gains PB temp HP at start of each turn.",
    "Hex":                 "Bonus action, Range 90 ft. Concentration 1 hr. +1d6 necrotic on each hit + disadvantage on one ability check.",
    "Hunter's Mark":       "Bonus action, Range 90 ft. Concentration 1 hr. +1d6 damage vs. marked target; advantage on Perception/Survival.",
    "Identify":            "Ritual, Touch. Learn the magical properties of an item or the spells affecting a creature. Essential loot tool.",
    "Illusory Script":     "Touch. Write a message only intended recipients can read; others see a different message. Social utility.",
    "Inflict Wounds":      "Melee spell attack. 3d10 necrotic damage on hit. Highest 1st-level damage—but requires melee contact.",
    "Jump":                "Touch. Concentration 1 min. Target's jump distance tripled. Useful for vertical traversal and obstacles.",
    "Longstrider":         "Touch. Speed increases by 10 ft. for 1 hr. No concentration. Stack with other movement bonuses.",
    "Mage Armor":          "Touch. Willing creature's AC = 13 + DEX mod for 8 hrs. No concentration. Essential for unarmored casters.",
    "Magic Missile":       "Range 120 ft. Three darts each deal 1d4+1 force—never misses. Reliable finisher for low-HP targets.",
    "Protection from Evil and Good":"Touch. Concentration 1 min. Blocks charm, fright, and possession from aberrations/celestials/fiends/undead.",
    "Purify Food and Drink":"Ritual, Range 10 ft. Purify 5-ft. sphere of food and water. Removes poison and disease from consumables.",
    "Ray of Sickness":     "Range 60 ft. Ranged spell attack: 2d8 poison, CON save or poisoned until end of next turn. Reliable condition.",
    "Sanctuary":           "Range 30 ft. Bonus action. Concentration 1 min. Attackers must make WIS save to target the warded creature.",
    "Searing Smite":       "Self. Concentration 1 min. Next hit: +1d6 fire; target ignites (1d6/turn, CON save each turn to extinguish).",
    "Shield":              "Reaction. +5 AC until next turn (including trigger). Also blocks Magic Missile. Best defense reaction in the game.",
    "Shield of Faith":     "Range 60 ft. Concentration 10 min. +2 AC to a creature. Excellent early tank or ally booster.",
    "Silent Image":        "Range 60 ft. 15-ft. cube illusion. Concentration 10 min. Visual only—no sound, smell, or physical presence.",
    "Silvery Barbs":       "Reaction, Range 60 ft. Force a d20 reroll (attack/save/check); another creature gains advantage on its next roll.",
    "Sleep":               "Range 90 ft. 20-ft. sphere. Knock unconscious creatures totaling 5d8 HP (lowest HP first). Very strong early.",
    "Snare":               "Touch. Set a magical trap on the ground—humanoid triggers it: DEX save or restrained for 8 hours.",
    "Speak with Animals":  "Ritual, Self, 1 hr. Comprehend and communicate with beasts. Roleplay and information powerhouse.",
    "Tasha's Caustic Brew":"Self, 30-ft. line. DEX save or doused in acid: 2d4 acid/turn (action to remove). Concentration.",
    "Tasha's Hideous Laughter":"Range 30 ft. WIS save. Target falls prone, incapacitated for 1 min (concentration). Strong CC vs. low-WIS foes.",
    "Tenser's Floating Disk":"Ritual, Range 30 ft. Floating disk follows you, holds 500 lbs. for 1 hr. Unlimited carrying capacity utility.",
    "Thunderous Smite":    "Self, Concentration 1 min. Next hit: +2d6 thunder; STR save or pushed 10 ft. and knocked prone.",
    "Thunderwave":         "Self, 15-ft. cube. CON save or 2d8 thunder + pushed 10 ft. Half on save. Excellent melee crowd control.",
    "Unseen Servant":      "Ritual, Range 60 ft. Invisible mindless servant (AC 10, 1 HP, STR 2) follows simple commands for 1 hr.",
    "Witch Bolt":          "Range 30 ft. Ranged spell attack: 1d12 lightning. Concentration: repeat damage as action on subsequent turns.",
    "Wrathful Smite":      "Self, Concentration 1 min. Next hit: +1d6 psychic; WIS save or frightened (save each turn to break).",
    "Zephyr Strike":       "Self, Concentration 1 min. Pass through creatures without OA; once: advantage on one attack + +1d8 force.",
}

# ── Loadout Data (per class) ──────────────────────────────────────────────────
LOADOUT_DATA = {
    "Barbarian": {
        "armor_choices":     ["Unarmored Defense (10 + DEX mod + CON mod)",
                              "Chain Mail (AC 16, Stealth disadvantage, requires STR 13)"],
        "weapon_primary":    ["Greataxe (1d12 slashing, Heavy, Two-Handed)",
                              "Greatsword (2d6 slashing, Heavy, Two-Handed)",
                              "Two Handaxes (1d6 slashing each, Light, Thrown 20/60 ft. — dual wield)"],
        "weapon_secondary":  ["Two Handaxes (1d6 slashing, Light, Thrown 20/60 ft.)",
                              "Any Simple Weapon"],
        "pack_choices":      ["Explorer's Pack", "Dungeoneer's Pack"],
        "focus_choices":     [],
        "instrument_choices":[],
        "fixed_gear":        ["4 Javelins (1d6 piercing, Thrown 30/120 ft.)"],
        "spellcaster":       False,
    },
    "Bard": {
        "armor_choices":     ["Leather Armor (AC 11 + DEX mod, no Stealth penalty)"],
        "weapon_primary":    ["Rapier (1d8 piercing, Finesse)",
                              "Longsword (1d8 slashing, Versatile)",
                              "Any Simple Weapon"],
        "weapon_secondary":  ["Dagger (1d4 piercing, Finesse, Light, Thrown 20/60 ft.)"],
        "pack_choices":      ["Diplomat's Pack", "Entertainer's Pack"],
        "focus_choices":     ["Musical Instrument (serves as spellcasting focus)"],
        "instrument_choices":["Lute","Lyre","Drum","Flute","Viol","Pan Flute","Shawm"],
        "fixed_gear":        [],
        "spellcaster":       True,
        "cantrips_label":    "Bard Cantrips Known (choose 2)",
        "cantrips_count":    2,
        "cantrip_pool":      ["Blade Ward","Dancing Lights","Friends","Light","Mage Hand",
                              "Minor Illusion","Prestidigitation","Thunderclap","True Strike","Vicious Mockery"],
        "spells_label":      "1st-Level Spells Known (choose 4)",
        "spells_count":      4,
        "spell_pool":        ["Animal Friendship","Bane","Charm Person","Color Spray","Command",
                              "Comprehend Languages","Cure Wounds","Detect Magic","Disguise Self",
                              "Dissonant Whispers","Earth Tremor","Faerie Fire","Feather Fall",
                              "Healing Word","Heroism","Identify","Longstrider","Silent Image",
                              "Silvery Barbs","Sleep","Speak with Animals","Tasha's Hideous Laughter",
                              "Thunderwave","Unseen Servant"],
        "slots_1st":         2,
    },
    "Cleric": {
        "armor_choices":     ["Scale Mail (AC 14, Stealth disadvantage)",
                              "Leather Armor (AC 11 + DEX mod)",
                              "Chain Mail (AC 16, requires STR 13)"],
        "weapon_primary":    ["Mace (1d6 bludgeoning, Simple)",
                              "Warhammer (1d8 bludgeoning, Versatile — martial proficiency required)",
                              "Morningstar (1d8 piercing, Simple Weapon, one-handed)"],
        "weapon_secondary":  ["Light Crossbow + 20 Bolts (1d8 piercing, range 80/320 ft.)",
                              "Any Simple Weapon"],
        "pack_choices":      ["Priest's Pack", "Explorer's Pack"],
        "focus_choices":     ["Holy Symbol (worn, emblazoned on shield, or held)"],
        "instrument_choices":[],
        "fixed_gear":        ["Shield (+2 AC when wielded)"],
        "spellcaster":       True,
        "cantrips_label":    "Cleric Cantrips Known (choose 3)",
        "cantrips_count":    3,
        "cantrip_pool":      ["Guidance","Light","Mending","Resistance","Sacred Flame",
                              "Spare the Dying","Thaumaturgy","Toll the Dead","Word of Radiance","Virtue"],
        "spells_label":      "1st-Level Spells Prepared (choose WIS mod + level, minimum 1)",
        "spells_count":      4,
        "spell_pool":        ["Bane","Bless","Command","Create or Destroy Water","Cure Wounds",
                              "Detect Evil and Good","Detect Magic","Detect Poison and Disease",
                              "Guiding Bolt","Healing Word","Inflict Wounds",
                              "Protection from Evil and Good","Purify Food and Drink",
                              "Sanctuary","Shield of Faith","Silvery Barbs"],
        "slots_1st":         2,
    },
    "Druid": {
        "armor_choices":     ["Leather Armor (AC 11 + DEX mod — compatible with Wild Shape)"],
        "weapon_primary":    ["Wooden Shield + Quarterstaff (1d6/d8 bludgeoning, Versatile — defensive caster)",
                              "Scimitar (1d6 slashing, Finesse, Light — offensive blade)",
                              "Two Simple Weapons (1d6+STR each — dual offense build)"],
        "weapon_secondary":  ["Scimitar (1d6 slashing, Finesse, Light)",
                              "Any Simple Melee Weapon"],
        "pack_choices":      ["Explorer's Pack"],
        "focus_choices":     ["Druidic Focus (staff, totem, sprig of mistletoe, or yew wand)"],
        "instrument_choices":[],
        "fixed_gear":        [],
        "spellcaster":       True,
        "cantrips_label":    "Druid Cantrips Known (choose 2)",
        "cantrips_count":    2,
        "cantrip_pool":      ["Druidcraft","Guidance","Mending","Poison Spray","Produce Flame",
                              "Resistance","Shape Water","Shillelagh","Spare the Dying","Thunderclap"],
        "spells_label":      "1st-Level Spells Prepared (choose WIS mod + level, minimum 1)",
        "spells_count":      4,
        "spell_pool":        ["Animal Friendship","Absorb Elements","Charm Person",
                              "Create or Destroy Water","Cure Wounds","Detect Magic",
                              "Detect Poison and Disease","Earth Tremor","Entangle",
                              "Faerie Fire","Fog Cloud","Goodberry","Healing Word",
                              "Jump","Longstrider","Purify Food and Drink",
                              "Speak with Animals","Thunderwave"],
        "slots_1st":         2,
    },
    "Fighter": {
        "armor_choices":     ["Chain Mail (AC 16, Stealth disadvantage, requires STR 13)",
                              "Leather Armor + Longbow + 20 Arrows (AC 11+DEX, stealth-friendly)"],
        "weapon_primary":    ["Longsword + Shield (1d8 slashing, Versatile; Shield +2 AC)",
                              "Greatsword (2d6 slashing, Heavy, Two-Handed — max damage build)",
                              "Two Handaxes (1d6 slashing, Light, Thrown — two-weapon fighting)"],
        "weapon_secondary":  ["Light Crossbow + 20 Bolts (1d8 piercing, range 80/320 ft.)",
                              "Two Handaxes (1d6 slashing, Light, Thrown)"],
        "pack_choices":      ["Dungeoneer's Pack", "Explorer's Pack"],
        "focus_choices":     [],
        "instrument_choices":[],
        "fixed_gear":        [],
        "spellcaster":       False,
    },
    "Monk": {
        "armor_choices":     ["Unarmored Defense (10 + DEX mod + WIS mod — no armor or shield)"],
        "weapon_primary":    ["Shortsword (1d6 piercing, Finesse, Light — standard Monk blade)",
                              "Quarterstaff (1d6/d8 bludgeoning, Versatile — scales with Martial Arts)",
                              "Spear (1d6/d8 piercing, Versatile, Thrown 20/60 ft.)"],
        "weapon_secondary":  ["Unarmed Strike (1 + STR mod, scales to d6 at Lv1 via Martial Arts)"],
        "pack_choices":      ["Dungeoneer's Pack", "Explorer's Pack"],
        "focus_choices":     [],
        "instrument_choices":[],
        "fixed_gear":        ["Ten Darts (1d4 piercing, Finesse, Thrown 20/60 ft.)"],
        "spellcaster":       False,
    },
    "Paladin": {
        "armor_choices":     ["Chain Mail (AC 16)",
                              "Leather Armor (AC 11+DEX for lower STR builds)"],
        "weapon_primary":    ["Longsword + Shield (1d8 slashing, Versatile; Shield +2 AC — classic Paladin)",
                              "Halberd (1d10 slashing, Heavy, Reach, Two-Handed — area smite style)",
                              "Two Shortswords (1d6 piercing, Finesse, Light — dual smite build)"],
        "weapon_secondary":  ["Five Javelins (1d6 piercing, Thrown 30/120 ft.)",
                              "Any Simple Melee Weapon"],
        "pack_choices":      ["Priest's Pack", "Explorer's Pack"],
        "focus_choices":     ["Holy Symbol (worn, emblazoned, or held)"],
        "instrument_choices":[],
        "fixed_gear":        [],
        "spellcaster":       True,
        "cantrips_label":    None,
        "cantrips_count":    0,
        "cantrip_pool":      [],
        "spells_label":      "1st-Level Spells Prepared (choose CHA mod + half-level, min 1)",
        "spells_count":      3,
        "spell_pool":        ["Bless","Command","Compelled Duel","Cure Wounds","Defense of the Faithful",
                              "Detect Evil and Good","Detect Magic","Detect Poison and Disease",
                              "Divine Favor","Heroism","Protection from Evil and Good",
                              "Purify Food and Drink","Searing Smite","Shield of Faith",
                              "Silvery Barbs","Thunderous Smite","Wrathful Smite"],
        "slots_1st":         2,
    },
    "Ranger": {
        "armor_choices":     ["Scale Mail (AC 14, Stealth disadvantage)",
                              "Leather Armor (AC 11+DEX, stealth-friendly)"],
        "weapon_primary":    ["Two Shortswords (1d6 piercing, Finesse, Light — two-weapon fighting)",
                              "Longbow + Quiver of 20 Arrows (1d8 piercing, range 150/600 ft. — pure archer)",
                              "Handaxe + Shortsword (1d6 each — mixed melee/thrown style)"],
        "weapon_secondary":  ["Longbow + Quiver of 20 Arrows (1d8 piercing, range 150/600 ft.)"],
        "pack_choices":      ["Dungeoneer's Pack", "Explorer's Pack"],
        "focus_choices":     [],
        "instrument_choices":[],
        "fixed_gear":        [],
        "spellcaster":       True,
        "cantrips_label":    None,
        "cantrips_count":    0,
        "cantrip_pool":      [],
        "spells_label":      "1st-Level Spells Known — Chronicles RPG (choose 2)",
        "spells_count":      2,
        "spell_pool":        ["Absorb Elements","Alarm","Animal Friendship","Cure Wounds",
                              "Detect Magic","Detect Poison and Disease","Entangle",
                              "Ensnaring Strike","Faerie Fire","Fog Cloud","Goodberry",
                              "Hail of Thorns","Hunter's Mark","Jump","Longstrider",
                              "Speak with Animals","Zephyr Strike"],
        "slots_1st":         2,
    },
    "Rogue": {
        "armor_choices":     ["Leather Armor (AC 11 + DEX mod, no Stealth penalty)"],
        "weapon_primary":    ["Rapier (1d8 piercing, Finesse — high single-target damage)",
                              "Shortsword (1d6 piercing, Finesse, Light — two-weapon option)",
                              "Hand Crossbow + 20 Bolts (1d6 piercing, Light, range 30/120 ft. — Sneak Attack eligible)"],
        "weapon_secondary":  ["Shortbow + Quiver of 20 Arrows (1d6 piercing, range 80/320 ft.)",
                              "Shortsword (second blade for two-weapon fighting)"],
        "pack_choices":      ["Burglar's Pack", "Dungeoneer's Pack", "Explorer's Pack"],
        "focus_choices":     [],
        "instrument_choices":[],
        "fixed_gear":        ["Two Daggers (1d4 piercing, Finesse, Light, Thrown 20/60 ft.)",
                              "Thieves' Tools"],
        "spellcaster":       False,
    },
    "Sorcerer": {
        "armor_choices":     ["No Armor (cast Mage Armor for AC 13+DEX, or Draconic Resilience if applicable)"],
        "weapon_primary":    ["Light Crossbow + 20 Bolts (1d8 piercing, range 80/320 ft. — ranged caster)",
                              "Quarterstaff (1d6/d8 bludgeoning, Versatile — melee backup)",
                              "Two Daggers (1d4 piercing, Finesse, Light, Thrown 20/60 ft. — ambush style)"],
        "weapon_secondary":  ["Two Daggers (1d4 piercing, Finesse, Light, Thrown 20/60 ft.)"],
        "pack_choices":      ["Dungeoneer's Pack", "Explorer's Pack"],
        "focus_choices":     ["Component Pouch", "Arcane Focus (crystal, orb, rod, staff, or wand)"],
        "instrument_choices":[],
        "fixed_gear":        [],
        "spellcaster":       True,
        "cantrips_label":    "Sorcerer Cantrips Known (choose 4)",
        "cantrips_count":    4,
        "cantrip_pool":      ["Acid Splash","Blade Ward","Booming Blade","Chill Touch","Control Flames",
                              "Create Bonfire","Dancing Lights","Fire Bolt","Friends","Green-Flame Blade",
                              "Gust","Infestation","Light","Mage Hand","Message","Minor Illusion",
                              "Mold Earth","Poison Spray","Prestidigitation","Ray of Frost",
                              "Shape Water","Shocking Grasp","Sword Burst","Thunderclap","True Strike"],
        "spells_label":      "1st-Level Spells Known (choose 2)",
        "spells_count":      2,
        "spell_pool":        ["Absorb Elements","Burning Hands","Charm Person","Chromatic Orb",
                              "Color Spray","Comprehend Languages","Detect Magic","Disguise Self",
                              "Expeditious Retreat","False Life","Feather Fall","Fog Cloud",
                              "Jump","Mage Armor","Magic Missile","Ray of Sickness",
                              "Shield","Silent Image","Silvery Barbs","Sleep","Thunderwave","Witch Bolt"],
        "slots_1st":         2,
    },
    "Warlock": {
        "armor_choices":     ["Leather Armor (AC 11 + DEX mod)"],
        "weapon_primary":    ["Quarterstaff (1d6/d8 bludgeoning, Versatile — Pact of the Blade synergy)",
                              "Light Crossbow + 20 Bolts (1d8 piercing, range 80/320 ft. — eldritch ranged)",
                              "Dagger (1d4 piercing, Finesse, Light, Thrown — Eldritch Smite option)"],
        "weapon_secondary":  ["Two Daggers (1d4 piercing, Finesse, Light, Thrown 20/60 ft.)"],
        "pack_choices":      ["Scholar's Pack", "Dungeoneer's Pack"],
        "focus_choices":     ["Component Pouch", "Arcane Focus (crystal, orb, rod, staff, or wand)"],
        "instrument_choices":[],
        "fixed_gear":        [],
        "spellcaster":       True,
        "cantrips_label":    "Warlock Cantrips Known (choose 2)",
        "cantrips_count":    2,
        "cantrip_pool":      ["Blade Ward","Booming Blade","Chill Touch","Create Bonfire","Eldritch Blast",
                              "Friends","Green-Flame Blade","Infestation","Mage Hand","Minor Illusion",
                              "Poison Spray","Prestidigitation","Sword Burst","Thunderclap","True Strike"],
        "spells_label":      "1st-Level Spells Known (choose 2)",
        "spells_count":      2,
        "spell_pool":        ["Armor of Agathys","Arms of Hadar","Cause Fear","Charm Person",
                              "Comprehend Languages","Expeditious Retreat","Hellish Rebuke",
                              "Hex","Illusory Script","Protection from Evil and Good",
                              "Silvery Barbs","Unseen Servant","Witch Bolt"],
        "slots_1st":         1,
    },
    "Wizard": {
        "armor_choices":     ["No Armor (cast Mage Armor for AC 13+DEX; Bladesinging adds INT to AC)"],
        "weapon_primary":    ["Quarterstaff (1d6/d8 bludgeoning, Versatile — Arcane Focus compatible)",
                              "Dagger (1d4 piercing, Finesse, Light, Thrown 20/60 ft. — concealed caster)",
                              "Light Crossbow + 20 Bolts (1d8 piercing, range 80/320 ft. — Bladesinger ranged)"],
        "weapon_secondary":  ["Dagger (backup melee or thrown option)"],
        "pack_choices":      ["Scholar's Pack", "Explorer's Pack"],
        "focus_choices":     ["Component Pouch", "Arcane Focus (crystal, orb, rod, staff, or wand)"],
        "instrument_choices":[],
        "fixed_gear":        ["Spellbook (6 1st-level spells + INT mod bonus spells inscribed)"],
        "spellcaster":       True,
        "cantrips_label":    "Wizard Cantrips Known (choose 3)",
        "cantrips_count":    3,
        "cantrip_pool":      ["Acid Splash","Blade Ward","Booming Blade","Chill Touch","Control Flames",
                              "Create Bonfire","Dancing Lights","Fire Bolt","Friends","Green-Flame Blade",
                              "Gust","Infestation","Light","Mage Hand","Message","Minor Illusion",
                              "Mold Earth","Poison Spray","Prestidigitation","Ray of Frost",
                              "Shape Water","Shocking Grasp","Sword Burst","Thunderclap","True Strike"],
        "spells_label":      "Spellbook — 1st-Level Spells (choose 6 + INT mod)",
        "spells_count":      6,
        "spell_pool":        ["Absorb Elements","Alarm","Burning Hands","Catapult","Cause Fear",
                              "Charm Person","Chromatic Orb","Color Spray","Comprehend Languages",
                              "Detect Magic","Disguise Self","Expeditious Retreat","False Life",
                              "Feather Fall","Find Familiar","Fog Cloud","Grease","Identify",
                              "Illusory Script","Jump","Longstrider","Mage Armor","Magic Missile",
                              "Protection from Evil and Good","Ray of Sickness","Shield",
                              "Silent Image","Silvery Barbs","Sleep","Snare",
                              "Tasha's Hideous Laughter","Tenser's Floating Disk",
                              "Thunderwave","Unseen Servant","Witch Bolt"],
        "slots_1st":         2,
    },
    "Artificer": {
        "armor_choices":     ["Scale Mail (AC 14, Stealth disadvantage)",
                              "Leather Armor (AC 11 + DEX mod)"],
        "weapon_primary":    ["Any Two Simple Weapons (e.g. Handaxe + Dagger, 1d6+1d4 — flexible melee)",
                              "Light Crossbow + 20 Bolts (1d8 piercing, range 80/320 ft. — construct support)",
                              "Quarterstaff + Shield (1d6/d8 bludgeoning, Versatile; Shield +2 AC — Battle Smith)"],
        "weapon_secondary":  ["Light Crossbow + 20 Bolts (secondary ranged option if two simple weapons chosen)"],
        "pack_choices":      ["Dungeoneer's Pack", "Scholar's Pack"],
        "focus_choices":     ["Thieves' Tools (Artificer spellcasting focus)", "Artisan's Tools of choice"],
        "instrument_choices":[],
        "fixed_gear":        ["Thieves' Tools"],
        "spellcaster":       True,
        "cantrips_label":    "Artificer Cantrips Known (choose 2)",
        "cantrips_count":    2,
        "cantrip_pool":      ["Acid Splash","Fire Bolt","Guidance","Light","Mage Hand","Mending",
                              "Message","Prestidigitation","Ray of Frost","Resistance",
                              "Shocking Grasp","Spare the Dying","Thunderclap"],
        "spells_label":      "1st-Level Spells Prepared (choose INT mod + half-level, min 1)",
        "spells_count":      3,
        "spell_pool":        ["Absorb Elements","Alarm","Catapult","Cure Wounds","Detect Magic",
                              "Disguise Self","Expeditious Retreat","Faerie Fire","False Life",
                              "Grease","Identify","Jump","Longstrider","Purify Food and Drink",
                              "Sanctuary","Snare","Tasha's Caustic Brew"],
        "slots_1st":         2,
    },
}

DM_SYSTEM_PROMPT = """You are a legendary, highly rigorous Dungeon Master executing a solo text Chronicles RPG campaign built dynamically around the player's custom Character Sheet.

WORLD ENGINE: Procedurally generate a completely custom, randomized sandbox fantasy world with unique lore, factions, and environmental layout as the user wanders.

STRICT RULE & ABILITY ADHERENCE: You must strictly track and enforce the mechanics of the Chronicles RPG ruleset. Closely manage character level, active health, environment continuity, spell levels, spell slot limits, resource pools, casting times, ranges, and saving throw DCs for every class feature or spell.

DICE NOTATION METRICS: Whenever the player activates a feature, triggers an ability, casts a spell, or hits an enemy, explicitly state the exact dice notation and mechanics being calculated (e.g., 'Your spell inflicts 3d6 fire damage', or 'The target must pass a DC 14 Dexterity saving throw') in the narrative block before resolving the outcome.

FLOW CONTROL: Never decide actions, move, or speak for the player character. When they attempt a challenging task, halt your narrative immediately and explicitly prompt them for a specific d20 skill check or saving throw matching a set Difficulty Class (DC). Wait for their input or dice roller result.

SUGGESTED ACTIONS: At the end of every narrative block, always append exactly 3 diverse, actionable player choices on separate lines starting with "► " — these are inspiration for the player, not mandatory choices.

MAPS & SCENERY: When the character travels to a fresh location, enters a dungeon crawl, or engages in combat, your terminal [IMAGE: ...] tag prompt must switch from a landscape style to a top-down tactical battlemap or regional fantasy map layout.

IMAGE END TAG: At the absolute conclusion of every narrative block (after the ► suggestions), you must append an image generation prompt summarizing the scene environment exactly inside brackets: [IMAGE: detailed fantasy art description of the current scene, lighting, atmosphere, style: digital painting, high detail]

MANUAL OVERRIDE: If the player's message begins with "Override:" followed by a command, treat this as a direct Game Master narrative directive. Immediately execute the stated narrative event without any mechanical checks, dice rolls, or skill challenges. Confirm execution with a brief "(Override applied)" note, then advance the story as commanded.

LEVEL-UP COACHING: When you receive a message beginning with "SYSTEM TRIGGER — LEVEL UP", immediately output a clean formatted 'Level Up Guide' card BEFORE resuming the narrative. The card must include: (1) HP gained at this level using the correct hit die, (2) every new class feature unlocked, (3) updated spell slots and spells known or prepared, (4) any Ability Score Improvement or Feat choice if applicable. Use Chronicles RPG rules. Format with clear headers. Then ask the player if they are ready to continue the adventure.

NPC DIALOGUE TAG: Whenever a named NPC speaks dialogue, precede their line with [SPEAKER: Name] on the same line. Example: [SPEAKER: Eldrin the Innkeeper] "Welcome, weary traveler!" This enables portrait display in the adventure log.

COMPANION ENGINE: The player may have at most 2 active traveling companions. When the narrative leads a named NPC to join the party, output on its own line: [COMPANION_JOIN: Name|Species|Class|MaxHP]. When a companion departs (contract fulfilled, slain, or story reason), output on its own line: [COMPANION_LEAVE: Name]. Track companions in all combat encounters and reference them in the narrative as active party members.

COMBAT TAGS: When a combat encounter begins, output on its own line immediately after the opening description: [COMBAT_HUD: enemies=EnemyName(HP:CurrentHP/MaxHP)|Enemy2(HP:X/Y), attacks=Attack1Description|Attack2Description]. Update this tag on significant HP changes by outputting a new [COMBAT_HUD:] line. When the combat fully concludes (all enemies slain/fled), output [COMBAT_END] on its own line.

ACTIVE CONDITIONS: If the system note flags active conditions on the player, enforce all mechanical penalties strictly in your rolls, narration, and DM rulings. Reference the condition's effects explicitly when they trigger.

Keep your narrative vivid, immersive, and flavourful. Use second-person perspective ("You see...", "You hear..."). Match difficulty to the character's level and class. Never break character."""


def init_session():
    defaults = {
        "messages": [],
        "scene_image_url": None,
        "scene_caption": "Your adventure awaits...",
        "last_roll": None,
        "game_started": False,
        "char_sheet": {
            "name": "Hero",
            "species": "Human",
            "char_class": "Fighter",
            "subclass": "Champion",
            "background": "Soldier",
            "proficiencies": [],
            "level": 1,
            "current_hp": 12,
            "max_hp": 12,
            "ac": 16,
            "gold": 10,
            "con_mod": 2,
            "inventory": "Longsword\nShield\nChain Mail\nExplorer's Pack",
        },
        "journal": "",
        "loadout": {
            "armor": "",
            "weapon": "",
            "secondary": "",
            "pack": "",
            "focus": "",
            "instrument": "",
            "cantrips": [],
            "spells_1st": [],
        },
        "suggestions": [],
        "conditions": [],
        "companions": [
            {"name":"","species":"","cls":"","hp":20,"max_hp":20,"relationship":"Hired","active":False},
            {"name":"","species":"","cls":"","hp":20,"max_hp":20,"relationship":"Hired","active":False},
        ],
        "combat_active": False,
        "enemies": [],
        "portrait_cache": {},
        "death_screen": False,
        "autosave_status": "",
        "_pending_dice_msg": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ── Auto-restore from autosave on startup ─────────────────────────────────────────────
def autoload_on_startup():
    """On first run of a fresh server session, restore from main_save.json if it exists."""
    if st.session_state.get("_autoloaded"):
        return
    st.session_state["_autoloaded"] = True
    for fname in ("main_save.json", "backup_save.json"):
        path = os.path.join(SAVE_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for key, value in data.items():
                if key != "version":
                    st.session_state[key] = value
            st.session_state["autosave_status"] = "✅ Session restored from autosave"
            return
        except Exception:
            continue

autoload_on_startup()

# ═════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════════════
def desc_box(text: str, style: str = "") -> None:
    if text:
        cls = f"desc-box {style}".strip()
        st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)

def get_item_desc(choice_str: str) -> str:
    for key in sorted(EQUIPMENT_DESC.keys(), key=len, reverse=True):
        if choice_str.startswith(key):
            return EQUIPMENT_DESC[key]
    return ""

def extract_image_prompt(text: str):
    match = re.search(r'\[IMAGE:\s*(.*?)\]', text, re.DOTALL | re.IGNORECASE)
    if match:
        prompt = match.group(1).strip()
        clean = re.sub(r'\[IMAGE:\s*.*?\]', '', text, flags=re.DOTALL | re.IGNORECASE).strip()
        return clean, prompt
    return text, None

def extract_suggestions(text: str):
    lines = text.split('\n')
    suggestions = []
    for line in lines:
        line = line.strip()
        if line.startswith('► '):
            suggestions.append(line[2:].strip())
    return suggestions[:3]

def build_image_url(prompt: str) -> str:
    encoded = quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=450&seed=42&nologo=true"

def get_char_summary() -> str:
    cs         = st.session_state.char_sheet
    ld         = st.session_state.loadout
    cantrips_str = ", ".join(ld.get("cantrips", [])) or "none"
    spells_str   = ", ".join(ld.get("spells_1st", [])) or "none"
    con_mod      = cs.get("con_mod", 0)
    conditions   = st.session_state.get("conditions", [])
    active_comps = [c for c in st.session_state.get("companions", [])
                    if c.get("active") and c.get("name","").strip()]
    comp_str = "; ".join(
        f"{c['name']} ({c.get('cls','?')} HP:{c.get('hp',0)}/{c.get('max_hp',0)} Rel:{c.get('relationship','')})"
        for c in active_comps
    ) or "none"
    cond_str = ", ".join(conditions) if conditions else "none"
    return (
        f"Character: {cs.get('name','Hero')}, {cs.get('species','Human')} "
        f"{cs.get('char_class','Fighter')} ({cs.get('subclass','')}) "
        f"Level {cs.get('level',1)}, Background: {cs.get('background','Soldier')}, "
        f"HP: {cs.get('current_hp',12)}/{cs.get('max_hp',12)}, "
        f"AC: {cs.get('ac',16)}, CON Mod: {'+' if con_mod >= 0 else ''}{con_mod}, "
        f"Gold: {cs.get('gold',10)}gp, "
        f"Proficiencies: {', '.join(cs.get('proficiencies',[]))}, "
        f"Cantrips: {cantrips_str}, Starting Spells: {spells_str}, "
        f"Inventory: {cs.get('inventory','')}, "
        f"Active Status Conditions: {cond_str}, "
        f"Party Companions: {comp_str}"
    )

def call_dm(user_input: str):
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
        return "⚠️ The Gemini API is not configured. Please check your setup."
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        system_with_char = str(DM_SYSTEM_PROMPT) + f"\n\nCURRENT CHARACTER SHEET:\n{get_char_summary()}"
        conditions = st.session_state.get("conditions", [])
        if conditions:
            cond_rules = "\n".join(f" - {CONDITIONS_RULES.get(c, c)}" for c in conditions)
            system_with_char += f"\n\n[SYSTEM — ACTIVE CONDITIONS ON PLAYER — ENFORCE STRICTLY]:\n{cond_rules}"
        contents_payload = []
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            contents_payload.append({"role": role, "parts": [{"text": msg["content"]}]})
        contents_payload.append({"role": "user", "parts": [{"text": user_input}]})
        payload = {
            "contents": contents_payload,
            "systemInstruction": {"parts": [{"text": system_with_char}]},
            "generationConfig": {"temperature": 0.9, "maxOutputTokens": 2048}
        }
        for attempt in range(3):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                if response.status_code == 503 and attempt < 2:
                    time.sleep(4)
                    continue
                res_json = response.json()
                if "candidates" in res_json:
                    return res_json["candidates"][0]["content"]["parts"][0]["text"]
                elif "error" in res_json:
                    msg = res_json["error"]["message"]
                    if "high demand" in msg.lower() and attempt < 2:
                        time.sleep(4)
                        continue
                    return f"❌ API Error: {msg}"
                return "❌ Error: Unexpected response format from Google."
            except Exception as e:
                if attempt < 2:
                    time.sleep(4)
                    continue
                return f"⚠️ The Dungeon Master encountered a mystical disturbance: {str(e)}"
        return "⚠️ The spirits are overwhelmed — please try again in a moment."
    except Exception as e:
        return f"⚠️ The Dungeon Master encountered a mystical disturbance: {str(e)}"

def parse_combat_tag(content: str) -> str:
    """Parse [COMBAT_HUD:] and [COMBAT_END] tags, update session state, return clean text."""
    hud_match = re.search(r'\[COMBAT_HUD:\s*([^\]]+)\]', content, re.IGNORECASE)
    if hud_match:
        data_str = hud_match.group(1)
        enemies  = []
        em = re.search(r'enemies=([^,\]]+(?:\|[^,\]]+)*)', data_str)
        am = re.search(r'attacks=([^\]]+)',               data_str)
        if em:
            atk_parts = [a.strip() for a in am.group(1).split('|')] if am else []
            for idx, ep in enumerate(em.group(1).split('|')):
                ep = ep.strip()
                hp_m = re.search(r'\(HP:(\d+)/(\d+)\)', ep)
                name = re.sub(r'\(HP:\d+/\d+\)', '', ep).strip()
                cur  = int(hp_m.group(1)) if hp_m else 20
                mx   = int(hp_m.group(2)) if hp_m else 20
                atks = [atk_parts[idx]] if idx < len(atk_parts) else []
                enemies.append({"name": name, "hp": cur, "max_hp": mx, "attacks": atks})
        if enemies:
            st.session_state.enemies      = enemies
            st.session_state.combat_active = True
        content = re.sub(r'\[COMBAT_HUD:\s*[^\]]+\]', '', content, flags=re.IGNORECASE).strip()
    if '[COMBAT_END]' in content:
        st.session_state.combat_active = False
        st.session_state.enemies       = []
        content = content.replace('[COMBAT_END]', '').strip()
    return content

def parse_companion_tags(content: str) -> str:
    """Parse [COMPANION_JOIN:] and [COMPANION_LEAVE:] tags, update session state."""
    companions = st.session_state.get("companions", [])
    joins = re.findall(r'\[COMPANION_JOIN:\s*([^\]]+)\]', content, re.IGNORECASE)
    for jm in joins:
        parts = [p.strip() for p in jm.split('|')]
        name  = parts[0] if parts else "Companion"
        sp    = parts[1] if len(parts) > 1 else "Human"
        cls   = parts[2] if len(parts) > 2 else "Fighter"
        hp    = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 20
        slot  = next((i for i, c in enumerate(companions) if not c.get("active")), None)
        if slot is None:
            slot = 1
        companions[slot] = {"name": name, "species": sp, "cls": cls,
                             "hp": hp, "max_hp": hp, "relationship": "Allied", "active": True}
    leaves = re.findall(r'\[COMPANION_LEAVE:\s*([^\]]+)\]', content, re.IGNORECASE)
    for lm in leaves:
        nm = lm.strip().lower()
        for c in companions:
            if c.get("name","").lower() == nm:
                c["active"] = False
    st.session_state.companions = companions
    clean = re.sub(r'\[COMPANION_JOIN:\s*[^\]]+\]',  '', content, flags=re.IGNORECASE)
    clean = re.sub(r'\[COMPANION_LEAVE:\s*[^\]]+\]', '', clean,   flags=re.IGNORECASE)
    return clean.strip()

def process_dm_response(raw: str):
    clean, img_prompt = extract_image_prompt(raw)
    clean = parse_combat_tag(clean)
    clean = parse_companion_tags(clean)
    suggestions = extract_suggestions(clean)
    if img_prompt:
        st.session_state.scene_image_url = build_image_url(img_prompt)
        st.session_state.scene_caption = img_prompt[:120] + ("..." if len(img_prompt) > 120 else "")
    st.session_state.suggestions = suggestions
    return clean

def do_roll(die_name: str, modifier: int = 0):
    sides = DICE[die_name]
    roll = random.randint(1, sides)
    total = roll + modifier
    mod_str = f" + {modifier} Mod = {total}" if modifier != 0 else f" = {total}"
    result_str = f"🎲 Rolled a {die_name}: **{roll}**{mod_str}"
    st.session_state.last_roll = {"die": die_name, "roll": roll, "total": total, "text": result_str}
    return result_str, total

def send_message(content: str):
    if not content.strip():
        return
    actual  = content
    stripped = content.strip()
    if stripped.lower().startswith("override:"):
        directive = stripped[9:].strip()
        actual = (
            f"[DM DIRECTIVE — OVERRIDE] The player is invoking narrative control. "
            f"Execute immediately without mechanical checks: {directive}"
        )
    st.session_state.messages.append({"role": "user", "content": content})
    with st.spinner("🐉 The Dungeon Master stirs..."):
        raw = call_dm(actual)
    clean = process_dm_response(raw)
    st.session_state.messages.append({"role": "assistant", "content": clean})
    st.session_state.game_started = True
    # ── Death detection ──
    cs = st.session_state.char_sheet
    if cs.get("current_hp", 1) <= 0 and st.session_state.game_started:
        st.session_state.death_screen = True
    # ── Autosave every turn ──
    autosave()

# ── Autosave Engine ───────────────────────────────────────────────────────────
def compress_messages_for_save(messages: list) -> list:
    """Compress long combat turns into single summary entries to keep files small."""
    compressed   = []
    combat_buffer = []
    in_combat    = False
    for msg in messages:
        content = msg.get("content", "")
        if not in_combat and ("[COMBAT_HUD:" in content or "initiative is rolled" in content.lower()):
            in_combat = True
        if in_combat:
            combat_buffer.append(msg)
            ended = (
                "[COMBAT_END]" in content or
                "the battle ends" in content.lower() or
                "combat is over" in content.lower() or
                "the fighting stops" in content.lower()
            )
            if ended:
                n = len(combat_buffer)
                summary = (
                    f"[Combat Encounter Resolution — {n} turns condensed. "
                    f"Outcome: Encounter concluded. Full detail omitted to conserve storage.]"
                )
                compressed.append({"role": "assistant", "content": summary})
                combat_buffer = []
                in_combat = False
        else:
            compressed.append(msg)
    if combat_buffer:
        n = len(combat_buffer)
        compressed.append({"role": "assistant",
                            "content": f"[Combat Encounter — {n} turns. Status: In Progress at save point.]"})
    return compressed

def autosave() -> bool:
    """Silently write main_save.json + backup_save.json to SAVE_DIR."""
    try:
        os.makedirs(SAVE_DIR, exist_ok=True)
        msgs = compress_messages_for_save(st.session_state.get("messages", []))
        data = {
            "version":         "2.0",
            "char_sheet":      st.session_state.get("char_sheet", {}),
            "loadout":         st.session_state.get("loadout", {}),
            "messages":        msgs,
            "scene_image_url": st.session_state.get("scene_image_url"),
            "scene_caption":   st.session_state.get("scene_caption", ""),
            "journal":         st.session_state.get("journal", ""),
            "suggestions":     st.session_state.get("suggestions", []),
            "game_started":    st.session_state.get("game_started", False),
            "companions":      st.session_state.get("companions", []),
            "conditions":      st.session_state.get("conditions", []),
        }
        for fname in ("main_save.json", "backup_save.json"):
            with open(os.path.join(SAVE_DIR, fname), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        st.session_state.autosave_status = f"✅ Autosaved — {len(msgs)} entries"
        return True
    except Exception as e:
        st.session_state.autosave_status = f"⚠️ Autosave failed: {e}"
        return False

# ── Portrait helpers ───────────────────────────────────────────────────────────
def get_npc_portrait_url(speaker_name: str) -> str:
    prompt  = f"fantasy portrait face closeup of {speaker_name}, medieval painterly art, detailed, no background"
    encoded = quote(prompt)
    seed    = abs(hash(speaker_name)) % 9999
    return f"https://image.pollinations.ai/prompt/{encoded}?width=80&height=80&seed={seed}&nologo=true"

def parse_speaker_tag(content: str):
    """Extract [SPEAKER: Name] from content. Returns (clean_text, speaker_name_or_None)."""
    m = re.search(r'\[SPEAKER:\s*([^\]]+)\]', content, re.IGNORECASE)
    if m:
        speaker = m.group(1).strip()
        clean   = re.sub(r'\[SPEAKER:\s*[^\]]+\]', '', content).strip()
        return clean, speaker
    return content, None

# ── Custom item AI lookup ──────────────────────────────────────────────────────
def do_custom_item_lookup(item_name: str) -> str:
    if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
        return f"{item_name} (Gemini unavailable — API key not set)"
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        prompt = (
            f"You are a Chronicles RPG rules reference. For the item '{item_name}', output ONLY a single "
            f"concise line in this format: '{item_name}: [damage or AC or effect], [properties], "
            f"[cost]'. No extra text or explanation. Just that one line."
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 80}
        }
        for attempt in range(2):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=15)
                if response.status_code == 503 and attempt < 1:
                    time.sleep(3)
                    continue
                res_json = response.json()
                if "candidates" in res_json:
                    return res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                return f"{item_name} (custom item)"
            except Exception:
                if attempt < 1:
                    time.sleep(3)
                    continue
                return f"{item_name} (custom item)"
        return f"{item_name} (custom item)"
    except Exception:
        return f"{item_name} (custom item)"

# ── Combat HUD renderer ────────────────────────────────────────────────────────
def render_combat_hud():
    if not st.session_state.get("combat_active") or not st.session_state.get("enemies"):
        return
    cs         = st.session_state.char_sheet
    enemies    = st.session_state.get("enemies", [])
    companions = [c for c in st.session_state.get("companions", [])
                  if c.get("active") and c.get("name","").strip()]

    def _bar(cur, mx, color):
        pct = min(100, int(cur / max(1, mx) * 100))
        return (
            f'<div style="background:#2A1A0A;border-radius:3px;height:9px;overflow:hidden;margin:2px 0 1px;">'
            f'<div style="width:{pct}%;background:{color};height:100%;"></div></div>'
            f'<div style="font-size:0.58rem;color:#7A6545;text-align:right;font-family:\'Cinzel Decorative\',serif;">'
            f'HP {cur}/{mx}</div>'
        )

    rows = []
    pct_p = min(100, int(cs.get("current_hp",0) / max(1,cs.get("max_hp",1)) * 100))
    pcol  = "#2E7D32" if pct_p > 60 else "#F9A825" if pct_p > 30 else "#C62828"
    cls_e = CLASS_PORTRAITS.get(cs.get("char_class","Fighter"), "🧝")
    rows.append(
        f'<div style="margin-bottom:0.45rem;">'
        f'<div style="font-family:\'EB Garamond\',serif;font-size:0.84rem;color:#E6C280;">'
        f'{cls_e} <strong>{cs.get("name","Hero")}</strong> <span style="font-size:0.7rem;color:#8B7355;">(You)</span></div>'
        + _bar(cs.get("current_hp",0), cs.get("max_hp",1), pcol) + '</div>'
    )
    for comp in companions:
        cpct  = min(100, int(comp.get("hp",0) / max(1,comp.get("max_hp",1)) * 100))
        cpcol = "#2E7D32" if cpct > 60 else "#F9A825" if cpct > 30 else "#C62828"
        rows.append(
            f'<div style="margin-bottom:0.45rem;">'
            f'<div style="font-family:\'EB Garamond\',serif;font-size:0.84rem;color:#A8D4A0;">'
            f'👤 <strong>{comp.get("name","Companion")}</strong> <span style="font-size:0.7rem;color:#8B7355;">({comp.get("cls","?")} · Ally)</span></div>'
            + _bar(comp.get("hp",0), comp.get("max_hp",1), cpcol) + '</div>'
        )
    enemy_rows = []
    for enemy in enemies:
        epct  = min(100, int(enemy.get("hp",20) / max(1,enemy.get("max_hp",20)) * 100))
        epcol = "#C62828" if epct > 60 else "#F9A825" if epct > 30 else "#555555"
        atk_str = ", ".join(enemy.get("attacks",[])) or "Unknown"
        enemy_rows.append(
            f'<div style="margin-bottom:0.45rem;">'
            f'<div style="font-family:\'EB Garamond\',serif;font-size:0.84rem;color:#FF7070;">'
            f'💀 <strong>{enemy.get("name","Enemy")}</strong></div>'
            + _bar(enemy.get("hp",20), enemy.get("max_hp",20), epcol)
            + f'<div style="font-family:\'EB Garamond\',serif;font-size:0.76rem;color:#B87070;margin-top:1px;">⚔ Attacks: {atk_str}</div></div>'
        )

    hud_html = (
        '<div style="background:linear-gradient(160deg,#1A0A08,#120806);border:2px solid #6B1A1A;'
        'border-radius:8px;padding:0.75rem 0.85rem;margin-bottom:0.6rem;">'
        '<div style="font-family:\'Cinzel Decorative\',serif;font-size:0.68rem;color:#C92A2A;'
        'text-align:center;letter-spacing:0.12em;margin-bottom:0.55rem;text-transform:uppercase;">'
        '⚔️ Combat HUD ⚔️</div>'
        + "".join(rows)
        + ('<div style="border-top:1px solid #3A1A1A;margin:0.4rem 0 0.4rem;"></div>' if enemy_rows else "")
        + "".join(enemy_rows)
        + '</div>'
    )
    st.markdown(hud_html, unsafe_allow_html=True)
    if st.button("✖ Dismiss Combat HUD", key="close_hud"):
        st.session_state.combat_active = False
        st.session_state.enemies = []
        st.rerun()

# ── Death screen ───────────────────────────────────────────────────────────────
def render_death_screen():
    cs         = st.session_state.char_sheet
    companions = [c for c in st.session_state.get("companions",[])
                  if c.get("active") and c.get("name","").strip()]
    st.markdown("""
    <div style="background:linear-gradient(180deg,#1F0000,#0A0000);border:3px solid #8B0000;
        border-radius:12px;padding:1.5rem;text-align:center;margin:0.5rem 0 1rem;">
        <div style="font-size:3.5rem;margin-bottom:0.3rem;">💀</div>
        <div style="font-family:'Cinzel Decorative',serif;font-size:1.3rem;color:#C92A2A;font-weight:700;
            text-shadow:0 0 18px rgba(201,42,42,0.7);margin-bottom:0.25rem;">YOUR HERO HAS FALLEN</div>
        <div style="font-family:'EB Garamond',serif;font-size:0.88rem;color:#7A5A4A;font-style:italic;">
            The candle of {name}'s adventure flickers out... yet fate offers one final mercy.
        </div>
    </div>
    """.replace("{name}", cs.get("name","your hero")), unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    card_style = 'style="text-align:center;padding:0.9rem;border-radius:8px;height:100%;"'

    with col1:
        st.markdown(f'<div {card_style} style="background:#1A0A0A;border:1px solid #4A1A1A;text-align:center;padding:0.9rem;border-radius:8px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Cinzel Decorative\',serif;font-size:0.75rem;color:#D4AF37;margin-bottom:0.3rem;">🔄 Restart Adventure</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'EB Garamond\',serif;font-size:0.8rem;color:#8B7355;margin-bottom:0.5rem;">Same hero, fresh world — the legend continues.</div>', unsafe_allow_html=True)
        if st.button("Restart Adventure", key="death_restart", use_container_width=True):
            cs["current_hp"] = cs.get("max_hp", 12)
            st.session_state.messages     = []
            st.session_state.enemies      = []
            st.session_state.combat_active = False
            st.session_state.death_screen = False
            st.session_state.game_started = False
            send_message(f"My hero {cs.get('name','Hero')} rises again — reborn by fate's mercy. Begin my adventure anew in a fresh world!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div style="background:#0A0A1A;border:1px solid #1A1A4A;text-align:center;padding:0.9rem;border-radius:8px;">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Cinzel Decorative\',serif;font-size:0.75rem;color:#D4AF37;margin-bottom:0.3rem;">⚔️ Introduce Successor</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'EB Garamond\',serif;font-size:0.8rem;color:#8B7355;margin-bottom:0.5rem;">New character, same ongoing story — pick up where they fell.</div>', unsafe_allow_html=True)
        if st.button("New Successor", key="death_successor", use_container_width=True):
            old_name = cs.get("name","Hero")
            st.session_state.death_screen  = False
            st.session_state.enemies       = []
            st.session_state.combat_active = False
            cs["current_hp"] = 12
            cs["max_hp"]     = 12
            cs["level"]      = 1
            cs["name"]       = "Successor"
            send_message(f"The brave {old_name} has fallen. A new hero arrives to continue the story in this same world. Introduce my successor and pick up the adventure exactly where the last hero fell.")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        if companions:
            comp = companions[0]
            st.markdown('<div style="background:#0A1A0A;border:1px solid #1A4A1A;text-align:center;padding:0.9rem;border-radius:8px;">', unsafe_allow_html=True)
            st.markdown(f'<div style="font-family:\'Cinzel Decorative\',serif;font-size:0.75rem;color:#D4AF37;margin-bottom:0.3rem;">👤 Play as {comp.get("name","Companion")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-family:\'EB Garamond\',serif;font-size:0.8rem;color:#8B7355;margin-bottom:0.5rem;">{comp.get("name","")} ({comp.get("cls","?")}) steps up as the new protagonist.</div>', unsafe_allow_html=True)
            if st.button(f"Play as {comp.get('name','Companion')}", key="death_companion", use_container_width=True):
                old_name = cs.get("name","Hero")
                cs["name"]       = comp.get("name","Companion")
                cs["char_class"] = comp.get("cls","Fighter")
                cs["species"]    = comp.get("species","Human")
                cs["current_hp"] = comp.get("hp", 20)
                cs["max_hp"]     = comp.get("max_hp", 20)
                comp["active"]   = False
                st.session_state.death_screen  = False
                st.session_state.enemies       = []
                st.session_state.combat_active = False
                send_message(f"The hero {old_name} has fallen. Their loyal companion {comp.get('name','')} takes up the mantle. Generate a character sheet for them as a {comp.get('cls','?')} and continue this exact adventure from this moment.")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background:#0A0A0A;border:1px solid #2A2A2A;text-align:center;padding:0.9rem;border-radius:8px;">', unsafe_allow_html=True)
            st.markdown('<div style="font-family:\'Cinzel Decorative\',serif;font-size:0.75rem;color:#3A3A3A;margin-bottom:0.3rem;">👤 No Companion</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-family:\'EB Garamond\',serif;font-size:0.8rem;color:#3A3A3A;">You traveled alone. No companion can take up the mantle.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ── Animated dice roller fragment ──────────────────────────────────────────────
@st.fragment
def dice_roller_section():
    st.markdown('<div class="dice-header">⚄ Dice Roller — click to roll & send to DM</div>', unsafe_allow_html=True)
    dice_cols  = st.columns(6)
    dice_names = list(DICE.keys())
    roll_ph    = st.empty()
    for i, col in enumerate(dice_cols):
        with col:
            if st.button(dice_names[i], key=f"roll_{dice_names[i]}"):
                sides = DICE[dice_names[i]]
                for j in range(9):
                    fake = random.randint(1, sides)
                    if j < 8:
                        roll_ph.markdown(
                            f'<div class="roll-result roll-animating">⚀ <strong>{fake}</strong></div>',
                            unsafe_allow_html=True,
                        )
                        time.sleep(0.11)
                    else:
                        final = random.randint(1, sides)
                        result_str = f"🎲 Rolled {dice_names[i]}: **{final}**"
                        st.session_state.last_roll = {
                            "die": dice_names[i], "roll": final, "total": final, "text": result_str
                        }
                        roll_ph.markdown(
                            f'<div class="roll-result roll-final-glow">✨ <strong>{final}</strong> — {dice_names[i]}</div>',
                            unsafe_allow_html=True,
                        )
                        time.sleep(0.35)
                        st.session_state._pending_dice_msg = result_str
                        st.rerun()
    if st.session_state.last_roll and not st.session_state.get("_pending_dice_msg"):
        st.markdown(
            f'<div class="roll-result">{st.session_state.last_roll["text"]}</div>',
            unsafe_allow_html=True,
        )

# ── Oracle Engine ─────────────────────────────────────────────────────────────
def ask_oracle(odds: str) -> str:
    thresholds = {"Unlikely": 25, "50/50": 50, "Likely": 75}
    threshold  = thresholds.get(odds, 50)
    roll       = random.randint(1, 100)
    is_yes     = roll <= threshold
    if roll <= 5:
        is_yes, qualifier = True, "and..."
    elif roll >= 96:
        is_yes, qualifier = False, "and..."
    elif abs(roll - threshold) <= 7:
        qualifier = "but..."
    else:
        qualifier = ""
    base   = "Yes" if is_yes else "No"
    result = f"{base}, {qualifier}" if qualifier else base
    flavors = {
        ("Yes",""):        "The fates align in your favor.",
        ("Yes","and..."):  "Fortune smiles greatly — an unexpected boon joins your success.",
        ("Yes","but..."):  "Success is yours, though a complication arises.",
        ("No",""):         "The dice are against you this time.",
        ("No","and..."):   "Failure, and matters grow worse still.",
        ("No","but..."):   "Denied — yet something unexpected softens the blow.",
    }
    flavor = flavors.get((base, qualifier if qualifier else ""), "")
    return (
        f"🔮 **Oracle Consulted** [{odds}] — Roll: **{roll}**/100\n\n"
        f"**{result}** — _{flavor}_"
    )

# ── Rest & Progression ────────────────────────────────────────────────────────
def do_short_rest() -> str:
    cs      = st.session_state.char_sheet
    cls     = cs.get("char_class", "Fighter")
    con_mod = cs.get("con_mod", 0)
    hit_die = HIT_DICE.get(cls, 8)
    roll    = random.randint(1, hit_die)
    raw_heal= roll + con_mod
    healing = max(1, raw_heal)
    old_hp  = cs.get("current_hp", 0)
    new_hp  = min(cs.get("max_hp", 12), old_hp + healing)
    cs["current_hp"] = new_hp
    sign    = "+" if con_mod >= 0 else ""
    return (
        f"⏱️ **Short Rest** — {cls} rolls 1d{hit_die}: **{roll}** "
        f"({sign}{con_mod} CON) = **{raw_heal}** HP recovered. "
        f"HP: {old_hp} → **{new_hp}/{cs.get('max_hp',12)}**"
    )

def do_long_rest() -> str:
    cs     = st.session_state.char_sheet
    old_hp = cs.get("current_hp", 0)
    cs["current_hp"] = cs.get("max_hp", 12)
    return (
        f"🌙 **Long Rest Completed** — Health fully restored and resource pools reset. "
        f"HP: {old_hp} → **{cs['current_hp']}/{cs['current_hp']}**. "
        f"All spell slots, Ki, Superiority Dice, and short-rest resources are refreshed."
    )

def do_level_up() -> tuple:
    cs      = st.session_state.char_sheet
    current = cs.get("level", 1)
    if current >= 20:
        return None, "⚠️ Already at Level 20 — the pinnacle of mortal power. No further advancement is possible."
    new_level = current + 1
    cs["level"] = new_level
    hit_die    = HIT_DICE.get(cs.get("char_class","Fighter"), 8)
    avg_hp     = hit_die // 2 + 1
    congrats   = f"🎉 **Level Up! You have reached Level {new_level}!**"
    guide_prompt = (
        f"SYSTEM TRIGGER — LEVEL UP: The player has advanced to Level {new_level} "
        f"as a {cs.get('char_class','Fighter')} ({cs.get('subclass','')}). "
        f"Output a formatted '⭐ Level {new_level} Level Up Guide' card now. "
        f"Do NOT continue the narrative yet. Include: "
        f"(1) HP gained — roll 1d{hit_die} + CON mod (fixed avg = {avg_hp} + CON mod), "
        f"(2) every new class feature unlocked at Level {new_level}, "
        f"(3) updated spell slots and spells known or prepared if applicable, "
        f"(4) any Ability Score Improvement or Feat choice if it falls on this level. "
        f"Use Chronicles RPG rules. Format with clear headers. "
        f"Then ask: 'Are you ready to continue your adventure?'"
    )
    return guide_prompt, congrats

# ── Save / Load / Export ──────────────────────────────────────────────────────
def export_save() -> str:
    save_data = {
        "version":        "1.0",
        "char_sheet":     st.session_state.get("char_sheet", {}),
        "loadout":        st.session_state.get("loadout", {}),
        "messages":       st.session_state.get("messages", []),
        "scene_image_url":st.session_state.get("scene_image_url"),
        "scene_caption":  st.session_state.get("scene_caption", ""),
        "journal":        st.session_state.get("journal", ""),
        "suggestions":    st.session_state.get("suggestions", []),
        "game_started":   st.session_state.get("game_started", False),
        "last_roll":      st.session_state.get("last_roll"),
    }
    return json.dumps(save_data, indent=2, ensure_ascii=False)

def import_save(save_str: str):
    try:
        data = json.loads(save_str.strip())
        for key, value in data.items():
            if key != "version":
                st.session_state[key] = value
        return True, "✅ Campaign loaded! Your adventure has been fully restored."
    except json.JSONDecodeError:
        return False, "❌ Invalid save code. Make sure you copied the entire JSON string."
    except Exception as e:
        return False, f"❌ Error loading save: {str(e)}"

def export_markdown() -> str:
    cs   = st.session_state.char_sheet
    msgs = st.session_state.get("messages", [])
    jrn  = st.session_state.get("journal", "")
    con_sign = "+" if cs.get("con_mod",0) >= 0 else ""
    lines = [
        "# ⚔️ Chronicles RPG — Adventure Log",
        "",
        f"**Character:** {cs.get('name','Hero')} · "
        f"Level {cs.get('level',1)} {cs.get('species','Human')} "
        f"{cs.get('char_class','Fighter')} ({cs.get('subclass','')})",
        f"**Background:** {cs.get('background','Soldier')} · "
        f"**AC:** {cs.get('ac',16)} · "
        f"**HP:** {cs.get('current_hp',12)}/{cs.get('max_hp',12)} · "
        f"**CON Mod:** {con_sign}{cs.get('con_mod',0)}",
        "",
        "---",
        "",
    ]
    if jrn.strip():
        lines += ["## 📔 Hero's Journal", "", jrn.strip(), "", "---", ""]
    lines += ["## 📜 Adventure Log", ""]
    for msg in msgs:
        if msg["role"] == "user":
            lines.append("### 🧝 You")
        else:
            lines.append("### 🐉 Dungeon Master")
        lines += ["", msg["content"], ""]
    return "\n".join(lines)

# ═════════════════════════════════════════════════════════════════════════════
# HEADER
# ═════════════════════════════════════════════════════════════════════════════
st.markdown('<h1 class="dnd-title">⚔️ Chronicles of the Forgotten Realm</h1>', unsafe_allow_html=True)
st.markdown('<p class="dnd-subtitle">Solo Chronicles RPG · Powered by Gemini AI</p>', unsafe_allow_html=True)
st.markdown('<hr class="dnd-divider">', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TABS
# ═════════════════════════════════════════════════════════════════════════════
tab_log, tab_scene, tab_sheet, tab_loadout, tab_saves = st.tabs([
    "📜 Adventure Log", "🖼️ Scene View", "🧝 Character Sheet", "⚔️ Loadout", "💾 Saves"
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — ADVENTURE LOG
# ═════════════════════════════════════════════════════════════════════════════
with tab_log:
    # ── Handle pending dice message from fragment ──
    if st.session_state.get("_pending_dice_msg"):
        _dm = st.session_state._pending_dice_msg
        st.session_state._pending_dice_msg = None
        send_message(_dm)
        st.rerun()

    # ── Death screen override ──
    if st.session_state.get("death_screen"):
        render_death_screen()
        st.markdown('<hr class="dnd-divider">', unsafe_allow_html=True)

    # ── Animated dice roller (fragment) ──
    dice_roller_section()

    st.markdown('<hr class="dnd-divider">', unsafe_allow_html=True)

    # ── Combat HUD ──
    render_combat_hud()

    # ── Oracle Engine ──
    st.markdown("""
    <div style="font-family:'Cinzel Decorative',serif;font-size:0.72rem;color:#8B7355;text-transform:uppercase;
         letter-spacing:0.1em;margin-bottom:0.4rem;">🔮 Oracle Engine — Ask a Yes/No Question</div>
    """, unsafe_allow_html=True)
    oracle_col1, oracle_col2, oracle_col3 = st.columns([2, 2, 1])
    with oracle_col1:
        oracle_odds = st.selectbox(
            "Odds", ["Unlikely", "50/50", "Likely"],
            key="oracle_odds", label_visibility="collapsed"
        )
    with oracle_col2:
        oracle_question = st.text_input(
            "Question", placeholder="Will the guard believe my bluff?",
            key="oracle_q", label_visibility="collapsed"
        )
    with oracle_col3:
        if st.button("Ask Oracle", key="oracle_btn", use_container_width=True):
            oracle_result = ask_oracle(oracle_odds)
            prefix = f"**❓ Question:** _{oracle_question}_\n\n" if oracle_question.strip() else ""
            full_oracle = prefix + oracle_result
            st.session_state.messages.append({"role": "assistant", "content": full_oracle})
            st.session_state.game_started = True
            st.rerun()

    st.markdown('<hr class="dnd-divider">', unsafe_allow_html=True)

    # ── Chat log with NPC portraits ──
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div style="text-align:center;padding:2rem;color:#5A4A30;font-family:'EB Garamond',serif;">
                <div style="font-size:2.5rem;margin-bottom:0.5rem;">🐉</div>
                <div style="font-family:'Cinzel Decorative',serif;font-size:1rem;color:#8B7355;margin-bottom:0.4rem;">The adventure awaits</div>
                <div>Build your character in the <strong style="color:#D4AF37">🧝 Character Sheet</strong> tab,<br>
                choose your gear in <strong style="color:#D4AF37">⚔️ Loadout</strong>, then type<br>
                <strong style="color:#D4AF37">"Begin my adventure"</strong> to start.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            portrait_cache = st.session_state.get("portrait_cache", {})
            for msg in st.session_state.messages:
                role = msg["role"]
                if role == "user":
                    cls_key = st.session_state.char_sheet.get("char_class", "Fighter")
                    avatar  = CLASS_PORTRAITS.get(cls_key, "🧝")
                    with st.chat_message(role, avatar=avatar):
                        st.markdown(msg["content"])
                else:
                    content, speaker = parse_speaker_tag(msg["content"])
                    if speaker:
                        if speaker not in portrait_cache:
                            portrait_cache[speaker] = get_npc_portrait_url(speaker)
                            st.session_state.portrait_cache = portrait_cache
                        portrait_url = portrait_cache[speaker]
                        with st.chat_message("assistant", avatar="🎭"):
                            st.markdown(
                                f'<div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.3rem;">'
                                f'<img src="{portrait_url}" class="npc-cameo" '
                                f'onerror="this.style.display=\'none\'">'
                                f'<span style="font-family:\'Cinzel Decorative\',serif;font-size:0.7rem;'
                                f'color:#E6C280;font-weight:700;">{speaker}</span></div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(content)
                    else:
                        with st.chat_message("assistant", avatar="🐉"):
                            st.markdown(content)

    if st.session_state.suggestions:
        st.markdown('<div class="suggestions-box">', unsafe_allow_html=True)
        st.markdown('<div class="suggestions-title">💡 Suggested Actions</div>', unsafe_allow_html=True)
        for i, suggestion in enumerate(st.session_state.suggestions):
            if st.button(f"► {suggestion}", key=f"suggest_{i}", use_container_width=True):
                send_message(suggestion)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    user_input = st.chat_input("What do you do? Type your action, or prefix with 'Override:' for GM control...")
    if user_input:
        send_message(user_input)
        st.rerun()

    # ── Hero's Journal ──
    with st.expander("📔 Hero's Journal — Notes & Campaign Log", expanded=False):
        st.markdown(
            '<div style="font-family:\'EB Garamond\',serif;font-size:0.82rem;color:#8B7355;'
            'margin-bottom:0.4rem;">Track clues, NPC names, quest notes, and milestone moments.</div>',
            unsafe_allow_html=True
        )
        journal_text = st.text_area(
            "Journal", value=st.session_state.get("journal",""),
            height=200, key="journal_area", label_visibility="collapsed",
            placeholder="The innkeeper mentioned a ruined tower to the north...\nNPC: Seraphine — elf scout, may be trustworthy\nQuest: Find the Ember Crown before the new moon..."
        )
        st.session_state.journal = journal_text
        if st.button("💾 Save Journal Entry", key="save_journal", use_container_width=True):
            st.success("📔 Journal saved!")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — SCENE VIEW
# ═════════════════════════════════════════════════════════════════════════════
with tab_scene:
    st.markdown('<div class="scene-header">🎨 Current Scene Visualization</div>', unsafe_allow_html=True)

    if st.session_state.scene_image_url:
        try:
            st.image(st.session_state.scene_image_url, use_container_width=True, caption=None)
            st.markdown(f'<div class="scene-caption">🌍 {st.session_state.scene_caption}</div>', unsafe_allow_html=True)
        except Exception:
            st.markdown('<div class="scene-placeholder"><div>🖼️ Scene image loading...</div></div>', unsafe_allow_html=True)

        st.markdown('<hr class="dnd-divider">', unsafe_allow_html=True)
        if st.button("🔄 Regenerate Scene Image", use_container_width=True):
            if st.session_state.scene_caption and st.session_state.scene_caption != "Your adventure awaits...":
                new_seed = random.randint(1, 9999)
                prompt_encoded = quote(st.session_state.scene_caption)
                st.session_state.scene_image_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=800&height=450&seed={new_seed}&nologo=true"
                st.rerun()
    else:
        st.markdown("""
        <div class="scene-placeholder" style="min-height:300px;">
            <div style="font-size:3rem;margin-bottom:0.75rem;">🗺️</div>
            <div style="font-family:'Cinzel Decorative',serif;font-size:0.9rem;color:#8B7355;margin-bottom:0.4rem;">No Scene Active</div>
            <div style="font-size:0.8rem;text-align:center;max-width:240px;line-height:1.5;">
                Start your adventure in the <strong style="color:#D4AF37">📜 Adventure Log</strong> tab.
                The AI DM generates scenes as your story unfolds.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:1rem;padding:0.6rem;background:#1A1410;border:1px solid #2A2010;border-radius:6px;">
        <div style="font-family:'Cinzel Decorative',serif;font-size:0.65rem;color:#8B7355;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;">Scene Types</div>
        <div style="font-family:'EB Garamond',serif;font-size:0.82rem;color:#C8B880;line-height:1.8;">
            🏞️ <strong style="color:#D4AF37">Landscape</strong> — Exploration & travel scenes<br>
            🗺️ <strong style="color:#D4AF37">Regional Map</strong> — New location discovery<br>
            ⚔️ <strong style="color:#D4AF37">Tactical Grid</strong> — Combat encounters<br>
            🏰 <strong style="color:#D4AF37">Dungeon Map</strong> — Interior exploration
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — CHARACTER SHEET
# ═════════════════════════════════════════════════════════════════════════════
with tab_sheet:
    cs = st.session_state.char_sheet

    # ── Identity ──
    st.markdown('<div class="sheet-section"><div class="sheet-section-title">⚔️ Identity</div>', unsafe_allow_html=True)
    cs["name"] = st.text_input("Character Name", value=cs.get("name","Hero"), key="cs_name")

    cs["species"] = st.selectbox("Species", SPECIES,
        index=SPECIES.index(cs.get("species","Human")), key="cs_species")
    desc_box(SPECIES_DESC.get(cs["species"],""), style="species")

    cs["background"] = st.selectbox("Background", BACKGROUNDS,
        index=BACKGROUNDS.index(cs.get("background","Soldier")), key="cs_bg")
    desc_box(BACKGROUND_DESC.get(cs["background"],""), style="bg")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Class ──
    st.markdown('<div class="sheet-section"><div class="sheet-section-title">🎭 Class & Subclass</div>', unsafe_allow_html=True)
    current_class = cs.get("char_class","Fighter")
    if current_class not in CLASSES:
        current_class = "Fighter"
    cs["char_class"] = st.selectbox("Class", CLASSES,
        index=CLASSES.index(current_class), key="cs_class")
    desc_box(CLASS_DESC.get(cs["char_class"],""), style="cls")

    available_subclasses = SUBCLASSES[cs["char_class"]]
    current_sub = cs.get("subclass", available_subclasses[0])
    if current_sub not in available_subclasses:
        current_sub = available_subclasses[0]
    cs["subclass"] = st.selectbox("Subclass", available_subclasses,
        index=available_subclasses.index(current_sub), key="cs_subclass")
    desc_box(SUBCLASS_DESC.get(cs["subclass"],""), style="subcls")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Proficiencies ──
    st.markdown('<div class="sheet-section"><div class="sheet-section-title">📚 Skill Proficiencies</div>', unsafe_allow_html=True)
    cs["proficiencies"] = st.multiselect("Proficiencies", SKILLS_LIST,
        default=cs.get("proficiencies",[]), key="cs_prof")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Stats ──
    st.markdown('<div class="sheet-section"><div class="sheet-section-title">📊 Combat Stats</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        cs["level"]      = st.number_input("Level",          min_value=1,  max_value=20,  value=cs.get("level",1),      step=1, key="cs_level")
        cs["current_hp"] = st.number_input("Current HP",     min_value=0,  max_value=999, value=cs.get("current_hp",12),step=1, key="cs_chp")
        cs["ac"]         = st.number_input("Armor Class (AC)",min_value=1,  max_value=30,  value=cs.get("ac",16),        step=1, key="cs_ac")
    with col2:
        cs["max_hp"]     = st.number_input("Max HP",         min_value=1,  max_value=999, value=cs.get("max_hp",12),    step=1, key="cs_mhp")
        cs["gold"]       = st.number_input("Gold (gp)",      min_value=0,  max_value=999999, value=cs.get("gold",10),   step=1, key="cs_gold")
        cs["con_mod"]    = st.number_input("CON Modifier",   min_value=-5, max_value=10,  value=cs.get("con_mod",2),    step=1, key="cs_con")

    if cs.get("max_hp",1) > 0:
        hp_pct   = min(100, int((cs.get("current_hp",0) / cs.get("max_hp",1)) * 100))
        hp_color = "#2E7D32" if hp_pct > 60 else "#F9A825" if hp_pct > 30 else "#C62828"
        st.markdown(f"""
        <div class="hp-bar-container">
            <div class="hp-bar-fill" style="width:{hp_pct}%;background:{hp_color};"></div>
        </div>
        <div style="text-align:right;font-family:'Cinzel Decorative',serif;font-size:0.65rem;color:#8B7355;margin-top:0.15rem;">
            HP: {cs.get('current_hp',0)}/{cs.get('max_hp',1)} ({hp_pct}%)
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Inventory ──
    st.markdown('<div class="sheet-section"><div class="sheet-section-title">🎒 Inventory & Backpack</div>', unsafe_allow_html=True)
    cs["inventory"] = st.text_area("Items (one per line)", value=cs.get("inventory",""),
        height=120, key="cs_inv", placeholder="Longsword\nShield\nExplorer's Pack\n...")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Active Status Conditions ──
    st.markdown('<div class="sheet-section"><div class="sheet-section-title">🩸 Active Status Conditions</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-family:\'EB Garamond\',serif;font-size:0.82rem;color:#8B7355;margin-bottom:0.4rem;">'
        'Conditions the DM will enforce mechanically in every roll and ruling.</div>',
        unsafe_allow_html=True
    )
    current_conds = [c for c in st.session_state.get("conditions",[]) if c in CONDITIONS_LIST]
    chosen_conds  = st.multiselect("Active Conditions", CONDITIONS_LIST,
                                   default=current_conds, key="cs_conditions")
    st.session_state.conditions = chosen_conds
    if chosen_conds:
        for cond in chosen_conds:
            rule = CONDITIONS_RULES.get(cond, "")
            st.markdown(
                f'<div style="background:#1A0A08;border:1px solid #4A1A1A;border-radius:4px;'
                f'padding:0.3rem 0.6rem;margin:0.15rem 0;font-family:\'EB Garamond\',serif;'
                f'font-size:0.8rem;color:#C87878;">'
                f'<strong style="color:#E67878;">{cond}:</strong> {rule}</div>',
                unsafe_allow_html=True,
            )
        if st.button("✖ Clear All Conditions", key="clear_conditions"):
            st.session_state.conditions = []
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Party Companions ──
    st.markdown('<div class="sheet-section"><div class="sheet-section-title">👥 Party Companions (max 2)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-family:\'EB Garamond\',serif;font-size:0.82rem;color:#8B7355;margin-bottom:0.5rem;">'
        'The DM auto-adds companions via story events. You can also track or edit them here.</div>',
        unsafe_allow_html=True,
    )
    for slot_i, comp in enumerate(st.session_state.companions):
        slot_label = f"Companion Slot {slot_i + 1}"
        with st.expander(f"{'🟢' if comp.get('active') else '⚫'} {slot_label}: {comp.get('name','(empty)') or '(empty)'}", expanded=comp.get("active", False)):
            comp["name"]         = st.text_input("Name",         value=comp.get("name",""),         key=f"comp_{slot_i}_name")
            comp["species"]      = st.text_input("Species",      value=comp.get("species",""),      key=f"comp_{slot_i}_species")
            comp["cls"]          = st.text_input("Class",        value=comp.get("cls",""),          key=f"comp_{slot_i}_cls")
            comp_c1, comp_c2     = st.columns(2)
            with comp_c1:
                comp["hp"]       = st.number_input("HP",         min_value=0, max_value=999, value=comp.get("hp",20),     step=1, key=f"comp_{slot_i}_hp")
            with comp_c2:
                comp["max_hp"]   = st.number_input("Max HP",     min_value=1, max_value=999, value=comp.get("max_hp",20), step=1, key=f"comp_{slot_i}_mhp")
            comp["relationship"] = st.selectbox("Relationship",  ["Hired","Ally","Allied","Sworn","Rival","Neutral"],
                                                index=["Hired","Ally","Allied","Sworn","Rival","Neutral"].index(
                                                    comp.get("relationship","Hired") if comp.get("relationship","Hired") in
                                                    ["Hired","Ally","Allied","Sworn","Rival","Neutral"] else "Hired"),
                                                key=f"comp_{slot_i}_rel")
            comp["active"]       = st.checkbox("Active in party", value=comp.get("active", False), key=f"comp_{slot_i}_active")
            if comp.get("active") and comp.get("hp", 0) > 0 and comp.get("max_hp", 1) > 0:
                cpct  = min(100, int(comp["hp"] / comp["max_hp"] * 100))
                cpcol = "#2E7D32" if cpct > 60 else "#F9A825" if cpct > 30 else "#C62828"
                st.markdown(f"""
                <div class="hp-bar-container"><div class="hp-bar-fill" style="width:{cpct}%;background:{cpcol};"></div></div>
                <div style="text-align:right;font-family:'Cinzel Decorative',serif;font-size:0.6rem;color:#8B7355;">
                    HP {comp["hp"]}/{comp["max_hp"]} ({cpct}%)</div>
                """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Rest & Progression ──
    st.markdown('<div class="sheet-section"><div class="sheet-section-title">🎲 Rest & Progression</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-family:\'Crimson Text\',serif;font-size:0.8rem;color:#8B7355;margin-bottom:0.5rem;">'
        'Short Rest uses your hit die + CON mod to recover HP. Long Rest fully restores. '
        'Level Up advances your character and triggers a DM Level Guide.</div>',
        unsafe_allow_html=True
    )
    rest_c1, rest_c2, rest_c3 = st.columns(3)
    with rest_c1:
        if st.button("⏱️ Short Rest", use_container_width=True, key="btn_short_rest"):
            if st.session_state.get("game_started", False):
                rest_msg = do_short_rest()
                st.session_state.messages.append({"role": "assistant", "content": rest_msg})
                st.rerun()
            else:
                st.warning("Start a campaign first!")
    with rest_c2:
        if st.button("🌙 Long Rest", use_container_width=True, key="btn_long_rest"):
            if st.session_state.get("game_started", False):
                rest_msg = do_long_rest()
                st.session_state.messages.append({"role": "assistant", "content": rest_msg})
                st.rerun()
            else:
                st.warning("Start a campaign first!")
    with rest_c3:
        if st.button("🎉 Level Up!", use_container_width=True, key="btn_level_up"):
            guide_prompt, congrats = do_level_up()
            st.session_state.messages.append({"role": "assistant", "content": congrats})
            if guide_prompt:
                with st.spinner("📜 Consulting the level tables..."):
                    raw_lv = call_dm(guide_prompt)
                clean_lv = process_dm_response(raw_lv)
                st.session_state.messages.append({"role": "assistant", "content": clean_lv})
            st.session_state.game_started = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Save & Start ──
    st.markdown('<hr class="dnd-divider">', unsafe_allow_html=True)
    if st.button("⚔️ Save Sheet & Begin Campaign", use_container_width=True, type="primary"):
        st.session_state.char_sheet = cs
        intro_msg = (
            f"I am {cs.get('name','Hero')}, a Level {cs.get('level',1)} "
            f"{cs.get('species','Human')} {cs.get('char_class','Fighter')} "
            f"({cs.get('subclass','')}) with the {cs.get('background','Soldier')} background. "
            f"My HP is {cs.get('current_hp',12)}/{cs.get('max_hp',12)}, AC {cs.get('ac',16)}, "
            f"and I carry {cs.get('gold',10)} gold. Begin my adventure!"
        )
        send_message(intro_msg)
        st.success("✅ Campaign started! Switch to the 📜 Adventure Log tab.")
        st.rerun()

    # ── Summary card ──
    st.markdown(f"""
    <div style="margin-top:0.5rem;padding:0.6rem;background:#0D0D0D;border:1px solid #2A1A1A;border-radius:6px;text-align:center;">
        <div style="font-family:'Cinzel Decorative',serif;font-size:1rem;color:#D4AF37;font-weight:700;">{cs.get('name','Hero')}</div>
        <div style="font-family:'EB Garamond',serif;font-size:0.85rem;color:#C8B880;margin-top:0.15rem;">
            Level {cs.get('level',1)} {cs.get('species','Human')} {cs.get('char_class','Fighter')}
        </div>
        <div style="font-family:'Cinzel Decorative',serif;font-size:0.7rem;color:#8B7355;margin-top:0.1rem;">
            {cs.get('subclass','')} · {cs.get('background','Soldier')}
        </div>
        <div style="display:flex;justify-content:center;gap:1rem;margin-top:0.5rem;">
            <span><span style="font-family:'Cinzel Decorative',serif;font-size:0.6rem;color:#8B7355;display:block;">HP</span>
                  <span style="font-family:'Cinzel Decorative',serif;font-size:1.1rem;color:#C92A2A;font-weight:700;">{cs.get('current_hp',12)}/{cs.get('max_hp',12)}</span></span>
            <span><span style="font-family:'Cinzel Decorative',serif;font-size:0.6rem;color:#8B7355;display:block;">AC</span>
                  <span style="font-family:'Cinzel Decorative',serif;font-size:1.1rem;color:#D4AF37;font-weight:700;">{cs.get('ac',16)}</span></span>
            <span><span style="font-family:'Cinzel Decorative',serif;font-size:0.6rem;color:#8B7355;display:block;">GP</span>
                  <span style="font-family:'Cinzel Decorative',serif;font-size:1.1rem;color:#D4AF37;font-weight:700;">{cs.get('gold',10)}</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — LOADOUT
# ═════════════════════════════════════════════════════════════════════════════
with tab_loadout:
    cs  = st.session_state.char_sheet
    ld  = st.session_state.loadout
    cls = cs.get("char_class","Fighter")
    lvl = cs.get("level", 1)
    ldata = LOADOUT_DATA.get(cls, {})

    # ── Class header ──
    st.markdown(f"""
    <div style="text-align:center;padding:0.5rem 0 0.2rem;">
        <div style="font-family:'Cinzel Decorative',serif;font-size:1rem;color:#D4AF37;font-weight:700;">
            {cls} · Level {lvl}
        </div>
        <div style="font-family:'EB Garamond',serif;font-size:0.82rem;color:#8B7355;font-style:italic;">
            Starting Equipment & Spell Selection
        </div>
    </div>
    <hr class="dnd-divider">
    """, unsafe_allow_html=True)

    if not ldata:
        st.info("No loadout data found for this class.")
    else:
        # ── Armor ──
        armor_choices = ldata.get("armor_choices", [])
        if armor_choices:
            st.markdown('<div class="sheet-section"><div class="sheet-section-title">🛡️ Armor & Defense</div>', unsafe_allow_html=True)
            default_armor = ld.get("armor", armor_choices[0]) if ld.get("armor","") in armor_choices else armor_choices[0]
            ld["armor"] = st.selectbox("Choose Armor", armor_choices,
                index=armor_choices.index(default_armor), key="ld_armor")
            desc_box(get_item_desc(ld["armor"]), style="equip")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Primary Weapon ──
        w_primary = ldata.get("weapon_primary", [])
        if w_primary:
            st.markdown('<div class="sheet-section"><div class="sheet-section-title">⚔️ Primary Weapon</div>', unsafe_allow_html=True)
            default_wp = ld.get("weapon","") if ld.get("weapon","") in w_primary else w_primary[0]
            ld["weapon"] = st.selectbox("Choose Primary Weapon", w_primary,
                index=w_primary.index(default_wp), key="ld_weapon")
            desc_box(get_item_desc(ld["weapon"]), style="equip")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Secondary / Ranged ──
        w_secondary = ldata.get("weapon_secondary", [])
        if w_secondary:
            st.markdown('<div class="sheet-section"><div class="sheet-section-title">🏹 Secondary / Off-Hand</div>', unsafe_allow_html=True)
            default_ws = ld.get("secondary","") if ld.get("secondary","") in w_secondary else w_secondary[0]
            ld["secondary"] = st.selectbox("Choose Secondary Weapon", w_secondary,
                index=w_secondary.index(default_ws), key="ld_secondary")
            desc_box(get_item_desc(ld["secondary"]), style="equip")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Adventuring Pack ──
        pack_choices = ldata.get("pack_choices", [])
        if pack_choices:
            st.markdown('<div class="sheet-section"><div class="sheet-section-title">🎒 Adventuring Pack</div>', unsafe_allow_html=True)
            default_pack = ld.get("pack","") if ld.get("pack","") in pack_choices else pack_choices[0]
            ld["pack"] = st.selectbox("Choose Pack", pack_choices,
                index=pack_choices.index(default_pack), key="ld_pack")
            desc_box(get_item_desc(ld["pack"]), style="equip")
            # Pack itemization
            pack_key = ld["pack"].split("'")[0].strip().replace(" Pack","").strip()
            pack_items = CLASS_PACKS.get(ld["pack"], CLASS_PACKS.get(pack_key, []))
            if pack_items:
                st.markdown(
                    '<div style="font-family:\'EB Garamond\',serif;font-size:0.8rem;color:#8B7355;'
                    'font-style:italic;margin:0.3rem 0 0.2rem;">Contains:</div>',
                    unsafe_allow_html=True,
                )
                for pi in pack_items:
                    st.markdown(
                        f'<div style="font-family:\'EB Garamond\',serif;font-size:0.82rem;color:#C8B880;'
                        f'padding:0.05rem 0 0.05rem 0.6rem;">• {pi}</div>',
                        unsafe_allow_html=True,
                    )
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Custom Item Lookup ──
        st.markdown('<div class="sheet-section"><div class="sheet-section-title">🔍 Custom Item Lookup</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-family:\'EB Garamond\',serif;font-size:0.82rem;color:#8B7355;margin-bottom:0.35rem;">'
            'Query the AI for any non-standard weapon, armor, or item stats.</div>',
            unsafe_allow_html=True,
        )
        lookup_col1, lookup_col2 = st.columns([3, 1])
        with lookup_col1:
            custom_item = st.text_input(
                "Item name", placeholder="e.g. Trident, Spiked Shield, Net...",
                key="custom_item_input", label_visibility="collapsed",
            )
        with lookup_col2:
            do_lookup = st.button("Look Up", key="custom_lookup_btn", use_container_width=True)
        if do_lookup and custom_item.strip():
            with st.spinner("Consulting the rulebooks..."):
                result = do_custom_item_lookup(custom_item.strip())
            st.markdown(
                f'<div style="background:#1A140A;border:1px solid #4A3820;border-radius:4px;'
                f'padding:0.45rem 0.7rem;font-family:\'EB Garamond\',serif;font-size:0.88rem;'
                f'color:#E6C280;margin-top:0.3rem;">{result}</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Focus (spellcasters) ──
        focus_choices = ldata.get("focus_choices", [])
        if focus_choices:
            st.markdown('<div class="sheet-section"><div class="sheet-section-title">✨ Spellcasting Focus</div>', unsafe_allow_html=True)
            default_focus = ld.get("focus","") if ld.get("focus","") in focus_choices else focus_choices[0]
            ld["focus"] = st.selectbox("Choose Focus", focus_choices,
                index=focus_choices.index(default_focus), key="ld_focus")
            desc_box(get_item_desc(ld["focus"]), style="equip")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Instrument (Bard only) ──
        instrument_choices = ldata.get("instrument_choices", [])
        if instrument_choices:
            st.markdown('<div class="sheet-section"><div class="sheet-section-title">🎵 Musical Instrument</div>', unsafe_allow_html=True)
            default_inst = ld.get("instrument","") if ld.get("instrument","") in instrument_choices else instrument_choices[0]
            ld["instrument"] = st.selectbox("Choose Instrument", instrument_choices,
                index=instrument_choices.index(default_inst), key="ld_instrument")
            desc_box(get_item_desc(ld["instrument"]), style="equip")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Fixed Gear ──
        fixed = ldata.get("fixed_gear", [])
        if fixed:
            st.markdown('<div class="sheet-section"><div class="sheet-section-title">📦 Standard Issue Gear</div>', unsafe_allow_html=True)
            for item in fixed:
                st.markdown(f'<div class="loadout-item">{item}</div>', unsafe_allow_html=True)
                fd = get_item_desc(item)
                if fd:
                    desc_box(fd, style="equip")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Cantrips ──
        if ldata.get("spellcaster") and ldata.get("cantrips_count", 0) > 0:
            cantrip_pool  = ldata.get("cantrip_pool", [])
            cantrips_lbl  = ldata.get("cantrips_label","Cantrips (choose)")
            cantrips_count= ldata.get("cantrips_count", 2)

            st.markdown(f'<div class="sheet-section"><div class="sheet-section-title">✦ Cantrips</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="slots-badge">🔮 Known: {cantrips_count} cantrip{"s" if cantrips_count>1 else ""}</div>', unsafe_allow_html=True)

            current_c = [c for c in ld.get("cantrips",[]) if c in cantrip_pool]
            ld["cantrips"] = st.multiselect(cantrips_lbl, cantrip_pool,
                default=current_c, key="ld_cantrips",
                help=f"Choose exactly {cantrips_count}. You may know more at higher levels.")

            if len(ld["cantrips"]) > cantrips_count:
                st.warning(f"⚠️ Select exactly {cantrips_count} cantrip(s). You have chosen {len(ld['cantrips'])}.")
            elif ld["cantrips"]:
                for c in ld["cantrips"]:
                    desc_box(f"**{c}** — {SPELL_DESC.get(c,'')}", style="spell")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── 1st-Level Spells ──
        if ldata.get("spellcaster") and ldata.get("spells_count", 0) > 0:
            spell_pool   = ldata.get("spell_pool", [])
            spells_lbl   = ldata.get("spells_label","1st-Level Spells")
            spells_count = ldata.get("spells_count", 2)
            slots_1st    = ldata.get("slots_1st", 2)

            st.markdown(f'<div class="sheet-section"><div class="sheet-section-title">📖 1st-Level Spells</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="slots-badge">💎 Spell Slots at Lv{lvl}: {slots_1st} × 1st-level</div>',
                unsafe_allow_html=True
            )

            current_s = [s for s in ld.get("spells_1st",[]) if s in spell_pool]
            ld["spells_1st"] = st.multiselect(spells_lbl, spell_pool,
                default=current_s, key="ld_spells",
                help=f"Choose {spells_count} spells. Some classes prepare from the full list each day.")

            if len(ld["spells_1st"]) > spells_count and cls not in ("Cleric","Druid","Paladin","Artificer"):
                st.warning(f"⚠️ Select exactly {spells_count} spell(s). You have chosen {len(ld['spells_1st'])}.")
            elif ld["spells_1st"]:
                for s in ld["spells_1st"]:
                    desc_box(f"**{s}** — {SPELL_DESC.get(s,'')}", style="spell")
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Apply to Inventory ──
        st.markdown('<hr class="dnd-divider">', unsafe_allow_html=True)
        if st.button("📋 Apply Loadout → Inventory", use_container_width=True, type="primary"):
            inv_lines = []
            if ld.get("armor"):     inv_lines.append(ld["armor"])
            if ld.get("weapon"):    inv_lines.append(ld["weapon"])
            if ld.get("secondary"): inv_lines.append(ld["secondary"])
            if ld.get("pack"):      inv_lines.append(ld["pack"])
            if ld.get("focus"):     inv_lines.append(ld["focus"])
            if ld.get("instrument"):inv_lines.append(ld["instrument"])
            for item in ldata.get("fixed_gear",[]):
                inv_lines.append(item)
            if ld.get("cantrips"):
                inv_lines.append("Cantrips: " + ", ".join(ld["cantrips"]))
            if ld.get("spells_1st"):
                inv_lines.append("1st-Level Spells: " + ", ".join(ld["spells_1st"]))
            st.session_state.char_sheet["inventory"] = "\n".join(inv_lines)
            st.session_state.loadout = ld
            st.success("✅ Loadout applied to Inventory! Go to 🧝 Character Sheet to review.")

        # ── Loadout preview summary ──
        st.markdown(f"""
        <div style="margin-top:0.5rem;padding:0.6rem;background:#0D0D0D;border:1px solid #2A2A1A;border-radius:6px;">
            <div style="font-family:'Cinzel Decorative',serif;font-size:0.65rem;color:#D4AF37;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;">
                Current Loadout Preview — {cls} Lv{lvl}
            </div>
            <div style="font-family:'EB Garamond',serif;font-size:0.84rem;color:#C8B880;line-height:1.7;">
                🛡️ <strong>Armor:</strong> {ld.get('armor','—')}<br>
                ⚔️ <strong>Primary:</strong> {ld.get('weapon','—')}<br>
                🏹 <strong>Secondary:</strong> {ld.get('secondary','—')}<br>
                🎒 <strong>Pack:</strong> {ld.get('pack','—')}<br>
                {"✨ <strong>Focus:</strong> " + ld.get('focus','—') + "<br>" if ldata.get('focus_choices') else ""}
                {"🎵 <strong>Instrument:</strong> " + ld.get('instrument','—') + "<br>" if ldata.get('instrument_choices') else ""}
                {"🔮 <strong>Cantrips:</strong> " + (", ".join(ld.get('cantrips',[])) or "none") + "<br>" if ldata.get('cantrips_count',0)>0 else ""}
                {"📖 <strong>Spells:</strong> " + (", ".join(ld.get('spells_1st',[])) or "none") + "<br>" if ldata.get('spells_count',0)>0 else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 5 — SAVES
# ═════════════════════════════════════════════════════════════════════════════
with tab_saves:
    sv_cs   = st.session_state.char_sheet
    sv_name = sv_cs.get("name", "Hero").replace(" ", "_")

    st.markdown("""
    <div style="text-align:center;padding:0.5rem 0 0.2rem;">
        <div style="font-family:'Cinzel Decorative',serif;font-size:1rem;color:#D4AF37;font-weight:700;">
            💾 Campaign Save & Restore
        </div>
        <div style="font-family:'EB Garamond',serif;font-size:0.82rem;color:#8B7355;font-style:italic;">
            Export your full campaign state, download the Adventure Log, or restore a previous session.
        </div>
    </div>
    <hr class="dnd-divider">
    """, unsafe_allow_html=True)

    # ── Autosave Status ──
    autosave_stat = st.session_state.get("autosave_status","")
    if autosave_stat:
        color = "#2E7D32" if autosave_stat.startswith("✅") else "#C62828"
        st.markdown(
            f'<div style="background:#0F0F0A;border:1px solid {color}55;border-radius:4px;'
            f'padding:0.35rem 0.75rem;font-family:\'EB Garamond\',serif;font-size:0.82rem;'
            f'color:{color};margin-bottom:0.5rem;">{autosave_stat}</div>',
            unsafe_allow_html=True,
        )
    # ── Manual trigger ──
    if st.button("💾 Save Now", key="manual_save_btn", use_container_width=True):
        ok = autosave()
        st.rerun()

    st.markdown('<hr class="dnd-divider">', unsafe_allow_html=True)

    # ── Export ──
    st.markdown('<div class="sheet-section"><div class="sheet-section-title">📤 Export Campaign</div>', unsafe_allow_html=True)
    save_json = export_save()

    dl_c1, dl_c2 = st.columns(2)
    with dl_c1:
        st.download_button(
            label="⬇️ Download Save File (.json)",
            data=save_json,
            file_name=f"chronicles_save_{sv_name}.json",
            mime="application/json",
            use_container_width=True,
            help="Download the full campaign state as a JSON file you can reload later."
        )
    with dl_c2:
        md_content = export_markdown()
        st.download_button(
            label="📖 Download Adventure Log (.md)",
            data=md_content,
            file_name=f"{sv_name}_adventure.md",
            mime="text/markdown",
            use_container_width=True,
            help="Download the full chat history and journal as a Markdown document."
        )

    with st.expander("📋 Copy Save Code (paste to restore on any device)", expanded=False):
        st.text_area(
            "Save Code — select all (Ctrl+A / Cmd+A) and copy",
            value=save_json,
            height=180,
            key="save_display_area",
            label_visibility="collapsed",
        )
        st.markdown(
            '<div style="font-family:\'Crimson Text\',serif;font-size:0.78rem;color:#8B7355;">'
            '⚠️ Select all text in the box above and copy it to restore your campaign elsewhere.</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="dnd-divider">', unsafe_allow_html=True)

    # ── Import ──
    st.markdown('<div class="sheet-section"><div class="sheet-section-title">📂 Restore Campaign</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-family:\'Crimson Text\',serif;font-size:0.8rem;color:#8B7355;margin-bottom:0.5rem;">'
        'Paste a previously exported Save Code below to fully restore your character, inventory, '
        'adventure log, and journal.</div>',
        unsafe_allow_html=True
    )
    import_str = st.text_area(
        "Save Code", height=140, key="import_area",
        label_visibility="collapsed",
        placeholder='Paste your exported save JSON here...\n{"version":"1.0","char_sheet":{...},...}'
    )
    if st.button("🔄 Load Campaign from Save Code", use_container_width=True, type="primary", key="btn_import"):
        if import_str.strip():
            ok, result_msg = import_save(import_str)
            if ok:
                st.success(result_msg)
                st.rerun()
            else:
                st.error(result_msg)
        else:
            st.warning("⚠️ Paste a save code into the box above first.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="dnd-divider">', unsafe_allow_html=True)

    # ── Campaign Summary ──
    msg_count  = len(st.session_state.get("messages", []))
    jrn_words  = len(st.session_state.get("journal","").split())
    game_on    = st.session_state.get("game_started", False)
    st.markdown(f"""
    <div style="padding:0.6rem;background:#0D0D0D;border:1px solid #2A1A1A;border-radius:6px;text-align:center;">
        <div style="font-family:'Cinzel Decorative',serif;font-size:0.65rem;color:#8B7355;text-transform:uppercase;
             letter-spacing:0.1em;margin-bottom:0.5rem;">Campaign Status</div>
        <div style="display:flex;justify-content:center;gap:1.5rem;">
            <span>
                <span style="font-family:'Cinzel Decorative',serif;font-size:0.6rem;color:#8B7355;display:block;">Status</span>
                <span style="font-family:'Cinzel Decorative',serif;font-size:0.9rem;color:{'#2E7D32' if game_on else '#8B7355'};font-weight:700;">
                    {'🟢 Active' if game_on else '⚫ Not Started'}
                </span>
            </span>
            <span>
                <span style="font-family:'Cinzel Decorative',serif;font-size:0.6rem;color:#8B7355;display:block;">Messages</span>
                <span style="font-family:'Cinzel Decorative',serif;font-size:0.9rem;color:#D4AF37;font-weight:700;">{msg_count}</span>
            </span>
            <span>
                <span style="font-family:'Cinzel Decorative',serif;font-size:0.6rem;color:#8B7355;display:block;">Journal</span>
                <span style="font-family:'Cinzel Decorative',serif;font-size:0.9rem;color:#D4AF37;font-weight:700;">{jrn_words} words</span>
            </span>
            <span>
                <span style="font-family:'Cinzel Decorative',serif;font-size:0.6rem;color:#8B7355;display:block;">Level</span>
                <span style="font-family:'Cinzel Decorative',serif;font-size:0.9rem;color:#D4AF37;font-weight:700;">{sv_cs.get('level',1)}</span>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
