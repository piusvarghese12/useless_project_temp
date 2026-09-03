import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
from torchvision.models import ResNet50_Weights
from transformers import AutoModel, AutoTokenizer
from PIL import Image
from typing import List, Dict, Union, Tuple, Optional


class VisionEncoder(nn.Module):
    """
    Vision Encoder using a ResNet-50 backbone projected to a 256-dimensional L2-normalized embedding space.
    """
    def __init__(self, embed_dim: int = 256, pretrained: bool = True):
        super().__init__()
        weights = ResNet50_Weights.DEFAULT if pretrained else None
        resnet = models.resnet50(weights=weights)
        in_features = resnet.fc.in_features  # 2048 for ResNet-50
        resnet.fc = nn.Identity()
        self.backbone = resnet
        self.projection = nn.Linear(in_features, embed_dim)

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        """
        Extract visual features and project to L2-normalized embedding.
        Args:
            images: Tensor of shape (B, 3, 224, 224)
        Returns:
            L2-normalized feature embeddings of shape (B, embed_dim)
        """
        features = self.backbone(images)
        embeddings = self.projection(features)
        return F.normalize(embeddings, p=2, dim=-1)


class TextEncoder(nn.Module):
    """
    Text Encoder using DistilBERT backbone projected to a 256-dimensional L2-normalized embedding space.
    """
    def __init__(self, embed_dim: int = 256, model_name: str = "distilbert-base-uncased"):
        super().__init__()
        self.backbone = AutoModel.from_pretrained(model_name)
        in_features = self.backbone.config.hidden_size  # 768 for DistilBERT
        self.projection = nn.Linear(in_features, embed_dim)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """
        Extract text features from [CLS] token output and project to L2-normalized embedding.
        Args:
            input_ids: Tensor of token IDs (B, seq_len)
            attention_mask: Tensor of attention mask (B, seq_len)
        Returns:
            L2-normalized feature embeddings of shape (B, embed_dim)
        """
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        cls_embedding = outputs.last_hidden_state[:, 0, :]  # Take [CLS] token representation
        embeddings = self.projection(cls_embedding)
        return F.normalize(embeddings, p=2, dim=-1)


class TwoTowerModel(nn.Module):
    """
    Two-Tower Contrastive Neural Network Architecture combining VisionEncoder and TextEncoder.
    """
    def __init__(self, embed_dim: int = 256, text_model_name: str = "distilbert-base-uncased", pretrained_vision: bool = True):
        super().__init__()
        self.vision_encoder = VisionEncoder(embed_dim=embed_dim, pretrained=pretrained_vision)
        self.text_encoder = TextEncoder(embed_dim=embed_dim, model_name=text_model_name)

    def forward(
        self,
        images: torch.Tensor,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass computing image embeddings, text embeddings, and pairwise cosine similarity.
        Args:
            images: Tensor of shape (B_img, 3, 224, 224)
            input_ids: Tensor of shape (B_text, seq_len)
            attention_mask: Tensor of shape (B_text, seq_len)
        Returns:
            Tuple of (image_embeds, text_embeds, similarity_matrix)
        """
        image_embeds = self.vision_encoder(images)
        text_embeds = self.text_encoder(input_ids=input_ids, attention_mask=attention_mask)
        # Cosine similarity between normalized vectors is dot product
        similarity_matrix = torch.matmul(image_embeds, text_embeds.T)
        return image_embeds, text_embeds, similarity_matrix


class ProductPredictor:
    """
    Inference helper for product image-text verification.
    """
    def __init__(
        self,
        model: Optional[TwoTowerModel] = None,
        text_model_name: str = "distilbert-base-uncased",
        device: Optional[str] = None
    ):
        from torchvision import transforms

        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        if model is None:
            self.model = TwoTowerModel(text_model_name=text_model_name).to(self.device)
        else:
            self.model = model.to(self.device)

        self.model.eval()

        self.tokenizer = AutoTokenizer.from_pretrained(text_model_name)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def preprocess_image(self, image: Union[Image.Image, str]) -> torch.Tensor:
        """
        Preprocess PIL Image or image file path.
        """
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")
        elif isinstance(image, Image.Image):
            image = image.convert("RGB")
        else:
            raise ValueError("Input image must be a file path string or PIL Image instance.")

        image_tensor = self.transform(image).unsqueeze(0)  # Shape: (1, 3, 224, 224)
        return image_tensor.to(self.device)

    def preprocess_texts(self, titles: List[str]) -> Dict[str, torch.Tensor]:
        """
        Tokenize candidate product titles.
        """
        encoding = self.tokenizer(
            titles,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors="pt"
        )
        return {
            "input_ids": encoding["input_ids"].to(self.device),
            "attention_mask": encoding["attention_mask"].to(self.device)
        }

    @torch.no_grad()
    def predict(
        self,
        image: Union[Image.Image, str],
        candidate_titles: List[str],
        temperature: float = 10.0
    ) -> Dict[str, Union[List[Dict[str, float]], str]]:
        """
        Verify product image against candidate product titles using cosine similarity and temperature-scaled softmax.
        Args:
            image: Image path or PIL Image object
            candidate_titles: List of candidate product title strings
            temperature: Temperature scaling factor (default 10.0)
        Returns:
            Dictionary containing prediction results, probabilities, and best match.
        """
        if not candidate_titles:
            raise ValueError("Candidate titles list cannot be empty.")

        image_tensor = self.preprocess_image(image)
        text_inputs = self.preprocess_texts(candidate_titles)

        image_embeds = self.model.vision_encoder(image_tensor)  # (1, 256)
        text_embeds = self.model.text_encoder(
            input_ids=text_inputs["input_ids"],
            attention_mask=text_inputs["attention_mask"]
        )  # (N_candidates, 256)

        # Cosine similarity matrix (1, N_candidates)
        cosine_sims = torch.matmul(image_embeds, text_embeds.T).squeeze(0)  # (N_candidates,)

        # Temperature-scaled Softmax
        scaled_logits = cosine_sims * temperature
        probabilities = F.softmax(scaled_logits, dim=-1)

        results = []
        for idx, title in enumerate(candidate_titles):
            sim_score = cosine_sims[idx].item()
            prob = probabilities[idx].item()
            results.append({
                "title": title,
                "similarity_score": round(sim_score, 4),
                "probability": round(prob, 4)
            })

        # Sort results by probability descending
        results = sorted(results, key=lambda x: x["probability"], reverse=True)

        return {
            "best_match": results[0]["title"],
            "best_match_probability": results[0]["probability"],
            "predictions": results
        }
