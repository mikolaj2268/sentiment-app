import streamlit as st
from google.cloud import firestore

# Show photo from photo/photo.jpg
st.image("photo/photo.jpg")

db = firestore.Client()
st.title("Przykładowy odczyt z Firestore")

docs = db.collection("test_collection").limit(1).stream()
doc = next(docs, None)

if doc:
    st.write("ID dokumentu:", doc.id)
    st.write("Zawartość:", doc.to_dict())
else:
    st.write("Nie znaleziono żadnego dokumentu w test_collection")