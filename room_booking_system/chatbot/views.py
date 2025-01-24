import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from .chatbot_service import get_chatbot_response  # Import chatbot logic

# Setup logger
logger = logging.getLogger(__name__)

@csrf_exempt
@ensure_csrf_cookie
def chatbot_api(request):
    """
    API endpoint for the chatbot.
    """
    if request.method == "POST":
        try:
            # Log request details for debugging
            logger.debug(f"Request Headers: {request.headers}")
            logger.debug(f"Session Key: {request.session.session_key}")
            logger.debug(f"Session Data: {dict(request.session.items())}")
            logger.debug(f"User: {request.user}, Authenticated: {request.user.is_authenticated}")
            logger.debug(f"Request User Object: {request.user}")
            logger.debug(f"Is Authenticated: {request.user.is_authenticated}")


            # Parse the request body
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"response": "Invalid JSON format."}, status=400)

            # Extract the user message
            user_input = data.get("message", "").strip()
            if not user_input:
                return JsonResponse({"response": "Message is required."}, status=400)

            # Fetch the logged-in user
            logged_in_user = request.user if request.user.is_authenticated else None
            logger.debug(f"Logged-in User: {logged_in_user}")
            
            # Generate chatbot response
            chatbot_response = get_chatbot_response(user_input, logged_in_user)
            return chatbot_response

        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=True)
            return JsonResponse({"response": f"Error: {str(e)}"}, status=500)
    else:
        return JsonResponse({"response": "Invalid request method. Use POST."}, status=405)
