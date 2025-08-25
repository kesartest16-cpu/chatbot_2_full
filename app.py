from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os

from utils.nlp import IntentMatcher
from utils.memory import Memory

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
INTENTS_PATH = os.path.join(APP_ROOT, 'data', 'intents.json')
WEB_DIR = os.path.join(APP_ROOT, 'web')

app = Flask(__name__, static_folder=None)
CORS(app)

matcher = IntentMatcher(INTENTS_PATH)
memory = Memory()

@app.post('/api/chat')
def chat():
    payload = request.get_json(force=True)
    text = payload.get('message', '')
    session_id = payload.get('session_id', 'default')

    memory.ensure_session(session_id)

    # Context that can be used in response templates
    context = {
        'user_name': memory.get(session_id, 'user_name', 'friend'),
        'time_now': datetime.now().strftime('%Y-%m-%d %H:%M')
    }

    # Special commands
    low = text.lower()
    if low.startswith('set my name to '):
        name = text.split('to', 1)[1].strip()
        memory.set(session_id, 'user_name', name)
        context['user_name'] = name
        return jsonify({
            'reply': f"Nice to meet you, {name}! I'll remember your name.",
            'context': context
        })

    # Match intent
    tag, slots, score = matcher.match(text)

    # Slot handling for wildcard name patterns
    if tag == 'name.user.set' and 'wildcard' in slots:
        name = slots['wildcard']
        memory.set(session_id, 'user_name', name)
        context['user_name'] = name

    reply = matcher.respond(tag, context)

    return jsonify({
        'reply': reply,
        'intent': tag,
        'score': score,
        'context': context
    })

@app.get('/')
@app.get('/chat')
def index():
    return send_from_directory(WEB_DIR, 'index.html')

@app.get('/<path:path>')
def static_proxy(path):
    return send_from_directory(WEB_DIR, path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)