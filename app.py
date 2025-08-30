# app.py
import base64
from io import BytesIO

import streamlit as st
from PIL import Image
from openai import OpenAI

st.set_page_config(page_title="Text → Image (OpenAI)", page_icon="🎨", layout="wide")
st.title("🎨 Text → Image Generator")
st.caption("Streamlit + OpenAI (DALL·E) — deployable on Streamlit Cloud")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Settings")
    size = st.sidebar.selectbox(
    "Image size",
    ["1024x1024", "1024x1536", "1536x1024", "auto"],
    index=0)
    n_images = st.slider("Images to generate", 1, 4, 1)

prompt = st.text_area("Prompt", "A fantasy castle on a mountain at sunset, watercolor, cinematic lighting", height=100)
gen = st.button("Generate", type="primary", use_container_width=True, disabled=not prompt)

def get_client() -> OpenAI:
    # Prefer Streamlit secrets; fallback to env var for local runs
    api_key = None
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", None)  # type: ignore[attr-defined]
    except Exception:
        api_key = None
    if not api_key:
        import os
        api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OpenAI API key. Set OPENAI_API_KEY in Streamlit secrets or as an environment variable.")
    return OpenAI(api_key=api_key)

if gen:
    try:
        client = get_client()
    except Exception as e:
        st.error(str(e))
        st.stop()

    cols = st.columns(n_images)
    for i in range(n_images):
        with st.spinner(f"Generating image {i+1}/{n_images}…"):
            try:
                result = client.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    size=size,
                )
                img_b64 = result.data[0].b64_json
                img_bytes = base64.b64decode(img_b64)
                image = Image.open(BytesIO(img_bytes)).convert("RGBA")
            except Exception as e:
                st.error(f"Generation error: {e}")
                st.stop()

        cols[i].image(image, caption=size, use_column_width=True)
        cols[i].download_button(
            "⬇️ Download PNG",
            data=img_bytes,
            file_name="text2image_openai.png",
            mime="image/png",
            use_container_width=True,
        )

with st.expander("ℹ️ Notes"):
    st.markdown(
        "- Requires an **OpenAI API key** set in Streamlit secrets (recommended) or as an environment variable locally.\n"
        "- Smaller sizes (256/512) are faster and cheaper.\n"
        "- For production, consider adding prompt moderation and usage logging."
    )
