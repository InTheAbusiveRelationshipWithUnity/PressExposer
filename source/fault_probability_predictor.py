import pandas as pd
import torch
import re
from catboost import CatBoostClassifier
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer
)

class ModelProbabilityAnalyzer:
    def __init__(self, catboost_model, rubert_model):
        self.cb_model = CatBoostClassifier()
        self.cb_model.load_model(catboost_model)
        
        self.tokenizer = AutoTokenizer.from_pretrained(rubert_model)
        self.rubert_model = AutoModelForSequenceClassification.from_pretrained(
            rubert_model
        )
        self.rubert_model.eval()
    
    def predict(self, title: str):
        caps_ratio = get_caps_ratio(title)
        caps_words_count = get_caps_words_count(title)
        
        data = pd.DataFrame(
            [[title, title.count("!"), title.count("?"), caps_ratio, caps_words_count]],
            columns=[
                "title_ru",
                "exclamation_marks",
                "question_marks",
                "caps_ratio",
                "caps_count",
            ],
        )
        
        catboost_prob = self.cb_model.predict_proba(data)[:, 1].item()
        
        inputs = self.tokenizer(
            title, return_tensors="pt", truncation=True, max_length=128
        )
        
        with torch.no_grad():
            output = self.rubert_model(**inputs)
            rubert_prob = (
                torch.softmax(output.logits, dim=1)[0][1].item()
            )
        
        return catboost_prob * 0.5 + rubert_prob * 0.5

def get_caps_ratio(text):
  text = str(text)
  if len(text) == 0:
    return 0.0

  letters = [c for c in text if c.isalpha()]

  if len(letters) == 0:
    return 0.0

  caps = [c for c in text if c.isupper()]

  return len(caps) / len(letters)

def get_caps_words_count(text):
  text = str(text)
  if len(text) == 0:
    return 0.0

  words = re.findall(r"\b\w+\b", text)

  caps = [c for c in words if c.isupper() and len(c) > 1]

  return len(caps)