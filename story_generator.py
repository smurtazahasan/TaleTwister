import requests
import json
import time
import sys
import os
import re

class InteractiveStoryGenerator:
    def __init__(self, model='llama3.2', ollama_url='http://127.0.0.1:11434/api'):
        self.model = model
        self.ollama_url = ollama_url
        self.story_context = []
        self.full_narrative = []

    def stream_response(self, text):
        """Stream text to console with a typing effect."""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.02)  # Adjust speed of text generation
        print()  # New line after streaming

    def generate_story_start_prompt(self, genre):
        """Generate a comprehensive prompt to start the story."""
        return f"""
            You are an expert storyteller creating an interactive narrative in the {genre} genre. 
            Your task is to:
            1. Begin a captivating story that has multiple potential paths that sticks to {genre} type of story
            2. Ensure there are multiple distinct narrative choices that relate to {genre}
            3. Make each choice a meaningful decision point
            4. Create an immersive, engaging narrative
            5. Include a 'STOP' option

            Rules:
            - Story must be creative and unpredictable
            - Choices should dramatically alter the narrative
            - Maintain a consistent and exciting tone

            Generate the opening of the story, setting the scene and introducing the main character. 
            After the narrative, provide multiple choices labeled A, B, C, D, including a 'STOP' option.

            Structure the multiple choice option in the following JSON format at the end. Insert 2 empty lines between the story and multiple choice options:
            {{
                'A': 'Choice A description here',
                'B': 'Choice B description here',
                'C': 'Choice B description here',
                'D': 'Choice B description here',
                'E': 'Stop'
            }}
        """

    def generate_choice_continuation_prompt(self, genre, previous_context, chosen_letter):
        """Generate a prompt to continue the story based on user's letter choice."""
        return f"""
            You are continuing an interactive {genre} story. 

            Previous Story Context:
            {previous_context}

            The user chose the action corresponding to the letter: {chosen_letter}

            Continue the story based on this choice. Narrative rules:
            1. Directly incorporate the consequences of the chosen action
            2. Create narrative tension
            3. Provide multiple distinct narrative choices
            4. Ensure each choice has significant impact
            5. Include a 'STOP' option

            Provide the story continuation and new choices labeled A, B, C, D.

            Structure the multiple choice option in the following JSON format at the end:
            {{
                'A': 'Choice A description here',
                'B': 'Choice B description here',
                'C': 'Choice B description here',
                'D': 'Choice B description here',
                'E': 'Stop'
            }}
        """

    def call_ollama_stream(self, prompt):
        """Call Ollama API with streaming response."""
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
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    if 'response' in json_response:
                        chunk = json_response['response']
                        full_response += chunk
                        sys.stdout.write(chunk)
                        sys.stdout.flush()
            
            print()  # New line after streaming
            return full_response
        
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Ollama: {e}")
            return None

    def remove_choices(self, text):
        """Remove choice options from the text."""
        # Remove lines starting with (A), (B), (C), (D), (E)
        choice_pattern = r'\((?:[A-E])\):.*$'
        cleaned_text = re.sub(choice_pattern, '', text, flags=re.MULTILINE)
        
        # Remove any leading/trailing whitespace and multiple consecutive newlines
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text.strip())
        
        return cleaned_text

    def save_story(self, genre):
        """Save the story to a text file."""
        # Create a directory for stories if it doesn't exist
        os.makedirs('stories', exist_ok=True)
        
        # Generate a filename based on genre and timestamp
        filename = f"stories/{genre}_story_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Remove choices from story segments
        clean_narrative = [self.remove_choices(segment) for segment in self.story_context]
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(f"Interactive {genre.capitalize()} Story\n")
                file.write("=" * 40 + "\n\n")
                file.write("\n\n".join(clean_narrative))
            
            print(f"\n📖 Story saved successfully to {filename}")
            return filename
        except Exception as e:
            print(f"\n❌ Error saving story: {e}")
            return None

    def get_genre_help(self):
        """Get genre help from Ollama."""
        help_prompt = """
            Provide a comprehensive list of engaging story genres up to 10. Include:
            1. A diverse range of genres up to 10
            2. A brief 1-2 word description or explanation for each genre
            3. Approximately 15-20 different genres

            Format the output as a clear, readable list with genres that spark imagination. Do not output anything other than the list of genres. No preamble or ending. Just the options.
        """
        
        return self.call_ollama_stream(help_prompt)

    def run_interactive_story(self, genre):
        """Main interactive story generation loop."""
        print(f"🌟 Generating an interactive {genre} story... 🌟\n")
        
        # Generate story start
        start_prompt = self.generate_story_start_prompt(genre)
        story_start = self.call_ollama_stream(start_prompt)
        
        self.story_context.append(story_start)
        
        while True:
            # Get user choice
            try:
                user_input = input("\nEnter the letter of your choice (or 'save' to save the story): ").upper()
                
                # If user inputs 'STOP', end the story
                if user_input in ['E', 'STOP']:
                    print("\n🏁 Story ended. Thank you for playing! 🏁")
                    break
                
                # Save story option
                if user_input == 'SAVE':
                    self.save_story(genre)
                    continue
                
                # Generate story continuation with the direct letter input
                continuation_prompt = self.generate_choice_continuation_prompt(
                    genre, 
                    "\n".join(self.story_context), 
                    user_input
                )
                
                story_continuation = self.call_ollama_stream(continuation_prompt)
                self.story_context.append(story_continuation)
                
            except KeyboardInterrupt:
                print("\n\n🏁 Story ended. Thank you for playing! 🏁")
                break

def main():
    while True:
        # Prompt user for genre
        genre = input("\nEnter the genre for your interactive story (or 'help' for suggestions): ").lower()
        
        if genre == 'help':
            print("\n🌈 Genre Suggestions:\n")
            genre_help = InteractiveStoryGenerator().get_genre_help()
            continue
        
        # Proceed with story generation
        story_generator = InteractiveStoryGenerator(model='llama3.2:3b')
        story_generator.run_interactive_story(genre)
        
        # Option to create another story
        play_again = input("\nWould you like to create another story? (yes/no): ").lower()
        if play_again != 'yes':
            break

if __name__ == "__main__":
    main()