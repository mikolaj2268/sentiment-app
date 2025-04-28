from google.cloud import firestore
import streamlit as st

COLLECTION = "test_collection"

def _client():
    try:
        return firestore.Client()
    except Exception as e:
        st.error(f"Firestore error: {e}")
        return None

def get_one_document():
    client = _client()
    if not client:
        return None
    docs = client.collection(COLLECTION).limit(1).stream()
    doc = next(docs, None)
    return doc.to_dict() if doc else None