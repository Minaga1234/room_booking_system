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
        logger.debug(f"Wit.ai response: {wit_data}")

        intents = wit_data.get("intents", [])
        intent = intents[0]["name"] if intents else None
        user_name = (
            logged_in_user.first_name if logged_in_user and not isinstance(logged_in_user, AnonymousUser) else "Guest"
        )

        # Greeting Intent
        if intent == "greeting":
            return JsonResponse({"response": f"Hello {user_name}! How can I assist you today?"})

        
        # Book Room Intent
        elif intent in ["book_room", "check_room_availability"]:
            synonyms = ["free", "empty", "available"]
            if any(word in user_input.lower() for word in synonyms):
                rooms = Room.objects.filter(is_available=True)
                if rooms.exists():
                    room_list = ", ".join([room.name for room in rooms])
                    return JsonResponse({"response": f"{user_name}, the following rooms are free and available for booking: {room_list}."})
                else:
                    return JsonResponse({"response": f"No rooms are currently free, {user_name}."})

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
            # Extract criteria from Wit.ai entities
            entities = wit_data.get("entities", {})
            capacity = entities.get("capacity:capacity", [{}])[0].get("value")  # Extract capacity if provided
            location = entities.get("location:location", [{}])[0].get("value")  # Extract location if provided
            synonyms = ["free", "available", "empty"]  # Add common synonyms for free rooms

            # Initialize filters dictionary
            filters = {}

            # Add capacity filter if capacity is specified
            if capacity:
                try:
                    capacity = int(capacity)  # Ensure capacity is an integer
                    filters["capacity__gte"] = capacity  # Filter for rooms with at least the given capacity
                except ValueError:
                    return JsonResponse({"response": "Invalid capacity value. Please provide a valid number."})

            # Add location filter if location is specified
            if location:
                filters["location__icontains"] = location  # Perform a case-insensitive search for location

            # Handle synonyms for free or available rooms
            if any(word in user_input.lower() for word in synonyms):
                filters["is_available"] = True  # Filter for rooms that are currently available

            # Query the Room model with the constructed filters
            matching_rooms = Room.objects.filter(**filters)

            # If matching rooms exist, construct the response
            if matching_rooms.exists():
                room_list = ", ".join([f"{room.name} ({room.location})" for room in matching_rooms])
                return JsonResponse({"response": f"The following rooms match your criteria: {room_list}."})
            else:
                # If no rooms match, return a no-match response
                return JsonResponse({"response": "No rooms match your criteria. Please try different filters."})
                            
        # Identify Room Intent
        elif intent == "identify_room":
            entities = wit_data.get("entities", {})
            room_name = entities.get("room_name:room_name", [{}])[0].get("value")

            if not room_name:
                return JsonResponse({"response": "Please specify the room name you want to inquire about."})

            room = find_room_by_name(room_name)

            if room:
                return JsonResponse({"response": f"Yes, {room.name} exists and is located on the {room.location}."})
            else:
                available_rooms = ", ".join(Room.objects.values_list("name", flat=True))
                return JsonResponse({"response": f"No, I couldn't find a room named '{room_name}'. Available rooms are: {available_rooms}"})

        # Check Room Occupancy Intent
        elif intent == "check_room_occupancy":
            entities = wit_data.get("entities", {})
            room_name = entities.get("room_name:room_name", [{}])[0].get("value")

            if not room_name:
                return JsonResponse({"response": "Please specify the room name to check its occupancy."})

            room = find_room_by_name(room_name)

            if room:
                if room.is_available:
                    return JsonResponse({"response": f"The {room.name} is currently free and available for booking."})
                else:
                    return JsonResponse({"response": f"The {room.name} is currently occupied."})
            else:
                available_rooms = ", ".join(Room.objects.values_list("name", flat=True))
                return JsonResponse({"response": f"I couldn't find a room named '{room_name}'. Available rooms are: {available_rooms}"})

        # List Available Rooms
        elif intent in ["book_room", "check_room_availability"]:
            synonyms = ["free", "empty", "available"]
            if any(word in user_input.lower() for word in synonyms):
                rooms = Room.objects.filter(is_available=True)
                if rooms.exists():
                    room_list = ", ".join([room.name for room in rooms])
                    return JsonResponse({"response": f"{user_name}, the following rooms are free and available for booking: {room_list}."})
                else:
                    return JsonResponse({"response": f"No rooms are currently free, {user_name}."})

        # Unknown Intent
        elif intent == "unknown":
            return JsonResponse({"response": f"Sorry, {user_name}, I cannot help with that. Please ask about room booking or availability."})

        # Fallback
        else:
            return JsonResponse({"response": f"I'm sorry, {user_name}, I didn't understand that. Can you rephrase?"})

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return JsonResponse({"response": f"Error: {str(e)}"})