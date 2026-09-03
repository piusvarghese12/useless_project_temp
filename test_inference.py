import torch
from PIL import Image, ImageDraw
from model import TwoTowerModel, ProductPredictor


def create_dummy_image() -> Image.Image:
    """Create a synthetic test image."""
    img = Image.new("RGB", (300, 300), color=(73, 109, 137))
    draw = ImageDraw.Draw(img)
    # Draw simple shapes to simulate a product image
    draw.rectangle([50, 50, 250, 250], fill=(255, 255, 255), outline=(0, 0, 0))
    draw.ellipse([100, 100, 200, 200], fill=(200, 50, 50))
    return img


def run_verification():
    print("=" * 60)
    print("Multimodal Product Image-Text Verification Inference Test")
    print("=" * 60)

    # 1. Instantiate Model & Predictor
    print("\n[1] Initializing ProductPredictor (Loading ResNet-50 & DistilBERT)...")
    predictor = ProductPredictor()
    print(f"Device in use: {predictor.device}")

    # 2. Test Architecture Vector Dimensions
    print("\n[2] Testing Architecture & Embedding Dimensions...")
    dummy_img = create_dummy_image()
    img_tensor = predictor.preprocess_image(dummy_img)

    titles = [
        "Wireless Noise-Canceling Bluetooth Over-Ear Headphones",
        "Ergonomic Mesh Office Chair with Lumbar Support",
        "Stainless Steel Thermal Coffee Travel Mug 16 oz",
        "Men's Lightweight Breathable Athletic Running Shoes"
    ]
    text_inputs = predictor.preprocess_texts(titles)

    with torch.no_grad():
        img_embed = predictor.model.vision_encoder(img_tensor)
        text_embeds = predictor.model.text_encoder(text_inputs["input_ids"], text_inputs["attention_mask"])

    print(f"Vision Embedding Shape: {img_embed.shape} (Expected: [1, 256])")
    print(f"Text Embedding Shape:   {text_embeds.shape} (Expected: [{len(titles)}, 256])")

    assert img_embed.shape == (1, 256), f"Unexpected vision embed shape: {img_embed.shape}"
    assert text_embeds.shape == (len(titles), 256), f"Unexpected text embed shape: {text_embeds.shape}"

    # Check L2 Normalization (norm should be ~1.0)
    img_norm = torch.norm(img_embed, dim=-1).item()
    text_norms = torch.norm(text_embeds, dim=-1).tolist()
    print(f"Vision Embedding Norm: {img_norm:.4f} (Expected: ~1.0)")
    print(f"Text Embeddings Norms: {[round(n, 4) for n in text_norms]} (Expected: all ~1.0)")

    # 3. Predict Verification
    print("\n[3] Running Inference Prediction...")
    output = predictor.predict(dummy_img, titles, temperature=10.0)

    print("\nPrediction Results:")
    print("-" * 60)
    for p in output["predictions"]:
        print(f"Title:       {p['title']}")
        print(f"Similarity:  {p['similarity_score']:.4f}")
        print(f"Probability: {p['probability']:.4f} ({p['probability'] * 100:.2f}%)")
        print("-" * 60)

    print(f"\nBest Match: {output['best_match']}")
    print(f"Best Match Probability: {output['best_match_probability']:.4f}")

    # Probability sum verification
    prob_sum = sum(p['probability'] for p in output['predictions'])
    print(f"\nSum of probabilities: {prob_sum:.4f} (Expected: ~1.0)")
    assert abs(prob_sum - 1.0) < 1e-3, "Probabilities do not sum to 1.0!"

    print("\n[SUCCESS] Multimodal Image-Text Verification pipeline test passed!")


if __name__ == "__main__":
    run_verification()
