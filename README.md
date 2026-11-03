# ThermoVox AI v0.2 — Dark public-registration prototype

## Included
- Dark teal/navy medical-AI interface
- Public self-registration and sign-in
- SQLite account storage with salted PBKDF2 password hashing
- Overview dashboard with simulated thermal and acoustic traces
- Thermal Lab controls: simulated breathing rate, thermal noise, ROI occlusion/motion
- Audio Lab controls and WAV upload placeholder
- Confidence-aware fusion engine and abstention gate
- Explainable CSV research report
- Per-user experiment library with saved run trend
- Research Notes and methodology tab
- Profile and security notes

## Run locally (Windows / VS Code)
1. Extract the ZIP and open the folder in VS Code.
2. In terminal:
   `py -m venv .venv`
3. Activate:
   `.venv\\Scripts\\Activate.ps1`
4. Install:
   `pip install -r requirements.txt`
5. Start:
   `streamlit run app.py`

The app opens in a browser. Anyone can create an account on the sign-up tab. Database file is created locally as `thermovox_users.db`.

## Research and safety notes
- Current signals and respiratory-rate values are synthetic simulations.
- WAV upload is a UI placeholder; no audio inference is connected yet.
- A normal RGB webcam cannot measure temperature; real thermal processing needs a thermal infrared camera.
- This is not a medical device and must not be used for diagnosis or clinical decisions.
- Public registration here means self-registration in the local app. This starter is not hardened for internet exposure. Before public deployment, implement HTTPS, secure secret handling, rate limits, account recovery, audit logging, access control, privacy controls, backups and a security review. Do not enter patient-identifiable information.
