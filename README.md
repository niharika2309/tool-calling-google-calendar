# tool-calling-google-calendar

A small project that shows **tool calling** in action: you talk to an AI in plain English, and it creates a real event in your **Google Calendar**.

## What is "tool calling"?

By itself, an AI can only produce text. It can't open your calendar or click anything. **Tool calling** lets you hand the AI a real tool — here, "create a Google Calendar event" — and let the AI decide when and how to use it.

The flow is simple:

1. **We tell the AI what tool it has.** We describe a tool called `create_calendar_event` and what it needs as input (a title, a start time, and an end time).
2. **You make a request in plain English.** For example: *"Schedule a 30-minute coffee chat with Sam on Friday at 2:00 PM."*
3. **The AI decides to use the tool.** Instead of just talking, it replies by asking to call `create_calendar_event`, and fills in the title, start time, and end time for you.
4. **The program runs the tool.** It creates a real event in your Google Calendar.
5. **You get a link** to the event you just created.

The whole idea in one line: **the AI does the thinking, the code does the doing.**

## What's in this folder

| File | What it does |
| --- | --- |
| `calendar_assistant.py` | The main program. Wires everything together and runs the conversation. |
| `authenticate.py` | Handles the one-time Google sign-in (OAuth) so the program is allowed to touch your calendar. |
| `app.py` | A small web server that powers the chatbot interface (optional — the command-line version above still works). |
| `templates/index.html` | The chatbot page you see in the browser. |
| `credentials.json` | Your Google app credentials. You download this from Google Cloud. **Secret — never shared.** |
| `token.json` | A saved sign-in token, created automatically the first time you run it. **Secret — never shared.** |
| `.gitignore` | Tells git to keep the secret files above out of the repository. |

## Setup (one time)

You'll need two things: a **Google Cloud** project and a running **AI** (any OpenAI-compatible API).

### 1. Connect your Google Calendar

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a project.
2. In that project, enable the **Google Calendar API** (*APIs & Services → Enable APIs*, then search for "Calendar API").
3. Under *APIs & Services → Credentials*, click **Create Credentials → OAuth client ID**, and choose the **Desktop app** type.
4. Download the JSON file it gives you and save it in this folder as **`credentials.json`**.

The first time you run the program, a browser window opens for you to sign in and approve access. After that, the sign-in is remembered in `token.json` and you won't be asked again.

### 2. Install the Python packages

From this folder, in your terminal:

```bash
pip install -r requirements.txt
```

This installs the four packages the project needs (the OpenAI client, and the Google sign-in / Calendar libraries).

### 3. Point it at an AI

The program talks to an AI through the OpenAI API. By default it points at a local server running the Qwen model:

```python
client = OpenAI(base_url="http://100.117.48.99:8888/v1", api_key="none")
```

If you use a different AI (for example, the real OpenAI service), change that line in `calendar_assistant.py` — the `base_url`, the `api_key`, and the model name.

## Run it

```bash
python calendar_assistant.py
```

When it asks, type what you'd like to schedule:

```
What event should I schedule?  Schedule a 30-minute coffee chat with Sam on Friday at 2:00 PM
```

If the AI decides to create the event, the program prints a link you can open in your browser.

## Run the web UI (optional)

There's also a simple **chatbot-style web interface** that does the same thing in your browser:

```bash
python app.py
```

Then open **http://127.0.0.1:5000**. Type what you'd like to schedule and hit **Send** (or press Enter). When the assistant creates the event, it confirms it and shows you a preview card with a link to open it in Google Calendar. Use the **Refresh** button to start a fresh conversation.

If the assistant is missing a detail (for example, you didn't say *when*), it will ask a short question — just answer it in the box and it'll pick up where it left off.

## A note on security

`credentials.json` and `token.json` let someone control your calendar. They are listed in `.gitignore`, so git will never commit them. **Don't remove them from `.gitignore`, and don't upload or share those files.**
