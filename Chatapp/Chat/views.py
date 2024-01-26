from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Conversation, Message, Profile
from .forms import messageForm
from django.db.models import Q
from django.contrib.auth.models import User
from translate import Translator
import json
import requests
from decouple import config


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# from django.utils import timezone
from datetime import datetime

# Create your views here.


def chatApp(request, convId):
    conversations = Conversation.objects.filter(
        Q(first_user=request.user.id) | Q(other_user=request.user.id)
    )
    # for conversation in conversations:
    #     print(conversation.members.all())
    activeConversation = Conversation.objects.get(id=convId)

    if activeConversation.first_user == request.user:
        other = activeConversation.other_user
    else:
        other = activeConversation.first_user

    otherProfile = Profile.objects.filter(user=other).first()
    print(otherProfile)

    bot = User.objects.filter(username="ChatBot").first()
    botConv = conversations.filter(other_user=bot).first()

    current_time = datetime.now()
    # print(current_time)

    return render(
        request,
        "chat/index.html",
        {
            "otherProfile": otherProfile,
            "conversations": conversations,
            "activeConversation": activeConversation,
            "botConv": botConv,
            "server_timestamp": current_time,
        },
    )


def emptyChat(request):
    if not request.user.is_authenticated:
        return redirect(reverse("login"))
    userProfile = Profile.objects.filter(user=request.user).first()
    conversations = Conversation.objects.filter(
        Q(first_user=request.user.id) | Q(other_user=request.user.id)
    )
    bot = User.objects.filter(username="ChatBot").first()
    if bot is None:
        bot = User(username="ChatBot", password="ChatBot")
        bot.save()
    botConv = conversations.filter(other_user=bot).first()
    if botConv is None:
        botConv = Conversation(first_user=request.user, other_user=bot)
        botConv.save()
    return render(
        request,
        "chat/empty-chat.html",
        {
            "userProfile": userProfile,
            "conversations": conversations,
            "botConv": botConv,
        },
    )


from openai import OpenAI


client = OpenAI(api_key = config("OPENAI_KEY"))

def gptTranslate(message):
   
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"You are AI assistant for a chat application. Your job is to translate to hindi. only write hindi, no english or any other language. your job is just to TRANSLATE. Now translate this: {message}",
            },
        ],
    )

    return completion.choices[0].message.content


@csrf_exempt
@require_POST
def chatbot(request):
    try:
        # Assuming you've set up your OpenAI credentials properly
        

        # Extract user message from the request
        request_data = json.loads(request.body)
        user_message = request_data.get("userMessage", "Default User Message")

        # Perform the completion using OpenAI API
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_message},
            ],
        )

        # Extract the messages from the completion
        responseMessage = completion.choices[0].message.content
        print(responseMessage)

        # Return the messages as JSON response
        return JsonResponse({"status": "success", "generatedText": responseMessage})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def newChat(request):
    conversations = Conversation.objects.filter(
        Q(first_user=request.user.id) | Q(other_user=request.user.id)
    )
    bot = User.objects.filter(username="ChatBot").first()
    botConv = conversations.filter(other_user=bot).first()
    errors = []

    if request.method == "POST":
        username = request.POST["username"]
        new_user = User.objects.filter(username=username).first()
        if not new_user:
            errors.append("User not found. Invalid Username.")
            return render(
                request,
                "chat/new-chat.html",
                {
                    "errors": errors,
                    "conversations": conversations,
                    "botConv": botConv,
                },
            )
        else:
            current_convs = request.user.my_conversations.all()
            # all_conv.append(current_convs)
            other_convs = request.user.other_conversations.all()
            # all_conv.append(other_convs)
            all_convs = list(current_convs) + list(other_convs)
            for conv in all_convs:
                print(conv)
                print(conv.first_user)
                print(conv.other_user)

                if (conv.first_user == new_user) or (conv.other_user == new_user):
                    errors.append("Chat with the user already exists")
                    return render(
                        request,
                        "chat/new-chat.html",
                        {
                            "errors": errors,
                            "conversations": conversations,
                            "botConv": botConv,
                        },
                    )
            new_conv = Conversation(first_user=request.user, other_user=new_user)
            new_conv.save()
            return redirect("chat:chatApp", convId=new_conv.id)

    if not request.user.is_authenticated:
        return redirect(reverse("login"))

    return render(
        request,
        "chat/new-chat.html",
        {
            "errors": errors,
            "conversations": conversations,
            "botConv": botConv,
        },
    )


def cropImage(request, convId):
    conversations = Conversation.objects.filter(
        Q(first_user=request.user.id) | Q(other_user=request.user.id)
    )
    activeConversation = Conversation.objects.get(id=convId)
    current_time = datetime.now()

    return render(
        request,
        "chat/crop-image.html",
        {
            "conversations": conversations,
            "activeConversation": activeConversation,
            "server_timestamp": current_time,
        },
    )


import os
from django.conf import settings


@csrf_exempt
def saveImage(request):
    if request.method == "POST" and request.FILES.get("uploaded-image"):
        uploaded_file = request.FILES["uploaded-image"]

        # Determine the file path within the 'media' folder
        file_path = os.path.join(
            settings.MEDIA_ROOT, "uploaded_images", uploaded_file.name
        )

        # Ensure the subfolder exists; create it if not
        os.makedirs(os.path.join(settings.MEDIA_ROOT, "uploaded_images"), exist_ok=True)

        # Determine your desired file path and save the file
        # file_path = '/uploaded-media/' + uploaded_file.name
        with open(file_path, "wb") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Return a JSON response indicating success
        return JsonResponse(
            {"status": "success", "message": "Image uploaded successfully."}
        )

    # Return a JSON response indicating failure if the file was not received
    return JsonResponse({"status": "error", "message": "No file received."})


@csrf_exempt
def saveChatbotMessage(request):
    if request.method == "POST":
        otherID = request.POST["otherID"]
        # otherID = request.FILES['otherID']
        convID = request.POST["convID"]
        message = request.POST["message"]

        if otherID and convID and message:
            # print("DEbugging:")
            # print(userID)
            # print(convID)
            # print(message)
            bot = User.objects.get(id=otherID)
            conv = Conversation.objects.get(id=convID)
            newMessage = Message(conversation=conv, content=message, created_by=bot)
            newMessage.save()
            conv.save()

            # Return a JSON response indicating success
            return JsonResponse(
                {"status": "success", "message": "Image uploaded successfully."}
            )

    # Return a JSON response indicating failure if the file was not received
    return JsonResponse({"status": "error", "message": "Message not saved."})


@csrf_exempt  # Only for demo purposes; consider proper CSRF protection in production
def getUpdatedConversations(request):
    # Fetch updated conversation data
    # Replace this with your logic to retrieve the updated data from the database
    updated_conversations = Conversation.objects.all().values(
        "id", "first_user", "other_user", "modified_at"
    )

    # Convert queryset to a list to serialize as JSON
    updated_conversations_list = list(updated_conversations)

    return JsonResponse(updated_conversations_list, safe=False)


@csrf_exempt
def translate_message(request):
    if request.method == "POST":
        try:
            # Retrieve the message content from the POST data
            data = json.loads(request.body)
            message_content = data.get("messageContent", "")

            # Perform translation logic here (replace this with your actual translation logic)
            # translator = Translator(to_lang="hi")
            # translation = translator.translate(message_content)
            # print(translation)
            # translated_message = f'Translated: {message_content}'

            translation = gptTranslate(message_content)
            print(translation)

            # Return the translated message as JSON response
            return JsonResponse({"translatedMessage": translation})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)
