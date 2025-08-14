// MORVO Onboarding JavaScript
class MorvoOnboarding {
    constructor() {
        this.currentStep = 1;
        this.userId = this.generateUserId();
        this.isOnboardingComplete = false;
        
        this.initializeElements();
        this.bindEvents();
        this.startOnboarding();
    }

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

    bindEvents() {
        this.nextButton.addEventListener('click', () => this.handleNext());
        this.backButton.addEventListener('click', () => this.handleBack());
        this.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleNext();
            }
        });
    }

    generateUserId() {
        // Check if user ID exists in localStorage
        let userId = localStorage.getItem('morvo_user_id');
        if (!userId) {
            userId = 'user_' + Date.now();
            localStorage.setItem('morvo_user_id', userId);
        }
        return userId;
    }

    showLoading() {
        this.loadingOverlay.style.display = 'flex';
    }

    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }

    updateProgress(step) {
        this.progressDots.forEach((dot, index) => {
            if (index < step) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
        
        // Disable back button on first step
        if (step === 1) {
            this.backButton.disabled = true;
            this.backButton.style.opacity = '0.5';
        } else {
            this.backButton.disabled = false;
            this.backButton.style.opacity = '1';
        }
    }

    displayMessage(message) {
        this.messageContent.textContent = message;
    }

    showTextInput() {
        this.textInputContainer.style.display = 'block';
        this.optionsContainer.style.display = 'none';
        this.textInput.focus();
    }

    showOptions(options) {
        this.textInputContainer.style.display = 'none';
        this.optionsContainer.style.display = 'block';
        
        this.optionsGrid.innerHTML = '';
        options.forEach(option => {
            const button = document.createElement('button');
            button.className = 'option-button';
            button.textContent = option;
            button.addEventListener('click', () => this.selectOption(option));
            this.optionsGrid.appendChild(button);
        });
    }

    selectOption(option) {
        this.textInput.value = option;
        this.handleNext();
    }

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
            this.displayMessage('عذراً، حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.');
        }
    }

    async handleNext() {
        const value = this.textInput.value.trim();
        if (!value) {
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
                    value: value
                })
            });

            const data = await response.json();
            this.hideLoading();

            console.log('Onboarding step response:', data);

            if (data.done) {
                // Onboarding completed - redirect to chat page
                this.isOnboardingComplete = true;
                localStorage.setItem('morvo_onboarding_complete', 'true');
                window.location.href = 'index.html';
                return;
            }

            // Clear input
            this.textInput.value = '';

            // Update UI based on response
            if (data.message) {
                this.displayMessage(data.message);
            }

            if (data.options && data.options.length > 0) {
                this.showOptions(data.options);
            } else {
                this.showTextInput();
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

        } catch (error) {
            this.hideLoading();
            console.error('Error in onboarding step:', error);
            this.displayMessage('عذراً، حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.');
        }
    }

    handleBack() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateProgress(this.currentStep);
            // For now, just go back to previous step
            // In a full implementation, you'd want to restore the previous state
        }
    }
}

// Initialize onboarding when page loads
document.addEventListener('DOMContentLoaded', () => {
    new MorvoOnboarding();
});
