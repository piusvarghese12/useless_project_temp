import streamlit as st
import torch
from PIL import Image, ImageDraw
import io
import time
from model import ProductPredictor


# Page configuration
st.set_page_config(
    page_title="Multimodal Product Image-Text Verifier",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design aesthetics
st.markdown("""
<style>
    /* Dark glassmorphism container styling */
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
    .prediction-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        margin-bottom: 12px;
        transition: transform 0.2s ease;
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
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def load_predictor():
    """Load and cache the ProductPredictor model."""
    return ProductPredictor()


def generate_sample_image(category: str) -> Image.Image:
    """Generate sample synthetic images for testing."""
    img = Image.new("RGB", (400, 400), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    if category == "Headphones":
        # Draw headphones illustration
        draw.ellipse([80, 80, 320, 320], outline="#38bdf8", width=12)
        draw.rectangle([60, 180, 110, 270], fill="#0284c7")
        draw.rectangle([290, 180, 340, 270], fill="#0284c7")
    elif category == "Running Shoes":
        # Draw shoe illustration
        draw.polygon([(80, 280), (320, 280), (300, 200), (220, 200), (160, 150), (80, 240)], fill="#f43f5e")
        draw.rectangle([80, 280, 320, 300], fill="#ffffff")
    elif category == "Coffee Mug":
        # Draw mug illustration
        draw.rectangle([120, 120, 280, 320], fill="#f59e0b", outline="#ffffff", width=4)
        draw.ellipse([270, 160, 330, 260], outline="#f59e0b", width=10)
    else:
        # Default camera/watch
        draw.ellipse([100, 100, 300, 300], fill="#8b5cf6")
        draw.ellipse([150, 150, 250, 250], fill="#4c1d95")

    return img


def main():
    # Header Banner
    st.markdown("""
    <div class="main-header">
        <h1>🛍️ Multimodal Product Image-Text Verification</h1>
        <p>Two-Tower Contrastive Neural Network Architecture (ResNet-50 Vision Encoder + DistilBERT Text Encoder)</p>
    </div>
    """, unsafe_allow_html=True)

    # Load Model with Spinner
    with st.spinner("Initializing Two-Tower Verification Model (ResNet-50 + DistilBERT)..."):
        predictor = load_predictor()

    # Sidebar Controls
    st.sidebar.header("⚙️ Configuration & Inputs")

    temperature = st.sidebar.slider(
        "Temperature Scaling Factor",
        min_value=1.0,
        max_value=30.0,
        value=10.0,
        step=0.5,
        help="Higher temperature sharpens softmax probability distribution across candidate titles."
    )

    image_source = st.sidebar.radio(
        "Select Image Input Source:",
        ["Sample Preset Products", "Upload Custom Image"]
    )

    image = None
    if image_source == "Sample Preset Products":
        sample_choice = st.sidebar.selectbox(
            "Choose Preset Sample Product:",
            ["Headphones", "Running Shoes", "Coffee Mug", "Smartwatch"]
        )
        image = generate_sample_image(sample_choice)
        default_titles = {
            "Headphones": [
                "Wireless Noise-Canceling Over-Ear Bluetooth Headphones",
                "Men's Lightweight Breathable Running Shoes",
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
    else:
        uploaded_file = st.sidebar.file_uploader(
            "Upload Product Image",
            type=["jpg", "jpeg", "png"]
        )
        if uploaded_file is not None:
            image = Image.open(uploaded_file).convert("RGB")
        else:
            image = generate_sample_image("Headphones")
        preset_candidate_list = [
            "Wireless Noise-Canceling Over-Ear Bluetooth Headphones",
            "Men's Lightweight Breathable Athletic Running Shoes",
            "Ceramic Thermal Coffee Mug 16 oz",
            "Ergonomic Mesh Swivel Office Chair"
        ]

    # Two-Column Layout
    col1, col2 = st.columns([1, 1.2], gap="large")

    with col1:
        st.subheader("🖼️ Target Product Image")
        if image is not None:
            st.image(image, use_container_width=True, caption=f"Product Image ({image.size[0]}x{image.size[1]} px)")
        
        st.info("💡 **How it works:** The ResNet-50 vision tower extracts spatial image features into a 256-dim L2-normalized embedding.")

    with col2:
        st.subheader("🏷️ Candidate Product Titles")
        st.caption("Enter one candidate product title per line:")

        titles_text = st.text_area(
            "Candidate Titles",
            value="\n".join(preset_candidate_list),
            height=160,
            help="Enter product titles to verify against the image."
        )

        candidate_titles = [line.strip() for line in titles_text.split("\n") if line.strip()]

        verify_btn = st.button("⚡ Verify Product Match", type="primary", use_container_width=True)

    if verify_btn or image is not None:
        if not candidate_titles:
            st.warning("Please enter at least one candidate product title.")
            return

        with st.spinner("Computing Two-Tower Cosine Similarities & Softmax..."):
            start_time = time.time()
            output = predictor.predict(image, candidate_titles, temperature=temperature)
            inference_ms = (time.time() - start_time) * 1000

        st.markdown("---")
        st.subheader("📊 Verification Predictions & Scores")
        st.caption(f"Inference latency: {inference_ms:.1f} ms | Device: `{predictor.device}`")

        best_match = output["predictions"][0]

        # Top Match Banner
        st.markdown(f"""
        <div class="top-match-card">
            <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">Best Predicted Match</div>
            <h2 style="margin: 8px 0; color: #ffffff;">{best_match['title']}</h2>
            <div style="margin-top: 12px;">
                <span class="metric-badge">Match Probability: {best_match['probability']*100:.2f}%</span>
                <span class="metric-badge" style="margin-left: 8px;">Cosine Similarity: {best_match['similarity_score']:.4f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Ranked Candidates Breakdown
        st.write("### Candidate Titles Breakdown")
        for rank, pred in enumerate(output["predictions"], start=1):
            prob_pct = pred["probability"] * 100
            sim_score = pred["similarity_score"]

            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"**#{rank}. {pred['title']}**")
                st.progress(min(max(pred["probability"], 0.0), 1.0))
            with col_b:
                st.metric(
                    label="Probability",
                    value=f"{prob_pct:.1f}%",
                    delta=f"Sim: {sim_score:.4f}"
                )
            st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
