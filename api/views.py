from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, BasePermission
from website.models import Paste, Language
from .serializers import PasteSerializer, LanguageSerializer
import hashlib
import random
from django.utils import timezone
from datetime import timedelta
from dotenv import load_dotenv
import os


load_dotenv()

class BotTokenPermission(BasePermission):
    """Custom permission to allow bot access with token"""
    
    def has_permission(self, request, view):
        # Allow if bot token is present
        bot_token = request.headers.get('X-Bot-Token')
        if bot_token == os.getenv("BOT_TOKEN"):
            return True
        # Also allow regular requests (for web interface)
        return True

class PasteListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PasteSerializer
    permission_classes = [BotTokenPermission]  # Use custom bot permission
    def generate_unique_id(self):
        while True:
            unique_string = f"{timezone.now().timestamp()}{random.randint(0, 999999)}"
            hash_object = hashlib.sha256(unique_string.encode())
            unique_id = hash_objectdotenv.hexdigest()[:6]
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
