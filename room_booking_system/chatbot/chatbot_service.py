import requests
from django.http import JsonResponse
from rooms.models import Room
from bookings.models import Booking
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from datetime import datetime
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

def book_room(user_input, logged_in_user):
    try:
        if not logged_in_user or isinstance(logged_in_user, AnonymousUser):
            return JsonResponse({"response": "You must be logged in to book a room. Please log in and try again."})

        wit_data = get_intent_from_witai(user_input)
        entities = wit_data.get("entities", {})
        room_name = entities.get("room_name:room_name", [{}])[0].get("value")
        datetime_entities = entities.get("wit$datetime:datetime", [])
        capacity = entities.get("capacity:capacity", [{}])[0].get("value")
        degree_major = entities.get("degree_major:degree_major", [{}])[0].get("value")
        purpose = entities.get("purpose:purpose", [{}])[0].get("value")

        # Validate Fields
        if not (room_name and datetime_entities and capacity and degree_major and purpose):
            return JsonResponse({"response": "Missing details. Provide all details as: 'Book [Room] from [Time] for [Capacity] in [Major] for [Purpose].'"})

        # Parse Times
        try:
            start_time = datetime.fromisoformat(datetime_entities[0]["from"]["value"])
            end_time = datetime.fromisoformat(datetime_entities[0]["to"]["value"])
        except (KeyError, ValueError):
            return JsonResponse({"response": "Invalid time format. Provide a valid start and end time."})

        # Parse Capacity
        try:
            import re
            capacity_match = re.search(r"\d+", capacity)
            if capacity_match:
                capacity = int(capacity_match.group())
            else:
                raise ValueError("No valid number found in capacity.")
        except ValueError:
            return JsonResponse({"response": "Invalid capacity. Provide a valid number of participants."})

        # Room Availability
        room = Room.objects.filter(
            name__iexact=room_name,
            is_available=True,
            capacity__gte=capacity
        ).exclude(
            bookings__start_time__lt=end_time,
            bookings__end_time__gt=start_time
        ).first()

        if not room:
            return JsonResponse({"response": f"Room '{room_name}' is not available for the specified time."})

        # Create Booking
        try:
            Booking.objects.create(
                room=room,
                user=logged_in_user,
                start_time=start_time,
                end_time=end_time,
                purpose=purpose,
                status="approved",
            )
            room.is_available = False
            room.save()

            return JsonResponse({"response": f"Room '{room_name}' booked from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')} for {purpose}."})
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            return JsonResponse({"response": "An error occurred. Please try again."})

    except Exception as e:
        logger.error(f"Unexpected error in booking: {e}")
        return JsonResponse({"response": "An error occurred while processing your request. Please try again."})

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

        # Check Room Availability Intent
        elif intent == "check_room_availability":
            rooms = Room.objects.filter(is_available=True)
            if rooms.exists():
                room_list = ", ".join([room.name for room in rooms])
                return JsonResponse({"response": f"The following rooms are currently available: {room_list}."})
            else:
                return JsonResponse({"response": "No rooms are currently available."})

        # Book Room Full Process Intent
        elif intent == "book_room_full_process":
            return book_room(user_input, logged_in_user)

        # Cancel Booking Intent
        elif intent == "cancel_booking":
            if logged_in_user and logged_in_user.is_authenticated:
                user_bookings = Booking.objects.filter(user_id=logged_in_user.id, status="approved")
                if user_bookings.exists():
                    booking_details = ", ".join(
                        [f"{booking.room.name} on {booking.start_time.date()}" for booking in user_bookings]
                    )
                    return JsonResponse({"response": f"Your current bookings are: {booking_details}. Contact admin to cancel a booking."})
                else:
                    return JsonResponse({"response": f"You have no active bookings to cancel, {user_name}."})
            else:
                return JsonResponse({"response": "You must be logged in to view or cancel bookings."})

        # Fallback Intent
        else:
            return JsonResponse({"response": f"I'm sorry, {user_name}, I didn't understand that. Can you rephrase?"})

    except Exception as e:
        logger.error(f"Unexpected error in chatbot response: {e}", exc_info=True)
        return JsonResponse({"response": f"Error: {str(e)}"}, status=500)
