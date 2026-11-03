# ThermoVox AI v0.4

## Run locally (Windows)
```cmd
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py -m streamlit run app.py
```
Open http://localhost:8501

## Deploy update
Replace `app.py`, `requirements.txt`, and `README.md` in your GitHub repository. Streamlit Community Cloud will redeploy.

## Enable the AI research assistant
In Streamlit Community Cloud, open your app → Settings → Secrets and add:
```toml
OPENAI_API_KEY = "your-api-key-here"
```
Save and reboot the app. An OpenAI API key is required for AI-generated answers and API usage may incur charges. Never commit the key to GitHub or paste it into the app's chat.

Without a key, the Research Assistant provides a limited guided explanation mode.

## Palette
- Deep Azure: #0B1F33
- Light Azure: #2563EB
- Soft Teal: #20BFC0
- Icy Cyan: #DDF6F7
- Icy Azure: #F8FBFC

Typography: Source Sans 3 for interface text, Manrope for headings.

## Limitations
All signals, charts, quality scores and respiratory estimates are synthetic demonstrations. WAV upload is not yet processed. The ROI graphic is a schematic, not a thermal image. A thermal infrared camera is required for real temperature measurements. The app is not a medical device. SQLite is local prototype storage and should be replaced with a managed cloud database for reliable public multi-user accounts and experiment history.
