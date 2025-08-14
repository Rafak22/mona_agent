// MORVO Frontend JavaScript
class MorvoApp {
    constructor() {
        this.userId = this.getUserId();
        this.userProfile = {};
        this.isOnboardingComplete = false;
        
        this.initializeElements();
        this.bindEvents();
        this.checkUserStatus();
    }

    // Initialize DOM elements
    initializeElements() {
        this.welcomeCard = document.getElementById('welcomeCard');
        this.chatInterface = document.getElementById('chatInterface');
        this.startButton = document.getElementById('startButton');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        
        // Chat elements
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
    }

    // Bind event listeners
    bindEvents() {
        this.startButton.addEventListener('click', () => this.startOnboarding());
        
        // Chat events
        this.sendButton.addEventListener('click', () => this.sendChatMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendChatMessage();
        });
    }

    // Get user ID from localStorage or generate new one
    getUserId() {
        return localStorage.getItem('morvo_user_id') || this.generateUserId();
    }

    // Generate unique user ID
    generateUserId() {
        return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // Show loading overlay
    showLoading() {
        this.loadingOverlay.style.display = 'flex';
    }

    // Hide loading overlay
    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }

    // Update progress indicator
    updateProgress(step) {
        this.progressDots.forEach((dot, index) => {
            dot.classList.remove('active', 'completed');
            if (index + 1 < step) {
                dot.classList.add('completed');
            } else if (index + 1 === step) {
                dot.classList.add('active');
            }
        });
    }

    // Display message
    displayMessage(message) {
        this.messageContent.textContent = message;
    }

    // Show text input
    showTextInput(placeholder = 'اكتب إجابتك هنا...') {
        this.textInputContainer.style.display = 'block';
        this.optionsContainer.style.display = 'none';
        this.textInput.placeholder = placeholder;
        this.textInput.value = '';
        this.textInput.focus();
    }

    // Show options
    showOptions(options) {
        this.textInputContainer.style.display = 'none';
        this.optionsContainer.style.display = 'block';
        this.optionsGrid.innerHTML = '';
        
        options.forEach(option => {
            const button = document.createElement('button');
            button.className = 'option-button';
            button.textContent = option;
            button.addEventListener('click', () => {
                this.selectOption(option);
            });
            this.optionsGrid.appendChild(button);
        });
    }

    // Select option
    selectOption(option) {
        // Remove previous selections
        document.querySelectorAll('.option-button').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        // Select current option
        event.target.classList.add('selected');
        this.textInput.value = option;
    }

    // Check user status and show appropriate interface
    async checkUserStatus() {
        if (!this.userId) {
            this.showWelcomeCard();
            return;
        }

        try {
            const response = await fetch(`https://monaagent-production-123a.up.railway.app/profile/status?user_id=${this.userId}`);
            const data = await response.json();
            
            if (data.has_profile) {
                this.showChatInterface();
            } else {
                this.showWelcomeCard();
            }
        } catch (error) {
            console.error('Error checking user status:', error);
            this.showWelcomeCard();
        }
    }

    // Show welcome card
    showWelcomeCard() {
        this.welcomeCard.style.display = 'block';
        this.chatInterface.style.display = 'none';
    }

    // Start onboarding (redirect to onboarding page)
    startOnboarding() {
        window.location.href = 'onboarding.html';
    }



    // Show chat interface
    showChatInterface() {
        this.welcomeCard.style.display = 'none';
        this.chatInterface.style.display = 'flex';
        
        // Add welcome message
        this.addChatMessage('assistant', 'مرحباً! كيف يمكنني مساعدتك اليوم؟');
    }

    // Add chat message
    addChatMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = `message-avatar ${role}`;
        avatar.textContent = role === 'assistant' ? 'م' : 'أنت';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    // Send chat message
    async sendChatMessage() {
        const message = this.chatInput.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addChatMessage('user', message);
        this.chatInput.value = '';

        // Show loading
        this.sendButton.disabled = true;
        this.sendButton.textContent = 'جاري الإرسال...';

        try {
            const response = await fetch('https://monaagent-production-123a.up.railway.app/chat', {
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
            
            // Add assistant response
            if (data.reply) {
                this.addChatMessage('assistant', data.reply);
            }

        } catch (error) {
            console.error('Error sending chat message:', error);
            this.addChatMessage('assistant', 'عذراً، حدث خطأ في إرسال الرسالة. يرجى المحاولة مرة أخرى.');
        } finally {
            this.sendButton.disabled = false;
            this.sendButton.innerHTML = '<span>إرسال</span>';
        }
    }

    // Reset user (for testing)
    resetUser() {
        localStorage.removeItem('morvo_user_id');
        this.userId = this.generateUserId();
        this.userProfile = {};
        this.isOnboardingComplete = false;
        this.showWelcomeCard();
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.morvoApp = new MorvoApp();
    
    // Add reset functionality for testing (remove in production)
    window.resetUser = () => {
        window.morvoApp.resetUser();
    };
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

// Add service worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
