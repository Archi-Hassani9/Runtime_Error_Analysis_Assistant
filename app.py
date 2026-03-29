from flask import Flask, request, jsonify, render_template
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

with open("Knowledge_Base.txt", "r", encoding="utf-8") as file:
    knowledge = file.read()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    with open("Knowledge_Base.txt", "r", encoding="utf-8") as f:
        knowledge = f.read()

    user_message = request.json.get("message", "").strip()

    if user_message.lower() in ["hi", "hello", "hey"]:
        return jsonify({
            "response": "Hello! How can I help you with runtime error analysis today?"
        })

    system_prompt = f"""You are a polite, professional Runtime Error Analysis Assistant.

RULES:
1. ONLY use the provided Knowledge Base below to answer questions.
2. Do NOT generate answers from outside knowledge.
3. Do NOT hallucinate or guess.
4. If the question is not covered in the Knowledge Base, reply exactly with:
   "Sorry, I don't have an answer for that question based on my current knowledge."
5. If the user asks anything unrelated to runtime errors, debugging, exception analysis, or outside the knowledge base, reply exactly with:
   "Sorry, I don't have an answer for that question based on my current knowledge."
6. Be clear, polite, and professional.

<KnowledgeBase>
{knowledge}
</KnowledgeBase>"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
        )
        bot_reply = completion.choices[0].message.content
    except Exception as e:
        bot_reply = "Sorry, I encountered an internal error connecting to my AI model."
        print(f"API Error: {e}")

    return jsonify({"response": bot_reply})


if __name__ == "__main__":
    app.run(debug=True)