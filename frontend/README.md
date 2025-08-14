# MORVO Frontend

Beautiful, modern frontend for the MORVO marketing assistant with Arabic RTL support.

## Features

- 🎨 **Modern Design** - Clean, responsive interface with beautiful gradients
- 🌍 **Arabic RTL Support** - Full right-to-left language support
- 📱 **Responsive** - Works perfectly on desktop, tablet, and mobile
- 🔄 **Smart Onboarding** - 8-step user profiling with progress tracking
- 💬 **Chat Interface** - Seamless transition to chat after onboarding
- ⚡ **Fast & Smooth** - Optimized animations and transitions

## File Structure

```
frontend/
├── start.html          # Entry point - redirects to appropriate page
├── onboarding.html     # Onboarding page (separate)
├── index.html          # Chat interface (main app)
├── styles.css          # CSS styling
├── onboarding.js       # Onboarding JavaScript
├── script.js           # Chat JavaScript
└── README.md           # This file
```

## Setup

1. **Place the frontend files** in your project's `frontend/` directory
2. **Ensure your backend is running** on the same domain (or configure CORS)
3. **Open `start.html`** in a web browser (this will redirect to the appropriate page)

## Usage

### Development
```bash
# Start your FastAPI backend
python main.py

# Open the frontend
# Navigate to frontend/start.html in your browser
# This will automatically redirect to onboarding or chat based on user status
```

### Production
- Serve the frontend files through your web server
- Ensure the backend API endpoints are accessible
- Configure CORS if needed

## API Endpoints Used

The frontend communicates with these backend endpoints:

- `POST /onboarding/start` - Start onboarding process
- `POST /onboarding/step` - Continue onboarding with user input
- `POST /chat` - Send chat messages

## Features

### User Flow
1. **Entry Point** (`start.html`) - Checks user status and redirects appropriately
2. **Onboarding** (`onboarding.html`) - 8-step user profiling (if new user)
3. **Chat Interface** (`index.html`) - Main chat application (if returning user)

### Onboarding Steps
1. **Welcome** - Initial greeting and introduction
2. **Name Collection** - User's first name with validation
3. **Role Selection** - Marketing role (manager, entrepreneur, etc.)
4. **Industry** - Business industry identification
5. **Company Size** - Organization size assessment
6. **Website Status** - Current website situation
7. **Website URL** - Website URL (if applicable)
8. **Goals** - Marketing objectives
9. **Budget** - Marketing budget range
10. **Completion** - Redirect to chat interface

### Chat Interface
- Real-time messaging with MORVO
- Message history
- Loading states
- Error handling

## Customization

### Colors
The main color scheme uses:
- Primary: `#667eea` (Purple)
- Secondary: `#764ba2` (Darker Purple)
- Success: `#4CAF50` (Green)
- Background: Gradient from primary to secondary

### Fonts
- **Cairo** - Arabic-optimized font from Google Fonts
- Fallback to system fonts

### Responsive Breakpoints
- Mobile: `< 768px`
- Tablet: `768px - 1024px`
- Desktop: `> 1024px`

## Browser Support

- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)
- ✅ Mobile browsers

## Testing

### Manual Testing
1. Complete the onboarding flow
2. Test chat functionality
3. Verify responsive design
4. Check RTL layout

### Keyboard Shortcuts
- `Enter` - Submit input/next step
- `Ctrl/Cmd + R` - Reset onboarding (for testing)

## Troubleshooting

### Common Issues

**API Connection Errors**
- Ensure backend is running
- Check CORS configuration
- Verify API endpoints

**RTL Layout Issues**
- Ensure `dir="rtl"` is set on HTML
- Check font loading
- Verify CSS direction properties

**Responsive Issues**
- Test on different screen sizes
- Check viewport meta tag
- Verify CSS media queries

## Development

### Adding New Features
1. Update HTML structure in `index.html`
2. Add styles in `styles.css`
3. Implement functionality in `script.js`
4. Test thoroughly

### Styling Guidelines
- Use CSS custom properties for colors
- Follow BEM methodology for class names
- Maintain responsive design principles
- Ensure accessibility standards

## Performance

### Optimizations
- Minified CSS and JS for production
- Optimized images
- Efficient DOM manipulation
- Lazy loading where appropriate

### Monitoring
- Console logging for debugging
- Error handling for API calls
- Loading states for user feedback

## Security

### Best Practices
- Input validation
- XSS prevention
- Secure API communication
- HTTPS in production

## License

This frontend is part of the MORVO project and follows the same license terms.
