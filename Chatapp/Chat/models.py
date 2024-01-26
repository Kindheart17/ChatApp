from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Conversation(models.Model):
    # members = models.ManyToManyField(User, related_name='conversations')
    first_user = models.ForeignKey(User, related_name='my_conversations', on_delete=models.CASCADE, null=True)
    other_user = models.ForeignKey(User, related_name='other_conversations', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-modified_at', )


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_messages', on_delete=models.CASCADE)


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE) # Delete profile when user is deleted
    image = models.ImageField(default='user-light.png', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'
    
    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return None