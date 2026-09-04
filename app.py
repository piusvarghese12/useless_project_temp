import streamlit as st
import torch
from PIL import Image, ImageDraw
import io
import time
import os
from model import ProductPredictor


# Page Configuration
st.set_page_config(
    page_title="AI vs User Conflict - OBJECT iDENTIFiER",
    page_icon="🕶️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS matching playful aesthetic with conflict badges
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
        font-size: 40px;
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

    /* Conflict vs Agreement Card Styling */
    .conflict-card {
        background-color: #fef2f2;
        border: 3px solid #ef4444;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        margin-top: 15px;
        box-shadow: 4px 4px 0px #ef4444;
    }

    .agreement-card {
        background-color: #f0fdf4;
        border: 3px solid #22c55e;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        margin-top: 15px;
        box-shadow: 4px 4px 0px #22c55e;
    }

    .verdict-header {
        font-family: 'Fredoka One', cursive;
        font-size: 26px;
        margin: 5px 0;
    }

    .footer-banner {
        background: #ffe4e6;
        border: 3px solid #2b2b2b;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        font-weight: 700;
        font-size: 15px;
        margin-top: 30px;
        box-shadow: 4px 4px 0px #2b2b2b;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def load_predictor():
    return ProductPredictor()


def add_pixel_sunglasses(image: Image.Image) -> Image.Image:
    """Draw funny pixel sunglasses on the result image."""
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
            <span style="font-size: 45px;">🍞</span>
            <div class="toast-speech">ARE YOU GASLIGHTING THE AI?</div>
        </div>
        """, unsafe_allow_html=True)

    with col_h2:
        st.markdown("""
        <div class="title-banner">
            <h1 class="title-main">OBJECT iDENTIFiER: AI vs USER CONFLICT</h1>
            <div class="title-sub">Upload an image. Type your claim. Watch the AI fight back! ⚔️</div>
        </div>
        """, unsafe_allow_html=True)

    with col_h3:
        st.markdown("""
        <div style="text-align: center;">
            <div class="warning-box">⚠️ <b>WARNING:</b> AI has strong opinions.</div>
            <div style="font-size: 35px; margin-top: 5px;">🦆</div>
            <div style="font-size: 11px; font-weight: bold;">IT IDENTIFIES & FIGHTS BACK.</div>
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
            img_name = "cat_looking_cute.jpg"

        st.image(image, caption=f"📸 {img_name}  ✅", use_container_width=True)
        st.caption("Go on, upload something. Let's see who wins.")

    # STEP 2: TELL US WHAT YOU CLAIM IT IS
    with col_step2:
        st.markdown("""
        <div class="step-badge step2-badge">2 YOUR CLAIM (HUMAN INPUT)</div>
        <p><b>Look at the image and type what YOU claim it is.</b><br>Will the AI agree or fight you? 🤨</p>
        """, unsafe_allow_html=True)

        user_input = st.text_input(
            "WHAT DO YOU CLAIM THIS IS?",
            value="banana",
            placeholder="Type your claim (e.g., cat, banana, your crush)..."
        )
        st.caption("Example: cat, dog, chair, banana, your crush 🤪")

        # Preset AI knowledge base categories to evaluate against user claim
        ai_known_categories = [
            "cute cat",
            "wireless noise-canceling headphones",
            "running athletic shoes",
            "coffee mug",
            "office desk chair",
            "banana fruit"
        ]

        user_label = user_input.strip() if user_input.strip() else "cat"

        # Combine User claim + AI categories for Two-Tower evaluation
        all_candidates = list(set([user_label] + ai_known_categories))

        identify_btn = st.button("⚔️ CHALLENGE THE AI MODEL", type="primary", use_container_width=True)

        st.markdown("""
        <br>
        <div style="background: #e0f2fe; border: 2px solid #0284c7; border-radius: 12px; padding: 12px; font-size: 13px;">
            🧠 <b>Two-Tower Battle:</b> ResNet-50 Vision Encoder extracts visual features while DistilBERT processes your claim to detect agreement or conflict!
        </div>
        """, unsafe_allow_html=True)

    # STEP 3: THE VERDICT & CONFLICT (AI vs USER)
    with col_step3:
        st.markdown("""
        <div class="step-badge step3-badge">3 THE AI VERDICT & CONFLICT</div>
        """, unsafe_allow_html=True)

        # Run PyTorch Model Inference
        output = predictor.predict(image, all_candidates, temperature=10.0)
        predictions = output["predictions"]

        # Find score for User's claim vs AI's top visual match
        user_pred = next((p for p in predictions if p["title"].lower() == user_label.lower()), predictions[0])
        ai_top_pred = predictions[0]

        is_conflict = (ai_top_pred["title"].lower() != user_label.lower()) and (user_pred["probability"] < 0.40)

        cool_img = add_pixel_sunglasses(image)

        if is_conflict:
            st.markdown(f"""
            <div class="conflict-card">
                <div style="color: #dc2626; font-weight: 800; font-size: 14px; text-transform: uppercase;">🚨 AI DISAGREEMENT DETECTED!</div>
                <div class="verdict-header" style="color: #b91c1c;">AI Refuses Your Claim!</div>
                <hr style="border: 1px solid #fca5a5; margin: 10px 0;">
                <div style="font-size: 14px; text-align: left;">
                    👤 <b>Your Claim:</b> <code>{user_label}</code> (Confidence: {user_pred['probability']*100:.1f}%)<br>
                    🤖 <b>AI Visual Verdict:</b> <code>{ai_top_pred['title']}</code> (Confidence: <b>{ai_top_pred['probability']*100:.1f}%</b>)
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.image(cool_img, use_container_width=True)
            st.error(f"🥊 **AI Conflict:** You typed '{user_label}', but ResNet-50 + DistilBERT is {ai_top_pred['probability']*100:.1f}% sure this is '{ai_top_pred['title']}'! Who is lying?!")
        else:
            st.markdown(f"""
            <div class="agreement-card">
                <div style="color: #16a34a; font-weight: 800; font-size: 14px; text-transform: uppercase;">🤝 AI & HUMAN IN AGREEMENT!</div>
                <div class="verdict-header" style="color: #15803d;">It is indeed: {user_label}!</div>
                <hr style="border: 1px solid #86efac; margin: 10px 0;">
                <div style="font-size: 14px; text-align: center;">
                    🤖 <b>AI Alignment:</b> {ai_top_pred['probability']*100:.1f}% confidence match!
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.image(cool_img, use_container_width=True)
            st.success(f"🎉 **AI Agreement:** The model agrees with your claim '{user_label}' with {ai_top_pred['probability']*100:.1f}% confidence!")

        # Detailed breakdown
        with st.expander("📊 View AI vs User Embedding Scores"):
            for p in predictions:
                st.write(f"**{p['title']}**: {p['probability']*100:.1f}% (Cosine Sim: `{p['similarity_score']:.4f}`)")

    # Bottom Footer Banner
    st.markdown("""
    <div class="footer-banner">
        💡 <b>AI vs User Conflict Mode:</b> Try uploading an image of a cat and typing "banana" or "your crush" to trigger AI rebellion!<br>
        <span style="font-size: 14px; color: #64748b;">What a time to be alive. 😎 &nbsp;|&nbsp; ⚔️ AI VS HUMAN &nbsp;|&nbsp; 🤖 POWERED BY PYTORCH TWO-TOWER MODEL</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
