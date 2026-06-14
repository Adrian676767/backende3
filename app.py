from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

students_db = [
    {"id": 1, "name": "Michal Horváth", "age": 16, "vyska": 175},
    {"id": 2, "name": "Sofia Kováčová", "age": 15, "vyska": 162},
    {"id": 3, "name": "Jakub Malý", "age": 17, "vyska": 182},
    {"id": 4, "name": "Ema Srncová", "age": 16, "vyska": 168},
    {"id": 5, "name": "Matúš Veľký", "age": 15, "vyska": 170},
    {"id": 6, "name": "Lucia Malá", "age": 17, "vyska": 160},
    {"id": 7, "name": "David Novák", "age": 16, "vyska": 178},
    {"id": 8, "name": "Peter Tóth", "age": 15, "vyska": 165},
    {"id": 9, "name": "Nela Szabóová", "age": 17, "vyska": 172},
    {"id": 10, "name": "Adam Molnár", "age": 16, "vyska": 180},
    {"id": 11, "name": "Nina Balážová", "age": 15, "vyska": 158}
]

chat_histories = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/students')
def get_students():
    sort_by = request.args.get('sort', 'name')
    if sort_by == 'name':
        sorted_students = sorted(students_db, key=lambda x: x['name'])
    elif sort_by == 'age':
        sorted_students = sorted(students_db, key=lambda x: x['age'])
    elif sort_by == 'vyska':
        sorted_students = sorted(students_db, key=lambda x: x['vyska'])
    else:
        sorted_students = students_db
    return jsonify(sorted_students)

@app.route('/chat', methods=['POST'])
def chat_ai():
    data = request.json
    user_message = data.get('message', '')
    student_info = data.get('student_info', {})
    student_id = student_info.get('id')
    
    if student_id not in chat_histories:
        chat_histories[student_id] = []
    
    chat_histories[student_id].append({"role": "user", "content": user_message})
    
    system_instruction = (
        f"Si žiak {student_info.get('name')}, máš {student_info.get('age')} rokov. "
        f"Odpovedaj uvoľnene, po slovensky, používaj emojis. Buď stručný."
    )
    
    messages_context = "\n".join([f"{m['role']}: {m['content']}" for m in chat_histories[student_id][-5:]])
    prompt = f"<|im_start|>system\n{system_instruction}<|im_end|>\n{messages_context}\n<|im_start|>assistant\n"

    try:
        API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct"
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 150, "temperature": 0.8}
        }
        response = requests.post(API_URL, json=payload, timeout=10)
        ai_response = response.json()[0]['generated_text'].strip()
        
        chat_histories[student_id].append({"role": "assistant", "content": ai_response})
        
        return jsonify({"response": ai_response})
    except Exception as e:
        return jsonify({"response": "Ups, niečo sa pokazilo, skúšam sa spamätať! 😅"})

if __name__ == '__main__':
    app.run(debug=True)
