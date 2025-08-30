# 🎨 Text → Image — Streamlit + OpenAI (DALL·E)

A minimal Streamlit app that generates images with **OpenAI** (model: `gpt-image-1`). Perfect for **GitHub → Streamlit Cloud** deployments.

---

## 🚀 Run locally
```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...   # Windows PowerShell: $env:OPENAI_API_KEY="sk-..."
streamlit run app.py
```

## ☁️ Deploy on Streamlit Community Cloud
1. Push this repo to GitHub.
2. On Streamlit Cloud: **New app** → pick your repo/branch.
3. In **App → Settings → Secrets**, paste:
```toml
OPENAI_API_KEY="sk-..."
```
4. **Deploy** and share your link!

---

## 🧩 Features
- Prompt box, size selector, multi-image generation (1–4)
- Download PNG button
- Uses Streamlit secrets for secure key management

## 🛡️ Safety
Add moderation filters and usage limits for public apps.
