# Login with ChatGPT

A middleware for "Login with ChatGPT" that enables context-aware onboarding. It auto-fills user data across apps, including preferences and behaviors. Before the data is shared, users can review and edit information before sharing it with an app. While OAuth shares static profile data, such a system can retrieve dynamic user data info from ChatGPT’s memories.

## How It Works
1. **Request:** Apps send field IDs and labels (`id:label` format).
2. **Query** Selenium automates ChatGPT interactions to extract user-specific answers. This is a temporary solution until public API access to ChatGPT Memories is available.
3. **Response:** The server returns a JSON of the requested data to the middleware.

## Setup
1. Install dependencies:
   ```bash
   pip install flask flask-cors undetected-chromedriver openai python-dotenv pyopenssl
   ```
2. Configure `.env`:
   ```bash
   OPENAI_API_KEY=your_api_key
   ```
3. Run the server:
   ```bash
   python auth.py
   ```

## API Example
```bash
curl "https://localhost:5000/verify?fields=name:Full Name,email:Email Address"
```
Response:
```json
{
  "results": {
    "name": {"label": "Full Name", "question": "What's your full name?", "answer": "John Doe"},
    "email": {"label": "Email Address", "question": "What's your email?", "answer": "john@example.com"}
  },
  "timestamp": 1707600000
}
```