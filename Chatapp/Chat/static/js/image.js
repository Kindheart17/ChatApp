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


socket.onopen = async function(e){
    console.log('open', e)
}
function scrollToBottom() {
    const chatContainer = document.getElementById('chat');
    console.log('scrolled');
    // Scroll to Bottom after each message
    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 50);
}

// IMAGE CODE
document.getElementById('file-input').addEventListener('change', handleFileSelect);
const submitBtn = document.getElementById('submit-btn');
const cropBtn = document.getElementById('btn-crop');
const imageForm = document.getElementById('image-form');
const backBtn = document.getElementById('back');
let originalFileName; 
let cropper;

function handleFileSelect(event) {
    const fileInput = event.target;
    const imageContainer = document.getElementById('image-container');
    const uploadedImage = document.getElementById('uploaded-image');
    
    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();

        reader.onload = function (e) {
            imageContainer.classList.remove('hidden');
            submitBtn.classList.remove('hidden');
            cropBtn.classList.remove('hidden');
            uploadedImage.src = e.target.result;
            
            originalFileName = fileInput.files[0].name;

            const image = document.getElementById('uploaded-image');
            cropper = new Cropper(image, {
                aspectRatio: 0,
            });

            document.querySelector('#btn-crop').addEventListener('click', function() {
                var croppedImage = cropper.getCroppedCanvas().toDataURL("image/png");
                document.getElementById('output').src = croppedImage;
                document.querySelector(".cropped-container").style.display = 'flex';
            });
        }
        reader.readAsDataURL(fileInput.files[0]);
    }
}

function dataURItoBlob(dataURI) {
    const byteString = atob(dataURI.split(',')[1]);
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);

    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }

    return new Blob([ab], { type: 'image/png' });
}

imageForm.addEventListener('submit', function (event) {
    event.preventDefault();

    const croppedImage = cropper.getCroppedCanvas().toDataURL("image/png");

    const formData = new FormData();
    const blob = dataURItoBlob(croppedImage);

    formData.append('uploaded-image', blob, originalFileName);

        // Call to API to store the image
        fetch('/chat/save-uploaded-image/', {
            method: 'POST',
            body: formData,
        }).then(response => {
            if (response.ok) {
                // Image upload successful
                console.log('Image uploaded successfully!');
            } else {
                // Errros
                console.error(`Image upload failed. HTTP status: ${response.status}`);
            }
        }).catch(error => {
            console.error('Fetch error:', error);
        });
    
    let msg = "Image Selected: " + originalFileName;
    console.log(msg);

    const data = {
        'message': msg,
        'created_by': USER_ID,
        'send_to': OTHER_ID,
        'conversation_id': CONVERSATION_ID,
    };

    const jsonData = JSON.stringify(data);
    socket.send(jsonData);

    backBtn.click();
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