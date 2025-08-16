# MORVO Streamlit Deployment Guide

## Overview

This guide explains how to deploy the MORVO AI agent using Streamlit instead of FastAPI. The Streamlit version provides the same functionality as the original FastAPI application but with a more user-friendly web interface.

## Features

- 🤖 **AI Chat Interface**: Interactive chat with MORVO marketing assistant
- 📊 **Onboarding Flow**: User profile creation and setup
- 💾 **Data Persistence**: Supabase integration for conversation history
- 🌐 **Arabic Language Support**: Full RTL support and Arabic interface
- 🔧 **Profile Management**: User profile storage and retrieval
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Migration from FastAPI to Streamlit

### What Changed

1. **Frontend**: Replaced HTML/CSS/JS frontend with Streamlit components
2. **Backend**: Converted FastAPI endpoints to Streamlit session state management
3. **Deployment**: Updated Docker configuration for Streamlit
4. **Port**: Changed from port 8000 (FastAPI) to port 8501 (Streamlit)

### What Stayed the Same

- ✅ All business logic (onboarding, chat, profile management)
- ✅ Supabase integration
- ✅ OpenAI integration
- ✅ Conversation logging
- ✅ Arabic language support
- ✅ All tools and utilities

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional)
- Environment variables set up

### Environment Variables

Create a `.env` file with:

```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Access the app**: Open http://localhost:8501

### Using the Deployment Script

```bash
# Run locally
python deploy_streamlit.py local

# Run in Docker
python deploy_streamlit.py docker

# Build Docker image only
python deploy_streamlit.py build
```

## Docker Deployment

### Build the Image

```bash
docker build -f Dockerfile.streamlit -t morvo-streamlit:latest .
```

### Run the Container

```bash
docker run -p 8501:8501 --env-file .env morvo-streamlit:latest
```

### Docker Compose (Optional)

Create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  morvo-streamlit:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    restart: unless-stopped
```

## Cloud Deployment

### Railway

1. **Update Railway configuration**:
   - Change the Dockerfile reference to `Dockerfile.streamlit`
   - Update port from 8000 to 8501

2. **Deploy**:
   ```bash
   railway up
   ```

### Render

1. **Create a new Web Service**
2. **Set build command**: `pip install -r requirements.txt`
3. **Set start command**: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
4. **Set environment variables**
5. **Deploy**

### Streamlit Cloud

1. **Push your code to GitHub**
2. **Connect to Streamlit Cloud**
3. **Set environment variables**
4. **Deploy**

## File Structure

```
mona_agent/
├── streamlit_app.py          # Main Streamlit application
├── Dockerfile.streamlit      # Docker configuration for Streamlit
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── deploy_streamlit.py       # Deployment script
├── requirements.txt          # Updated with Streamlit
├── main.py                   # Original FastAPI app (kept for reference)
├── Dockerfile               # Original Dockerfile (kept for reference)
└── ...                      # All other existing files
```

## Configuration

### Streamlit Configuration

The `.streamlit/config.toml` file contains:

- **Server settings**: Port, address, CORS settings
- **Theme**: Custom colors and fonts
- **Security**: XSRF protection settings

### Customization

You can customize the appearance by modifying:

1. **CSS styles** in `streamlit_app.py`
2. **Theme settings** in `.streamlit/config.toml`
3. **Layout** using Streamlit components

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Kill process using port 8501
   lsof -ti:8501 | xargs kill -9
   ```

2. **Environment variables not loaded**:
   - Ensure `.env` file exists
   - Check variable names match exactly

3. **Supabase connection issues**:
   - Verify URL and API key
   - Check network connectivity

4. **OpenAI API errors**:
   - Verify API key is valid
   - Check API quota and limits

### Debug Mode

Run with debug information:

```bash
streamlit run streamlit_app.py --logger.level=debug
```

## Performance Optimization

### For Production

1. **Enable caching**:
   ```python
   @st.cache_data
   def expensive_function():
       # Your expensive computation
       pass
   ```

2. **Use session state efficiently**:
   - Minimize state updates
   - Clear unused state variables

3. **Optimize database queries**:
   - Use connection pooling
   - Implement query caching

## Monitoring

### Health Checks

The application includes health checks at:
- `http://localhost:8501/_stcore/health`

### Logging

Logs are available in:
- Streamlit logs (console)
- Application logs (if configured)

## Migration Checklist

- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Database schema verified
- [ ] API keys tested
- [ ] Local deployment working
- [ ] Docker build successful
- [ ] Cloud deployment configured
- [ ] Health checks passing
- [ ] User testing completed

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review Streamlit documentation
3. Check application logs
4. Verify environment configuration

## License

This project maintains the same license as the original MORVO agent. 