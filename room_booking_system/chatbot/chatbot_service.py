import requests
from django.http import JsonResponse
from rooms.models import Room  # Import for room-related queries
from bookings.models import Booking  # Import for booking-related queries
from users.models import CustomUser  # Import for user-related queries
from django.contrib.auth.models import AnonymousUser

# Wit.ai Token
WIT_AI_TOKEN = "VMSEAGIHOYNO3UPF6RIL7CJ2OVJRKUP6"

# Function to interact with Wit.ai
def get_intent_from_witai(user_input):
    """
    Get intent and entities from Wit.ai
    """
    headers = {"Authorization": f"Bearer {WIT_AI_TOKEN}"}
    params = {"q": user_input}
    response = requests.get("https://api.wit.ai/message", headers=headers, params=params)
    return response.json()

# Function to get chatbot response
def get_chatbot_response(user_input, logged_in_user):
    try:
        # Step 1: Get Intent from Wit.ai
        wit_data = get_intent_from_witai(user_input)
        intent = wit_data.get("intents", [])[0]["name"] if wit_data.get("intents") else None

        # Step 2: Fetch user details
        user_name = "Guest"
        if not isinstance(logged_in_user, AnonymousUser):
            user_name = logged_in_user.first_name or logged_in_user.username

        # Step 3: Generate Response Based on Intent
        if intent == "greeting":
            return JsonResponse({"response": f"Hello {user_name}! How can I assist you today?"})

        elif intent == "book_room":
            rooms = Room.objects.filter(is_available=True)  # Query all available rooms
            if rooms.exists():
                room_list = ", ".join([room.name for room in rooms])
                return JsonResponse({"response": f"{user_name}, the following rooms are available for booking: {room_list}."})
            else:
                return JsonResponse({"response": f"Currently, no rooms are available for booking, {user_name}."})

        elif intent == "check_availability":
            available_rooms = Room.objects.filter(is_available=True)  # Query all available rooms
            if available_rooms.exists():
                room_list = ", ".join([room.name for room in available_rooms])
                return JsonResponse({"response": f"The following rooms are available: {room_list}."})
            else:
                return JsonResponse({"response": "No rooms are currently available for booking."})

        elif intent == "cancel_booking":
            user_bookings = Booking.objects.filter(user_id=logged_in_user.id, status='approved')
            if user_bookings.exists():
                booking_details = ", ".join(
                    [f"Room {booking.room_id} from {booking.start_time} to {booking.end_time}" for booking in user_bookings]
                )
                return JsonResponse({"response": f"{user_name}, your approved bookings are: {booking_details}"})
            else:
                return JsonResponse({"response": f"You have no active bookings to cancel, {user_name}."})

        elif intent == "search_room":
            # Extract criteria from Wit.ai entities (if available)
            location = wit_data.get("entities", {}).get("location:location", [{}])[0].get("value")
            capacity = wit_data.get("entities", {}).get("number:capacity", [{}])[0].get("value")
            availability = wit_data.get("entities", {}).get("availability:availability", [{}])[0].get("value")

            # Build the query based on the extracted criteria
            filters = {}
            if location:
                filters["location__icontains"] = location  # Case-insensitive match
            if capacity:
                filters["capacity__gte"] = int(capacity)  # Greater than or equal to capacity
            if availability == "available":
                filters["is_available"] = True

            # Query the Room model
            matching_rooms = Room.objects.filter(**filters)
            if matching_rooms.exists():
                room_list = ", ".join([f"{room.name} ({room.location})" for room in matching_rooms])
                return JsonResponse({"response": f"The following rooms match your criteria: {room_list}."})
            else:
                return JsonResponse({"response": "No rooms match your criteria. Please try different filters."})

        elif intent == "unknown":  # Handling for unknown intent
            return JsonResponse({"response": f"I'm sorry, {user_name}, I can't help with that. Please ask about room bookings or availability."})

        else:  # Fallback for when no intent is detected
            return JsonResponse({"response": f"I'm sorry, {user_name}, I didn't understand that. Can you rephrase?"})

    except Exception as e:
        return JsonResponse({"response": f"Error: {str(e)}"})
