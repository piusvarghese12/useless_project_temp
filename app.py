import streamlit as st
import torch
from PIL import Image, ImageDraw
import io
import time
import os
from model import ProductPredictor


# Page Configuration
st.set_page_config(
    page_title=" OBJECT iDENTIFiER",
    page_icon="🕶️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS matching meme / playful light cream aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Quicksand:wght@500;700&display=swap');

    .stApp {
        background-color: #fcf9f2;
        font-family: 'Quicksand', sans-serif;
        color: #2b2b2b;
    }

    .toast-speech {
        background: #ffffff;
        border: 2px solid #2b2b2b;
        border-radius: 15px;
        padding: 8px 14px;
        font-weight: 700;
        font-size: 13px;
        box-shadow: 3px 3px 0px #2b2b2b;
    }

    .title-banner {
        text-align: center;
    }

    .title-main {
        font-family: 'Fredoka One', cursive;
        font-size: 42px;
        color: #1e1e24;
        margin: 0;
        letter-spacing: 1px;
    }

    .title-sub {
        background-color: #ffb5c5;
        border: 2px solid #2b2b2b;
        border-radius: 20px;
        padding: 6px 20px;
        display: inline-block;
        font-weight: 700;
        font-size: 14px;
        margin-top: 8px;
        box-shadow: 2px 2px 0px #2b2b2b;
    }

    .warning-box {
        background-color: #ffeb3b;
        border: 2px solid #2b2b2b;
        border-radius: 12px;
        padding: 10px 14px;
        font-weight: 700;
        font-size: 13px;
        box-shadow: 3px 3px 0px #2b2b2b;
    }

    .step-badge {
        display: inline-block;
        border-radius: 20px;
        padding: 4px 14px;
        font-weight: 800;
        color: #ffffff;
        font-size: 15px;
        margin-bottom: 15px;
    }

    .step1-badge { background-color: #7c3aed; }
    .step2-badge { background-color: #2563eb; }
    .step3-badge { background-color: #16a34a; }

    .result-box {
        background-color: #dcfce7;
        border: 2px solid #16a34a;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin-top: 15px;
    }

    .result-text {
        font-family: 'Fredoka One', cursive;
        font-size: 48px;
        color: #15803d;
        margin: 10px 0;
    }

    .footer-banner {
        background: #ffe4e6;
        border: 3px solid #2b2b2b;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        font-weight: 700;
        font-size: 16px;
        margin-top: 30px;
        box-shadow: 4px 4px 0px #2b2b2b;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def load_predictor():
    return ProductPredictor()


def add_pixel_sunglasses(image: Image.Image) -> Image.Image:
    """Draw cool pixel sunglasses on the image."""
    img = image.copy().convert("RGBA")
    draw = ImageDraw.Draw(img)
    w, h = img.size

    gw = int(w * 0.5)
    gh = int(h * 0.12)
    gx = int((w - gw) / 2)
    gy = int(h * 0.35)

    draw.rectangle([gx, gy, gx + gw, gy + gh], fill=(0, 0, 0, 240))
    glint_w = max(2, int(gw * 0.1))
    draw.rectangle([gx + 4, gy + 4, gx + 4 + glint_w, gy + 4 + glint_w], fill=(255, 255, 255, 255))
    draw.rectangle([gx + int(gw / 2) + 4, gy + 4, gx + int(gw / 2) + 4 + glint_w, gy + 4 + glint_w], fill=(255, 255, 255, 255))

    return img


def generate_default_cat() -> Image.Image:
    """Default cute cat image placeholder."""
    img = Image.new("RGB", (350, 350), color=(230, 200, 170))
    draw = ImageDraw.Draw(img)
    draw.ellipse([70, 70, 280, 280], fill=(210, 140, 80))
    draw.polygon([(70, 100), (110, 30), (140, 90)], fill=(210, 140, 80))
    draw.polygon([(210, 90), (240, 30), (280, 100)], fill=(210, 140, 80))
    draw.ellipse([110, 130, 140, 160], fill=(0, 0, 0))
    draw.ellipse([210, 130, 240, 160], fill=(0, 0, 0))
    draw.polygon([(165, 175), (185, 175), (175, 190)], fill=(230, 100, 100))
    return img


def main():
    # Header Section
    col_h1, col_h2, col_h3 = st.columns([1, 2.5, 1])

    with col_h1:
        st.markdown("""
        <div style="text-align: center;">
            <span style="font-size: 50px;">🍞</span>
            <div class="toast-speech">WHY ARE YOU EVEN USING THIS?</div>
        </div>
        """, unsafe_allow_html=True)

    with col_h2:
        st.markdown("""
        <div class="title-banner">
            <h1 class="title-main"> OBJECT iDENTIFiER</h1>
            <div class="title-sub">Upload an image. Tell us what it is. Get the same thing back. Mind = Blown 🤯</div>
        </div>
        """, unsafe_allow_html=True)

    with col_h3:
        st.markdown("""
        <div style="text-align: center;">
            <div class="warning-box">⚠️ <b>WARNING:</b> This project serves purpose.</div>
            <div style="font-size: 40px; margin-top: 5px;">🦆</div>
            <div style="font-size: 11px; font-weight: bold;">IT IDENTIFIES. THAT'S IT.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    predictor = load_predictor()

    col_step1, col_step2, col_step3 = st.columns(3, gap="medium")

    # STEP 1: UPLOAD IMAGE
    with col_step1:
        st.markdown("""
        <div class="step-badge step1-badge">1 UPLOAD IMAGE</div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Drag & drop your image here or click to upload",
            type=["jpg", "jpeg", "png"]
        )

        if uploaded_file is not None:
            image = Image.open(uploaded_file).convert("RGB")
            img_name = uploaded_file.name
        else:
            image = generate_default_cat()
            img_name = "looking_cute.jpg"

        st.image(image, caption=f"📸 {img_name}  ✅", use_container_width=True)
        st.caption("Go on, do it. I dare you.")

    # STEP 2: TELL US WHAT IT IS
    with col_step2:
        st.markdown("""
        <div class="step-badge step2-badge">2 TELL US WHAT IT IS</div>
        <p><b>Look at the image and type the object name.</b><br>Be honest. We won't judge. 🤨</p>
        """, unsafe_allow_html=True)

        user_input = st.text_input(
            "WHAT IS THIS?",
            value="",
            placeholder="Type object name here..."
        )
        st.caption("Example: cat, dog, chair, banana, your crush 🤪")

        candidates = [
            user_input.strip() if user_input.strip() else "cat",
            "completely wrong object",
            "a random banana",
            "something else entirely"
        ]

        identify_btn = st.button("✨ IDENTIFY THIS OBJECT", type="primary", use_container_width=True)

        st.markdown("""
        <br>
        <div style="background: #e0f2fe; border: 2px solid #0284c7; border-radius: 12px; padding: 12px; font-size: 13px;">
            🧠 <b>Fun Fact:</b> This AI doesn't use AI (except under the hood it actually runs ResNet-50 + DistilBERT cosine embeddings!).
        </div>
        """, unsafe_allow_html=True)

    # STEP 3: THE RESULT (SHOCKER!)
    with col_step3:
        st.markdown("""
        <div class="step-badge step3-badge">3 THE RESULT (SHOCKER!)</div>
        <p><b>Drumroll please... 🥁</b></p>
        """, unsafe_allow_html=True)

        output = predictor.predict(image, candidates, temperature=10.0)
        best_title = user_input.strip() if user_input.strip() else output["best_match"]

        cool_img = add_pixel_sunglasses(image)

        st.markdown(f"""
        <div class="result-box">
            <div style="font-weight: 700; font-size: 18px; color: #166534;">It is...</div>
            <div class="result-text">{best_title}</div>
        </div>
        """, unsafe_allow_html=True)

        st.image(cool_img, use_container_width=True)

        st.markdown("""
        <div style="background: #f0fdf4; border: 2px solid #22c55e; border-radius: 12px; padding: 10px; text-align: center; margin-top: 10px; font-size: 13px;">
            🎉 <b>Wow. Groundbreaking.</b><br>Truly, we are in the future.
        </div>
        """, unsafe_allow_html=True)

    # Bottom Footer Banner
    st.markdown("""
    <div class="footer-banner">
        💡 <b>Congratulations!</b> You've used a completely pointless project that does exactly what you tell it to.<br>
        <span style="font-size: 14px; color: #64748b;">What a time to be alive. 😎 &nbsp;|&nbsp; 👾 SO USELESS LOL &nbsp;|&nbsp; 🍩 I EXIST FOR NO REASON</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
