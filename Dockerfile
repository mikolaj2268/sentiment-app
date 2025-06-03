FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y build-essential gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt "huggingface_hub[cli]>=0.22"

# Download the HuggingFace model during build using a more reliable Python approach
RUN mkdir -p /app/models/distilbert-sst2
RUN python -c 'from transformers import AutoTokenizer, AutoModelForSequenceClassification; \
    model_name = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"; \
    model_path = "/app/models/distilbert-sst2"; \
    tokenizer = AutoTokenizer.from_pretrained(model_name); \
    model = AutoModelForSequenceClassification.from_pretrained(model_name); \
    tokenizer.save_pretrained(model_path); \
    model.save_pretrained(model_path); \
    print("✅ Model successfully downloaded and saved to", model_path)'

# Let Cloud Run tell us which port to open
ENV PORT=8080
EXPOSE 8080
CMD ["sh","-c","streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true --server.enableCORS=false"]