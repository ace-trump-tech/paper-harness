from __future__ import annotations

from typing import Dict


class ImageProvider:
    """Boundary for image generation; providers must return provenance metadata."""

    name = "base"

    def generate(self, prompt: str, **kwargs) -> Dict[str, str]:
        raise NotImplementedError


class LocalImageProvider(ImageProvider):
    name = "local-placeholder"

    def generate(self, prompt: str, **kwargs) -> Dict[str, str]:
        return {"status": "planned", "prompt": prompt, "provider": self.name,
                "message": "Connect an approved image provider to generate pixels."}

