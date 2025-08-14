from django.shortcuts import get_object_or_404
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, BasePermission
from website.models import Paste, Language
from .serializers import PasteSerializer, LanguageSerializer
import hashlib
import random
import time
from django.utils import timezone
from datetime import timedelta
from dotenv import load_dotenv
import os
import json
import logging
from django.http import JsonResponse, StreamingHttpResponse

# Import the new duck_ai function
from .duck_ai import get_ai_response


load_dotenv()
logger = logging.getLogger(__name__)

class BotTokenPermission(BasePermission):
    """Custom permission to allow bot access with token"""
    
    def has_permission(self, request, view):
        return True

class PasteListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PasteSerializer
    permission_classes = [BotTokenPermission]  # Use custom bot permission
    def generate_unique_id(self):
        while True:
            unique_string = f"{timezone.now().timestamp()}{random.randint(0, 999999)}"
            hash_object = hashlib.sha256(unique_string.encode())
            unique_id = hash_object.hexdigest()[:6]
            if not Paste.objects.filter(id=unique_id).exists():
                return unique_id
    def create(self, request, *args, **kwargs):
        id = self.generate_unique_id()
        print(f"Generated ID: {id} (Type: {type(id)})")
        content = request.data.get('content')
        password = request.data.get('password')
        lang_id = request.data.get('language')
        print(lang_id)
        lang = get_object_or_404(Language, id=lang_id)
        expiration_days = request.data.get('expiration')
        one_time = request.data.get('one_time', False)

        if not lang_id:
            return Response({"error": "Language is required."}, status=status.HTTP_400_BAD_REQUEST)

        lang = get_object_or_404(Language, id=lang_id)

        if content:
            id = self.generate_unique_id()
            expires = None
            if expiration_days:
                expires = timezone.now() + timedelta(days=int(expiration_days))
            paste = Paste.objects.create(id=id, salt=None, iv=None, ciphertext=content, lang=lang, expires=expires, one_time=one_time)
            pastes_cookie = request.COOKIES.get('pasteHistory', '')
            if pastes_cookie:
                pastes_list = pastes_cookie.split(',')
                if id not in pastes_list:
                    pastes_list.append(id)
            else:
                pastes_list = [id]
            response = Response({"id": id}, status=status.HTTP_201_CREATED)
            response.set_cookie('pasteHistory', ','.join(pastes_list), max_age=31536000)
            return response
        return Response({"error": "Content is required."}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        pastes_cookie = self.request.COOKIES.get('pasteHistory', '')
        pastes_list = pastes_cookie.split(',') if pastes_cookie else []
        return Paste.objects.filter(id__in=pastes_list)

    def get(self, request, *args, **kwargs):
        pastes = self.get_queryset()
        paste_list = [{"id": paste.id, "created": paste.created} for paste in pastes]
        return Response(paste_list)


class PasteRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Paste.objects.all()
    serializer_class = PasteSerializer


class LanguageListAPIView(generics.ListAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [BotTokenPermission]  # Use custom bot permission

# Add the new chatbot view
class ChatbotAPIView(views.APIView):
    permission_classes = [BotTokenPermission]

    def stream_ai_response(self, prompt):
        """
        Generator function to stream the AI response, ensuring all chunks are
        properly formatted as JSON strings.
        """
        try:
            logger.info("Streaming AI response...")
            # Send an initial comment to kick-start the event stream and flush proxies
            yield ": connected" + "\n\n"
            for chunk in get_ai_response(prompt):
                # Ensure the chunk is a string and not empty before processing.
                if isinstance(chunk, str) and chunk.strip():
                    # Always wrap the chunk in a JSON object.
                    response_data = {'response_chunk': chunk}
                    yield f"data: {json.dumps(response_data)}\n\n"
                else:
                    # Log and skip non-string or empty chunks.
                    logger.warning(f"Skipping invalid chunk: {chunk}")
            
            # Signal the end of the stream.
            yield f"data: {json.dumps({'end_of_stream': True})}\n\n"
            logger.info("Finished streaming AI response.")

        except Exception as e:
            logger.error(f"Error during streaming: {e}", exc_info=True)
            # Yield a JSON-formatted error.
            error_data = {'error': str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"

    def post(self, request, *args, **kwargs):
        logger.info("ChatbotAPIView received a POST request.")
        paste_id = request.data.get('paste_id')
        question = request.data.get('question')

        if not all([paste_id, question]):
            logger.error("Missing paste_id or question.")
            return Response({"error": "paste_id and question are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            logger.info(f"Fetching paste with id: {paste_id}")
            paste = Paste.objects.get(id=paste_id)
            logger.info("Paste fetched successfully.")
            prompt = (
                f"Please answer the following question about the provided code. "
                f"Keep your answer concise and to the point. "
                f"Use Markdown for formatting, especially for code snippets, and use lists to break up long paragraphs.\n\n"
                f"Here is the code:\n\n{paste.ciphertext}\n\n"
                f"Question: {question}"
            )
            
            response = StreamingHttpResponse(
                self.stream_ai_response(prompt),
                content_type='text/event-stream; charset=utf-8'
            )
            # Required headers to avoid buffering and enable incremental flush
            response['Cache-Control'] = 'no-cache, no-transform'
            response['X-Accel-Buffering'] = 'no'
            response['Connection'] = 'keep-alive'
            return response
            
        except Paste.DoesNotExist:
            logger.error(f"Paste with id {paste_id} not found.")
            return JsonResponse({"error": "Paste not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def test_view(request):
    return JsonResponse({"status": "ok"})
