const USER_ID = document.getElementById('logged-in-user').value;
const OTHER_ID = document.getElementById('other-user').value;
const OTHER_USERNAME = document.getElementById('other-user-name').value;
const CONVERSATION_ID = document.getElementById('conversation-id').value;

console.log(USER_ID);
let loc = window.location
let wsStart = 'ws://'

if(location.protocol === 'https'){
    wsStart = 'wss://'
}

let endpoint = wsStart + loc.host + loc.pathname
var socket = new WebSocket(endpoint)

const messageInput = document.getElementById('messageInput');
const messageForm = document.getElementById('message-form');

socket.onopen = async function(e){
    console.log('open', e)
}
function scrollToBottom() {
    const chatContainer = document.getElementById('chat');
    console.log('scrolled');
    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 50);
}

async function query(userMessage) {
    try {
        const response = await fetch('/chat/chatbot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userMessage: userMessage,
            }),
        });

        if (!response.ok) {
            console.log('Network response was not ok');
        }

        const data = await response.json();
        console.log('API Response:', data);
        return data;

    } catch (error) {
        console.error('Error:', error);
    }
}

function waitingMessage() {
    let messageListItem = document.createElement('li');
    messageListItem.className = 'you';

    let messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    messageDiv.textContent = '...';

    messageListItem.appendChild(messageDiv);

    setTimeout(function () {
        document.getElementById('chat').appendChild(messageListItem);
        scrollToBottom();
    }, 500);

    return messageListItem;
}

messageForm.addEventListener("submit", function (e) {
    e.preventDefault();
    console.log(OTHER_USERNAME);
    let msg = messageInput.value;

    const data = {
        'message': msg,
        'created_by': USER_ID,
        'send_to': OTHER_ID,
        'conversation_id': CONVERSATION_ID,
    };

    const jsonData = JSON.stringify(data);
    socket.send(jsonData);

    if (OTHER_USERNAME=='ChatBot'){
        let msg = messageInput.value;
        console.log('Message sent to chatbot.');

        let tempMessageElement = waitingMessage();

        let cht = document.getElementById("chat");
        query(msg).then((response) => {
            console.log(JSON.stringify(response));
            let generatedText = response.generatedText;
            if (generatedText != undefined)
                console.log(generatedText);
            else
                generatedText = response.error;

            console.log(tempMessageElement)
            console.log(cht)
            cht.removeChild(tempMessageElement);
            newMessage(generatedText, OTHER_ID);
            saveMessage(OTHER_ID, CONVERSATION_ID, generatedText)
        });
    }

    messageInput.value = '';
    messageInput.placeholder = 'Type your message';
    messageInput.disabled = false;
    messageForm.reset();
    scrollToBottom();
});

socket.onmessage = async function(e){
    console.log('message', e)
    let data = JSON.parse(e.data)
    let message = data['content']
    let created_by_id = data['created_by']
    let sent_to_id = data['send_to']
    console.log(sent_to_id)
    if ((created_by_id == USER_ID) || ((sent_to_id == USER_ID) && (created_by_id == OTHER_ID))){
        newMessage(message, created_by_id)
    }

}
socket.onerror = async function(e){
    console.log('error', e)
}
socket.onclose = async function(e){
    console.log('close', e)
}


// Function to create a new message
function newMessage(message, sent_by_id) {
    if (message.trim() === '') {
        return false;
    }
    let content = ``
    const chat = document.getElementById("chat");
    const serverTimeElement = document.querySelector('.server-time');
    const serverTimestamp = new Date(serverTimeElement.textContent);
    if (sent_by_id == USER_ID){
        if (message.includes("Image Selected:")) {
            var imageName = message.slice(16).trim();
            content = `
                    <li class="me">
                            <h3 class="time">${serverTimestamp.toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: 'numeric', hour12: true })}</h3>
                            <div class="message photo">
                            <img src="../media/uploaded_images/${imageName}" alt="Image Loading...">
                        </div>
                    </li>
                `
        }
        else{
        content = `
                    <li class="me">
                        <h3 class="time">${serverTimestamp.toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: 'numeric', hour12: true })}</h3>
                        <button onclick="translateMessage(this, true)" class="tBtn transition-opacity opacity-0 content-T text-center rounded-full border-2 border-26CAAD me-2 px-2 h-25 w-25 bg-opacity-40 bg-gray-700" style="color: #26CAAD;">
                                T
                        </button>
                        <div class="message">${message}</div>
                    </li>
                `;
        }
    }   
    else {
        if (message.includes("Image Selected:")) {
            var imageName = message.slice(16).trim();
            content = `
                    <li class="you">
                            <h3 class="time">${serverTimestamp.toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: 'numeric', hour12: true })}</h3>
                        <div class="message photo">
                            <img src="../media/uploaded_images/${imageName}" alt="Image Loading...">
                        </div>
                    </li>
                `
        }
        else{
        content = `
                    <li class="you">
                        <h3 class="time">${serverTimestamp.toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: 'numeric', hour12: true })}</h3>
                        <div class="message">${message}</div>
                        <button onclick="translateMessage(this, false)" class="tBtn transition-opacity opacity-0 content-T text-center rounded-full border-2 border-26CAAD ms-2 px-2 h-25 w-25 bg-opacity-40 bg-gray-700" style="color: #26CAAD;">T</button>
                    </li>
                `;
        }
    }
    chat.innerHTML += content;
    scrollToBottom();
}

function saveMessage(otherID, convID, message){
    const formData = new FormData();
        formData.append('otherID', otherID);
        formData.append('message', message);
        formData.append('convID', convID);

        // Call to API to store the image
        fetch('/chat/save-chatbot-message/', {
            method: 'POST',
            body: formData,
        }).then(response => {
            if (response.ok) {
                // Image upload successful
                console.log('Chatbot Message Saved.');
            } else {
                // Handle errors
                console.error(`Message not Saved. HTTP status: ${response.status}`);
            }
        }).catch(error => {
            // Handle errors
            console.error('Fetch error:', error);
        });
}