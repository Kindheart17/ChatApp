from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name='chat'

urlpatterns=[
    path('', views.emptyChat, name='emptyChat'),
    path('<int:convId>/', views.chatApp, name='chatApp'),
    path('new-chat/', views.newChat, name='newChat'),
    path('crop-image/<int:convId>/', views.cropImage, name='cropImage'),
    path('save-uploaded-image/', views.saveImage, name='saveImage'),
    path('save-chatbot-message/', views.saveChatbotMessage, name='saveChatbotMessage'),
    path('get-updated-conversations/', views.getUpdatedConversations, name='get_updated_conversations'),
    path('translate-message/', views.translate_message, name='translate_message'),
    path('chatbot/', views.chatbot, name='chatbot'),
    # path('', views.inbox, name='inbox'),
    # path('chat/<int:pk>', views.chat, name='chat'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)