from flask import Flask, render_template, request
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import os
import json

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

if not HF_API_KEY:
    raise RuntimeError("Set HF_API_KEY in .env")

# choose a chat-capable model that your provider supports
HF_MODEL = "meta-llama/Llama-3.1-8B-Instruct"  # works with chat-completion; substitute if needed

client = InferenceClient(token=HF_API_KEY)

app = Flask(__name__, template_folder="templates", static_folder="static")


def call_chat_model(prompt, max_tokens=300, temperature=0.3):
    try:
        response = client.chat_completion(
            model=HF_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        if hasattr(response, "choices"):
            return response.choices[0].message["content"]

        return str(response)

    except Exception as e:
        return f"ERROR: {e}"



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    msg = ""
    if request.method == "POST":
        name = request.form.get("name", "")
        message = request.form.get("message", "")
        msg = f"Thanks {name}, your message received!"
    return render_template("contact.html", msg=msg)


@app.route("/ask", methods=["GET", "POST"])
def ask():
    answer = ""
    if request.method == "POST":
        q = request.form.get("question", "").strip()
        if q:
            prompt = f"You are a helpful teaching assistant. Answer clearly and concisely.\n\nQuestion: {q}\n\nAnswer:"
            answer = call_chat_model(prompt, max_tokens=250, temperature=0.6)
    return render_template("ask.html", answer=answer)


@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    suggestions = []
    if request.method == "POST":
        area = request.form.get("area", "").strip()
        if area:
            prompt = (
                "You are an assistant that suggests short learning topics.\n"
                "Return a JSON array (list) of 5 short topic strings (2-4 words each) only.\n\n"
                f"Input: {area}\n\nOutput JSON:"
            )
            out = call_chat_model(prompt, max_tokens=200, temperature=0.2)
            try:
                parsed = json.loads(out)
                if isinstance(parsed, list):
                    suggestions = parsed
            except:
                # fallback parse lines
                lines = [l.strip(" -•\t") for l in out.splitlines() if l.strip()]
                suggestions = [l for l in lines][:10]
    return render_template("recommend.html", topics=suggestions)


def parse_quiz_from_text(text):
    # try JSON first
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            clean = []
            for item in parsed:
                if isinstance(item, dict) and "q" in item and "options" in item and "answer" in item:
                    clean.append({"q": item["q"], "options": item["options"][:4], "answer": item["answer"]})
            if clean:
                return clean[:5]
    except:
        pass
    # fallback: simple parsing by lines
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    quiz = []
    i = 0
    while i < len(lines) and len(quiz) < 5:
        line = lines[i]
        if (line.lower().startswith("q:") or line.endswith("?")):
            qtext = line[2:].strip() if line.lower().startswith("q:") else line
            opts = []
            i += 1
            while i < len(lines) and len(opts) < 4:
                ln = lines[i]
                if ln.lower().startswith(("a:", "option", "1)","1.")) or "|" in ln or len(ln) < 200:
                    # remove leading labels
                    ln_clean = ln
                    for p in ["a:", "b:", "c:", "d:", "1)", "2)", "3)", "4)", "1.", "2.", "3.", "4."]:
                        if ln_clean.lower().startswith(p):
                            ln_clean = ln_clean[len(p):].strip()
                    opts.append(ln_clean)
                    i += 1
                else:
                    break
            answer = opts[0] if opts else ""
            quiz.append({"q": qtext, "options": opts if opts else ["True", "False"], "answer": answer})
        else:
            i += 1
    return quiz[:5]


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    quiz_list = None
    quiz_json = None
    topic = None

    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        if topic:
            quiz_list = generate_quiz(topic)

            if not quiz_list or not isinstance(quiz_list, list):
                quiz_list = [
                    {
                        "q": f"Sample question for {topic}?",
                        "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                        "answer": "Option 1"
                    }
                ]

            quiz_json = json.dumps(quiz_list)

    return render_template("quiz.html", quiz=quiz_list, quiz_json=quiz_json, selected_topic=topic)


@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    quiz_json = request.form.get("quiz_json", "[]")
    try:
        quiz_list = json.loads(quiz_json)
    except:
        quiz_list = []
    total = len(quiz_list)
    score = 0
    for i, q in enumerate(quiz_list):
        user_ans = request.form.get(f"q{i}")
        if user_ans and q.get("answer") and user_ans.strip() == q.get("answer").strip():
            score += 1
    return render_template("quiz_result.html", score=score, total=total)


if __name__ == "__main__":
    app.run(debug=True)
