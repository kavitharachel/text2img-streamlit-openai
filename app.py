# app.py
import streamlit as st
from huggingface_hub import InferenceClient
from io import BytesIO

APP_TITLE = "🎨 Text → Image (Hugging Face API)"
st.set_page_config(page_title=APP_TITLE, page_icon="🎨", layout="wide")
st.title(APP_TITLE)
st.caption("Streamlit + Hugging Face Inference API (no local GPU needed).")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings")
    model = st.selectbox(
        "Choose a model",
        [
            "stabilityai/stable-diffusion-xl-base-1.0",
            "runwayml/stable-diffusion-v1-5"
        ],
        index=0,
    )
    steps = st.slider("Steps", 5, 50, 30)
    guidance = st.slider("Guidance Scale", 1.0, 15.0, 7.5)
    size = st.selectbox("Resolution", ["512x512", "768x768", "1024x1024"], index=0)
    width, height = map(int, size.split("x"))
    n_images = st.slider("Images to generate", 1, 3, 1)

# Prompt input
prompt = st.text_area("Enter your prompt:", "A fantasy castle on a mountain at sunset")
generate = st.button("Generate", type="primary", use_container_width=True)

if generate and prompt:
    try:
        client = InferenceClient(model=model, token=st.secrets["HF_TOKEN"])
    except Exception as e:
        st.error(f"Missing or invalid Hugging Face token: {e}")
        st.stop()

    cols = st.columns(n_images)
    for i in range(n_images):
        with st.spinner(f"Generating image {i+1}/{n_images}…"):
            try:
                img = client.text_to_image(
                    prompt=prompt,
                    num_inference_steps=steps,
                    guidance_scale=guidance,
                    width=width,
                    height=height,
                )
                buf = BytesIO()
                img.save(buf, format="PNG")
                cols[i].image(img, caption=f"{width}x{height}", use_column_width=True)
                cols[i].download_button(
                    "⬇️ Download Image",
                    buf.getvalue(),
                    file_name=f"image_{i+1}.png",
                    mime="image/png",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Error: {e}")
