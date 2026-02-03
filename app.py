from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_engine import retrieve_context
from llm import generate_answer

app = Flask(__name__)
CORS(app)   # ✅ THIS LINE FIXES THE ISSUE

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")

    retrieved_docs = retrieve_context(user_message)
    answer = generate_answer(user_message, retrieved_docs)
   
    return jsonify({"reply": answer })

if __name__ == "__main__":
    app.run(debug=True)
