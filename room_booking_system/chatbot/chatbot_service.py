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
        logger.debug(f"Wit.ai response: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Wit.ai API error: {e}")
        raise Exception(f"Wit.ai API error: {e}")

# Normalize room names for better matching
def normalize_room_name(name):
    return " ".join(name.strip().lower().split())

# Search for room by name with partial match support
def find_room_by_name(room_name):
    normalized_name = normalize_room_name(room_name)
    return Room.objects.filter(name__icontains=normalized_name).first()

# Chatbot response logic
def get_chatbot_response(user_input, logged_in_user):
    try:
        # Step 1: Get Intent from Wit.ai
        wit_data = get_intent_from_witai(user_input)
        logger.debug(f"Parsed Wit.ai data: {wit_data}")

        intents = wit_data.get("intents", [])
        intent = intents[0]["name"] if intents else None

        # Use username from the database
        user_name = (
            logged_in_user.username if logged_in_user and not isinstance(logged_in_user, AnonymousUser) else "Guest"
        )

        logger.debug(f"Detected intent: {intent}, User: {user_name}")

        # Greeting Intent
        if intent == "greeting":
            return JsonResponse({"response": f"Hello {user_name}! How can I assist you today?"})

        # Book Room Intent
        elif intent == "book_room":
            if not logged_in_user or isinstance(logged_in_user, AnonymousUser):
                return JsonResponse({"response": "You must be logged in to book a room. Please log in and try again."})

            return JsonResponse({"response": "Which floor is more convenient for you?", "next_step": "select_floor"})

        # Check Room Availability Intent
        elif intent == "check_room_availability":
            rooms = Room.objects.filter(is_available=True)
            if rooms.exists():
                room_list = ", ".join([room.name for room in rooms])
                return JsonResponse({"response": f"The following rooms are currently available: {room_list}."})
            else:
                return JsonResponse({"response": "No rooms are currently available."})

        # Check Room Occupancy Intent
        elif intent == "check_room_occupancy":
            entities = wit_data.get("entities", {})
            room_name = entities.get("room_name:room_name", [{}])[0].get("value")

            if not room_name:
                return JsonResponse({"response": "Please specify the room name to check its occupancy."})

            # Normalize input and compare
            room_name = room_name.strip().lower()
            room = Room.objects.filter(name__iexact=room_name).first()

            if room:
                if room.is_available:
                    return JsonResponse({"response": f"The {room.name} is currently available."})
                else:
                    return JsonResponse({"response": f"The {room.name} is currently occupied."})
            else:
                available_rooms = ", ".join(Room.objects.values_list("name", flat=True))
                return JsonResponse({"response": f"I couldn't find a room named {room_name}. Available rooms are: {available_rooms}"})

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
            capacity = entities.get("capacity:capacity", [{}])[0].get("value")
            location = entities.get("location:location", [{}])[0].get("value")

            filters = {}
            if capacity:
                try:
                    capacity = int(capacity)
                    filters["capacity__gte"] = capacity
                except ValueError:
                    logger.error(f"Invalid capacity value: {capacity}")
                    return JsonResponse({"response": "Invalid capacity value. Please provide a valid number."})

            if location:
                filters["location__icontains"] = location

            matching_rooms = Room.objects.filter(**filters, is_available=True)
            if matching_rooms.exists():
                room_list = ", ".join([f"{room.name} ({room.location})" for room in matching_rooms])
                return JsonResponse({"response": f"The following rooms match your criteria: {room_list}."})
            else:
                return JsonResponse({"response": "No rooms match your criteria. Please try different filters."})

        # Unknown Intent
        elif intent == "unknown":
            return JsonResponse({"response": f"Sorry, {user_name}, I cannot help with that. Please ask about room booking or availability."})

        # Fallback
        else:
            return JsonResponse({"response": f"I'm sorry, {user_name}, I didn't understand that. Can you rephrase?"})

    except Exception as e:
        logger.error(f"Unexpected error in chatbot response: {e}", exc_info=True)
        return JsonResponse({"response": f"Error: {str(e)}"}, status=500)
