from typing import Optional

try:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

MODEL_NAME = "google/flan-t5-small"


class LLMService:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self._loaded = False

    def load(self):
        if self._loaded or not TRANSFORMERS_AVAILABLE:
            self._loaded = True
            return

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
        except Exception:
            self.model = None
            self.tokenizer = None
        finally:
            self._loaded = True

    def generate(self, prompt: str, max_length: int = 220) -> str:
        if not TRANSFORMERS_AVAILABLE:
            return prompt
        self.load()
        if not self.model or not self.tokenizer:
            return prompt

        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        outputs = self.model.generate(**inputs, max_length=max_length, num_beams=2, early_stopping=True)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def is_available(self) -> bool:
        return TRANSFORMERS_AVAILABLE
