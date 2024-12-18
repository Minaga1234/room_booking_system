import openai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatbotLog
from rooms.models import Room

# Set your OpenAI API key
openai.api_key = 'your_openai_api_key'

class ChatbotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_query = request.data.get('query')
        user = request.user

        try:
            # Generate response from OpenAI
            response = openai.Completion.create(
                engine="text-davinci-003",  # You can use other engines like "gpt-3.5-turbo"
                prompt=user_query,
                max_tokens=150
            )
            chatbot_response = response.choices[0].text.strip()

            # Log the query and response
            ChatbotLog.objects.create(user=user, query=user_query, response=chatbot_response)

            return Response({"response": chatbot_response})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def recommend_rooms(self, query):
        # Example: Recommend available rooms based on query
        available_rooms = Room.objects.filter(is_available=True).order_by('capacity')[:5]
        recommendations = [f"{room.name} - {room.location}" for room in available_rooms]
        return "Recommended Rooms: " + ", ".join(recommendations)

    def post(self, request):
        user_query = request.data.get('query')

        if "recommend" in user_query.lower():
            recommendations = self.recommend_rooms(user_query)
            return Response({"response": recommendations})
        
        # Existing OpenAI logic for other queries
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=user_query,
            max_tokens=150
        )
        chatbot_response = response.choices[0].text.strip()

        ChatbotLog.objects.create(user=request.user, query=user_query, response=chatbot_response)
        return Response({"response": chatbot_response})