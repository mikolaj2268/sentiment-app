# Używamy lekkiego obrazu Pythona
FROM python:3.9-slim

# Ustawiamy katalog roboczy
WORKDIR /app

# Kopiujemy plik z zależnościami i instalujemy je
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy całą aplikację do obrazu
COPY . .

# Ustawiamy port, na którym będzie działać aplikacja
EXPOSE 8501

# Uruchamiamy aplikację Streamlit, przekazując opcje:
# --server.port=8501 - ustawia port,
# --server.enableCORS=false - wyłącza mechanizm CORS, co jest często wymagane na Cloud Run
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8080} --server.enableCORS=false"]