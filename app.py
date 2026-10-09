"""
A simple chatbot-style web UI for the calendar assistant.

Run it with:
    python app.py
then open  http://127.0.0.1:5000  in your browser.

How it works:
  * Serves the chat page (templates/index.html).
  * Talks to the same AI as calendar_assistant.py.
  * When the AI asks to create an event, it creates it in your Google
    Calendar and tells the page about the result.

The command-line version (calendar_assistant.py) still works too - pick
whichever you prefer.
"""

import json

from openai import OpenAI
from flask import Flask, render_template, request, jsonify

from authenticate import get_calendar_service

# ---------------------------------------------------------------------------
# Settings - change these if you use a different AI service.
# (Keep them in sync with calendar_assistant.py.)
# ---------------------------------------------------------------------------
AI_URL = "http://100.117.48.99:8888/v1"   # where the AI lives
AI_MODEL = "Qwen3.8-27B"                  # which AI to ask
AI_KEY = "none"                           # this local AI ignores the key

client = OpenAI(base_url=AI_URL, api_key=AI_KEY)

# We connect to Google lazily (on first use) so the page always loads,
# even before you've signed in.
service = None


def get_service():
    """Connect to Google Calendar on first use (opens a browser to sign in)."""
    global service
    if service is None:
        service = get_calendar_service()
    return service


app = Flask(__name__)


def create_calendar_event(title, start_time, end_time):
    """Create a real event in your Google Calendar and return its details."""
    event = {
        "summary": title,
        "start": {"dateTime": start_time},
        "end": {"dateTime": end_time},
    }
    return get_service().events().insert(calendarId="primary", body=event).execute()


# The one tool the AI is allowed to use (same shape as calendar_assistant.py).
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Create a Google Calendar event",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "start_time": {
                        "type": "string",
                        "description": "ISO 8601 date-time with timezone",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "ISO 8601 date-time with timezone",
                    },
                },
                "required": ["title", "start_time", "end_time"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

SYSTEM_PROMPT = (
    "You are a friendly calendar assistant. "
    "When the user asks to schedule something, use the calendar tool. "
    "Convert dates and times to ISO 8601 format with the America/Chicago timezone. "
    "If a needed detail (what, when, or how long) is missing, ask for it in one short question. "
    "Never guess a missing date or time. Keep your replies short and friendly."
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("messages") or []

    if not user_message:
        return jsonify({"error": "Please type what you'd like to schedule."}), 400

    # Build the message list: instructions, then the recent conversation,
    # then the user's new message.
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history[-20:]  # keep only the last 20 turns so the list stays small
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(model=AI_MODEL, messages=messages, tools=TOOLS)
    message = response.choices[0].message
    reply = (message.content or "").strip()

    # Did the AI decide to create an event?
    event = None
    if message.tool_calls:
        for tool_call in message.tool_calls:
            if tool_call.function.name == "create_calendar_event":
                args = json.loads(tool_call.function.arguments)
                try:
                    result = create_calendar_event(**args)
                    event = {
                        "title": args.get("title"),
                        "start": args.get("start_time"),
                        "end": args.get("end_time"),
                        "link": result.get("htmlLink"),
                    }
                    reply = "Done! ✅ Your event is on the calendar - go check it."
                except Exception as exc:  # surface a friendly, readable error
                    reply = f"I tried to create that event, but Google Calendar said: {exc}"

    return jsonify({"reply": reply, "event": event})


if __name__ == "__main__":
    app.run(debug=False, port=5000)
