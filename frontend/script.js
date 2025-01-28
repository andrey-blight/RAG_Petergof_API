// API URL
const API_URL = 'http://127.0.0.1:8000/api/v1/answer';

// Form
document.getElementById('chat-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const userInput = document.getElementById('user-input');
    const userMessage = userInput.value.trim();

    if (userMessage === '') return;

    // add user question to chat
    addMessageToChat(userMessage, 'user-message');
    userInput.value = '';

    try {
        // Send request
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({"question": userMessage})
        });

        if (!response.ok) {
            throw new Error('API request failed');
        }

        const data = await response.json();

        // Add rag answer to chat
        addMessageToChat(data.answer, 'bot-message');
    } catch (error) {
        addMessageToChat('Error: Unable to get response from API.', 'bot-message');
        console.error(error);
    }
});

// Add message to chat
function addMessageToChat(message, className) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    messageDiv.textContent = message;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}