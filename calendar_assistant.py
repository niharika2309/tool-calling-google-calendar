import json
from openai import OpenAI

from authenticate import get_calendar_service

# Connect to Google Calendar and OpenAI
service = get_calendar_service()
# Local OpenAI-compatible endpoint (Qwen3.8-27B) — it ignores auth, but the SDK requires a non-empty key
client = OpenAI(base_url="http://100.117.48.99:8888/v1", api_key="none")


# This Python function creates a calendar event
def create_calendar_event(title, start_time, end_time):
    event = {
        "summary": title,
        "start": {"dateTime": start_time},
        "end": {"dateTime": end_time},
    }

    result = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return result["htmlLink"]


# Tell the LLM which tool it can use
tools = [
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
                        "description": "ISO 8601 date-time with timezone"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "ISO 8601 date-time with timezone"
                    },
                },
                "required": ["title", "start_time", "end_time"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]


# Ask the user what event to create
user_request = input("What event should I schedule? ")

response = client.chat.completions.create(
    model="Qwen3.8-27B",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a calendar assistant. "
                "Use the calendar tool when the user requests an event. "
                "Convert dates and times to ISO 8601 format with a timezone. "
                "Use America/Chicago time for Dallas events. "
                "Do not guess missing dates or times."
            ),
        },
        {"role": "user", "content": user_request},
    ],
    tools=tools,
)

# Check whether the LLM requested the tool
tool_calls = response.choices[0].message.tool_calls

if not tool_calls:
    print(response.choices[0].message.content)
else:
    for tool_call in tool_calls:
        if tool_call.function.name == "create_calendar_event":
            arguments = json.loads(tool_call.function.arguments)

            event_link = create_calendar_event(**arguments)

            print("Event created successfully!")
            print("Open your event:", event_link)