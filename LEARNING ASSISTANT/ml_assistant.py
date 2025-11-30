from huggingface_hub import InferenceClient

client = InferenceClient("mistralai/Mistral-7B-Instruct-v0.2")

def ask_ai(question):
    try:
        response = client.text_generation(
            question,
            max_new_tokens=150,
            temperature=0.7
        )
        return response
    except:
        return "AI Service Error. Please try again."

def generate_topics(input_text):
    prompt = f"Suggest 5 learning topics based on: {input_text}"
    return ask_ai(prompt)

def generate_quiz(topic):
    prompt = f"Generate 5 multiple choice questions on {topic}. Provide format: Q, option1, option2, option3, option4, answer."
    return ask_ai(prompt)
