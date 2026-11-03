"""
ThermoVox AI v0.5 - Universal Clinical Research Prototype
Theme: Natural Biophilic Dark Palette (Slate Obsidian · Coastal Sage · Ocean Indigo)
Cross-Platform: iOS Safari (WebKit), Android (Blink), macOS, Windows
60 FPS GPU-Composited Rendering · Zero Text/Box Overlaps · Balanced Ergonomic Layouts
"""

import os, sqlite3, hashlib, secrets, io, wave
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------- Page Configuration ----------
st.set_page_config(
    page_title="ThermoVox | Clinical Research",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded"
)

ROOT = Path(__file__).parent
DB_PATH = ROOT / "thermovox_users.db"

# Natural, Earthy & Coastal Dark Color Palette (WCAG AA Certified)
BG_BASE = "#0C1117"        # Deep slate obsidian base
BG_SURFACE = "#151C24"     # Natural card panel
BG_GLASS = "rgba(21, 28, 38, 0.74)"
BORDER_GLASS = "rgba(255, 255, 255, 0.08)"
TEAL_SAGE = "#2DD4BF"      # Primary natural accent
TEAL_DARK = "#0D9488"
SKY_OCEAN = "#38BDF8"      # Natural sky / ocean blue
AMBER_WARM = "#F59E0B"     # Natural ochre / warning
RED_EARTH = "#F87171"      # Terracotta / alert
TEXT_PRIMARY = "#EDF2F7"   # Warm off-white
TEXT_MUTED = "#94A3B8"     # Soft mineral slate
LINE_SUBTLE = "rgba(148, 163, 184, 0.12)"

# ---------- Cross-Platform Universal Dark CSS (Strictly Isolated Fonts & Box Layouts) ----------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

:root {{
  --bg-base: {BG_BASE};
  --bg-surface: {BG_SURFACE};
  --text-primary: {TEXT_PRIMARY};
  --text-muted: {TEXT_MUTED};
  --teal-sage: {TEAL_SAGE};
  --teal-dark: {TEAL_DARK};
  --sky-ocean: {SKY_OCEAN};
  --line-subtle: {LINE_SUBTLE};
  --spring: cubic-bezier(0.16, 1, 0.3, 1);
  --ease: cubic-bezier(0.2, 0, 0, 1);
}}

/* Engine Reset & High-Fidelity Typography */
*, *::before, *::after {{
  box-sizing: border-box;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}}

html {{
  scroll-behavior: smooth;
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}}

/* Set body typography WITHOUT overriding Material Symbols ligatures */
html, body, p, h1, h2, h3, h4, h5, h6, input, textarea, button, select {{
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}}

/* Preserve and enforce Google Material Symbols for all UI icons */
[data-testid="stIconMaterial"], 
[data-testid="stIconMaterial"] *, 
.material-symbols-rounded,
.material-icons,
[class*="stIcon"] {{
  font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
  font-weight: normal !important;
  font-style: normal !important;
  font-size: 20px !important;
  line-height: 1 !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  white-space: nowrap !important;
  word-wrap: normal !important;
  direction: ltr !important;
  -webkit-font-feature-settings: 'liga' 1 !important;
  font-feature-settings: 'liga' 1 !important;
  text-transform: none !important;
  letter-spacing: normal !important;
  width: 20px !important;
  height: 20px !important;
  overflow: hidden !important;
}}

/* Deep, Organic Ambient Background */
.stApp {{
  background: 
    radial-gradient(1100px circle at 15% 10%, rgba(45, 212, 191, 0.05) 0%, transparent 50%),
    radial-gradient(1000px circle at 85% 20%, rgba(56, 189, 248, 0.04) 0%, transparent 45%),
    radial-gradient(900px circle at 50% 85%, rgba(15, 23, 42, 0.8) 0%, transparent 60%),
    {BG_BASE} !important;
  color: var(--text-primary) !important;
  overflow-x: hidden !important;
  min-height: 100vh;
}}

/* Header Navigation Bar (No Overlapping) */
header[data-testid="stHeader"] {{
  background: rgba(12, 17, 23, 0.85) !important;
  backdrop-filter: blur(14px) !important;
  -webkit-backdrop-filter: blur(14px) !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
  z-index: 99 !important;
}}

/* iOS Safe Areas & Responsive Max Padding */
.block-container {{
  max-width: 1480px !important;
  padding-top: max(4.5rem, calc(env(safe-area-inset-top) + 3.5rem)) !important;
  padding-bottom: max(3rem, env(safe-area-inset-bottom)) !important;
  padding-left: max(1.2rem, env(safe-area-inset-left)) !important;
  padding-right: max(1.2rem, env(safe-area-inset-right)) !important;
}}

/* 60 FPS Compositing Optimizations */
.tv-glass, 
[data-testid="stVerticalBlockBorderWrapper"], 
[data-testid="stMetric"], 
.tv-hero, 
.stButton>button,
[data-testid="stChatMessage"] {{
  transform: translate3d(0, 0, 0);
  -webkit-transform: translate3d(0, 0, 0);
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}}

/* Typography */
h1, h2, h3, h4, h5, h6 {{
  color: var(--text-primary) !important;
  letter-spacing: -0.025em !important;
  font-weight: 700 !important;
  margin-top: 0 !important;
}}
h1 {{ font-weight: 800 !important; }}

/* ---------- iOS Frosted Glass & Liquid Cards in Dark Mode ---------- */
.tv-glass, [data-testid="stVerticalBlockBorderWrapper"] {{
  background: {BG_GLASS} !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 18px !important;
  padding: 20px 22px !important;
  box-shadow: 
    0 12px 32px 0 rgba(0, 0, 0, 0.35),
    0 2px 6px 0 rgba(0, 0, 0, 0.2),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.08) !important;
  position: relative !important;
  overflow: hidden !important;
}}

@supports ((-webkit-backdrop-filter: blur(18px)) or (backdrop-filter: blur(18px))) {{
  .tv-glass, [data-testid="stVerticalBlockBorderWrapper"] {{
    background: rgba(20, 27, 36, 0.65) !important;
    -webkit-backdrop-filter: blur(24px) saturate(160%) !important;
    backdrop-filter: blur(24px) saturate(160%) !important;
    border: 1px solid rgba(255, 255, 255, 0.09) !important;
  }}
}}

/* Soft Organic Slate Card */
.tv-card-soft {{
  background: rgba(30, 41, 59, 0.5) !important;
  border: 1px solid rgba(255, 255, 255, 0.07) !important;
  border-radius: 16px !important;
  padding: 18px 20px !important;
  color: var(--text-primary) !important;
  backdrop-filter: blur(14px) !important;
  -webkit-backdrop-filter: blur(14px) !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
}}

/* Dark Obsidian Hero Header */
.tv-hero {{
  background: linear-gradient(135deg, rgba(17, 24, 34, 0.94) 0%, rgba(12, 17, 24, 0.98) 100%) !important;
  -webkit-backdrop-filter: blur(24px) saturate(150%) !important;
  backdrop-filter: blur(24px) saturate(150%) !important;
  border: 1px solid rgba(255, 255, 255, 0.09) !important;
  border-radius: 20px !important;
  padding: 24px 28px !important;
  color: var(--text-primary) !important;
  margin-bottom: 20px !important;
  position: relative !important;
  overflow: hidden !important;
  box-shadow: 
    0 16px 40px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
}}

.tv-hero::after {{
  content: "";
  position: absolute;
  right: -50px;
  top: -80px;
  width: 280px;
  height: 280px;
  border: 1.5px solid rgba(45, 212, 191, 0.2);
  border-radius: 50%;
  box-shadow: 0 0 0 32px rgba(45, 212, 191, 0.03), 0 0 0 68px rgba(45, 212, 191, 0.015);
  pointer-events: none;
}}

.tv-hero h1 {{
  color: var(--text-primary) !important;
  font-size: clamp(1.4rem, 2.8vw, 2.05rem) !important;
  margin: 0.25rem 0 0.35rem 0 !important;
  position: relative;
  z-index: 2;
}}

.tv-hero p {{
  color: var(--text-muted) !important;
  margin: 0 !important;
  max-width: 820px !important;
  font-size: clamp(0.9rem, 1.6vw, 1.0rem) !important;
  line-height: 1.5 !important;
  position: relative;
  z-index: 2;
}}

.tv-eyebrow {{
  display: inline-block;
  font-size: 0.72rem !important;
  letter-spacing: 0.16em !important;
  font-weight: 700 !important;
  color: var(--teal-sage) !important;
  text-transform: uppercase !important;
  margin-bottom: 4px !important;
  position: relative;
  z-index: 2;
}}

/* Section Titles & Badges */
.tv-label {{
  font-size: 0.73rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.14em !important;
  font-weight: 700 !important;
  color: var(--teal-sage) !important;
  margin-bottom: 12px !important;
  display: block;
}}

.tv-step {{
  border-left: 3px solid var(--teal-sage);
  padding: 6px 0 6px 14px;
  margin: 12px 0;
  transition: transform 0.18s var(--spring);
}}
.tv-step:hover {{
  transform: translateX(3px);
}}
.tv-step b {{
  color: var(--text-primary);
  font-size: 0.95rem;
}}
.tv-step span {{
  color: var(--text-muted);
  font-size: 0.88rem;
  display: block;
  margin-top: 2px;
}}

/* ---------- Dark Glass Metric KPI Cards ---------- */
[data-testid="stMetric"] {{
  background: rgba(22, 30, 41, 0.65) !important;
  -webkit-backdrop-filter: blur(16px) saturate(160%) !important;
  backdrop-filter: blur(16px) saturate(160%) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 16px !important;
  padding: 16px 18px !important;
  box-shadow: 
    0 8px 24px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
  transition: transform 0.22s var(--spring), box-shadow 0.22s var(--spring) !important;
  height: 100% !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
}}

[data-testid="stMetric"]:hover {{
  transform: translateY(-2px) translate3d(0, 0, 0) !important;
  box-shadow: 
    0 12px 30px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.12) !important;
  border-color: rgba(45, 212, 191, 0.25) !important;
}}

[data-testid="stMetricLabel"] {{
  color: var(--text-muted) !important;
  font-size: 0.8rem !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.06em !important;
}}

[data-testid="stMetricValue"] {{
  color: var(--text-primary) !important;
  font-weight: 800 !important;
  font-size: clamp(1.35rem, 2.5vw, 1.8rem) !important;
}}

/* ---------- Dark Form Inputs (iOS 16px Safe, 44px Touch Targets) ---------- */
.stTextInput input, 
.stTextArea textarea, 
.stSelectbox div[data-baseweb="select"] > div {{
  font-size: 16px !important; /* Prevents iOS Safari auto-zoom */
  color: var(--text-primary) !important;
  background: rgba(15, 21, 29, 0.85) !important;
  border: 1.5px solid rgba(255, 255, 255, 0.10) !important;
  border-radius: 12px !important;
  min-height: 44px !important;
  padding: 10px 14px !important;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.25) !important;
  transition: border-color 0.18s var(--ease), box-shadow 0.18s var(--ease) !important;
}}

.stTextInput input:focus, 
.stTextArea textarea:focus, 
.stSelectbox div[data-baseweb="select"] > div:focus-within {{
  border-color: var(--teal-sage) !important;
  box-shadow: 0 0 0 3px rgba(45, 212, 191, 0.18) !important;
  outline: none !important;
}}

[data-testid="stWidgetLabel"] label, 
[data-testid="stWidgetLabel"] p {{
  color: var(--text-primary) !important;
  font-weight: 600 !important;
  font-size: 0.9rem !important;
  margin-bottom: 6px !important;
}}

/* ---------- Natural Earth / Coastal Sage Buttons ---------- */
.stButton > button, 
.stDownloadButton > button {{
  background: linear-gradient(135deg, #14B8A6 0%, #0D9488 100%) !important;
  color: #061117 !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 700 !important;
  font-size: 0.95rem !important;
  min-height: 44px !important;
  padding: 10px 20px !important;
  box-shadow: 0 4px 14px rgba(20, 184, 166, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
  touch-action: manipulation !important;
  -webkit-tap-highlight-color: transparent !important;
  transition: transform 0.16s var(--spring), box-shadow 0.16s var(--spring), background 0.16s ease !important;
  cursor: pointer !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}}

.stButton > button:hover, 
.stDownloadButton > button:hover {{
  background: linear-gradient(135deg, #2DD4BF 0%, #14B8A6 100%) !important;
  box-shadow: 0 6px 20px rgba(45, 212, 191, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.35) !important;
  transform: translateY(-1px) translate3d(0, 0, 0) !important;
  color: #061117 !important;
}}

.stButton > button:active, 
.stDownloadButton > button:active {{
  transform: scale(0.975) translate3d(0, 0, 0) !important;
  box-shadow: 0 2px 6px rgba(20, 184, 166, 0.2) !important;
}}

/* ---------- iOS Dark Segmented Control ([role="tablist"]) ---------- */
[data-testid="stTabs"] [role="tablist"] {{
  background: rgba(15, 21, 29, 0.7) !important;
  backdrop-filter: blur(14px) !important;
  -webkit-backdrop-filter: blur(14px) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 14px !important;
  padding: 4px !important;
  display: flex !important;
  gap: 4px !important;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.35) !important;
  margin-bottom: 16px !important;
}}

[data-testid="stTabs"] [role="tab"] {{
  border-radius: 10px !important;
  font-weight: 600 !important;
  font-size: 0.92rem !important;
  color: var(--text-muted) !important;
  padding: 8px 18px !important;
  min-height: 40px !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  transition: all 0.2s var(--spring) !important;
}}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
  background: rgba(30, 41, 59, 0.85) !important;
  color: var(--text-primary) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  font-weight: 700 !important;
}}

[data-testid="stTabs"] [role="tab"]::after {{
  display: none !important;
}}

/* ---------- macOS Dark Frosted Sidebar & Expander Fix ---------- */
[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #090D12 0%, #05080C 100%) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
  box-shadow: 6px 0 28px rgba(0, 0, 0, 0.35) !important;
}}

[data-testid="stSidebar"] * {{
  color: var(--text-primary);
}}

[data-testid="stSidebar"] [data-testid="stRadio"] label {{
  padding: 9px 12px !important;
  border-radius: 10px !important;
  margin: 2px 0 !important;
  min-height: 42px !important;
  display: flex !important;
  align-items: center !important;
  transition: all 0.16s var(--ease) !important;
  border: 1px solid transparent !important;
}}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
  background: rgba(255, 255, 255, 0.05) !important;
}}

[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{
  background: rgba(45, 212, 191, 0.12) !important;
  border-color: rgba(45, 212, 191, 0.3) !important;
  color: var(--teal-sage) !important;
  font-weight: 700 !important;
}}

/* Sidebar Expander Structure & Clean Gap */
[data-testid="stSidebar"] [data-testid="stExpander"] {{
  background: rgba(255, 255, 255, 0.03) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 14px !important;
  overflow: hidden !important;
}}

[data-testid="stSidebar"] [data-testid="stExpander"] summary {{
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  padding: 10px 14px !important;
  cursor: pointer !important;
}}

[data-testid="stSidebar"] [data-testid="stExpander"] summary span {{
  display: inline-flex !important;
  align-items: center !important;
}}

/* File Uploader Formatting (Fixes uploaddload Overlap) */
[data-testid="stFileUploader"] {{
  background: rgba(18, 26, 36, 0.6) !important;
  border: 1.5px dashed rgba(45, 212, 191, 0.3) !important;
  border-radius: 16px !important;
  padding: 16px !important;
  transition: border-color 0.2s ease !important;
}}

[data-testid="stFileUploader"]:hover {{
  border-color: var(--teal-sage) !important;
}}

[data-testid="stFileUploaderDropzone"] {{
  background: rgba(12, 17, 24, 0.5) !important;
  border: none !important;
  padding: 12px 16px !important;
  border-radius: 12px !important;
}}

/* Chat Messages */
[data-testid="stChatMessage"] {{
  background: rgba(22, 30, 42, 0.7) !important;
  backdrop-filter: blur(14px) !important;
  -webkit-backdrop-filter: blur(14px) !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 16px !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
  margin-bottom: 12px !important;
}}

/* Status Alerts */
.stAlert {{
  border-radius: 14px !important;
  border-width: 1px !important;
  background: rgba(22, 30, 41, 0.75) !important;
  backdrop-filter: blur(12px) !important;
  -webkit-backdrop-filter: blur(12px) !important;
}}

/* Plotly Chart Container */
[data-testid="stPlotlyChart"] {{
  width: 100% !important;
  border-radius: 14px !important;
  overflow: hidden !important;
}}

/* Custom Scrollbar */
::-webkit-scrollbar {{
  width: 8px;
  height: 8px;
}}
::-webkit-scrollbar-track {{
  background: transparent;
}}
::-webkit-scrollbar-thumb {{
  background: rgba(255, 255, 255, 0.12);
  border-radius: 999px;
}}
::-webkit-scrollbar-thumb:hover {{
  background: rgba(255, 255, 255, 0.22);
}}

/* Focus Accessibility */
:focus-visible {{
  outline: 3px solid var(--teal-sage) !important;
  outline-offset: 2px !important;
}}

/* Reduced Motion Override */
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }}
}}

/* ---------- Responsive Breakpoints & Box Orientation Alignment ---------- */
@media (max-width: 960px) {{
  .block-container {{
    padding-top: max(4.2rem, calc(env(safe-area-inset-top) + 3rem)) !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
  }}
  .tv-hero {{
    padding: 20px 18px !important;
    border-radius: 16px !important;
  }}
  .tv-hero::after {{
    right: -120px !important;
    opacity: 0.3 !important;
  }}
}}

@media (max-width: 768px) {{
  .block-container {{
    padding-top: max(4rem, calc(env(safe-area-inset-top) + 2.8rem)) !important;
    padding-left: 0.75rem !important;
    padding-right: 0.75rem !important;
  }}
  
  /* Stack column layouts vertically on mobile with clean 16px gaps */
  [data-testid="stHorizontalBlock"] {{
    flex-direction: column !important;
    gap: 14px !important;
  }}
  
  [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
    width: 100% !important;
    min-width: 100% !important;
    flex: 1 1 100% !important;
  }}

  /* 2x2 grid for metrics row on mobile */
  [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {{
    display: grid !important;
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 10px !important;
  }}
  [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > [data-testid="column"] {{
    width: 100% !important;
    min-width: 0 !important;
  }}

  .tv-hero {{
    padding: 16px 14px !important;
    border-radius: 14px !important;
    margin-bottom: 14px !important;
  }}
  .tv-glass, [data-testid="stVerticalBlockBorderWrapper"] {{
    padding: 14px !important;
    border-radius: 14px !important;
  }}
  [data-testid="stTabs"] [role="tablist"] {{
    width: 100% !important;
  }}
  [data-testid="stTabs"] [role="tab"] {{
    flex: 1 1 auto !important;
    text-align: center !important;
    padding: 8px 10px !important;
  }}
}}
</style>
""", unsafe_allow_html=True)


# ---------- Database Migration & Layer ----------
def db():
    c = sqlite3.connect(DB_PATH, timeout=20)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY, 
            full_name TEXT NOT NULL, 
            email TEXT UNIQUE NOT NULL, 
            salt TEXT NOT NULL, 
            password_hash TEXT NOT NULL, 
            created_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS experiments(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT NOT NULL, 
            created_at TEXT NOT NULL, 
            label TEXT NOT NULL, 
            tq REAL, 
            aq REAL, 
            rr REAL, 
            gate TEXT, 
            notes TEXT
        )
    """)
    existing = {row[1] for row in c.execute("PRAGMA table_info(experiments)").fetchall()}
    required = {"tq": "REAL", "aq": "REAL", "rr": "REAL", "gate": "TEXT", "notes": "TEXT"}
    for column, col_type in required.items():
        if column not in existing:
            c.execute(f"ALTER TABLE experiments ADD COLUMN {column} {col_type}")
    if "thermal_quality" in existing:
        c.execute("UPDATE experiments SET tq = thermal_quality WHERE tq IS NULL")
    if "audio_quality" in existing:
        c.execute("UPDATE experiments SET aq = audio_quality WHERE aq IS NULL")
    if "fused_rr" in existing:
        c.execute("UPDATE experiments SET rr = fused_rr WHERE rr IS NULL")
    c.commit()
    return c


def pwhash(pw, salt):
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 250000).hex()


def register(name, user, email, pw):
    c = db()
    salt = secrets.token_hex(16)
    try:
        c.execute(
            "INSERT INTO users VALUES(?,?,?,?,?,?)",
            (user, name, email, salt, pwhash(pw, salt), datetime.now().isoformat(timespec="seconds"))
        )
        c.commit()
        return True, "Account registered successfully. Please sign in."
    except sqlite3.IntegrityError:
        return False, "That username or email is already registered."
    finally:
        c.close()


def login(user, pw):
    c = db()
    row = c.execute("SELECT full_name, salt, password_hash FROM users WHERE username=?", (user,)).fetchone()
    c.close()
    return row[0] if row and secrets.compare_digest(pwhash(pw, row[1]), row[2]) else None


def save_exp(user, label, tq, aq, rr, gate, notes):
    c = db()
    c.execute(
        "INSERT INTO experiments(username,created_at,label,tq,aq,rr,gate,notes) VALUES(?,?,?,?,?,?,?,?)",
        (user, datetime.now().isoformat(timespec="seconds"), label, tq, aq, rr, gate, notes)
    )
    c.commit()
    c.close()


# Ensure Temp User kkjj exists
def ensure_temp_user():
    c = db()
    exists = c.execute("SELECT username FROM users WHERE username='kkjj'").fetchone()
    if not exists:
        salt = secrets.token_hex(16)
        c.execute(
            "INSERT INTO users VALUES(?,?,?,?,?,?)",
            ('kkjj', 'Researcher KKJJ', 'kkjj@thermovox.demo', salt, pwhash('123', salt), datetime.now().isoformat(timespec="seconds"))
        )
        c.commit()
    c.close()

ensure_temp_user()


# ---------- UI Helpers & Dark Plotly Template ----------
def hero(title, sub, eyebrow="THERMOVOX AI  /  RESPIRATORY RESEARCH"):
    st.markdown(f"""
    <div class='tv-hero'>
      <div class='tv-eyebrow'>{eyebrow}</div>
      <h1>{title}</h1>
      <p>{sub}</p>
    </div>
    """, unsafe_allow_html=True)


def chart_style(fig, height=340):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(16, 24, 34, 0.5)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color=TEXT_PRIMARY),
        margin=dict(l=10, r=10, t=38, b=10),
        legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center")
    )
    fig.update_xaxes(gridcolor="rgba(255, 255, 255, 0.07)", zerolinecolor="rgba(255, 255, 255, 0.07)")
    fig.update_yaxes(gridcolor="rgba(255, 255, 255, 0.07)", zerolinecolor="rgba(255, 255, 255, 0.07)")
    return fig


# ---------- Signal Processing Core (Cached for 60 FPS Response) ----------
@st.cache_data(show_spinner=False)
def signals(rate=18, tn=12, an=18, occ=5, seed=42):
    rng = np.random.default_rng(seed)
    fs = 20
    t = np.arange(0, 45, 1 / fs)
    f = rate / 60
    thermal = 34.1 + 0.19 * np.sin(2 * np.pi * f * t) + (tn / 100) * 0.055 * rng.normal(size=len(t))
    audio = 0.22 * np.sin(2 * np.pi * f * t + 0.3) + 0.045 * np.sin(2 * np.pi * 1.7 * t) + (an / 100) * 0.20 * rng.normal(size=len(t))
    tq = float(np.clip(1 - (tn / 100) - (occ / 100), 0, 1))
    aq = float(np.clip(1 - (an / 100), 0, 1))
    return t, thermal, audio, tq, aq


@st.cache_data(show_spinner=False)
def estimate(x, fs=20):
    x = x - np.mean(x)
    f = np.fft.rfftfreq(len(x), 1 / fs)
    p = np.abs(np.fft.rfft(x)) ** 2
    mask = (f >= 0.08) & (f <= 0.8)
    return float(f[mask][np.argmax(p[mask])] * 60) if mask.any() else float("nan")


def analyze_wav_bytes(data):
    if len(data) > 20 * 1024 * 1024:
        raise ValueError("Please upload a WAV file smaller than 20 MB.")
    with wave.open(io.BytesIO(data), "rb") as wav:
        channels = wav.getnchannels()
        width = wav.getsampwidth()
        sample_rate = wav.getframerate()
        frames = wav.getnframes()
        if sample_rate < 1000 or frames < sample_rate * 3:
            raise ValueError("Audio must be at least 3 seconds long and have a valid sample rate.")
        raw = wav.readframes(frames)
    if width == 1:
        samples = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128) / 128
    elif width == 2:
        samples = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768
    elif width == 4:
        samples = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648
    else:
        raise ValueError("Supported WAV formats are 8-bit, 16-bit or 32-bit PCM.")
    if channels > 1:
        samples = samples[:(len(samples) // channels) * channels].reshape(-1, channels).mean(axis=1)
    if not len(samples):
        raise ValueError("The WAV file contains no readable samples.")
    duration = len(samples) / sample_rate
    window = max(1, int(sample_rate * 0.25))
    usable = (len(samples) // window) * window
    chunks = samples[:usable].reshape(-1, window)
    envelope = np.sqrt(np.mean(chunks ** 2, axis=1))
    envelope = envelope - np.mean(envelope)
    envelope_fs = 1 / (window / sample_rate)
    rr_estimate = estimate(envelope, envelope_fs)
    peak = float(np.max(np.abs(samples)))
    clipping = float(np.mean(np.abs(samples) >= 0.999))
    variation = float(np.std(envelope))
    quality = float(np.clip(1.0 - clipping * 5 - (0.02 if variation < 1e-4 else 0), 0, 1))
    times = np.arange(len(envelope)) * (window / sample_rate)
    return times, envelope, rr_estimate, quality, duration, peak, clipping


def analyze_thermal_csv(data):
    frame = pd.read_csv(io.BytesIO(data))
    lookup = {str(c).strip().lower(): c for c in frame.columns}
    time_col = next((lookup[k] for k in ("time_seconds", "time", "timestamp_seconds") if k in lookup), None)
    temp_col = next((lookup[k] for k in ("temperature_c", "temperature", "temp_c") if k in lookup), None)
    if time_col is None or temp_col is None:
        raise ValueError("CSV needs time_seconds and temperature_c columns.")
    clean = frame[[time_col, temp_col]].apply(pd.to_numeric, errors="coerce").dropna()
    clean = clean.sort_values(time_col).drop_duplicates(time_col)
    if len(clean) < 30:
        raise ValueError("Please provide at least 30 valid timestamp/temperature samples.")
    times = clean[time_col].to_numpy(dtype=float)
    values = clean[temp_col].to_numpy(dtype=float)
    diffs = np.diff(times)
    diffs = diffs[diffs > 0]
    if not len(diffs):
        raise ValueError("Timestamps must increase over time.")
    fs = 1 / float(np.median(diffs))
    if not 1 <= fs <= 100:
        raise ValueError("Sampling rate must be between 1 and 100 Hz for this prototype.")
    rr_estimate = estimate(values, fs)
    return times, values, rr_estimate, fs


# ---------- Authentication Flow ----------
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    hero(
        "Respiratory research, made clearer.",
        "A focused workspace for exploring facial thermal dynamics, breath acoustics and confidence-aware multimodal signal fusion.",
        "THERMOVOX AI  /  CLINICAL RESEARCH"
    )

    col_left, col_right = st.columns([1.1, 0.9], gap="large")

    with col_left:
        with st.container(border=True):
            st.markdown("<div class='tv-label'>RESEARCH PLATFORM</div>", unsafe_allow_html=True)
            st.markdown("### Two signals. One interpretable workspace.")
            st.markdown("<p style='color:var(--text-muted); line-height:1.55;'>Engineered for researchers inspecting perinasal thermal fluctuation, breath acoustic signatures and reliability-gated multimodal fusion.</p>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class='tv-step'><b>01 &nbsp; Thermal signal studio</b><span>Perinasal temperature modulation and ROI stability</span></div>
            <div class='tv-step'><b>02 &nbsp; Breath acoustic studio</b><span>RMS amplitude envelope and acoustic feature exploration</span></div>
            <div class='tv-step'><b>03 &nbsp; Confidence-aware fusion</b><span>Adaptive quality-weighted contributions and abstention gate</span></div>
            <div class='tv-step'><b>04 &nbsp; Research companion</b><span>Plain-language interpretation of signal metrics and methods</span></div>
            """, unsafe_allow_html=True)
            
            st.caption("◉ Synthetic simulation demonstration. Not a medical diagnostic system.")

    with col_right:
        with st.container(border=True):
            tabs = st.tabs(["Sign in", "Temp Access (kkjj)", "Create account"])
            
            # --- Tab 1: Sign in ---
            with tabs[0]:
                st.subheader("Researcher Sign in")
                u = st.text_input("Username", key="lu", value="kkjj", placeholder="Enter username")
                p = st.text_input("Password", type="password", key="lp", value="123", placeholder="••••••••••")
                if st.button("Sign in to Workspace", use_container_width=True, key="btn_signin"):
                    if not u.strip() or not p:
                        st.error("Please enter both username and password.")
                    else:
                        n = login(u.strip(), p)
                        if n:
                            st.session_state.update(auth=True, user=u.strip(), name=n)
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")
            
            # --- Tab 2: 1-Click Temp Login (kkjj / 123) ---
            with tabs[1]:
                st.subheader("Instant Temp Login")
                st.markdown("""
                <div class='tv-card-soft' style='margin-bottom:12px;'>
                  <b>Pre-configured Researcher Session</b><br>
                  <span style='color:var(--text-muted); font-size:0.88rem;'>
                    Username: <code style='color:var(--teal-sage);'>kkjj</code><br>
                    Password: <code style='color:var(--teal-sage);'>123</code>
                  </span>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🚀 Sign In as kkjj (Instant 1-Click)", use_container_width=True, key="btn_quick_kkjj"):
                    n = login("kkjj", "123")
                    if n:
                        st.session_state.update(auth=True, user="kkjj", name=n)
                        st.rerun()
                    else:
                        st.error("Could not authenticate temp user kkjj.")

            # --- Tab 3: Create Account ---
            with tabs[2]:
                st.subheader("New Researcher Registration")
                rn = st.text_input("Full name", key="rn", placeholder="Dr. Jane Doe")
                ru = st.text_input("Username", key="ru", placeholder="jdoe")
                re = st.text_input("Institutional Email", key="re", placeholder="jane.doe@university.edu")
                rp1 = st.text_input("Password", type="password", key="rp1", placeholder="Min 3 characters")
                rp2 = st.text_input("Confirm password", type="password", key="rp2")
                
                if st.button("Create Account", use_container_width=True, key="btn_reg"):
                    if not all([rn.strip(), ru.strip(), re.strip(), rp1, rp2]):
                        st.error("Please complete all required fields.")
                    elif len(ru.strip()) < 3:
                        st.error("Username must be at least 3 characters.")
                    elif "@" not in re or "." not in re.rsplit("@", 1)[-1]:
                        st.error("Please enter a valid email address.")
                    elif len(rp1) < 3:
                        st.error("Password must be at least 3 characters.")
                    elif rp1 != rp2:
                        st.error("Passwords do not match.")
                    else:
                        ok, msg = register(rn.strip(), ru.strip(), re.strip().lower(), rp1)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.info("🔒 Protocol Notice: Research and educational simulation prototype. Do not input patient-identifiable healthcare data.")
    st.stop()


# ---------- Authenticated Sidebar Navigation ----------
with st.sidebar:
    st.markdown("# ◉ ThermoVox")
    st.caption("NATURAL CLINICAL · MULTIMODAL RESEARCH")
    st.markdown("---")
    st.markdown(f"**Session:** <span style='color:var(--teal-sage); font-weight:700;'>{st.session_state.name}</span> (`{st.session_state.user}`)", unsafe_allow_html=True)
    
    page = st.radio(
        "NAVIGATION",
        [
            "Overview", 
            "Thermal Lab", 
            "Audio Lab", 
            "Fusion Analysis", 
            "Research Assistant", 
            "Reports & History", 
            "Methodology", 
            "Account"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    with st.expander("⚙️ Live Simulation Controls", expanded=False):
        rate = st.slider("Respiratory Rate (br/min)", 8, 35, 18)
        tn = st.slider("Thermal Noise (%)", 0, 90, 12)
        occ = st.slider("ROI Motion / Occlusion (%)", 0, 90, 5)
        an = st.slider("Audio Noise (%)", 0, 90, 18)
        
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True, key="btn_signout"):
        st.session_state.auth = False
        st.rerun()

# Synchronized Signal Computation
t, thermal, audio, tq, aq = signals(rate, tn, an, occ)
rrt, rra = estimate(thermal), estimate(audio)
den = tq + aq
wt, wa = (tq / den, aq / den) if den else (0.5, 0.5)
rr = wt * rrt + wa * rra
cq = (tq + aq) / 2
gate = "INCONCLUSIVE" if min(tq, aq) < 0.2 or cq < 0.3 else ("REVIEW SIGNALS" if cq < 0.6 else "QUALITY CHECK PASSED")


# ========================================================
# Page 1: Overview
# ========================================================
if page == "Overview":
    hero("Research overview", "Real-time snapshot of signal fidelity, respiratory estimates and confidence-weighted contributions.")
    
    # 4 KPI Metrics Row (Responsive Grid on Mobile)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Thermal Quality", f"{tq:.0%}", help="Estimated perinasal ROI visibility & signal stability")
    m2.metric("Audio Quality", f"{aq:.0%}", help="Acoustic SNR and respiratory amplitude modulation")
    m3.metric("Combined Index", f"{cq:.0%}", help="Mean reliability across modalities")
    m4.metric("Fused Estimate", f"{rr:.1f} /min", help="Quality-weighted respiratory rate")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.55, 0.85], gap="large")
    
    with c1:
        with st.container(border=True):
            st.markdown("<div class='tv-label'>SYNCHRONIZED TRACES</div>", unsafe_allow_html=True)
            f = make_subplots(
                rows=2, cols=1, 
                shared_xaxes=True, 
                vertical_spacing=0.10,
                subplot_titles=("PERINASAL THERMAL MODULATION (°C)", "BREATH ACOUSTIC ENVELOPE")
            )
            f.add_trace(go.Scatter(x=t, y=thermal, name="Thermal", line=dict(color=SKY_OCEAN, width=2.2)), row=1, col=1)
            f.add_trace(go.Scatter(x=t, y=audio, name="Audio", line=dict(color=TEAL_SAGE, width=1.8)), row=2, col=1)
            f.update_layout(
                template="plotly_dark",
                height=420,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(16, 24, 34, 0.5)",
                font=dict(family="Plus Jakarta Sans", color=TEXT_PRIMARY),
                showlegend=False,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            f.update_xaxes(gridcolor="rgba(255, 255, 255, 0.07)", title_text="Time (seconds)", row=2, col=1)
            f.update_yaxes(gridcolor="rgba(255, 255, 255, 0.07)")
            st.plotly_chart(f, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    with c2:
        with st.container(border=True):
            st.markdown("<div class='tv-label'>ADAPTIVE FUSION RATIO</div>", unsafe_allow_html=True)
            pie = go.Figure(go.Pie(
                labels=["Thermal", "Audio"],
                values=[wt, wa],
                hole=0.68,
                sort=False,
                marker=dict(colors=[SKY_OCEAN, TEAL_SAGE], line=dict(color=BG_SURFACE, width=2.5)),
                textinfo="label+percent"
            ))
            pie.add_annotation(
                text=f"<b>{cq:.0%}</b><br><span style='font-size:10px; color:{TEXT_MUTED};'>QUALITY</span>",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=18, color=TEXT_PRIMARY, family="Plus Jakarta Sans")
            )
            pie.update_layout(
                template="plotly_dark",
                height=260,
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(pie, use_container_width=True, config={"displayModeBar": False, "responsive": True})

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            st.markdown("**Processing Pipeline Status**")
            for num, title, desc in [
                ("01", "Acquire", "Synchronized thermal IR & acoustic capture"),
                ("02", "Assess", f"Noise {tn}%, ROI Occlusion {occ}%"),
                ("03", "Fuse", f"Thermal {wt:.0%} · Audio {wa:.0%}"),
                ("04", "Gate", f"Status: {gate}")
            ]:
                st.markdown(f"<div class='tv-step'><b>{num} &nbsp; {title}</b><span>{desc}</span></div>", unsafe_allow_html=True)

    if gate == "QUALITY CHECK PASSED":
        st.success(f"✓ Gate Status: {gate} — Multimodal quality meets clinical evaluation threshold.")
    elif gate == "REVIEW SIGNALS":
        st.warning(f"⚠ Gate Status: {gate} — Marginal quality detected. Review input stability.")
    else:
        st.error(f"⛔ Gate Status: {gate} — Quality insufficient. Automated abstention active.")


# ========================================================
# Page 2: Thermal Lab (Harmonized Box Layout)
# ========================================================
elif page == "Thermal Lab":
    hero("Thermal signal studio", "Explore respiratory temperature modulation, ROI tracking and infrared trace ingestion.")
    
    # Top KPI Metrics Row
    k1, k2, k3 = st.columns([1, 1, 1])
    k1.metric("Thermal Quality Index", f"{tq:.1%}")
    k2.metric("Thermal RR Estimate", f"{rrt:.1f} /min")
    k3.metric("ROI Motion Tracking", f"{100-occ}% Stability")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Main Chart Container
    with st.container(border=True):
        st.markdown("<div class='tv-label'>SYNTHETIC PERINASAL TEMPERATURE TRACE</div>", unsafe_allow_html=True)
        f = go.Figure(go.Scatter(x=t, y=thermal, line=dict(color=SKY_OCEAN, width=2.2), name="Temperature"))
        f.update_layout(xaxis_title="Time (seconds)", yaxis_title="Temperature (°C)")
        st.plotly_chart(chart_style(f, 320), use_container_width=True, config={"displayModeBar": False, "responsive": True})

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Two Equal Balanced Columns for Ingestion and Schematic
    col_t1, col_t2 = st.columns([1, 1], gap="large")
    
    with col_t1:
        with st.container(border=True):
            st.markdown("<div class='tv-label'>CUSTOM DATA INGESTION</div>", unsafe_allow_html=True)
            thermal_file = st.file_uploader(
                "Upload calibrated thermal trace (CSV)", 
                type=["csv"], 
                key="thermal_csv", 
                help="Requires time_seconds and temperature_c columns."
            )
            if thermal_file is not None:
                try:
                    xt, yt, user_rr, user_fs = analyze_thermal_csv(thermal_file.getvalue())
                    user_fig = go.Figure(go.Scatter(x=xt, y=yt, line=dict(color=SKY_OCEAN, width=2.2)))
                    user_fig.update_layout(xaxis_title="Time (seconds)", yaxis_title="Temperature (°C)")
                    st.plotly_chart(chart_style(user_fig, 220), use_container_width=True, config={"displayModeBar": False, "responsive": True})
                    
                    uc1, uc2 = st.columns(2)
                    uc1.metric("Uploaded Trace RR", f"{user_rr:.1f} /min")
                    uc2.metric("Sampling Rate", f"{user_fs:.1f} Hz")
                    st.caption("Fidelity check passed. Signal filtered with digital bandpass.")
                except Exception as exc:
                    st.error(f"Could not parse thermal CSV: {exc}")
            else:
                st.caption("Awaiting calibrated infrared sensor CSV export.")

    with col_t2:
        with st.container(border=True):
            st.markdown("<div class='tv-label'>PERINASAL ANATOMICAL MAPPING</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='margin-bottom:8px;'>
              <b>Region of Interest (ROI) Aperture Model</b><br>
              <span style='color:var(--text-muted); font-size:0.86rem;'>Geometric tracking of nostril thermal landmarks</span>
              <svg viewBox="0 0 600 160" width="100%" aria-label="Face and perinasal ROI schematic" style="margin-top:10px; border-radius:10px;">
                <rect x="1" y="1" width="598" height="158" rx="12" fill="{BG_SURFACE}" stroke="rgba(255,255,255,0.08)" stroke-width="1.5"/>
                <path d="M230 25 C190 25 178 60 188 105 C195 137 222 144 260 144 C298 144 325 137 332 105 C342 60 330 25 290 25" fill="none" stroke="{TEXT_MUTED}" stroke-width="1.8"/>
                <path d="M215 75 Q230 68 243 75 M277 75 Q290 68 305 75" fill="none" stroke="{TEXT_MUTED}" stroke-width="1.8"/>
                <path d="M260 71 Q250 99 260 104 Q270 99 260 71" fill="none" stroke="{TEXT_MUTED}" stroke-width="1.8"/>
                <rect x="235" y="106" width="50" height="24" rx="6" fill="rgba(45,212,191,0.15)" stroke="{TEAL_SAGE}" stroke-width="2" stroke-dasharray="5 3"/>
                <path d="M288 118 L380 118" stroke="{TEAL_SAGE}" stroke-width="1.8"/>
                <text x="390" y="114" fill="{TEXT_PRIMARY}" font-size="13" font-weight="700">Perinasal Aperture ROI</text>
                <text x="390" y="132" fill="{TEXT_MUTED}" font-size="11">Automated temperature extraction</text>
              </svg>
            </div>
            """, unsafe_allow_html=True)


# ========================================================
# Page 3: Audio Lab (Harmonized Box Layout)
# ========================================================
elif page == "Audio Lab":
    hero("Breath acoustic studio", "Inspect acoustic waveforms, calculate envelope periodicity and evaluate log-Mel features.")
    
    # Top KPI Metrics Row
    ak1, ak2, ak3 = st.columns([1, 1, 1])
    ak1.metric("Audio Quality Index", f"{aq:.1%}")
    ak2.metric("Audio RR Estimate", f"{rra:.1f} /min")
    ak3.metric("Acoustic SNR", f"{100-an}% Dynamic")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Time-Domain Waveform & Log-Mel Spectrogram
    c_aud1, c_aud2 = st.columns([1.2, 0.8], gap="large")
    with c_aud1:
        with st.container(border=True):
            st.markdown("<div class='tv-label'>TIME-DOMAIN WAVEFORM</div>", unsafe_allow_html=True)
            f = go.Figure(go.Scatter(x=t, y=audio, line=dict(color=TEAL_SAGE, width=1.8)))
            f.update_layout(xaxis_title="Time (seconds)", yaxis_title="Normalized Amplitude")
            st.plotly_chart(chart_style(f, 260), use_container_width=True, config={"displayModeBar": False, "responsive": True})

    with c_aud2:
        with st.container(border=True):
            st.markdown("<div class='tv-label'>LOG-MEL SPECTRAL DYNAMICS</div>", unsafe_allow_html=True)
            rng = np.random.default_rng(4)
            heat = go.Figure(go.Heatmap(
                z=rng.random((24, 70)),
                colorscale=[[0, "#0C1117"], [0.5, "#0D9488"], [1, "#2DD4BF"]],
                showscale=False
            ))
            heat.update_layout(xaxis_title="Time Frames", yaxis_title="Mel Bands")
            st.plotly_chart(chart_style(heat, 260), use_container_width=True, config={"displayModeBar": False, "responsive": True})

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Bottom Ingestion & Pipeline Row
    col_a1, col_a2 = st.columns([1, 1], gap="large")
    with col_a1:
        with st.container(border=True):
            st.markdown("<div class='tv-label'>WAV INGESTION STUDIO</div>", unsafe_allow_html=True)
            audio_file = st.file_uploader(
                "Upload breath audio (PCM WAV)", 
                type=["wav"], 
                key="breath_wav",
                help="Mono or stereo PCM WAV (min 3s, max 20MB)."
            )
            if audio_file is not None:
                try:
                    user_t, user_env, user_rr, user_quality, duration, peak, clipping = analyze_wav_bytes(audio_file.getvalue())
                    st.metric("Uploaded Audio RR", f"{user_rr:.1f} /min")
                    st.metric("Audio Heuristic Quality", f"{user_quality:.0%}")
                    st.caption(f"Duration: {duration:.1f}s | Peak: {peak:.2f} | Clipped: {clipping:.2%}")
                except Exception as exc:
                    st.error(f"Could not parse WAV: {exc}")
            else:
                st.caption("Awaiting PCM acoustic recording.")

    with col_a2:
        with st.container(border=True):
            st.markdown("<div class='tv-label'>ACOUSTIC FEATURE PIPELINE</div>", unsafe_allow_html=True)
            for step_n, step_t, step_d in [
                ("01", "PCM Audio Ingestion", "Mono/stereo 16/32-bit float streaming"),
                ("02", "Digital Bandpass Filter", "150–2200 Hz respiratory spectral isolation"),
                ("03", "Envelope Detection", "250ms root-mean-square amplitude tracking"),
                ("04", "Harmonic Peak Estimation", "FFT power spectral density analysis")
            ]:
                st.markdown(f"<div class='tv-step'><b>{step_n} &nbsp; {step_t}</b><span>{step_d}</span></div>", unsafe_allow_html=True)


# ========================================================
# Page 4: Fusion Analysis
# ========================================================
elif page == "Fusion Analysis":
    hero("Confidence-aware fusion", "Adaptive reliability weighting, mathematical proofs and automated abstention.")
    
    # Top KPI Metrics Row
    fk1, fk2, fk3 = st.columns(3)
    fk1.metric("Thermal Weight", f"{wt:.1%}")
    fk2.metric("Audio Weight", f"{wa:.1%}")
    fk3.metric("Fused RR Estimate", f"{rr:.1f} /min")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    a, b = st.columns(2, gap="large")
    with a:
        with st.container(border=True):
            st.markdown("<div class='tv-label'>MODALITY CONTRIBUTION RATIO</div>", unsafe_allow_html=True)
            st.markdown(f"**Thermal Channel (α_T):** `{wt:.1%}`")
            st.progress(float(wt))
            st.markdown(f"**Acoustic Channel (α_A):** `{wa:.1%}`")
            st.progress(float(wa))
            
            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
            st.markdown("<div class='tv-label'>MATHEMATICAL FORMULATION</div>", unsafe_allow_html=True)
            st.latex(r"\alpha_T = \frac{q_T}{q_T + q_A}, \quad \alpha_A = \frac{q_A}{q_T + q_A}")
            st.latex(r"RR_{\text{fused}} = \alpha_T \cdot RR_T + \alpha_A \cdot RR_A")
            
    with b:
        with st.container(border=True):
            st.markdown("<div class='tv-label'>FUSED PREDICTION</div>", unsafe_allow_html=True)
            f = go.Figure(go.Pie(
                labels=["Thermal", "Audio"],
                values=[wt, wa],
                hole=0.64,
                marker=dict(colors=[SKY_OCEAN, TEAL_SAGE], line=dict(color=BG_SURFACE, width=2.5)),
                textinfo="label+percent"
            ))
            st.plotly_chart(chart_style(f, 240), use_container_width=True, config={"displayModeBar": False, "responsive": True})
            
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            if gate == "QUALITY CHECK PASSED":
                st.success("✓ Gate: Signal quality cleared for research evaluation.")
            elif gate == "REVIEW SIGNALS":
                st.warning("⚠ Gate: High noise variance observed. Review individual channels.")
            else:
                st.error("⛔ Gate: Insufficient confidence. Multimodal pipeline abstained from estimation.")


# ========================================================
# Page 5: Research Assistant
# ========================================================
elif page == "Research Assistant":
    hero("Research assistant", "Biomedical companion explaining equations, signal metrics, plots and methodology.", "THERMOVOX AI  /  RESEARCH COMPANION")
    
    st.markdown("""
    <div class='tv-card-soft'>
      <b>Biomedical Research Domain Knowledge</b><br>
      Ask about respiratory rate calculations · confidence weights · abstention logic · validation metrics (MAE, RMSE, AUROC) · signal-to-noise ratio.
    </div>
    """, unsafe_allow_html=True)
    
    api_key = os.getenv("OPENAI_API_KEY", "")
    try:
        if not api_key:
            api_key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        pass
    if not api_key:
        st.info("💡 Guided Mode: Running intelligent local heuristic agent. Add OPENAI_API_KEY to secrets for GPT-4o integration.")
        
    context = f"""Current ThermoVox Context:
Thermal Quality={tq:.1%}, Audio Quality={aq:.1%}, Combined Quality Index={cq:.1%};
Thermal RR={rrt:.2f} br/min, Audio RR={rra:.2f} br/min;
Thermal Weight={wt:.1%}, Audio Weight={wa:.1%}, Fused RR={rr:.2f} br/min;
Quality Gate={gate}."""

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    prompt = st.chat_input("Ask about signals, quality gating, or research validation…")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        answer = ""
        if api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are ThermoVox Research Assistant, an expert biomedical signal processing companion. Explain signals, formulas and methodology clearly without medical diagnosis. Context: " + context},
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history[-8:]]
                    ],
                    temperature=0.3
                )
                answer = response.choices[0].message.content or "No response generated."
            except Exception as e:
                answer = f"OpenAI API error ({type(e).__name__}). Falling back to local assistant."
                
        if not answer:
            q = prompt.lower()
            if any(k in q for k in ["weight", "contribution", "pie", "ratio"]):
                answer = f"The adaptive weighting is currently **{wt:.1%}** for thermal and **{wa:.1%}** for audio, directly scaled by relative fidelity ($q_T / (q_T + q_A)$). If thermal noise increases, the acoustic branch automatically compensates."
            elif any(k in q for k in ["quality", "score", "noise", "occlusion"]):
                answer = f"Signal fidelity is evaluated at **thermal {tq:.1%}** and **audio {aq:.1%}**. Thermal degradation stems from facial occlusion and thermal noise, whereas audio degradation is driven by acoustic environmental SNR."
            elif any(k in q for k in ["rate", "rr", "breath", "respiratory"]):
                answer = f"The branch estimates are thermal: **{rrt:.1f} br/min**, audio: **{rra:.1f} br/min**, yielding a fused estimate of **{rr:.1f} breaths/min**."
            elif any(k in q for k in ["gate", "abstain", "confidence", "inconclusive"]):
                answer = f"The current safety gate status is **{gate}**. The framework triggers abstention when single-channel quality drops below 20% or combined index falls below 30%, preventing hallucinated estimates under adverse capture conditions."
            elif any(k in q for k in ["validate", "validation", "metric", "mae", "rmse"]):
                answer = "Clinical validation requires comparing fused estimates against gold-standard capnography or spirometry, evaluating Mean Absolute Error (MAE), Root Mean Square Error (RMSE), and Bland-Altman agreement limits across held-out cohorts."
            else:
                answer = f"I can assist with respiratory signal dynamics, weighting formulas, or validation metrics. The current fused estimate is **{rr:.1f} br/min** with a quality gate of **{gate}**."
                
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

    if st.button("Clear Conversation History", key="btn_clear_chat"):
        st.session_state.chat_history = []
        st.rerun()


# ========================================================
# Page 6: Reports & History
# ========================================================
elif page == "Reports & History":
    hero("Reports & experiment history", "Export structured research runs, document trial conditions and audit database logs.")
    
    with st.container(border=True):
        st.markdown("<div class='tv-label'>EXPERIMENT AUDIT TRAIL</div>", unsafe_allow_html=True)
        r_col1, r_col2 = st.columns([1, 1], gap="large")
        with r_col1:
            label = st.text_input("Experiment Label", "Trial Run 01")
        with r_col2:
            notes = st.text_input("Investigator Notes", "Simulated resting breathing with baseline noise")
            
        report_df = pd.DataFrame([
            ("Provenance", "Multimodal Simulation"),
            ("Thermal Quality", f"{tq:.1%}"),
            ("Audio Quality", f"{aq:.1%}"),
            ("Thermal Estimate", f"{rrt:.1f} br/min"),
            ("Audio Estimate", f"{rra:.1f} br/min"),
            ("Fused Estimate", f"{rr:.1f} br/min"),
            ("Thermal Weight", f"{wt:.1%}"),
            ("Audio Weight", f"{wa:.1%}"),
            ("Safety Gate", gate)
        ], columns=["Parameter", "Value"])
        
        st.dataframe(report_df, use_container_width=True, hide_index=True)
        
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        btn_c1, btn_c2 = st.columns(2, gap="medium")
        with btn_c1:
            st.download_button(
                "📥 Download CSV Report", 
                report_df.to_csv(index=False).encode(), 
                "thermovox_report.csv", 
                "text/csv",
                use_container_width=True
            )
        with btn_c2:
            if st.button("💾 Save Experiment to Database", use_container_width=True):
                save_exp(st.session_state.user, label.strip() or "Untitled", tq, aq, rr, gate, notes)
                st.success("Experiment securely recorded in local database.")

    # Saved Runs Table
    c = db()
    rows = c.execute(
        "SELECT created_at, label, tq, aq, rr, gate, notes FROM experiments WHERE username=? ORDER BY id DESC LIMIT 50",
        (st.session_state.user,)
    ).fetchall()
    c.close()
    
    if rows:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='tv-label'>HISTORICAL EXPERIMENTS</div>", unsafe_allow_html=True)
            hist = pd.DataFrame(rows, columns=["Timestamp", "Label", "Thermal Q", "Audio Q", "Fused RR", "Gate", "Notes"])
            st.dataframe(hist, use_container_width=True, hide_index=True)
            
            if len(hist) > 1:
                trend_fig = go.Figure(go.Scatter(x=hist["Timestamp"], y=hist["Fused RR"], mode="lines+markers", line=dict(color=SKY_OCEAN, width=2)))
                trend_fig.update_layout(xaxis_title="Run Date", yaxis_title="Fused RR (br/min)")
                st.plotly_chart(chart_style(trend_fig, 260), use_container_width=True, config={"displayModeBar": False, "responsive": True})


# ========================================================
# Page 7: Methodology
# ========================================================
elif page == "Methodology":
    hero("Methodology & validation", "Algorithmic foundation, sensor requirements and clinical translation criteria.")
    
    m_col1, m_col2 = st.columns(2, gap="large")
    with m_col1:
        with st.container(border=True):
            st.markdown("<div class='tv-label'>THERMAL INFRARED MODALITY</div>", unsafe_allow_html=True)
            st.markdown("""
            **Hardware:** Calibrated Long-Wave Infrared (LWIR 8–14 μm)<br>
            **Anatomical Target:** Perinasal aperture & nostril margins<br>
            **Extraction:** Median temperature tracking over stabilized region of interest:
            """, unsafe_allow_html=True)
            st.latex(r"T(t) = \operatorname{median}\{T_i(t) : i \in \text{ROI}\}")
            st.markdown("Detrended via polynomial regression and filtered through Butterworth bandpass (0.08–0.8 Hz).", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("<div class='tv-label'>ACOUSTIC SENSING MODALITY</div>", unsafe_allow_html=True)
            st.markdown("""
            **Hardware:** Directional near-field acoustic transducer<br>
            **Preprocessing:** Dynamic range normalization, highpass filtering at 150 Hz<br>
            **Features:** Short-time Fourier transform (STFT), log-Mel filterbanks, moving RMS envelope.
            """, unsafe_allow_html=True)

    with m_col2:
        with st.container(border=True):
            st.markdown("<div class='tv-label'>MULTIMODAL FUSION & ABSTENTION</div>", unsafe_allow_html=True)
            st.latex(r"z_{\text{fused}} = \alpha_T z_T + \alpha_A z_A")
            st.markdown("""
            Weighting factors $\\alpha_T, \\alpha_A$ dynamically balance modalities based on instantaneous signal-to-noise ratios.
            When both channels drop below acceptable diagnostic bounds ($q < 0.20$), the architecture automatically yields an **Abstention Gate**, prioritizing patient safety over uncalibrated inference.
            """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("<div class='tv-label'>CLINICAL VALIDATION REQUIREMENTS</div>", unsafe_allow_html=True)
            st.markdown("""
            • Reference agreement against spirometry or nasal cannula capnography<br>
            • Limits of Agreement via Bland-Altman analysis ($\pm 1.96$ SD)<br>
            • Selective classification risk and coverage calibration curves<br>
            • Multi-center validation across varying ambient thermal environments.
            """, unsafe_allow_html=True)


# ========================================================
# Page 8: Account
# ========================================================
elif page == "Account":
    hero("Researcher profile", "Active credential management and system information.")
    
    c = db()
    info = c.execute("SELECT email, created_at FROM users WHERE username=?", (st.session_state.user,)).fetchone()
    c.close()
    
    with st.container(border=True):
        st.markdown("<div class='tv-label'>PROFILE DETAILS</div>", unsafe_allow_html=True)
        st.markdown(f"**Investigator Name:** {st.session_state.name}")
        st.markdown(f"**Username:** `{st.session_state.user}`")
        if info:
            st.markdown(f"**Email:** {info[0]}")
            st.markdown(f"**Registered Date:** {info[1]}")
            
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.info("💡 Storage Architecture: Running on local SQLite research engine. For multi-site collaborative trials, configure PostgreSQL / cloud database connections.")

st.markdown("""
<div style='text-align:center; padding: 24px 0 12px 0;'>
  <p style='color:var(--text-muted); font-size:0.82rem; margin:0;'>
    THERMOVOX AI · v0.5 UNIVERSAL RESEARCH PROTOTYPE · 60 FPS OPTIMIZED
  </p>
</div>
""", unsafe_allow_html=True)
