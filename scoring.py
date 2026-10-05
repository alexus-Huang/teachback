import re
import streamlit as st
from sentence_transformers import SentenceTransformer, util


@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if len(p.strip()) > 3]


def score_coverage(student_text, concepts, threshold=0.45):
    sentences = split_sentences(student_text)
    if not sentences or not concepts:
        return [{"concept": c, "score": 0.0, "covered": False} for c in concepts]

    model = load_model()
    sentence_vecs = model.encode(sentences, convert_to_tensor=True)
    concept_vecs = model.encode(concepts, convert_to_tensor=True)
    sims = util.cos_sim(concept_vecs, sentence_vecs)

    results = []
    for i, concept in enumerate(concepts):
        best = float(sims[i].max())
        results.append({"concept": concept, "score": best, "covered": best >= threshold})
    return results