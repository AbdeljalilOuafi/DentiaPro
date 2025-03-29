import requests
import json
from decouple import config
from rest_framework.exceptions import APIException

class GeminiAPIError(APIException):
    status_code = 503  # Service Unavailable
    default_detail = "Error communicating with AI service"

def get_response(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    api_key = config("GEMINI_API_KEY")  
    url_with_key = f"{url}?key={api_key}"

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
    "contents": [
        {
        "parts": [{"text": prompt}]
        }
    ]
    }

    try:
        response = requests.post(url_with_key, headers=headers, data=json.dumps(data))

        # Raise HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()

        # Parse JSON response
        response_json = response.json()

        # Extract text from the first candidate
        answer = response_json['candidates'][0]['content']['parts'][0]['text']
        return answer

    except requests.exceptions.RequestException as e:
        error_message = f"Gemini API error: {str(e)}"
        raise GeminiAPIError(detail=error_message)
    except (json.JSONDecodeError, KeyError) as e:
        error_message = "Invalid response from AI service"
        raise GeminiAPIError(detail=error_message)