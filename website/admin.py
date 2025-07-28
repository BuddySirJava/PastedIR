from django.contrib import admin

from website.models import Paste, Language, User

admin.site.register(Paste)
admin.site.register(Language)
admin.site.register(User)

