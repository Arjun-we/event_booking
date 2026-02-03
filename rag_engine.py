from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from vendors_data import VENDORS

documents = [
    f"{v['name']} {v['category']} {v['description']} Budget {v['cost']} Capacity {v['capacity']}"
    for v in VENDORS
]

vectorizer = TfidfVectorizer()
doc_vectors = vectorizer.fit_transform(documents)

def retrieve_context(query, top_k=5):
    q_vec = vectorizer.transform([query])
    scores = cosine_similarity(q_vec, doc_vectors)[0]
    top_idx = scores.argsort()[-top_k:][::-1]
    return [VENDORS[i] for i in top_idx]
