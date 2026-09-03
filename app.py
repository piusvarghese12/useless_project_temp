import streamlit as st
import torch
from PIL import Image, ImageDraw
import io
import time
import json
import os
from datetime import datetime
import pandas as pd
from model import ProductPredictor


# Page configuration
st.set_page_config(
    page_title="Multimodal Product Verification & Live Tracking System",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design aesthetics & live tracking gallery
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #334155;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    .main-header h1 {
        color: #f8fafc;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
        color: #94a3b8;
        margin-top: 8px;
        margin-bottom: 0;
    }
    .top-match-card {
        background: linear-gradient(135deg, #065f46 0%, #047857 100%);
        border-radius: 14px;
        padding: 24px;
        border: 1px solid #10b981;
        color: #ecfdf5;
        margin-bottom: 24px;
        box-shadow: 0 10px 20px -5px rgba(16, 185, 129, 0.3);
    }
    .metric-badge {
        background: rgba(255, 255, 255, 0.15);
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
        display: inline-block;
    }
    .history-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #334155;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

TRACKING_DIR = "tracked_products"
HISTORY_FILE = os.path.join(TRACKING_DIR, "history.json")


def init_tracking_system():
    """Ensure directory and history log exist."""
    os.makedirs(TRACKING_DIR, exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)


def load_history() -> list:
    """Load tracked product history."""
    init_tracking_system()
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_to_history(image: Image.Image, image_name: str, prediction_result: dict):
    """Save verified product image and prediction metadata to tracking store."""
    init_tracking_system()
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    saved_filename = f"product_{timestamp_str}.png"
    saved_path = os.path.join(TRACKING_DIR, saved_filename)

    # Save thumbnail image to disk
    image.convert("RGB").save(saved_path, "PNG")

    record = {
        "id": timestamp_str,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "original_filename": image_name,
        "image_path": saved_path,
        "best_match": prediction_result["best_match"],
        "probability": prediction_result["best_match_probability"],
        "predictions": prediction_result["predictions"]
    }

    history = load_history()
    history.insert(0, record)  # Newest first

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


@st.cache_resource(show_spinner=False)
def load_predictor():
    """Load and cache ProductPredictor."""
    return ProductPredictor()


def generate_sample_image(category: str) -> Image.Image:
    """Generate sample synthetic product image."""
    img = Image.new("RGB", (400, 400), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    if category == "Headphones":
        draw.ellipse([80, 80, 320, 320], outline="#38bdf8", width=12)
        draw.rectangle([60, 180, 110, 270], fill="#0284c7")
        draw.rectangle([290, 180, 340, 270], fill="#0284c7")
    elif category == "Running Shoes":
        draw.polygon([(80, 280), (320, 280), (300, 200), (220, 200), (160, 150), (80, 240)], fill="#f43f5e")
        draw.rectangle([80, 280, 320, 300], fill="#ffffff")
    elif category == "Coffee Mug":
        draw.rectangle([120, 120, 280, 320], fill="#f59e0b", outline="#ffffff", width=4)
        draw.ellipse([270, 160, 330, 260], outline="#f59e0b", width=10)
    else:
        draw.ellipse([100, 100, 300, 300], fill="#8b5cf6")
        draw.ellipse([150, 150, 250, 250], fill="#4c1d95")

    return img


def main():
    # Header Banner
    st.markdown("""
    <div class="main-header">
        <h1>🛍️ Multimodal Product Image-Text Verification & Live Tracking System</h1>
        <p>Live uploaded product verification system with real-time tracking, history audit, and ResNet-50 + DistilBERT predictions</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Initializing Two-Tower Verification Model (ResNet-50 + DistilBERT)..."):
        predictor = load_predictor()

    # Create Navigation Tabs
    tab_verify, tab_history = st.tabs(["🔍 Verify New Product Image", "📦 Live Tracked Products History"])

    # Sidebar Controls
    st.sidebar.header("⚙️ Configuration & Controls")

    temperature = st.sidebar.slider(
        "Temperature Scaling Factor",
        min_value=1.0,
        max_value=30.0,
        value=10.0,
        step=0.5,
        help="Higher temperature sharpens softmax probability distribution across candidate titles."
    )

    # TAB 1: VERIFY NEW PRODUCT IMAGE
    with tab_verify:
        st.subheader("Upload Product Image for Verification")

        image_source = st.radio(
            "Select Image Input Mode:",
            ["Upload Custom Image File", "Use Sample Product Preset"],
            horizontal=True
        )

        image = None
        image_name = "sample_product.png"

        if image_source == "Upload Custom Image File":
            uploaded_file = st.file_uploader(
                "Upload a Product Image (.jpg, .jpeg, .png):",
                type=["jpg", "jpeg", "png"],
                key="uploader"
            )
            if uploaded_file is not None:
                image = Image.open(uploaded_file).convert("RGB")
                image_name = uploaded_file.name
                st.success(f"Image uploaded successfully: `{image_name}` ({image.size[0]}x{image.size[1]} px)")
            else:
                st.info("👆 Please upload an image file above to begin live verification and tracking.")
            preset_candidate_list = [
                "Wireless Noise-Canceling Over-Ear Bluetooth Headphones",
                "Men's Lightweight Breathable Athletic Running Shoes",
                "Ceramic Thermal Coffee Mug 16 oz with Lid",
                "Ergonomic Mesh Swivel Office Chair"
            ]
        else:
            sample_choice = st.selectbox(
                "Select Preset Product Sample:",
                ["Headphones", "Running Shoes", "Coffee Mug", "Smartwatch"]
            )
            image = generate_sample_image(sample_choice)
            image_name = f"sample_{sample_choice.lower().replace(' ', '_')}.png"
            default_titles = {
                "Headphones": [
                    "Wireless Noise-Canceling Over-Ear Bluetooth Headphones",
                    "Men's Lightweight Breathable Athletic Running Shoes",
                    "Ceramic Thermal Coffee Mug 16 oz",
                    "Ergonomic Mesh Swivel Office Chair"
                ],
                "Running Shoes": [
                    "Men's Lightweight Breathable Athletic Running Shoes",
                    "Wireless Noise-Canceling Over-Ear Bluetooth Headphones",
                    "Stainless Steel Thermal Travel Mug 16 oz",
                    "Waterproof Fitness Smartwatch with Heart Rate Monitor"
                ],
                "Coffee Mug": [
                    "Ceramic Thermal Coffee Mug 16 oz with Lid",
                    "Ergonomic Mesh Swivel Office Chair",
                    "Men's Lightweight Breathable Athletic Running Shoes",
                    "Wireless Noise-Canceling Over-Ear Bluetooth Headphones"
                ],
                "Smartwatch": [
                    "Waterproof Fitness Smartwatch with Heart Rate Monitor",
                    "Wireless Noise-Canceling Over-Ear Bluetooth Headphones",
                    "Men's Lightweight Breathable Athletic Running Shoes",
                    "Ceramic Thermal Coffee Mug 16 oz"
                ]
            }
            preset_candidate_list = default_titles[sample_choice]

        col1, col2 = st.columns([1, 1.2], gap="large")

        with col1:
            st.write("**Image Preview:**")
            if image is not None:
                st.image(image, use_container_width=True, caption=image_name)

        with col2:
            st.write("**Candidate Product Titles:**")
            titles_text = st.text_area(
                "Enter product titles to test (one per line):",
                value="\n".join(preset_candidate_list),
                height=160
            )
            candidate_titles = [line.strip() for line in titles_text.split("\n") if line.strip()]

            run_btn = st.button("⚡ Verify & Save to Live Tracking System", type="primary", use_container_width=True)

        if run_btn and image is not None:
            if not candidate_titles:
                st.error("Please enter at least one candidate product title.")
            else:
                with st.spinner("Computing ResNet-50 + DistilBERT Embeddings..."):
                    start_t = time.time()
                    output = predictor.predict(image, candidate_titles, temperature=temperature)
                    latency = (time.time() - start_t) * 1000

                # Save to live tracking system
                save_to_history(image, image_name, output)

                st.success(f" Verification complete in {latency:.1f} ms! Product saved to Live Tracking System.")

                best_match = output["predictions"][0]

                # Top Match Banner
                st.markdown(f"""
                <div class="top-match-card">
                    <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">Best Verified Match</div>
                    <h2 style="margin: 8px 0; color: #ffffff;">{best_match['title']}</h2>
                    <div style="margin-top: 12px;">
                        <span class="metric-badge">Match Probability: {best_match['probability']*100:.2f}%</span>
                        <span class="metric-badge" style="margin-left: 8px;">Cosine Similarity: {best_match['similarity_score']:.4f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.write("### Prediction Confidence Breakdown")
                for rank, pred in enumerate(output["predictions"], start=1):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"**#{rank}. {pred['title']}**")
                        st.progress(min(max(pred["probability"], 0.0), 1.0))
                    with col_b:
                        st.metric("Probability", f"{pred['probability']*100:.1f}%", f"Sim: {pred['similarity_score']:.4f}")

    # TAB 2: LIVE TRACKED PRODUCTS HISTORY
    with tab_history:
        st.subheader("📦 Live Tracked & Verified Product Catalog")
        history = load_history()

        if not history:
            st.info("No products tracked yet. Upload a product image in the 'Verify New Product Image' tab to track it here.")
        else:
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Total Products Tracked", len(history))
            with col_m2:
                avg_prob = sum(item["probability"] for item in history) / len(history)
                st.metric("Average Match Confidence", f"{avg_prob*100:.1f}%")
            with col_m3:
                st.metric("Storage Engine", "Local File/JSON Tracking Store")

            if st.button("🗑️ Clear Tracking History"):
                with open(HISTORY_FILE, "w") as f:
                    json.dump([], f)
                st.rerun()

            st.markdown("---")

            # Table view options
            df_records = []
            for item in history:
                df_records.append({
                    "Timestamp": item["timestamp"],
                    "Image Name": item["original_filename"],
                    "Best Matched Title": item["best_match"],
                    "Confidence Probability": f"{item['probability']*100:.2f}%"
                })
            st.dataframe(pd.DataFrame(df_records), use_container_width=True)

            st.write("### Tracked Product Visual Audit Gallery")
            grid_cols = st.columns(3)

            for idx, item in enumerate(history):
                col = grid_cols[idx % 3]
                with col:
                    st.markdown('<div class="history-card">', unsafe_allow_html=True)
                    if os.path.exists(item["image_path"]):
                        st.image(item["image_path"], use_container_width=True)
                    st.write(f"**Title:** {item['best_match']}")
                    st.caption(f"📅 Verified: {item['timestamp']}")
                    st.markdown(f"**Confidence:** `{item['probability']*100:.2f}%`")
                    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
