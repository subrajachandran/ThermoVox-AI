import streamlit as st
import numpy as np
import pandas as pd
import sqlite3, hashlib, secrets, json
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT=Path(__file__).parent
DB=ROOT/"thermovox_users.db"
st.set_page_config(page_title="ThermoVox AI",page_icon="🫁",layout="wide",initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:radial-gradient(ellipse at 15% 0%,#153e46 0%,#0a1c27 36%,#07131d 78%);color:#edf7f7}
h1,h2,h3{font-family:'Space Grotesk',sans-serif;color:#f4fbfb}
[data-testid="stSidebar"]{background:#091d27;border-right:1px solid #244b54}
[data-testid="stMetric"]{background:linear-gradient(135deg,#102b35,#12343b);padding:15px;border:1px solid #28515a;border-radius:16px}
.stButton>button{background:linear-gradient(90deg,#16a995,#59d8bd);color:#041b20;border:0;border-radius:10px;font-weight:700}
.stButton>button:hover{background:#80ead0;color:#041b20}
.hero{padding:27px 30px;border:1px solid #2a555c;border-radius:22px;background:linear-gradient(115deg,rgba(21,74,79,.92),rgba(11,31,44,.96))}
.muted{color:#a8c4c8}.eyebrow{letter-spacing:2px;color:#75e0c5;font-size:11px;font-weight:700}
.panel{padding:16px;border:1px solid #28515a;border-radius:15px;background:#102832}
div[data-testid="stTabs"] button{color:#d9eeee}
</style>""",unsafe_allow_html=True)

# Database: public self-registration; local research prototype only.
def db():
    c=sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS users(
      username TEXT PRIMARY KEY, full_name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
      salt TEXT NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS experiments(
      id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, created_at TEXT NOT NULL,
      label TEXT NOT NULL, thermal_quality REAL, audio_quality REAL, fused_rr REAL,
      gate TEXT, notes TEXT)""")
    c.commit()
    return c

def pw_hash(password,salt):
    return hashlib.pbkdf2_hmac("sha256",password.encode(),salt.encode(),220000).hex()

def register(full_name,username,email,password):
    salt=secrets.token_hex(16)
    c=db()
    try:
        c.execute("INSERT INTO users VALUES(?,?,?,?,?,?)",(username,full_name,email,salt,pw_hash(password,salt),datetime.now().isoformat(timespec="seconds")))
        c.commit()
        return True,"Account created. You can now sign in."
    except sqlite3.IntegrityError:
        return False,"That username or email is already registered."
    finally:c.close()

def authenticate(username,password):
    c=db(); row=c.execute("SELECT full_name,salt,password_hash FROM users WHERE username=?",(username,)).fetchone(); c.close()
    if not row:return None
    return row[0] if secrets.compare_digest(pw_hash(password,row[1]),row[2]) else None

def demo_signals(seed=42,duration=40,fs=20,rate=18):
    rng=np.random.default_rng(seed); t=np.arange(0,duration,1/fs); f=rate/60
    thermal=34.2+0.20*np.sin(2*np.pi*f*t)+0.025*rng.normal(size=len(t))
    audio=0.24*np.sin(2*np.pi*f*t+.25)+0.045*np.sin(2*np.pi*1.6*t)+0.06*rng.normal(size=len(t))
    return t,thermal,audio

def estimate_rr(x,fs):
    x=x-np.mean(x); freqs=np.fft.rfftfreq(len(x),d=1/fs); power=np.abs(np.fft.rfft(x))**2
    band=(freqs>=.08)&(freqs<=.8)
    return float(freqs[band][np.argmax(power[band])]*60)

def qscore(noise,occlusion=0):
    return float(np.clip(1-noise/100-occlusion/100,0,1))

def header(title,subtitle):
    st.markdown(f"<div class='hero'><div class='eyebrow'>THERMOVOX AI · RESEARCH WORKSPACE</div><h1 style='font-size:35px;margin:8px 0'>{title}</h1><p class='muted' style='margin:0'>{subtitle}</p></div>",unsafe_allow_html=True)
    st.write("")

def save_experiment(user,label,qt,qa,rr,gate,notes):
    c=db(); c.execute("INSERT INTO experiments(username,created_at,label,thermal_quality,audio_quality,fused_rr,gate,notes) VALUES(?,?,?,?,?,?,?,?)",
       (user,datetime.now().isoformat(timespec="seconds"),label,qt,qa,rr,gate,notes)); c.commit(); c.close()

# ---------- Authentication ----------
if "authenticated" not in st.session_state: st.session_state.authenticated=False
if not st.session_state.authenticated:
    header("Welcome to ThermoVox AI","A confidence-aware multimodal platform for respiratory signal research.")
    left,right=st.columns([1.15,1])
    with left:
        st.markdown("### Hear the signals. Read the patterns. Trust the quality.")
        st.write("Explore the relationship between facial thermal dynamics and breath acoustics through an interactive research workspace.")
        st.markdown("""
        <div class='panel'>
        <div class='eyebrow'>PLATFORM MODULES</div>
        <p>◈ Thermal Signal Studio</p><p>◈ Breath Acoustic Studio</p><p>◈ Confidence-Aware Fusion Engine</p><p>◈ Explainable Research Reports</p><p>◈ Personal Experiment Library</p>
        </div>""",unsafe_allow_html=True)
        st.caption("Public registration is enabled. Each researcher has a separate local account and experiment history.")
    with right:
        login_tab,signup_tab=st.tabs(["Sign in","Create account"])
        with login_tab:
            st.subheader("Welcome back")
            u=st.text_input("Username",key="login_u"); p=st.text_input("Password",type="password",key="login_p")
            if st.button("Sign in",use_container_width=True):
                name=authenticate(u.strip(),p)
                if name:
                    st.session_state.update(authenticated=True,username=u.strip(),full_name=name); st.rerun()
                else:st.error("Username or password is incorrect.")
        with signup_tab:
            st.subheader("Create your researcher account")
            n=st.text_input("Full name",key="signup_n"); un=st.text_input("Username",key="signup_u")
            em=st.text_input("Email address",key="signup_e"); p1=st.text_input("Password (minimum 10 characters)",type="password",key="signup_p1")
            p2=st.text_input("Confirm password",type="password",key="signup_p2")
            if st.button("Create account",use_container_width=True):
                if not all([n.strip(),un.strip(),em.strip(),p1]):st.error("Please complete every field.")
                elif len(p1)<10:st.error("Use at least 10 characters for the password.")
                elif p1!=p2:st.error("Passwords do not match.")
                elif "@" not in em or "." not in em.split("@")[-1]:st.error("Enter a valid email address.")
                else:
                    ok,msg=register(n.strip(),un.strip(),em.strip(),p1); (st.success if ok else st.error)(msg)
    st.warning("Research prototype only. Synthetic demo signals are not patient data and must not be used for diagnosis.")
    st.stop()

# ---------- Workspace shell ----------
with st.sidebar:
    st.markdown("## 🫁 ThermoVox AI")
    st.caption("Multimodal respiratory research")
    st.write(f"Researcher: **{st.session_state.full_name}**")
    st.markdown("---")
    page=st.radio("WORKSPACE",["Overview","Thermal Lab","Audio Lab","Fusion Engine","Screening Report","Experiment Library","Research Notes","Profile & Settings"])
    st.markdown("---")
    st.markdown("<span class='eyebrow'>SYSTEM STATUS</span>",unsafe_allow_html=True)
    st.success("Simulation environment active")
    if st.button("Sign out",use_container_width=True):
        st.session_state.authenticated=False; st.rerun()

# Shared simulation controls
if "demo_rate" not in st.session_state:st.session_state.demo_rate=18
if "thermal_noise" not in st.session_state:st.session_state.thermal_noise=18
if "audio_noise" not in st.session_state:st.session_state.audio_noise=24
if "occlusion" not in st.session_state:st.session_state.occlusion=5
t,thermal,audio=demo_signals(rate=st.session_state.demo_rate)
qt=qscore(st.session_state.thermal_noise,st.session_state.occlusion)
qa=qscore(st.session_state.audio_noise)
rrt=estimate_rr(thermal,20); rra=estimate_rr(audio,20)
wt=qt/(qt+qa+1e-9); wa=qa/(qt+qa+1e-9)
fused=wt*rrt+wa*rra; confidence=(qt+qa)/2
gate="INCONCLUSIVE" if min(qt,qa)<.25 or confidence<.35 else ("LOW CONFIDENCE — REVIEW" if confidence<.60 else "QUALITY GATE PASSED")

if page=="Overview":
    header("Respiratory Intelligence, Reimagined","Your unified command centre for contactless thermal and acoustic signal research.")
    metrics=st.columns(4)
    for col,label,value in zip(metrics,["Thermal quality","Audio quality","Combined quality*","Demo respiratory rate"],[f"{qt:.0%}",f"{qa:.0%}",f"{confidence:.0%}",f"{fused:.1f} /min"]):col.metric(label,value)
    st.caption("*Prototype quality index; not a calibrated clinical confidence probability.")
    a,b=st.columns([1.45,1])
    with a:
        fig=make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=.1,subplot_titles=("Perinasal thermal trace · simulated","Breath acoustic envelope · simulated"))
        fig.add_trace(go.Scatter(x=t,y=thermal,mode="lines",name="Thermal"),row=1,col=1)
        fig.add_trace(go.Scatter(x=t,y=audio,mode="lines",name="Audio"),row=2,col=1)
        fig.update_layout(height=450,template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#0b202a",margin=dict(l=10,r=10,t=55,b=10),showlegend=False)
        fig.update_xaxes(title="Time (seconds)",row=2,col=1); st.plotly_chart(fig,use_container_width=True)
    with b:
        st.subheader("Analysis pipeline")
        for no,title,desc in [("01","Signal acquisition","Thermal + breath acoustics"),("02","Quality assessment","Noise · motion · occlusion"),("03","Adaptive fusion","Reliability-weighted features"),("04","Confidence gate","Abstain when evidence is weak")]:
            st.markdown(f"<div class='panel' style='margin-bottom:10px'><span class='eyebrow'>{no}</span><br><b>{title}</b><p class='muted' style='margin:4px 0 0'>{desc}</p></div>",unsafe_allow_html=True)
        st.info("No clinical diagnosis is generated by this prototype.")

elif page=="Thermal Lab":
    header("Thermal Signal Studio","Explore respiratory temperature modulation and signal-quality controls.")
    x,y=st.columns([.85,1.6])
    with x:
        st.slider("Simulated breathing rate (breaths/min)",8,35,st.session_state.demo_rate,key="demo_rate")
        st.slider("Thermal noise (%)",0,90,st.session_state.thermal_noise,key="thermal_noise")
        st.slider("ROI occlusion / motion (%)",0,90,st.session_state.occlusion,key="occlusion")
        st.metric("Thermal quality score",f"{qt:.1%}")
    with y:
        f=go.Figure(go.Scatter(x=t,y=thermal,mode="lines",name="Temperature"))
        f.update_layout(title="Synthetic perinasal temperature trace",xaxis_title="Time (s)",yaxis_title="Temperature (°C)",height=400,template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#0b202a")
        st.plotly_chart(f,use_container_width=True)
    st.markdown("**Next integration:** thermal video input → face detection → perinasal ROI tracking → temporal filtering → respiratory-cycle estimation.")
    st.warning("A standard RGB webcam cannot measure temperature. Real thermal analysis requires a thermal infrared camera.")

elif page=="Audio Lab":
    header("Breath Acoustic Studio","Inspect breath-sound patterns and configure the audio signal pipeline.")
    x,y=st.columns([.85,1.6])
    with x:
        st.slider("Audio noise (%)",0,90,st.session_state.audio_noise,key="audio_noise")
        st.metric("Audio quality score",f"{qa:.1%}")
        st.file_uploader("Upload a WAV recording",type=["wav"],help="Upload is enabled for the next audio-processing integration. No clinical interpretation is performed.")
        st.caption("WAV analysis is not connected in this prototype.")
    with y:
        f=go.Figure(go.Scatter(x=t,y=audio,mode="lines",name="Audio envelope"))
        f.update_layout(title="Synthetic breath-acoustic envelope",xaxis_title="Time (s)",yaxis_title="Normalised amplitude",height=400,template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#0b202a")
        st.plotly_chart(f,use_container_width=True)
    st.markdown("**Next integration:** WAV → band-pass filtering → segmentation → MFCC/log-mel features → respiratory sound classifier.")

elif page=="Fusion Engine":
    header("Confidence-Aware Fusion Engine","Explore adaptive weighting and the abstention mechanism.")
    x,y=st.columns(2)
    with x:
        st.metric("Thermal modality weight",f"{wt:.1%}"); st.progress(wt)
        st.metric("Audio modality weight",f"{wa:.1%}"); st.progress(wa)
        st.latex(r"\\alpha_T=\\frac{q_T}{q_T+q_A},\\quad \\alpha_A=\\frac{q_A}{q_T+q_A}")
        st.latex(r"RR_{fused}=\\alpha_T RR_T+\\alpha_A RR_A")
    with y:
        f=go.Figure(go.Pie(labels=["Thermal","Audio"],values=[wt,wa],hole=.62))
        f.update_layout(title="Adaptive modality contribution",height=340,template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(f,use_container_width=True)
        st.metric("Fused demo estimate",f"{fused:.1f} breaths/min")
    if gate=="INCONCLUSIVE":st.error("ABSTENTION: signal quality is too low. The system declines to provide a screening-style output.")
    elif confidence<.60:st.warning("LOW CONFIDENCE: repeat acquisition or inspect signal quality.")
    else:st.success("QUALITY GATE PASSED: prototype quality threshold met.")
    st.caption("The current quality functions are illustrative heuristics, not clinically validated quality estimators.")

elif page=="Screening Report":
    header("Explainable Research Report","Export the current synthetic run with provenance and quality metadata.")
    st.error("NOT FOR CLINICAL USE · This report is not a diagnosis or medical recommendation.")
    label=st.text_input("Experiment label",value="ThermoVox demo run")
    notes=st.text_area("Research notes",placeholder="Describe the simulation settings or observation...")
    report=pd.DataFrame([["Data provenance","Synthetic simulation"],["Thermal quality",f"{qt:.1%}"],["Audio quality",f"{qa:.1%}"],["Thermal RR estimate",f"{rrt:.1f} breaths/min"],["Audio RR estimate",f"{rra:.1f} breaths/min"],["Fused RR estimate",f"{fused:.1f} breaths/min"],["Thermal weight",f"{wt:.1%}"],["Audio weight",f"{wa:.1%}"],["Confidence gate",gate]],columns=["Parameter","Value"])
    st.dataframe(report,use_container_width=True,hide_index=True)
    st.download_button("Download CSV report",report.to_csv(index=False).encode("utf-8"),"thermovox_research_report.csv","text/csv")
    if st.button("Save this experiment"):
        save_experiment(st.session_state.username,label,qt,qa,fused,gate,notes)
        st.success("Experiment saved to your personal library.")

elif page=="Experiment Library":
    header("Experiment Library","Review your saved runs and compare the prototype outputs.")
    c=db(); rows=c.execute("SELECT created_at,label,thermal_quality,audio_quality,fused_rr,gate,notes FROM experiments WHERE username=? ORDER BY id DESC LIMIT 100",(st.session_state.username,)).fetchall(); c.close()
    if rows:
        hist=pd.DataFrame(rows,columns=["Created","Experiment","Thermal Q","Audio Q","Fused RR","Gate","Notes"])
        st.dataframe(hist,use_container_width=True,hide_index=True)
        if len(hist)>1:
            chart=go.Figure()
            chart.add_trace(go.Scatter(x=hist["Created"],y=hist["Fused RR"],mode="lines+markers",name="Fused demo RR"))
            chart.update_layout(title="Saved run trend · synthetic runs only",yaxis_title="Breaths/min",template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(chart,use_container_width=True)
        st.download_button("Export experiment library",hist.to_csv(index=False).encode(),"thermovox_experiment_history.csv","text/csv")
    else:st.info("No saved experiments yet. Create one from the Screening Report tab.")

elif page=="Research Notes":
    header("Research Notes & Methodology","The key technical ideas behind the ThermoVox AI framework.")
    tab1,tab2,tab3=st.tabs(["Thermal branch","Acoustic branch","Fusion & validation"])
    with tab1:
        st.markdown("**Input:** thermal video frames.  \n**ROI:** perinasal region tracked across frames.  \n**Processing:** temperature extraction, motion compensation, detrending and filtering.  \n**Output:** thermal respiratory trace and quality indicators.")
        st.latex(r"T(t)=\\operatorname{median}\\{T_i(t):i\\in ROI\\}")
    with tab2:
        st.markdown("**Input:** synchronised breath audio.  \n**Processing:** resampling, filtering, segmentation and spectro-temporal features.  \n**Features:** MFCC, log-mel energies, spectral centroid, RMS energy and temporal descriptors.")
        st.latex(r"X_{audio}=\\operatorname{LogMel}(x[n])")
    with tab3:
        st.markdown("Estimate a quality score for each modality, normalise the weights, and abstain if both signals are poor or one falls below the minimum reliability threshold.")
        st.latex(r"z=\\alpha_T z_T+\\alpha_A z_A")
        st.markdown("**Evaluation:** respiratory-rate MAE/RMSE; sensitivity, specificity, F1 and AUROC for classification; coverage, selective risk and calibration for confidence-aware behaviour.")
    st.warning("Do not report simulated outputs as measured clinical performance. The thermal and audio modalities need synchronised real-world validation.")

elif page=="Profile & Settings":
    header("Researcher Profile","Your account details and workspace preferences.")
    st.subheader("Account details")
    st.write(f"**Name:** {st.session_state.full_name}  \n**Username:** {st.session_state.username}")
    c=db(); email=c.execute("SELECT email,created_at FROM users WHERE username=?",(st.session_state.username,)).fetchone(); c.close()
    if email:st.write(f"**Email:** {email[0]}  \n**Member since:** {email[1]}")
    st.subheader("Application information")
    st.write("ThermoVox AI · Version 0.2 · Dark research interface · Public self-registration")
    st.subheader("Privacy and security")
    st.warning("This local prototype stores account records and experiment metadata in a local SQLite database. Do not use real patient-identifiable information. Before public deployment, add HTTPS, secure secrets management, rate limiting, account recovery, access controls, audit logging, backups and a security review.")

st.markdown("<hr><p style='color:#8daeb4;font-size:12px'>THERMOVOX AI · v0.2 · Research prototype · Synthetic data mode</p>",unsafe_allow_html=True)
