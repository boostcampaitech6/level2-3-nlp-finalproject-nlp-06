document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('user-input');
    const lineHeight = parseFloat(window.getComputedStyle(userInput).lineHeight);
    const maxLines = 5;
    const maxHeight = lineHeight * maxLines;

    userInput.addEventListener('input', function() {
        this.style.height = 'auto'; // Reset height to recalculate
        if (this.scrollHeight <= maxHeight) {
            this.style.height = `${Math.max(this.scrollHeight, lineHeight)}px`;
            this.style.overflowY = 'hidden'; // Hide scrollbar when content is within maxLines
        } else {
            this.style.height = `${maxHeight}px`;
            this.style.overflowY = 'scroll'; // Show scrollbar when content exceeds maxLines
        }
    });
});


const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const chatFormTextArea = chatForm.querySelector('#user-input');

chatForm.addEventListener('submit', function (event) {
    // When the route is index, execute ordinary form submission without js intervention
    const currentUrl = window.location.href;
    if (currentUrl.includes('/index')) {
        const spinner = document.createElement('div');
        spinner.classList.add('spinner');
        spinner.innerHTML = `
        <i class="zmdi zmdi-spinner zmdi-hc-lg"></i>
        `;
        chatWindow.appendChild(spinner);
        return; 
    }

    // Otherwise, prevent the default form submission and proceed with custom logic
    event.preventDefault();

    const userInput = chatFormTextArea.value.trim();
    // console.log(userInput);
    chatFormTextArea.value = '';
    if (!userInput) {
        return;
    }

    const userProfileData = document.getElementById('user-profile-data');
    const botProfileData = document.getElementById('bot-profile-data');

    const messageItem = document.createElement('div');
    messageItem.classList.add('message');
    messageItem.innerHTML = `
    <div class="message-profile">
        <img src="${userProfileData.dataset.imageUrl}" alt="">
    </div>
    <div class="message-content">
        <div class="message-profile-name">${userProfileData.dataset.name}</div>
        <div class="message-text">${userInput}</div>
    </div>
    `;

    const spinner = document.createElement('div');
    spinner.classList.add('spinner');
    spinner.innerHTML = `
    <i class="zmdi zmdi-spinner zmdi-hc-lg"></i>
    `;

    chatWindow.appendChild(messageItem);
    chatWindow.appendChild(spinner);

    
    fetch('', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            "csrfmiddlewaretoken": document.querySelector('input[name="csrfmiddlewaretoken"]').value,
            "message": userInput
        }).toString()
    })
        .then(response => response.json())
        .then(data => {
            const botResponse = data.response.text.trim();
            const userPersonas = data.response.personas;
            const messageItem = document.createElement('div');
            messageItem.classList.add('message');
            
            // make sure there's no space between the opening tag, the text content, and the closing tag.
            messageItem.innerHTML = `
            <div class="message-profile">
                <img src="${botProfileData.dataset.imageUrl}" alt="">
            </div>
            <div class="message-content">
                <div class="message-profile-name">${botProfileData.dataset.name}</div>
                <div class="message-text">${botResponse}</div>
            </div>
            `;

            // const messagePersona = messageItem.querySelector('.message-persona ul');
            // userPersonas.forEach(persona => {
            //     const personaItem = document.createElement('li');
            //     personaItem.textContent = persona;
            //     messagePersona.appendChild(personaItem);
            // });
            
            spinner.remove();
            chatWindow.appendChild(messageItem);
        });
});



const deleteHistoryButton = document.getElementById('delete-history');
deleteHistoryButton.addEventListener('click', function (event) {
    event.preventDefault();
    const csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];
    // const userData = document.getElementById('user-data');
    // const username = userData.dataset.username;
    fetch(``, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        credentials: 'same-origin',
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            window.location.reload();
            // return response.json();
            return null;
        })
});

