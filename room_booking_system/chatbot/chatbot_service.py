import requests
from django.http import JsonResponse
from rooms.models import Room
from bookings.models import Booking
from django.contrib.auth.models import AnonymousUser
from datetime import datetime
from django.utils.timezone import make_aware
import pytz
import logging
import re

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

# Parse datetime entities
def parse_datetime(datetime_entity):
    try:
        start_time_str = datetime_entity.get("from", {}).get("value")
        end_time_str = datetime_entity.get("to", {}).get("value")
        logger.debug(f"Datetime entity 'from': {start_time_str}, 'to': {end_time_str}")

        if not start_time_str or not end_time_str:
            raise ValueError("Missing 'from' or 'to' datetime values.")

        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)

        # Make datetime timezone-aware
        if start_time.tzinfo is None:
            start_time = make_aware(start_time, pytz.UTC)
        if end_time.tzinfo is None:
            end_time = make_aware(end_time, pytz.UTC)

        logger.debug(f"Parsed datetime: Start Time: {start_time}, End Time: {end_time}")
        return start_time, end_time
    except Exception as e:
        logger.error(f"Error parsing datetime entity: {e}")
        return None, None

# Book a room
def book_room(user_input, logged_in_user):
    try:
        if not logged_in_user or isinstance(logged_in_user, AnonymousUser):
            logger.debug("User is not logged in.")
            return JsonResponse({"response": "You must be logged in to book a room. Please log in and try again."})

        wit_data = get_intent_from_witai(user_input)
        entities = wit_data.get("entities", {})
        logger.debug(f"Extracted entities from Wit.ai: {entities}")

        room_name = entities.get("room_name:room_name", [{}])[0].get("value")
        datetime_entities = entities.get("wit$datetime:datetime", [])
        capacity = entities.get("capacity:capacity", [{}])[0].get("value")
        degree_major = entities.get("degree_major:degree_major", [{}])[0].get("value")
        purpose = entities.get("purpose:purpose", [{}])[0].get("value")

        logger.debug(f"Extracted values - Room: {room_name}, Datetime: {datetime_entities}, Capacity: {capacity}, "
                     f"Degree Major: {degree_major}, Purpose: {purpose}")

        if not (room_name and datetime_entities and capacity and degree_major and purpose):
            logger.debug("Missing required booking details.")
            return JsonResponse({
                "response": "Missing details. Provide all details as: 'Book [Room] from [Time] for [Capacity] in [Major] for [Purpose].'"
            })

        # Parse datetime entities
        start_time, end_time = parse_datetime(datetime_entities[0])
        if not start_time or not end_time:
            logger.debug("Invalid datetime parsing.")
            return JsonResponse({
                "response": "Invalid time format. Please provide valid start and end times. Example: 'From 2 PM to 4 PM today.'"
            })

        # Parse capacity
        capacity_match = re.search(r"\d+", capacity)
        if capacity_match:
            capacity = int(capacity_match.group())
            logger.debug(f"Parsed capacity: {capacity}")
        else:
            logger.debug("Capacity parsing failed.")
            return JsonResponse({"response": "Invalid capacity. Provide a valid number of participants."})

        # Check overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            room__name__iexact=room_name,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
        logger.debug(f"Overlapping bookings check: {overlapping_bookings.exists()}")
        if overlapping_bookings.exists():
            return JsonResponse({
                "response": f"The room '{room_name}' is already booked during the specified time. Please choose another time or room."
            })

        # Check room availability
        room = Room.objects.filter(
            name__iexact=room_name,
            is_available=True,
            capacity__gte=capacity
        ).first()
        logger.debug(f"Room availability check: {room}")

        if not room:
            return JsonResponse({"response": f"Room '{room_name}' is not available for the specified time."})

        # Create booking
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

            logger.debug(f"Booking created successfully for room '{room_name}' from {start_time} to {end_time}.")
            return JsonResponse({
                "response": f"Room '{room_name}' booked from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')} for {purpose}."
            })
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            return JsonResponse({"response": "An error occurred. Please try again."})

    except Exception as e:
        logger.error(f"Unexpected error in booking: {e}")
        return JsonResponse({"response": "An error occurred while processing your request. Please try again."})

# Chatbot response logic
def get_chatbot_response(user_input, logged_in_user):
    try:
        wit_data = get_intent_from_witai(user_input)
        intents = wit_data.get("intents", [])
        intent = intents[0]["name"] if intents else None

        user_name = (
            logged_in_user.username if logged_in_user and not isinstance(logged_in_user, AnonymousUser) else "Guest"
        )

        logger.debug(f"Detected intent: {intent}, User: {user_name}")

        if intent == "greeting":
            return JsonResponse({"response": f"Hello {user_name}! How can I assist you today?"})

        elif intent == "check_room_availability":
            rooms = Room.objects.filter(is_available=True)
            logger.debug(f"Available rooms: {rooms}")
            if rooms.exists():
                room_list = ", ".join([room.name for room in rooms])
                return JsonResponse({"response": f"The following rooms are currently available: {room_list}."})
            else:
                return JsonResponse({"response": "No rooms are currently available."})

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

        elif intent == "search_room":
            entities = wit_data.get("entities", {})
            capacity = entities.get("capacity:capacity", [{}])[0].get("value")
            location = entities.get("location:location", [{}])[0].get("value")

            filters = {}
            if capacity:
                capacity_match = re.search(r"\d+", capacity)
                if capacity_match:
                    filters["capacity__gte"] = int(capacity_match.group())
                else:
                    return JsonResponse({"response": "Invalid capacity value. Please provide a valid number."})
            if location:
                filters["location__icontains"] = location

            matching_rooms = Room.objects.filter(**filters)
            if matching_rooms.exists():
                room_list = ", ".join([f"{room.name} ({room.location})" for room in matching_rooms])
                return JsonResponse({"response": f"The following rooms match your criteria: {room_list}."})
            else:
                return JsonResponse({"response": "No rooms match your criteria. Please try different filters."})

        elif intent == "book_room_full_process":
            return book_room(user_input, logged_in_user)

        elif intent == "cancel_booking":
            if logged_in_user and logged_in_user.is_authenticated:
                user_bookings = Booking.objects.filter(user_id=logged_in_user.id, status="approved")
                logger.debug(f"User bookings: {user_bookings}")
                if user_bookings.exists():
                    booking_details = ", ".join(
                        [f"{booking.room.name} on {booking.start_time.date()}" for booking in user_bookings]
                    )
                    return JsonResponse({"response": f"Your current bookings are: {booking_details}. Contact admin to cancel a booking."})
                else:
                    return JsonResponse({"response": f"You have no active bookings to cancel, {user_name}."})
            else:
                return JsonResponse({"response": "You must be logged in to view or cancel bookings."})

        else:
            return JsonResponse({"response": f"I'm sorry, {user_name}, I didn't understand that. Can you rephrase?"})

    except Exception as e:
        logger.error(f"Unexpected error in chatbot response: {e}", exc_info=True)
        return JsonResponse({"response": f"Error: {str(e)}"}, status=500)