import os, sqlite3, hashlib, secrets
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="ThermoVox | Clinical Research", page_icon="◉", layout="wide", initial_sidebar_state="expanded")
ROOT = Path(__file__).parent
DB_PATH = ROOT / "thermovox_users.db"

# Healthcare palette supplied by the project owner
NAVY = "#0B1F33"
AZURE = "#2563EB"
TEAL = "#20BFC0"
CYAN = "#DDF6F7"
ICE = "#F8FBFC"
INK = "#173247"
MUTED = "#637887"
BORDER = "#DCE7EC"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root{--navy:#0B1F33;--azure:#2563EB;--teal:#20BFC0;--cyan:#DDF6F7;--ice:#F8FBFC;--ink:#173247;--muted:#637887;--line:#DCE7EC}
html,body,[class*="css"]{font-family:'Source Sans 3',sans-serif}
.stApp{background:var(--ice);color:var(--ink)}
h1,h2,h3,h4{font-family:'Manrope',sans-serif;color:var(--navy);letter-spacing:-.025em}
h1{font-weight:800}
[data-testid="stSidebar"]{background:var(--navy);border-right:0}
[data-testid="stSidebar"] *{color:#F4FAFC}
[data-testid="stSidebar"] [data-testid="stRadio"] label{padding:7px 9px;border-radius:7px}
.block-container{max-width:1500px;padding-top:1.7rem;padding-bottom:3rem}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);padding:15px 17px;border-radius:12px;box-shadow:0 2px 8px rgba(11,31,51,.035)}
[data-testid="stMetricLabel"]{color:var(--muted);font-weight:600}
[data-testid="stMetricValue"]{color:var(--navy);font-family:'Manrope',sans-serif}
.stButton>button,.stDownloadButton>button{background:var(--azure);color:white;border:1px solid var(--azure);border-radius:8px;font-weight:700;min-height:2.55rem}
.stButton>button:hover,.stDownloadButton>button:hover{background:#174fc9;color:white;border-color:#174fc9}
.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"]>div{border-radius:8px}
[data-testid="stTabs"] button{font-weight:700;color:var(--navy)}
hr{border-color:var(--line)}
.tv-hero{background:var(--navy);border-radius:16px;padding:26px 30px;color:white;margin-bottom:18px;position:relative;overflow:hidden}
.tv-hero:after{content:"";position:absolute;right:-40px;top:-100px;width:270px;height:270px;border:1px solid rgba(32,191,192,.25);border-radius:50%;box-shadow:0 0 0 28px rgba(32,191,192,.05),0 0 0 58px rgba(32,191,192,.035)}
.tv-hero h1{color:white;font-size:2.05rem;margin:.25rem 0 .35rem;position:relative;z-index:1}
.tv-hero p{color:#D5E5EC;margin:0;max-width:800px;position:relative;z-index:1}
.tv-eyebrow{font-size:.72rem;letter-spacing:.15em;font-weight:700;color:var(--teal);text-transform:uppercase;position:relative;z-index:1}
.tv-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:17px 19px}
.tv-card-soft{background:var(--cyan);border:1px solid #c6e9eb;border-radius:12px;padding:16px}
.tv-label{font-size:.72rem;text-transform:uppercase;letter-spacing:.13em;font-weight:700;color:#287c86}
.tv-muted{color:var(--muted)}
.tv-step{border-left:3px solid var(--teal);padding:3px 0 4px 12px;margin:12px 0}
.tv-step b{color:var(--navy)}
.tv-step span{color:var(--muted);font-size:.92rem}
[data-testid="stChatMessage"]{background:white;border:1px solid var(--line);border-radius:12px}
.stAlert{border-radius:9px}
</style>
""", unsafe_allow_html=True)

def db():
    c=sqlite3.connect(DB_PATH, timeout=20)
    c.execute("""CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, full_name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, salt TEXT NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS experiments(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, created_at TEXT NOT NULL, label TEXT NOT NULL, tq REAL, aq REAL, rr REAL, gate TEXT, notes TEXT)""")
    # Migrate older v0.2/v0.3 databases without deleting existing accounts or runs.
    existing = {row[1] for row in c.execute("PRAGMA table_info(experiments)").fetchall()}
    required = {"tq": "REAL", "aq": "REAL", "rr": "REAL", "gate": "TEXT", "notes": "TEXT"}
    for column, col_type in required.items():
        if column not in existing:
            c.execute(f"ALTER TABLE experiments ADD COLUMN {column} {col_type}")
    # Preserve values saved under the legacy column names.
    if "thermal_quality" in existing:
        c.execute("UPDATE experiments SET tq = thermal_quality WHERE tq IS NULL")
    if "audio_quality" in existing:
        c.execute("UPDATE experiments SET aq = audio_quality WHERE aq IS NULL")
    if "fused_rr" in existing:
        c.execute("UPDATE experiments SET rr = fused_rr WHERE rr IS NULL")
    c.commit()
    return c

def pwhash(pw,salt):
    return hashlib.pbkdf2_hmac("sha256",pw.encode(),salt.encode(),250000).hex()

def register(name,user,email,pw):
    c=db(); salt=secrets.token_hex(16)
    try:
        c.execute("INSERT INTO users VALUES(?,?,?,?,?,?)",(user,name,email,salt,pwhash(pw,salt),datetime.now().isoformat(timespec="seconds")))
        c.commit(); return True,"Account created. Please sign in."
    except sqlite3.IntegrityError:
        return False,"That username or email is already registered."
    finally:c.close()

def login(user,pw):
    c=db(); row=c.execute("SELECT full_name,salt,password_hash FROM users WHERE username=?",(user,)).fetchone(); c.close()
    return row[0] if row and secrets.compare_digest(pwhash(pw,row[1]),row[2]) else None

def hero(title,sub,eyebrow="THERMOVOX AI  /  RESPIRATORY RESEARCH"):
    st.markdown(f"<div class='tv-hero'><div class='tv-eyebrow'>{eyebrow}</div><h1>{title}</h1><p>{sub}</p></div>",unsafe_allow_html=True)

def chart_style(fig,height=340):
    fig.update_layout(template="plotly_white",height=height,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#FFFFFF",font=dict(family="Source Sans 3",color=INK),margin=dict(l=12,r=12,t=48,b=12),legend=dict(orientation="h",y=-.2))
    fig.update_xaxes(gridcolor="#E8EFF2",zerolinecolor="#E8EFF2")
    fig.update_yaxes(gridcolor="#E8EFF2",zerolinecolor="#E8EFF2")
    return fig

def signals(rate=18,tn=12,an=18,occ=5,seed=42):
    rng=np.random.default_rng(seed); fs=20; t=np.arange(0,45,1/fs); f=rate/60
    thermal=34.1+.19*np.sin(2*np.pi*f*t)+tn/100*.055*rng.normal(size=len(t))
    audio=.22*np.sin(2*np.pi*f*t+.3)+.045*np.sin(2*np.pi*1.7*t)+an/100*.20*rng.normal(size=len(t))
    return t,thermal,audio,float(np.clip(1-tn/100-occ/100,0,1)),float(np.clip(1-an/100,0,1))

def estimate(x,fs=20):
    x=x-np.mean(x); f=np.fft.rfftfreq(len(x),1/fs); p=np.abs(np.fft.rfft(x))**2; mask=(f>=.08)&(f<=.8)
    return float(f[mask][np.argmax(p[mask])]*60) if mask.any() else float("nan")

def save_exp(user,label,tq,aq,rr,gate,notes):
    c=db(); c.execute("INSERT INTO experiments(username,created_at,label,tq,aq,rr,gate,notes) VALUES(?,?,?,?,?,?,?,?)",(user,datetime.now().isoformat(timespec="seconds"),label,tq,aq,rr,gate,notes)); c.commit(); c.close()

# ---------- Authentication ----------
if "auth" not in st.session_state: st.session_state.auth=False
if not st.session_state.auth:
    hero("Respiratory research, made clearer.","A focused workspace for exploring facial thermal dynamics, breath acoustics and confidence-aware signal fusion.","THERMOVOX AI  /  CLEAN CLINICAL")
    left,right=st.columns([1.15,.85],gap="large")
    with left:
        st.markdown("### Two signals. One interpretable workspace.")
        st.markdown("<p class='tv-muted'>Designed for researchers who need to inspect signal quality, understand modality contribution and document experiments.</p>",unsafe_allow_html=True)
        st.markdown("""<div class='tv-card'>
        <div class='tv-label'>RESEARCH WORKSPACE</div>
        <div class='tv-step'><b>01 &nbsp; Thermal signal studio</b><br><span>Perinasal temperature variation and ROI quality</span></div>
        <div class='tv-step'><b>02 &nbsp; Breath acoustic studio</b><br><span>Waveform and acoustic feature exploration</span></div>
        <div class='tv-step'><b>03 &nbsp; Confidence-aware fusion</b><br><span>Reliability-weighted contributions and abstention</span></div>
        <div class='tv-step'><b>04 &nbsp; Research companion</b><br><span>Explain values, plots and methodology in plain language</span></div></div>""",unsafe_allow_html=True)
        st.caption("Synthetic demonstration data only. Not a medical diagnostic system.")
    with right:
        st.markdown("<div class='tv-card'>",unsafe_allow_html=True)
        a,b=st.tabs(["Sign in","Create account"])
        with a:
            st.subheader("Welcome back")
            u=st.text_input("Username",key="lu"); p=st.text_input("Password",type="password",key="lp")
            if st.button("Sign in",use_container_width=True):
                n=login(u.strip(),p)
                if n: st.session_state.update(auth=True,user=u.strip(),name=n); st.rerun()
                else: st.error("Username or password is incorrect.")
        with b:
            st.subheader("Researcher registration")
            n=st.text_input("Full name",key="rn"); un=st.text_input("Username",key="ru"); em=st.text_input("Email",key="re")
            p1=st.text_input("Password (10+ characters)",type="password",key="rp1"); p2=st.text_input("Confirm password",type="password",key="rp2")
            if st.button("Create account",use_container_width=True):
                if not all([n.strip(),un.strip(),em.strip(),p1,p2]): st.error("Complete all fields.")
                elif len(un.strip())<3: st.error("Username must have at least 3 characters.")
                elif "@" not in em or "." not in em.rsplit("@",1)[-1]: st.error("Enter a valid email.")
                elif len(p1)<10: st.error("Password must have at least 10 characters.")
                elif p1!=p2: st.error("Passwords do not match.")
                else:
                    ok,msg=register(n.strip(),un.strip(),em.strip().lower(),p1); (st.success if ok else st.error)(msg)
        st.markdown("</div>",unsafe_allow_html=True)
    st.info("For research and education only. Do not enter patient-identifiable information.")
    st.stop()

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("# ◉ ThermoVox")
    st.caption("CLEAN CLINICAL · RESEARCH")
    st.markdown("---")
    st.write(f"Researcher: **{st.session_state.name}**")
    page=st.radio("NAVIGATION",["Overview","Thermal Lab","Audio Lab","Fusion Analysis","Research Assistant","Reports & History","Methodology","Account"])
    st.markdown("---")
    with st.expander("Demo signal controls"):
        rate=st.slider("Respiratory rate",8,35,18)
        tn=st.slider("Thermal noise (%)",0,90,12)
        occ=st.slider("ROI motion / occlusion (%)",0,90,5)
        an=st.slider("Audio noise (%)",0,90,18)
    if st.button("Sign out",use_container_width=True): st.session_state.auth=False; st.rerun()

t,thermal,audio,tq,aq=signals(rate,tn,an,occ)
rrt,rra=estimate(thermal),estimate(audio)
den=tq+aq
wt,wa=(tq/den,aq/den) if den else (0.5,0.5)
rr=wt*rrt+wa*rra
cq=(tq+aq)/2
gate="INCONCLUSIVE" if min(tq,aq)<.2 or cq<.3 else ("REVIEW SIGNALS" if cq<.6 else "QUALITY CHECK PASSED")

# ---------- Overview ----------
if page=="Overview":
    hero("Research overview","A clear snapshot of signal quality, respiratory estimates and modality contribution.")
    m=st.columns(4)
    for col,label,val in zip(m,["Thermal quality","Audio quality","Combined quality index","Fused demo estimate"],[f"{tq:.0%}",f"{aq:.0%}",f"{cq:.0%}",f"{rr:.1f} /min"]): col.metric(label,val)
    st.caption("Quality scores are illustrative heuristics, not calibrated clinical confidence probabilities.")
    c1,c2=st.columns([1.5,.85],gap="large")
    with c1:
        f=make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=.12,subplot_titles=("FACIAL THERMAL TRACE · SIMULATED","BREATH ACOUSTIC TRACE · SIMULATED"))
        f.add_trace(go.Scatter(x=t,y=thermal,name="Thermal",line=dict(color=AZURE,width=2)),row=1,col=1)
        f.add_trace(go.Scatter(x=t,y=audio,name="Audio",line=dict(color=TEAL,width=1.6)),row=2,col=1)
        f.update_layout(template="plotly_white",height=460,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="white",font=dict(family="Source Sans 3",color=INK),showlegend=False,margin=dict(l=10,r=10,t=55,b=10))
        f.update_xaxes(gridcolor="#E8EFF2",title_text="Time (seconds)",row=2,col=1); f.update_yaxes(gridcolor="#E8EFF2")
        st.plotly_chart(f,use_container_width=True)
    with c2:
        st.markdown("<div class='tv-card'><div class='tv-label'>MODALITY CONTRIBUTION</div>",unsafe_allow_html=True)
        pie=go.Figure(go.Pie(labels=["Thermal","Audio"],values=[wt,wa],hole=.65,sort=False,marker=dict(colors=[AZURE,TEAL],line=dict(color="white",width=3)),textinfo="label+percent"))
        pie.add_annotation(text=f"{cq:.0%}<br><sup>quality index</sup>",x=.5,y=.5,showarrow=False,font=dict(size=17,color=NAVY))
        pie.update_layout(template="plotly_white",height=300,paper_bgcolor="rgba(0,0,0,0)",showlegend=False,margin=dict(l=0,r=0,t=18,b=0))
        st.plotly_chart(pie,use_container_width=True)
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("**Analysis pathway**")
        for num,title,desc in [("01","Acquire","Thermal and breath audio"),("02","Assess","Noise, motion and occlusion"),("03","Fuse","Reliability-weighted signals"),("04","Review","Abstain if evidence is weak")]:
            st.markdown(f"<div class='tv-step'><b>{num} &nbsp; {title}</b><br><span>{desc}</span></div>",unsafe_allow_html=True)
    (st.warning if gate=="INCONCLUSIVE" else st.success)(f"Current simulation status: {gate}.")

# ---------- Thermal ----------
elif page=="Thermal Lab":
    hero("Thermal signal studio","Explore respiratory temperature modulation and acquisition quality.")
    a,b=st.columns([.8,1.5],gap="large")
    with a:
        st.metric("Thermal quality",f"{tq:.1%}"); st.metric("Thermal RR estimate",f"{rrt:.1f} /min")
        st.markdown("<div class='tv-card'><div class='tv-label'>QUALITY CHECKLIST</div><p>• ROI visibility</p><p>• Motion stability</p><p>• Thermal variation</p><p>• Temporal continuity</p></div>",unsafe_allow_html=True)
    with b:
        f=go.Figure(go.Scatter(x=t,y=thermal,line=dict(color=AZURE,width=2),name="Temperature"))
        f.update_layout(title="Perinasal temperature trace · synthetic",xaxis_title="Time (seconds)",yaxis_title="Temperature (°C)")
        st.plotly_chart(chart_style(f,390),use_container_width=True)
        st.markdown("""<div class='tv-card-soft'><b>Perinasal region of interest (ROI)</b><br><span class='tv-muted'>Conceptual illustration only — not a real thermal-camera frame.</span>
        <svg viewBox="0 0 600 150" width="100%" aria-label="Face and perinasal ROI schematic">
        <rect x="1" y="1" width="598" height="148" rx="10" fill="#F8FBFC" stroke="#B9DDE1"/>
        <path d="M230 20 C190 20 178 55 188 100 C195 132 222 139 260 139 C298 139 325 132 332 100 C342 55 330 20 290 20" fill="none" stroke="#0B1F33" stroke-width="2"/>
        <path d="M215 70 Q230 63 243 70 M277 70 Q290 63 305 70" fill="none" stroke="#0B1F33" stroke-width="2"/>
        <path d="M260 66 Q250 94 260 99 Q270 94 260 66" fill="none" stroke="#0B1F33" stroke-width="2"/>
        <rect x="235" y="101" width="50" height="22" rx="5" fill="none" stroke="#20BFC0" stroke-width="3" stroke-dasharray="5 3"/>
        <path d="M288 112 L390 112" stroke="#20BFC0" stroke-width="2"/><text x="400" y="108" fill="#0B1F33" font-size="13">Perinasal ROI</text><text x="400" y="126" fill="#637887" font-size="11">concept only</text></svg></div>""",unsafe_allow_html=True)
    st.warning("Actual temperature extraction requires a thermal infrared camera. RGB webcams cannot measure temperature.")

# ---------- Audio ----------
elif page=="Audio Lab":
    hero("Breath acoustic studio","Inspect the waveform and understand the planned signal-processing workflow.")
    a,b=st.columns([.8,1.5],gap="large")
    with a:
        st.metric("Audio quality",f"{aq:.1%}"); st.metric("Audio RR estimate",f"{rra:.1f} /min")
        st.markdown("<div class='tv-card'><div class='tv-label'>PROCESSING PIPELINE</div><p>01 · WAV ingestion</p><p>02 · Filtering and segmentation</p><p>03 · MFCC / log-Mel features</p><p>04 · Model inference</p></div>",unsafe_allow_html=True)
        st.file_uploader("Upload WAV audio",type=["wav"],help="The upload is not processed in this prototype.")
        st.caption("Audio analysis is not connected yet.")
    with b:
        f=go.Figure(go.Scatter(x=t,y=audio,line=dict(color=TEAL,width=1.5)))
        f.update_layout(title="Breath acoustic waveform · synthetic",xaxis_title="Time (seconds)",yaxis_title="Normalised amplitude")
        st.plotly_chart(chart_style(f,360),use_container_width=True)
        rng=np.random.default_rng(4)
        heat=go.Figure(go.Heatmap(z=rng.random((24,70)),colorscale=[[0,"#DDF6F7"],[.5,"#20BFC0"],[1,"#2563EB"]],showscale=False))
        heat.update_layout(title="Illustrative log-Mel feature map · synthetic",xaxis_title="Time frames",yaxis_title="Mel bands")
        st.plotly_chart(chart_style(heat,260),use_container_width=True)
    st.info("The feature map is illustrative and is not calculated from the uploaded WAV file.")

# ---------- Fusion ----------
elif page=="Fusion Analysis":
    hero("Confidence-aware fusion","Understand how each modality contributes and when the framework should abstain.")
    a,b=st.columns(2,gap="large")
    with a:
        st.metric("Thermal contribution",f"{wt:.1%}"); st.progress(wt)
        st.metric("Audio contribution",f"{wa:.1%}"); st.progress(wa)
        st.latex(r"\\alpha_T=\\frac{q_T}{q_T+q_A},\\quad \\alpha_A=\\frac{q_A}{q_T+q_A}")
        st.latex(r"RR_{fused}=\\alpha_T RR_T+\\alpha_A RR_A")
    with b:
        f=go.Figure(go.Pie(labels=["Thermal","Audio"],values=[wt,wa],hole=.62,marker=dict(colors=[AZURE,TEAL]),textinfo="label+percent"))
        f.update_layout(title="Adaptive modality contribution")
        st.plotly_chart(chart_style(f,350),use_container_width=True)
        st.metric("Fused demo estimate",f"{rr:.1f} breaths/min")
    if gate=="INCONCLUSIVE": st.error("ABSTENTION: simulated signal quality is below the illustrative threshold.")
    elif gate=="REVIEW SIGNALS": st.warning("Review signal quality before interpreting this simulated output.")
    else: st.success("Illustrative quality threshold passed.")
    st.caption("These weights and quality scores are demo heuristics, not clinically validated estimators.")

# ---------- Research Assistant ----------
elif page=="Research Assistant":
    hero("Research assistant","Ask about the displayed metrics, signal quality, plots, equations and research methodology.","THERMOVOX AI  /  RESEARCH COMPANION")
    st.markdown("<div class='tv-card-soft'><b>What I can help explain</b><br>Respiratory-rate estimates · modality weights · quality scores · abstention logic · chart interpretation · validation metrics · research writing</div>",unsafe_allow_html=True)
    api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY",""))
    if not api_key:
        st.info("Research assistant is in guided demo mode. To enable AI-generated answers, add an OPENAI_API_KEY to Streamlit Cloud → App settings → Secrets. Never paste your API key into this chat or GitHub.")
    context=f"""Current ThermoVox demo context (synthetic, not patient data):
Thermal quality={tq:.1%}; audio quality={aq:.1%}; combined quality index={cq:.1%};
thermal RR estimate={rrt:.2f} breaths/min; audio RR estimate={rra:.2f} breaths/min;
thermal weight={wt:.1%}; audio weight={wa:.1%}; fused estimate={rr:.2f} breaths/min; quality gate={gate}.
These values are generated from synthetic signals. Quality scores are illustrative heuristics, not clinical confidence probabilities. The app is not a diagnostic device."""
    if "chat_history" not in st.session_state: st.session_state.chat_history=[]
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    prompt=st.chat_input("Ask about your current results…")
    if prompt:
        st.session_state.chat_history.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        answer=""
        if api_key:
            try:
                from openai import OpenAI
                client=OpenAI(api_key=api_key)
                response=client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role":"system","content":"You are ThermoVox Research Assistant, a careful biomedical signal-processing research helper. Explain plots, signal quality, equations and research methods in clear language. Never diagnose, prescribe, infer disease from these demo metrics, invent validation results, or present synthetic values as patient measurements. State limitations and distinguish observed values from interpretation. Context: "+context},
                        *[{"role":m["role"],"content":m["content"]} for m in st.session_state.chat_history[-10:]]
                    ],
                    temperature=0.3,
                )
                answer=response.choices[0].message.content or "I couldn't generate a response. Please try again."
            except Exception as e:
                answer=f"I couldn't reach the AI service ({type(e).__name__}). Check the API key and deployment logs, then try again."
        else:
            q=prompt.lower()
            if any(k in q for k in ["weight","contribution","pie","fusion"]):
                answer=f"Your current simulated fusion assigns **{wt:.1%}** weight to the thermal branch and **{wa:.1%}** to audio. The weighting is proportional to the two heuristic quality scores. It describes how the prototype combines these demo signals; it is not a clinical confidence measure."
            elif any(k in q for k in ["quality","score","noise","occlusion"]):
                answer=f"The current quality indices are **thermal {tq:.1%}** and **audio {aq:.1%}**. In this prototype, thermal quality decreases with simulated noise and ROI occlusion, while audio quality decreases with simulated noise. These are simple illustrative rules, not validated signal-quality algorithms."
            elif any(k in q for k in ["rate","rr","breath","respiratory"]):
                answer=f"The synthetic branch estimates are thermal **{rrt:.1f} breaths/min** and audio **{rra:.1f} breaths/min**. The quality-weighted fused demo estimate is **{rr:.1f} breaths/min**. These are generated simulation outputs, not measurements from a person."
            elif any(k in q for k in ["inconclusive","abstain","gate","confidence"]):
                answer=f"The current gate is **{gate}**. The prototype abstains when either modality quality falls below 20% or the combined quality index falls below 30%. This threshold is illustrative and requires validation before research claims."
            elif any(k in q for k in ["validate","metric","mae","rmse","auc","f1"]):
                answer="For validation, compare respiratory-rate estimates against a reference measurement and report MAE and RMSE. For anomaly classification, report sensitivity, specificity, precision, F1 and AUROC. For confidence-aware abstention, report coverage, selective risk and calibration. Use held-out participants and synchronized thermal/audio recordings; do not treat synthetic data as validation."
            else:
                answer="I can help explain the current thermal/audio values, fusion weights, quality gate, respiratory-rate estimates, plots and validation metrics. Ask me something like “Why is the audio weight higher?” or “How should we validate this model?” For open-ended AI answers, configure an OpenAI API key in Streamlit Cloud Secrets."
        st.session_state.chat_history.append({"role":"assistant","content":answer})
        with st.chat_message("assistant"): st.markdown(answer)
    if st.button("Clear conversation"):
        st.session_state.chat_history=[]; st.rerun()

# ---------- Reports ----------
elif page=="Reports & History":
    hero("Reports & experiment history","Export the current synthetic run and review saved experiments.")
    st.error("RESEARCH PROTOTYPE · NOT FOR CLINICAL USE")
    label=st.text_input("Experiment label","ThermoVox demo run")
    notes=st.text_area("Research notes",placeholder="Describe the simulation settings or observations…")
    report=pd.DataFrame([("Provenance","Synthetic simulation"),("Thermal quality",f"{tq:.1%}"),("Audio quality",f"{aq:.1%}"),("Thermal RR",f"{rrt:.1f} breaths/min"),("Audio RR",f"{rra:.1f} breaths/min"),("Fused RR",f"{rr:.1f} breaths/min"),("Thermal weight",f"{wt:.1%}"),("Audio weight",f"{wa:.1%}"),("Gate",gate)],columns=["Parameter","Value"])
    st.dataframe(report,use_container_width=True,hide_index=True)
    st.download_button("Download CSV report",report.to_csv(index=False).encode(), "thermovox_report.csv","text/csv")
    if st.button("Save this experiment"):
        save_exp(st.session_state.user,label.strip() or "Untitled",tq,aq,rr,gate,notes); st.success("Saved to the local prototype database.")
    c=db(); rows=c.execute("SELECT created_at,label,tq,aq,rr,gate,notes FROM experiments WHERE username=? ORDER BY id DESC LIMIT 100",(st.session_state.user,)).fetchall(); c.close()
    if rows:
        hist=pd.DataFrame(rows,columns=["Created","Experiment","Thermal Q","Audio Q","Fused RR","Gate","Notes"])
        st.subheader("Saved runs"); st.dataframe(hist,use_container_width=True,hide_index=True)
        if len(hist)>1:
            f=go.Figure(go.Scatter(x=hist["Created"],y=hist["Fused RR"],mode="lines+markers",line=dict(color=AZURE)))
            f.update_layout(title="Saved run trend",yaxis_title="Breaths/min")
            st.plotly_chart(chart_style(f,300),use_container_width=True)

# ---------- Methodology ----------
elif page=="Methodology":
    hero("Methodology & validation","The framework's processing logic and the evidence required before clinical claims.")
    a,b=st.columns(2)
    with a:
        st.markdown("### Thermal branch")
        st.markdown("<div class='tv-card'>Input: thermal infrared frames<br>ROI: perinasal region<br>Processing: temperature extraction, motion compensation, detrending and filtering<br>Output: respiratory trace and quality indicators</div>",unsafe_allow_html=True)
        st.latex(r"T(t)=\\operatorname{median}\\{T_i(t):i\\in ROI\\}")
        st.markdown("### Acoustic branch")
        st.markdown("<div class='tv-card'>Input: synchronized breath audio<br>Processing: resampling, filtering and segmentation<br>Features: MFCC, log-Mel energy, RMS and spectral descriptors</div>",unsafe_allow_html=True)
    with b:
        st.markdown("### Fusion and abstention")
        st.latex(r"z=\\alpha_T z_T+\\alpha_A z_A")
        st.write("Estimate modality quality, normalise weights and abstain when evidence is insufficient.")
        st.markdown("### Validation metrics")
        st.write("• Respiratory-rate MAE and RMSE")
        st.write("• Sensitivity, specificity, F1 and AUROC")
        st.write("• Coverage, selective risk and calibration")
        st.warning("Full multimodal validation needs synchronized real thermal and audio recordings with reference labels.")

# ---------- Account ----------
elif page=="Account":
    hero("Researcher profile","Account details and prototype storage notes.")
    c=db(); info=c.execute("SELECT email,created_at FROM users WHERE username=?",(st.session_state.user,)).fetchone(); c.close()
    st.markdown("<div class='tv-card'>",unsafe_allow_html=True)
    st.write(f"**Name:** {st.session_state.name}")
    st.write(f"**Username:** {st.session_state.user}")
    if info: st.write(f"**Email:** {info[0]}"); st.write(f"**Member since:** {info[1]}")
    st.markdown("</div>",unsafe_allow_html=True)
    st.warning("SQLite is local prototype storage and is not reliable persistent shared storage on Streamlit Cloud. Before relying on public accounts, use a managed cloud database. Do not store patient-identifiable data.")

st.markdown("<hr><p class='tv-muted' style='font-size:.8rem'>THERMOVOX AI · v0.4 · CLEAN CLINICAL · SYNTHETIC DEMO MODE</p>",unsafe_allow_html=True)
