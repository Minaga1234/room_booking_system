from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .chatbot_service import get_chatbot_response

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_input = data.get("message", "")
            if not user_input:
                return JsonResponse({"response": "Message is required."}, status=400)

            # Get chatbot response
            return get_chatbot_response(user_input)

        except Exception as e:
            return JsonResponse({"response": f"Error: {str(e)}"}, status=500)
    else:
        return JsonResponse({"response": "Invalid request method. Use POST."}, status=405)

# Create your views here.
