# MORVO Agent - Quick Reference Guide

## 🚀 Project Summary
**MORVO** is an intelligent Arabic marketing assistant for the Saudi market, built with FastAPI, LangGraph, and OpenAI GPT-4o-mini.

## 📁 Key Files
- `main.py` - FastAPI application with endpoints
- `onboarding_graph.py` - LangGraph-based smart onboarding
- `agent.py` - Enhanced agent with tool routing
- `tools/openai_insights_tool.py` - Marketing insights and analysis tools
- `schema.py` - Pydantic models
- `memory_store.py` - User state management

## 🔧 Core Features
1. **Smart Onboarding** - AI-powered user profiling
2. **Intelligent Chat** - Context-aware responses
3. **Marketing Tools** - Strategy, content, competitor analysis
4. **Saudi Market Focus** - Cultural and business considerations

## 🛠️ Tech Stack
- **Backend**: FastAPI + Python 3.8+
- **AI**: OpenAI GPT-4o-mini
- **Workflow**: LangGraph
- **Database**: Supabase (PostgreSQL)
- **State Management**: In-memory + persistent storage

## 🔑 Environment Variables
```env
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
```

## 📡 API Endpoints
- `POST /chat` - Main conversation
- `POST /onboarding/start` - Start onboarding
- `POST /onboarding/step` - Continue onboarding
- `GET /profile/status` - Check user profile
- `POST /reset` - Reset conversation/profile

## 🗄️ Database Tables
### Profiles
- `user_id` (UUID, PK)
- `user_role`, `industry`, `company_size`
- `website_status`, `website_url`
- `primary_goals` (array), `budget_range`

### Messages
- `user_id`, `role`, `content`, `created_at`

## 🔄 User Flow
1. **Greeting** → System detects new user
2. **Onboarding** → 8-step profile collection
3. **Chat** → Profile-aware conversations
4. **Tools** → Specialized marketing insights

## 🎯 Onboarding Steps
1. Name (with Arabic/Latin validation)
2. Role (marketing manager, entrepreneur, etc.)
3. Industry (with suggestions)
4. Company size
5. Website status
6. Website URL (if applicable)
7. Marketing goals
8. Budget range

## 🛠️ Available Tools
- `fetch_openai_insight()` - General marketing insights
- `analyze_marketing_strategy()` - Strategy development
- `generate_content_ideas()` - Content planning
- `analyze_competitor_strategy()` - Competitive analysis
- `calculate_roi_metrics()` - Performance analysis
- `analyze_seo()` - SEO insights
- `fetch_mentions()` - Brand monitoring
- `fetch_posts()` - Social media analysis

## 🔍 Query Routing
The agent automatically routes queries to specialized tools based on keywords:
- "استراتيجية" → Marketing strategy analysis
- "محتوى" → Content ideas generation
- "منافسين" → Competitor analysis
- "roi" → ROI calculation
- "seo" → SEO analysis

## 🎨 Cultural Features
- **Arabic-first design** with RTL support
- **Saudi business context** awareness
- **Local market trends** integration
- **Cultural sensitivity** in responses
- **Budget in Saudi Riyals**

## 🚀 Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your_key"
export SUPABASE_URL="your_url"
export SUPABASE_ANON_KEY="your_key"

# Run application
python main.py
```

## 🧪 Testing
```bash
# Test the system
python test_enhanced_system.py

# Test specific components
python -c "from onboarding_graph import start_onboarding; print(start_onboarding('test_user'))"
```

## 📊 Key Functions

### Onboarding
```python
from onboarding_graph import start_onboarding, resume_onboarding

# Start onboarding
result = start_onboarding("user123")

# Continue with user input
result = resume_onboarding("user123", "أحمد")
```

### Agent
```python
from agent import run_agent

# Get response with profile context
response = run_agent("كيف أحسن التسويق؟", user_profile=profile_data)
```

### Tools
```python
from tools.openai_insights_tool import fetch_openai_insight

# Get marketing insights
insight = fetch_openai_insight("نصائح للتسويق الرقمي")
```

## 🔧 Common Issues & Solutions

### OpenAI API Errors
- **Authentication Error**: Check API key
- **Rate Limit**: Implement retry logic
- **Timeout**: Increase timeout settings

### Database Issues
- **Connection Failed**: Check Supabase credentials
- **Table Missing**: Run database migrations
- **Data Not Saving**: Check table permissions

### Onboarding Issues
- **Validation Errors**: Check input format
- **State Loss**: Verify LangGraph configuration
- **UI Not Updating**: Check response format

## 📈 Performance Tips
- Cache user profiles in memory
- Limit conversation history to last 10 messages
- Use async operations where possible
- Implement rate limiting for API calls

## 🔒 Security Considerations
- Validate all user inputs
- Sanitize database queries
- Protect API keys
- Implement proper error handling
- Use HTTPS in production

## 📝 Development Notes
- Follow Arabic-first design principles
- Maintain cultural sensitivity
- Use comprehensive error handling
- Write clear documentation
- Include unit tests for new features

---

**For detailed information, see:**
- `PROJECT_DESCRIPTION.md` - Complete project overview
- `TECHNICAL_SPECIFICATION.md` - Detailed technical docs
