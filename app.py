# app.py
# Streamlit + OpenAI (DALL·E / gpt-image-1)
# - Supports sizes: 1024x1024, 1024x1536, 1536x1024, auto
# - Reads OPENAI_API_KEY (required) and OPENAI_ORG (optional) from:
#   1) Streamlit secrets, or 2) environment variables
# - Deployable on Streamlit Community Cloud

import os
import base64
from io import BytesIO

import streamlit as st
from PIL import Image
from openai import OpenAI

APP_TITLE = "🎨 Text → Image (OpenAI gpt-image-1)"

# ---- Page config ----
st.set_page_config(page_title="Text → Image", page_icon="🎨", layout="wide")
st.title(APP_TITLE)
st.caption("Streamlit + OpenAI Images API. Add your OpenAI key in Settings → Secrets.")

# ---- Helpers ----
ALLOWED_SIZES = {"1024x1024", "1024x1536", "1536x1024", "auto"}

def get_secret(name: str) -> str | None:
    """Read from Streamlit secrets first, else env var."""
    try:
        val = st.secrets.get(name)  # type: ignore[attr-defined]
    except Exception:
        val = None
    return val or os.environ.get(name)

def get_client() -> OpenAI:
    api_key = get_secret("OPENAI_API_KEY")
    org = get_secret("OPENAI_ORG")  # optional
    if not api_key:
        raise RuntimeError(
            "Missing OpenAI API key. Set OPENAI_API_KEY in Streamlit Secrets "
            "(⋮ → Settings → Secrets) or as an environment variable."
        )
    return OpenAI(api_key=api_key, organization=org) if org else OpenAI(api_key=api_key)

def decode_image_to_pil(b64: str) -> Image.Image:
    img_bytes = base64.b64decode(b64)
    return Image.open(BytesIO(img_bytes)).convert("RGBA"), img_bytes

# ---- Sidebar ----
with st.sidebar:
    st.header("⚙️ Settings")
    size = st.selectbox(
        "Image size",
        options=["1024x1024", "1024x1536", "1536x1024", "auto"],
        index=0,
        help="Supported sizes for gpt-image-1. 'auto' lets the API pick."
    )
    n_images = st.slider("Images to generate", min_value=1, max_value=4, value=1)
    st.markdown("---")
    st.subheader("🔐 Secrets needed")
    st.code('OPENAI_API_KEY = "sk-..."\n# (Optional) OPENAI_ORG = "org_..."', language="toml")
    st.caption("Add in Streamlit: ⋮ → Settings → Secrets")

# ---- Prompt UI ----
prompt = st.text_area(
    "Prompt",
    placeholder="A fantasy castle on a mountain at sunset, watercolor, cinematic lighting",
    height=100,
)
generate = st.button("Generate", type="primary", use_container_width=True, disabled=not prompt)

# ---- Main action ----
if generate and prompt:
    # Guard against invalid sizes just in case
    if size not in ALLOWED_SIZES:
        st.warning("Invalid size selected; defaulting to 1024x1024.")
        size = "1024x1024"

    # Create columns for multiple images
    cols = st.columns(n_images)

    # Get client (and fail fast if secrets missing)
    try:
        client = get_client()
    except Exception as e:
        st.error(str(e))
        st.stop()

    for i in range(n_images):
        with cols[i]:
            with st.spinner(f"Generating image {i+1}/{n_images}…"):
                try:
                    # OpenAI Images API
                    result = client.images.generate(
                        model="gpt-image-1",
                        prompt=prompt,
                        size=size,  # must be one of ALLOWED_SIZES
                    )
                    b64 = result.data[0].b64_json
                    image, img_bytes = decode_image_to_pil(b64)
                except Exception as e:
                    # Show helpful guidance for common errors
                    msg = str(e)
                    if "organization must be verified" in msg.lower():
                        st.error(
                            "OpenAI error: This key's organization must be verified for `gpt-image-1`.\n"
                            "• Try a personal API key, or\n"
                            "• Verify your org in OpenAI dashboard (Settings → Organization → Verify), then retry."
                        )
                    elif "invalid value" in msg.lower() and "size" in msg.lower():
                        st.error(
                            "OpenAI error: Unsupported size. Use one of "
                            "`1024x1024`, `1024x1536`, `1536x1024`, or `auto`."
                        )
                    else:
                        st.error(f"Generation error: {e}")
                    st.stop()

            # Show and allow download
            st.image(image, caption=size, use_column_width=True)
            st.download_button(
                "⬇️ Download PNG",
                data=img_bytes,
                file_name=f"image_{i+1}.png",
                mime="image/png",
                use_container_width=True,
            )

# ---- Tips ----
with st.expander("ℹ️ Tips & Notes"):
    st.markdown(
        "- Use descriptive style cues: *watercolor, studio photo, cinematic lighting, isometric, 8k render*.\n"
        "- Smaller *concepts* often work better than long paragraphs—be specific.\n"
        "- If you belong to multiple OpenAI orgs, set `OPENAI_ORG` in Secrets to target the verified one."
    )
