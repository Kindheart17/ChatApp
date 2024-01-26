from django import forms
from .models import Conversation, Message

class messageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content', )
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full py-4 px-6 rounded-xl border'
            })
        }