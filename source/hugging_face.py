from huggingface_hub import login
from transformers import AutoModelForSequenceClassification, AutoTokenizer

login("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")

model = AutoModelForSequenceClassification.from_pretrained(
    "models/rubert"
)
tokenizer = AutoTokenizer.from_pretrained("models/rubert")

repo_name = "alcofighter/rubert"
model.push_to_hub(repo_name)
tokenizer.push_to_hub(repo_name)