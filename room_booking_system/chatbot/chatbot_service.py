import requests
from flask import jsonify
from django.http import JsonResponse
from rooms.models import Room  # Corrected import for the Room model
from bookings.models import Booking
from users.models import CustomUser

# Wit.ai Token
WIT_AI_TOKEN = "VMSEAGIHOYNO3UPF6RIL7CJ2OVJRKUP6"

# Function to interact with Wit.ai
def get_intent_from_witai(user_input):
    headers = {"Authorization": f"Bearer {WIT_AI_TOKEN}"}
    params = {"q": user_input}
    response = requests.get("https://api.wit.ai/message", headers=headers, params=params)
    return response.json()

# Function to get chatbot response
def get_chatbot_response(user_input):
    try:
        # Step 1: Get Intent from Wit.ai
        wit_data = get_intent_from_witai(user_input)
        intent = wit_data.get("intents", [])[0]["name"] if wit_data.get("intents") else None

        # Step 2: Generate Response Based on Intent
        if intent == "greeting":
            return JsonResponse({"response": "Hello! How can I assist you today?"})

        elif intent == "book_room":
            rooms = Room.objects.filter(is_available=True)  # Corrected to Room
            if rooms.exists():
                return JsonResponse({"response": "Rooms are available for booking. Please visit the booking section."})
            else:
                return JsonResponse({"response": "Currently, no rooms are available for booking."})

        elif intent == "check_availability":
            available_rooms = Room.objects.filter(is_available=True)  # Corrected to Room
            return JsonResponse({"response": f"There are {available_rooms.count()} rooms available right now."})

        elif intent == "cancel_booking":
            return JsonResponse({"response": "To cancel a booking, please visit the 'My Bookings' section."})

        else:
            return JsonResponse({"response": "I'm sorry, I didn't understand that. Can you rephrase?"})

    except Exception as e:
        return JsonResponse({"response": f"Error: {str(e)}"})
