// MORVO Frontend JavaScript
class MorvoApp {
    constructor() {
        this.currentStep = 1;
        this.userId = this.generateUserId();
        this.userProfile = {};
        this.isOnboardingComplete = false;
        
        this.initializeElements();
        this.bindEvents();
        this.startOnboarding();
    }

    // Initialize DOM elements
    initializeElements() {
        this.onboardingCard = document.getElementById('onboardingCard');
        this.chatInterface = document.getElementById('chatInterface');
        this.messageContent = document.getElementById('messageContent');
        this.textInput = document.getElementById('textInput');
        this.nextButton = document.getElementById('nextButton');
        this.optionsContainer = document.getElementById('optionsContainer');
        this.optionsGrid = document.getElementById('optionsGrid');
        this.textInputContainer = document.getElementById('textInputContainer');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.progressDots = document.querySelectorAll('.progress-dot');
        
        // Chat elements
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
    }

    // Bind event listeners
    bindEvents() {
        this.nextButton.addEventListener('click', () => this.handleNext());
        this.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleNext();
        });
        
        // Chat events
        this.sendButton.addEventListener('click', () => this.sendChatMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendChatMessage();
        });
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

    // Start onboarding
    async startOnboarding() {
        this.showLoading();
        try {
            const response = await fetch('/onboarding/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId
                })
            });

            const data = await response.json();
            this.hideLoading();
            
            if (data.message) {
                this.displayMessage(data.message);
            }
            
            this.updateProgress(1);
        } catch (error) {
            this.hideLoading();
            console.error('Error starting onboarding:', error);
            this.displayMessage('عذراً، حدث خطأ في بدء العملية. يرجى المحاولة مرة أخرى.');
        }
    }

    // Handle next step
    async handleNext() {
        const userInput = this.textInput.value.trim();
        
        if (!userInput) {
            this.textInput.focus();
            return;
        }

        this.showLoading();
        try {
            const response = await fetch('/onboarding/step', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    value: userInput
                })
            });

            const data = await response.json();
            this.hideLoading();

            if (data.done) {
                // Onboarding complete
                this.isOnboardingComplete = true;
                this.showChatInterface();
                return;
            }

            // Update UI based on response
            if (data.message) {
                this.displayMessage(data.message);
            }

            // Update progress
            if (data.state_updates && data.state_updates.step) {
                this.currentStep = data.state_updates.step;
                this.updateProgress(this.currentStep);
            }

            // Show appropriate input type
            if (data.ui_type === 'options' && data.options) {
                this.showOptions(data.options);
            } else {
                this.showTextInput();
            }

        } catch (error) {
            this.hideLoading();
            console.error('Error in onboarding step:', error);
            this.displayMessage('عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.');
        }
    }

    // Show chat interface
    showChatInterface() {
        this.onboardingCard.style.display = 'none';
        this.chatInterface.style.display = 'flex';
        
        // Add welcome message
        this.addChatMessage('assistant', 'مرحباً! تم إكمال التسجيل بنجاح. كيف يمكنني مساعدتك اليوم؟');
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
            const response = await fetch('/chat', {
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

    // Reset onboarding (for testing)
    resetOnboarding() {
        this.currentStep = 1;
        this.userProfile = {};
        this.isOnboardingComplete = false;
        this.onboardingCard.style.display = 'block';
        this.chatInterface.style.display = 'none';
        this.updateProgress(1);
        this.startOnboarding();
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.morvoApp = new MorvoApp();
    
    // Add reset functionality for testing (remove in production)
    window.resetOnboarding = () => {
        window.morvoApp.resetOnboarding();
    };
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + R to reset (for testing)
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        if (window.morvoApp) {
            window.morvoApp.resetOnboarding();
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
