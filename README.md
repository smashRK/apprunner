# Greeting App

A simple Flask application that provides a greeting API and web interface.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

3. Open your browser and visit: `http://localhost:5000`

## API Usage

- GET `/api/greet?name=YourName`: Returns a greeting with the provided name
- If no name is provided, returns a message asking to enter a name

## Features

- Simple web interface with input field and button
- REST API endpoint for greetings
- Error handling for missing name parameter