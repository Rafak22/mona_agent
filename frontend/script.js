// MORVO Frontend JavaScript
class MorvoApp {
    constructor() {
        this.userId = this.getUserId();
        this.initializeElements();
        this.bindEvents();
        this.checkUserStatus();
    }

    initializeElements() {
        this.welcomeCard = document.getElementById('welcomeCard');
        this.startButton = document.getElementById('startButton');
        this.chatInterface = document.getElementById('chatInterface');
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.loadingOverlay = document.getElementById('loadingOverlay');
    }

    bindEvents() {
        this.startButton.addEventListener('click', () => this.startOnboarding());
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    getUserId() {
        return localStorage.getItem('morvo_user_id') || 'user_' + Date.now();
    }

    checkUserStatus() {
        const onboardingComplete = localStorage.getItem('morvo_onboarding_complete');
        
        if (onboardingComplete === 'true') {
            // User completed onboarding - show chat interface
            this.showChatInterface();
        } else {
            // User hasn't completed onboarding - show welcome card
            this.showWelcomeCard();
        }
    }

    showWelcomeCard() {
        this.welcomeCard.style.display = 'block';
        this.chatInterface.style.display = 'none';
    }

    startOnboarding() {
        // Redirect to onboarding page
        window.location.href = 'onboarding.html';
    }

    showChatInterface() {
        this.welcomeCard.style.display = 'none';
        this.chatInterface.style.display = 'block';
        
        // Add welcome message for returning users
        this.addMessage('assistant', 'أهلاً برجعتك! أنا MORVO 🤝 جاهز أساعدك. وش حاب نبدأ فيه اليوم؟');
        
        // Focus on chat input
        this.chatInput.focus();
    }

    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;
        
        messageDiv.appendChild(messageContent);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    showLoading() {
        this.loadingOverlay.style.display = 'flex';
    }

    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }

    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addMessage('user', message);
        this.chatInput.value = '';

        // Show loading
        this.showLoading();

        try {
            const response = await fetch('https://sweet-stillness-production.up.railway.app/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    message: message
                })
            });

            const data = await response.json();
            this.hideLoading();

            if (data.reply) {
                this.addMessage('assistant', data.reply);
            } else {
                this.addMessage('assistant', 'عذراً، حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.');
            }

        } catch (error) {
            this.hideLoading();
            console.error('Error sending message:', error);
            this.addMessage('assistant', 'عذراً، حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.');
        }
    }

    resetUser() {
        // Clear localStorage and show welcome card
        localStorage.removeItem('morvo_user_id');
        localStorage.removeItem('morvo_onboarding_complete');
        this.showWelcomeCard();
    }
}

// Initialize app when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.morvoApp = new MorvoApp();
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + R to reset (for testing)
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        if (window.morvoApp) {
            window.morvoApp.resetUser();
        }
    }
});

// Global function for reset (can be called from console)
window.resetOnboarding = function() {
    if (window.morvoApp) {
        window.morvoApp.resetUser();
    }
};
