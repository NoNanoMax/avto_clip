import torch
import numpy as np
from PIL import Image
import io
from transformers import CLIPModel, CLIPProcessor


class ClipHFEmbedder:

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32", device: str | None = None):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.model = CLIPModel.from_pretrained(model_name).to(self.device).eval()
        self.processor = CLIPProcessor.from_pretrained(model_name)


    @property
    def dim(self) -> int:
        return self.model.config.projection_dim
    

    @torch.inference_mode()
    def embed_text(self, text: str) -> list[float]:
        inputs = self.processor(text=[text], return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        feat = self.model.get_text_features(**inputs).pooler_output  # (1, 512)
        print(feat)
        print(feat.shape)
        feat = torch.nn.functional.normalize(feat, p=2, dim=-1)
        return feat[0].detach().cpu().float().tolist()
    

    @torch.inference_mode()
    def embed_image_bytes(self, image_bytes: bytes) -> list[float]:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        inputs = self.processor(images=[img], return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        feat = self.model.get_image_features(**inputs).pooler_output  # (1, 512)
        feat = torch.nn.functional.normalize(feat, p=2, dim=-1)
        return feat[0].detach().cpu().float().tolist()
