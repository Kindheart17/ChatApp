import json
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
user = get_user_model()
from . models import Conversation, Message
from django.utils import timezone

class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('connected', event)
        user = self.scope['user']
        chat_room = f'user_chatroom_{user.id}'
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.send({
            'type': 'websocket.accept'
        })
    
    async def websocket_receive(self, event):
        print('receive', event)
        received_data = json.loads(event['text'])
        msg = received_data.get('message')
        created_by_id = received_data.get('created_by')
        sent_to_id = received_data.get('send_to')
        conv_id = received_data.get('conversation_id')

        if not msg:
            return False
        
        created_by_user = await self.get_user_object(created_by_id)
        sent_to_user = await self.get_user_object(sent_to_id)

        if not created_by_user:
            print('Created_by user is incorrect.')
        if not sent_to_user:
            print('Sent_to user is incorrect.')
        
        await self.save_message(created_by_user, conv_id, msg)

        other_user_chat_room = f'user_chatroom_{sent_to_id}'
        self_user = self.scope['user']    
        response = {
            'content': msg,
            'created_by': self_user.id,
            'send_to': sent_to_id
        }

        await self.channel_layer.group_send(
            other_user_chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )
        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

        # await self.send({
        #     'type': 'websocket.send',
        #     'text': json.dumps(response)
        # })
    
    async def chat_message(self, event):
        print('chat_message', event)
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })


    async def websocket_disconnect(self, event):
        print('disconnect', event)


    @database_sync_to_async
    def get_user_object(self, user_id):
        print(user_id)
        qs = user.objects.filter(id=user_id)
        print(qs)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        
        return obj
    
    @database_sync_to_async
    def save_message(self, user, conv_id, msg):
        conv = Conversation.objects.get(id=conv_id)
        newMessage = Message(conversation=conv, content=msg, created_by=user)
        print(conv.modified_at)
        # conv.modified_at = timezone.now()
        newMessage.save()
        conv.save()
        print(conv.modified_at)