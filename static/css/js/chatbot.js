/**
 * Chatbot functionality for CivicAI
 */

const CHAT_MESSAGES_KEY = 'civicai_chat_messages';

/**
 * Initialize chatbot
 */
function initializeChatbot() {
    const chatWidget = document.getElementById('chatbot-widget');
    if (!chatWidget) return;

    loadChatMessages();
    setupChatListeners();
}

/**
 * Setup chat event listeners
 */
function setupChatListeners() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('chat-send');
    const closeButton = document.getElementById('chat-close');
    const minimizeButton = document.getElementById('chat-minimize');

    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    if (closeButton) {
        closeButton.addEventListener('click', closeChatbot);
    }

    if (minimizeButton) {
        minimizeButton.addEventListener('click', minimizeChatbot);
    }
}

/**
 * Send message to chatbot
 */
function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    addChatMessage(message, 'user');
    input.value = '';

    // Get bot response
    fetch('/api/chatbot/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        addChatMessage(data.response, 'bot');
        saveChatMessage(message, data.response);
    })
    .catch(error => {
        addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
    });
}

/**
 * Add message to chat window
 */
function addChatMessage(message, sender = 'bot') {
    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message chat-message-${sender}`;

    const messageContent = document.createElement('div');
    messageContent.className = 'chat-message-content';
    messageContent.innerHTML = message; // Allow HTML for formatting

    messageDiv.appendChild(messageContent);
    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Load previous chat messages
 */
function loadChatMessages() {
    const messages = localStorage.getItem(CHAT_MESSAGES_KEY);
    if (messages) {
        const chatHistory = JSON.parse(messages);
        chatHistory.forEach(chat => {
            addChatMessage(chat.user, 'user');
            addChatMessage(chat.bot, 'bot');
        });
    }
}

/**
 * Save chat message
 */
function saveChatMessage(userMsg, botMsg) {
    let history = [];
    const saved = localStorage.getItem(CHAT_MESSAGES_KEY);
    if (saved) {
        history = JSON.parse(saved);
    }

    history.push({
        user: userMsg,
        bot: botMsg,
        timestamp: new Date().toISOString()
    });

    // Keep only last 50 messages
    if (history.length > 50) {
        history = history.slice(-50);
    }

    localStorage.setItem(CHAT_MESSAGES_KEY, JSON.stringify(history));
}

/**
 * Clear chat history
 */
function clearChatHistory() {
    if (confirm('Clear chat history?')) {
        localStorage.removeItem(CHAT_MESSAGES_KEY);
        const messagesContainer = document.getElementById('chat-messages');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }
    }
}

/**
 * Close chatbot
 */
function closeChatbot() {
    const chatWidget = document.getElementById('chatbot-widget');
    if (chatWidget) {
        chatWidget.style.display = 'none';
    }
}

/**
 * Minimize chatbot
 */
function minimizeChatbot() {
    const chatBox = document.querySelector('.chat-box');
    if (chatBox) {
        chatBox.classList.toggle('minimized');
    }
}

/**
 * Open chatbot
 */
function openChatbot() {
    const chatWidget = document.getElementById('chatbot-widget');
    if (chatWidget) {
        chatWidget.style.display = 'flex';
    }
}

// Add chatbot CSS dynamically
function addChatbotStyles() {
    const style = document.createElement('style');
    style.textContent = `
        #chatbot-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 380px;
            height: 600px;
            border-radius: 12px;
            box-shadow: 0 5px 40px rgba(0,0,0,0.16);
            display: flex;
            flex-direction: column;
            background: white;
            z-index: 999;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .chat-header {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
            padding: 1rem;
            border-radius: 12px 12px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chat-header-title {
            font-weight: 600;
            font-size: 1rem;
        }

        .chat-header-buttons {
            display: flex;
            gap: 0.5rem;
        }

        .chat-header-btn {
            background: rgba(255,255,255,0.3);
            border: none;
            color: white;
            cursor: pointer;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 1rem;
            transition: background 0.3s;
        }

        .chat-header-btn:hover {
            background: rgba(255,255,255,0.5);
        }

        #chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            background: #f9fafb;
        }

        .chat-message {
            margin-bottom: 1rem;
            display: flex;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .chat-message-user {
            justify-content: flex-end;
        }

        .chat-message-bot {
            justify-content: flex-start;
        }

        .chat-message-content {
            max-width: 80%;
            padding: 0.75rem 1rem;
            border-radius: 12px;
            font-size: 0.9rem;
            line-height: 1.4;
            word-wrap: break-word;
        }

        .chat-message-user .chat-message-content {
            background: #1e40af;
            color: white;
            border-bottom-right-radius: 4px;
        }

        .chat-message-bot .chat-message-content {
            background: white;
            color: #1f2937;
            border: 1px solid #e5e7eb;
            border-bottom-left-radius: 4px;
        }

        .chat-input-area {
            border-top: 1px solid #e5e7eb;
            padding: 1rem;
            display: flex;
            gap: 0.5rem;
        }

        #chat-input {
            flex: 1;
            padding: 0.5rem 0.75rem;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            font-size: 0.9rem;
            font-family: inherit;
        }

        #chat-input:focus {
            outline: none;
            border-color: #1e40af;
            box-shadow: 0 0 0 2px rgba(30,64,175,0.1);
        }

        #chat-send {
            background: #1e40af;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: background 0.3s;
        }

        #chat-send:hover {
            background: #1e3a8a;
        }

        @media (max-width: 480px) {
            #chatbot-widget {
                width: 100%;
                height: 100%;
                bottom: 0;
                right: 0;
                border-radius: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    addChatbotStyles();
    initializeChatbot();
});