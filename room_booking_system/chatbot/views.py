from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .chatbot_service import get_chatbot_response

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        try:
            # Debugging: Log the logged-in user's information
            print(f"User logged in: {request.user}, Is authenticated: {request.user.is_authenticated}")

            # Parse the request body
            data = json.loads(request.body)
            user_input = data.get("message", "")
            if not user_input:
                return JsonResponse({"response": "Message is required."}, status=400)

            # Fetch the logged-in user
            logged_in_user = request.user  # Fetch the currently logged-in user (AnonymousUser if not logged in)

            # Get chatbot response
            return get_chatbot_response(user_input, logged_in_user)

        except Exception as e:
            # Handle unexpected errors
            return JsonResponse({"response": f"Error: {str(e)}"}, status=500)
    else:
        # Reject non-POST requests
        return JsonResponse({"response": "Invalid request method. Use POST."}, status=405)
