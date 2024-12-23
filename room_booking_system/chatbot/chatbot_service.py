import requests
from django.http import JsonResponse
from rooms.models import Room
from bookings.models import Booking
from django.contrib.auth.models import AnonymousUser
import logging

# Logger setup
logger = logging.getLogger(__name__)

# Wit.ai Token
WIT_AI_TOKEN = "VMSEAGIHOYNO3UPF6RIL7CJ2OVJRKUP6"

# Function to interact with Wit.ai
def get_intent_from_witai(user_input):
    try:
        headers = {"Authorization": f"Bearer {WIT_AI_TOKEN}"}
        params = {"q": user_input.strip()}
        response = requests.get("https://api.wit.ai/message", headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Wit.ai API error: {e}")

# Chatbot response logic
def get_chatbot_response(user_input, logged_in_user):
    try:
        # Step 1: Get Intent from Wit.ai
        wit_data = get_intent_from_witai(user_input)
        logger.debug(f"Wit.ai response: {wit_data}")

        intents = wit_data.get("intents", [])
        intent = intents[0]["name"] if intents else None
        user_name = logged_in_user.first_name if logged_in_user and not isinstance(logged_in_user, AnonymousUser) else "Guest"

        # Greeting Intent
        if intent == "greeting":
            return JsonResponse({"response": f"Hello {user_name}! How can I assist you today?"})

        # Book Room Intent
        elif intent == "book_room":
            rooms = Room.objects.filter(is_available=True)
            if rooms.exists():
                room_list = ", ".join([room.name for room in rooms])
                return JsonResponse({"response": f"{user_name}, the following rooms are available for booking: {room_list}."})
            else:
                return JsonResponse({"response": f"No rooms are available for booking, {user_name}."})

        # Cancel Booking Intent
        elif intent == "cancel_booking":
            if logged_in_user and logged_in_user.is_authenticated:
                user_bookings = Booking.objects.filter(user_id=logged_in_user.id, status="approved")
                if user_bookings.exists():
                    booking_details = ", ".join(
                        [f"{booking.room_id} on {booking.start_time.date()}" for booking in user_bookings]
                    )
                    return JsonResponse({"response": f"Your current bookings are: {booking_details}. Contact admin to cancel a booking."})
                else:
                    return JsonResponse({"response": f"You have no active bookings to cancel, {user_name}."})
            else:
                return JsonResponse({"response": "You must be logged in to view or cancel bookings."})

        # Search Room Intent
        elif intent == "search_room":
            entities = wit_data.get("entities", {})
            location = entities.get("location:location", [{}])[0].get("value")
            capacity = entities.get("number:capacity", [{}])[0].get("value")
            filters = {}
            if location:
                filters["location__icontains"] = location
            if capacity:
                filters["capacity__gte"] = int(capacity)
            matching_rooms = Room.objects.filter(**filters, is_available=True)
            if matching_rooms.exists():
                room_list = ", ".join([f"{room.name} ({room.location})" for room in matching_rooms])
                return JsonResponse({"response": f"The following rooms match your criteria: {room_list}."})
            else:
                return JsonResponse({"response": "No rooms match your criteria."})

        # Unknown Intent
        elif intent == "unknown":
            return JsonResponse({"response": f"Sorry, {user_name}, I cannot help with that. Please ask about room booking or availability."})

        # Fallback
        else:
            return JsonResponse({"response": f"I'm sorry, {user_name}, I didn't understand that. Can you rephrase?"})

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return JsonResponse({"response": f"Error: {str(e)}"})

