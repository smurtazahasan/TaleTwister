# TaleTwister

An interactive story generation application that creates unique narratives based on user choices and selected genres, utilizing Ollama AI model for enhanced storytelling capabilities.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Code Structure](#code-structure)
- [Current Improvements](#current-improvements)
- [Contributing](#contributing)

## Features (as implemented)

- **Genre Selection:** Users can choose from various genres to generate tailored stories.
- **Branching Narratives:** Decision points allow users to shape their story's path, leading to unique outcomes.
- **AI-assisted Generation:** Ollama AI model helps create engaging and coherent narratives based on user inputs and choices.
- **Live Interaction:** Real-time interaction between the front-end and back-end to provide immediate feedback and narrative progression.

## Tech Stack

- **Backend:** Python (3.10+)
  - [Ollama](https://ollama.ai/) (For text generation and branching narrative assistance)
  - [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- **Frontend:** HTML, CSS, and JavaScript for a responsive and interactive user interface.
-   Socket.IO for real-time communication.

## Getting Started

1. Clone this repository: `git clone https://github.com/smurtazahasan/TaleTwister.git`
2. Navigate to the project directory: cd TaleTwister
3. Install dependencies: `pip install -r requirements.txt`
4. Set up Ollama AI model (Follow instructions in [Ollama documentation](https://ollama.ai/docs/)).
5. Install desired model: `ollama pull llama3.2:latest`
6. Run the application: `python app.py`
7. Open a browser and navigate to `http://127.0.0.1:5000/` to start generating stories.

## Usage

1. Select a genre from the given options.
2. Read through the generated story and make decisions at branching points.
3. Experience the unique narrative shaped by your choices, enhanced by Ollama AI model.

## Code Structure

### Backend (Flask)
- The main entry point of the application:
  - Sets up the Flask server and Socket.IO for real-time communication.
  - Handles requests from the frontend to start stories and process user choices.
  - Integrates with the story_generator.py module for generating story content.

### Backend (Ollama)
- A modular library for story creation:
  - Contains logic for interacting with the Ollama AI model.
  - Provides functions to generate initial stories and continue narratives based on user input.
  - Supports genre-specific storytelling and dynamic branching.

### Frontend (HTML)
- The index.html file serves as the interface:
  - Users can input genres and view story updates in real time.
  - Buttons dynamically appear for decision-making at story branches.
  - Communicates with the backend via Socket.IO to provide a seamless experience.

## Current Improvements

- **Additional Genres:** Implement more genres to expand storytelling possibilities (e.g., mystery, romance, sci-fi).
- **User-defined Branching Points:** Allow users to define their own decision points within the story.
- **Save/Load Stories:** Implement functionality to save and load stories for later continuation.
- **Community Features:** Add features like sharing stories, voting on branching points, or collaborative storytelling.

## Contributing

Contributions are welcome!

1. Fork this repository.
2. Create a new branch (`git checkout -b <new-branch-name>`).
3. Make changes and commit (`git commit -m "Your commit message"`).
4. Push to the forked repository (`git push origin <new-branch-name>`).
5. Open a pull request from your forked repository back to this one.
