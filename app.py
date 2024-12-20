import os
import sys
import subprocess
import json
import re
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit

# Add the directory containing story_generator.py to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from story_generator import InteractiveStoryGenerator

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure random key
socketio = SocketIO(app)

class WebStoryGenerator(InteractiveStoryGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket_io = None  # Will be set when initializing with socketio

    def stream_response(self, text):
        """Override stream method to emit socket events instead of printing"""
        if self.socket_io:
            for char in text:
                self.socket_io.emit('story_stream', {'text': char})
                socketio.sleep(0.02)  # Simulate typing effect

    def call_ollama_stream(self, prompt):
        """Modified to work with web streaming"""
        try:
            response = self.stream_ollama_request(prompt)
            return response
        except Exception as e:
            if self.socket_io:
                self.socket_io.emit('error', {'message': str(e)})
            return None

    def stream_ollama_request(self, prompt):
        """Custom method to stream Ollama response with socketio"""
        import requests
        import json

        full_response = ""
        try:
            response = requests.post(
                f'{self.ollama_url}/generate', 
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': True
                },
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    if 'response' in json_response:
                        chunk = json_response['response']
                        full_response += chunk
                        if self.socket_io:
                            self.socket_io.emit('story_stream', {'text': chunk})
            
            return full_response
        
        except requests.exceptions.RequestException as e:
            if self.socket_io:
                self.socket_io.emit('error', {'message': str(e)})
            return None

    def extract_choices(self, text):
        """Robustly extract choices from the story text"""
        # First, try to find JSON within curly braces
        json_match = re.search(r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}', text, re.DOTALL)
        
        if json_match:
            try:
                # Try to parse the matched text as JSON
                choices = json.loads(json_match.group(0))
                return choices
            except json.JSONDecodeError:
                # If JSON parsing fails, try a more lenient approach
                pass
        
        # If JSON parsing fails, try to manually extract choices
        choice_pattern = r"'([A-E])'\s*:\s*['\"]([^'\"]+)['\"]"
        matches = re.findall(choice_pattern, text)
        
        if matches:
            return dict(matches)
        
        return None

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('get_genre_help')
def handle_genre_help():
    generator = WebStoryGenerator()
    genres = generator.get_genre_help()
    emit('genre_help', {'genres': genres})

@socketio.on('start_story')
def start_story(data):
    genre = data.get('genre', 'adventure')
    generator = WebStoryGenerator(model='llama3.2:3b')
    generator.socket_io = socketio  # Set socketio for streaming

    # Generate story start
    start_prompt = generator.generate_story_start_prompt(genre)
    story_start = generator.call_ollama_stream(start_prompt)
    
    # Extract choices
    choices = generator.extract_choices(story_start)
    
    # Store context in session
    session['story_context'] = [story_start]
    session['genre'] = genre

    emit('story_started', {
        'story': story_start,
        'choices': choices
    })

@socketio.on('make_choice')
def make_story_choice(data):
    choice = data.get('choice', '')
    genre = session.get('genre', 'adventure')
    story_context = session.get('story_context', [])

    generator = WebStoryGenerator(model='llama3.2:3b')
    generator.socket_io = socketio  # Set socketio for streaming

    # Generate story continuation
    continuation_prompt = generator.generate_choice_continuation_prompt(
        genre, 
        "\n".join(story_context), 
        choice
    )
    
    story_continuation = generator.call_ollama_stream(continuation_prompt)
    
    # Extract choices
    choices = generator.extract_choices(story_continuation)
    
    # Update session context
    story_context.append(story_continuation)
    session['story_context'] = story_context

    emit('story_continued', {
        'story': story_continuation,
        'choices': choices
    })

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)