import torch
import json
import os
from transformers import AutoTokenizer
from vncorenlp import VnCoreNLP
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pyserini.search.lucene import LuceneSearcher
from src.model import PhoBERTChatBot
from src.utils import problem_response, get_label, disease_response, chatgpt_response

searcher = LuceneSearcher('lookup_db')
searcher.set_language('vn')
searcher.set_bm25()

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.static_folder = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'patients.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'random string'
app.app_context().push()

db = SQLAlchemy(app)

class Patients(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    sex = db.Column(db.String(50))
    age = db.Column(db.Integer)
    diagnosis = db.Column(db.String(1000))
    date = db.Column(db.String(100))

    def __init__(self, name, sex, age, diagnosis, date):
        self.name = name
        self.sex = sex
        self.age = age
        self.diagnosis = diagnosis
        self.date = date

rdrsegmenter = VnCoreNLP("./vncorenlp/VnCoreNLP-1.1.1.jar", annotators="wseg", max_heap_size='-Xmx500m')
with open('./data/intent_train.json', 'r', encoding='utf-8') as json_data:
    contents = json.load(json_data)

model = PhoBERTChatBot('vinai/phobert-base', 8)
model.load_state_dict(torch.load('weight/saved_weights.pth',  map_location=torch.device('cpu')))
tokenizer = AutoTokenizer.from_pretrained('vinai/phobert-base')
tags_set, contents = get_label('./data/intent_train.json')
print("=== DEBUG: Greeting responses loaded ===")
for intent in contents['intents']:
    if intent['tag'] == 'greeting':
        print(f"Tag: {intent['tag']}")
        print(f"Responses: {intent['responses']}")

@app.route('/delete/<int:id>')
def delete(id):
    id_delete = Patients.query.get_or_404(id)
    db.session.delete(id_delete)
    db.session.commit()
    return redirect(url_for('database'))

@app.route('/')
def home():   
    return render_template('chatbot.html')

@app.route('/get')
def get_bot_response():
    userText = request.args.get('msg')
    mode = request.args.get('mode')
    # answer, _ = chatbot_response(userText)
    answer, prob = disease_response(model, tokenizer, userText, rdrsegmenter, tags_set, contents)
    print(f"=== DEBUG REQUEST ===")
    print(f"User: {userText}")
    print(f"Mode: {mode}")
    print(f"Answer: {answer}")
    print(f"Confidence: {prob}")
    print(f"=====================")
    if mode == 'problem':
        if answer == 'Dạ bạn cho mình xin họ và tên ạ':
            return redirect(url_for('form'))
        if answer.startswith('bạn có thể') and len(userText.split(',')) < 3:
            return 'mình chưa rõ lắm, bạn có thể cho mình xin thêm thông tin về vấn đề bạn đang gặp phải không ạ'
        return answer
    elif mode == 'thongtin':
        return problem_response(searcher, userText)
    elif mode == 'chatgpt':
        return chatgpt_response(userText)

@app.route('/database')
def database():
    return render_template('database.html', results=Patients.query.all())

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['name']
        sex = request.form['sex']
        age = request.form['age']
        phone = request.form['phone']
        date = request.form['date']

        patient = Patients(name, sex, age, phone, date)
        db.session.add(patient)
        db.session.commit()
        flash('Sucessfully')
        return redirect(url_for('database'))
    return render_template('form.html')

# ==================== REST API ENDPOINTS ====================

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """
    Chat API endpoint
    Request body: {"message": "your message", "mode": "problem|thongtin|chatgpt"}
    Response: {"response": "bot response", "confidence": float, "intent": "detected intent"}
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message field'}), 400
        
        user_message = data['message']
        mode = data.get('mode', 'problem')
        
        # Get disease response (intent classification)
        answer, prob = disease_response(model, tokenizer, user_message, rdrsegmenter, tags_set, contents)
        
        # Get detected intent tag
        sentence = ' '.join(rdrsegmenter.tokenize(user_message)[0])
        token = tokenizer.encode_plus(sentence, truncation=True, add_special_tokens=True,
                                      max_length=30, padding='max_length',
                                      return_attention_mask=True, return_token_type_ids=False,
                                      return_tensors='pt')
        with torch.inference_mode():
            output = model(token['input_ids'], token['attention_mask'])
        preds = torch.argmax(output, dim=1)
        detected_intent = tags_set[preds.item()]
        
        # Handle different modes
        if mode == 'problem':
            final_answer = answer
        elif mode == 'thongtin':
            final_answer = problem_response(searcher, user_message)
        elif mode == 'chatgpt':
            final_answer = chatgpt_response(user_message)
        else:
            final_answer = answer
        
        return jsonify({
            'response': final_answer,
            'confidence': prob,
            'intent': detected_intent,
            'mode': mode
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/intents', methods=['GET'])
def api_intents():
    """
    Get list of all available intents/tags
    Response: {"intents": [{"tag": "...", "patterns_count": int, "responses_count": int}]}
    """
    intents_list = []
    for intent in contents['intents']:
        intents_list.append({
            'tag': intent['tag'],
            'patterns_count': len(intent['patterns']),
            'responses_count': len(intent['responses']),
            'sample_patterns': intent['patterns'][:3]  # First 3 patterns as examples
        })
    return jsonify({'intents': intents_list, 'total': len(intents_list)})

@app.route('/api/search', methods=['GET'])
def api_search():
    """
    Search information using Lucene
    Query params: ?q=search_query&limit=5
    Response: {"results": [{"id": "...", "content": "..."}]}
    """
    query = request.args.get('q', '')
    limit = request.args.get('limit', 5, type=int)
    
    if not query:
        return jsonify({'error': 'Missing query parameter q'}), 400
    
    hits = searcher.search(query, k=limit)
    results = []
    for hit in hits:
        doc = searcher.doc(hit.docid)
        json_doc = json.loads(doc.raw())
        results.append({
            'id': json_doc.get('id', hit.docid),
            'content': json_doc.get('contents', ''),
            'score': hit.score
        })
    
    return jsonify({'query': query, 'results': results, 'total': len(results)})

@app.route('/api/patients', methods=['GET', 'POST'])
def api_patients():
    """
    Patients CRUD API
    GET: List all patients
    POST: Add new patient {"name": "...", "sex": "...", "age": int, "diagnosis": "...", "date": "..."}
    """
    if request.method == 'GET':
        patients = Patients.query.all()
        patients_list = [{
            'id': p.id,
            'name': p.name,
            'sex': p.sex,
            'age': p.age,
            'diagnosis': p.diagnosis,
            'date': p.date
        } for p in patients]
        return jsonify({'patients': patients_list, 'total': len(patients_list)})
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            patient = Patients(
                name=data.get('name', ''),
                sex=data.get('sex', ''),
                age=data.get('age', 0),
                diagnosis=data.get('diagnosis', ''),
                date=data.get('date', '')
            )
            db.session.add(patient)
            db.session.commit()
            return jsonify({'message': 'Patient added successfully', 'id': patient.id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/patients/<int:id>', methods=['GET', 'DELETE'])
def api_patient_detail(id):
    """
    Get or delete specific patient
    """
    patient = Patients.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify({
            'id': patient.id,
            'name': patient.name,
            'sex': patient.sex,
            'age': patient.age,
            'diagnosis': patient.diagnosis,
            'date': patient.date
        })
    
    elif request.method == 'DELETE':
        db.session.delete(patient)
        db.session.commit()
        return jsonify({'message': 'Patient deleted successfully'})

# ==================== END API ENDPOINTS ====================
    
if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=False)
