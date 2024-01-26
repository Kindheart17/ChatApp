from django.contrib import admin

# Register your models here.
from .models import Message, Conversation, Profile

admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Profile)