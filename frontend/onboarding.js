// MORVO Onboarding JavaScript
class MorvoOnboarding {
    constructor() {
        this.currentStep = 1;
        this.userId = this.generateUserId();
        this.userProfile = {};
        
        this.initializeElements();
        this.bindEvents();
        this.startOnboarding();
    }

    // Initialize DOM elements
    initializeElements() {
        this.onboardingCard = document.getElementById('onboardingCard');
        this.messageContent = document.getElementById('messageContent');
        this.textInput = document.getElementById('textInput');
        this.nextButton = document.getElementById('nextButton');
        this.backButton = document.getElementById('backButton');
        this.optionsContainer = document.getElementById('optionsContainer');
        this.optionsGrid = document.getElementById('optionsGrid');
        this.textInputContainer = document.getElementById('textInputContainer');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.progressDots = document.querySelectorAll('.progress-dot');
    }

    // Bind event listeners
    bindEvents() {
        this.nextButton.addEventListener('click', () => this.handleNext());
        this.backButton.addEventListener('click', () => this.handleBack());
        this.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleNext();
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
        
        // Update back button state
        this.backButton.disabled = step <= 1;
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
            const response = await fetch('https://sweet-stillness-production.up.railway.app/onboarding/start', {
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
            
            console.log('Onboarding start response:', data);
            
            if (data.message) {
                this.displayMessage(data.message);
            }
            
            // Show text input for user response
            this.showTextInput();
            this.updateProgress(1);
        } catch (error) {
            this.hideLoading();
            console.error('Error starting onboarding:', error);
            this.displayMessage('عذراً، حدث خطأ في بدء العملية. يرجى المحاولة مرة أخرى.');
        }
    }

    // Handle back step
    handleBack() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateProgress(this.currentStep);
            // For now, just go back to previous step
            // In a full implementation, you'd want to restore previous state
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
            const response = await fetch('https://sweet-stillness-production.up.railway.app/onboarding/step', {
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

            console.log('Onboarding step response:', data);

            if (data.done) {
                // Onboarding complete - redirect to chat
                this.completeOnboarding();
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
            } else {
                // Increment step if no specific step info
                this.currentStep++;
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

    // Complete onboarding and redirect to chat
    completeOnboarding() {
        // Store user ID in localStorage for chat page
        localStorage.setItem('morvo_user_id', this.userId);
        
        // Show completion message
        this.displayMessage('تم إكمال التسجيل بنجاح! جاري الانتقال إلى المحادثة...');
        
        // Redirect to chat page after a short delay
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 2000);
    }
}

// Initialize the onboarding when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.morvoOnboarding = new MorvoOnboarding();
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + R to restart (for testing)
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        if (window.morvoOnboarding) {
            window.location.reload();
        }
    }
});
