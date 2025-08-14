# MORVO Agent - Smart Marketing Assistant for Saudi Market

## Project Overview

MORVO is an intelligent Arabic marketing assistant designed specifically for the Saudi market. It provides personalized marketing consultations, analyzes brand data, and offers actionable insights for businesses in Saudi Arabia.

## Core Features

### 🤖 Smart Onboarding System
- **LangGraph-based onboarding flow** with AI-powered responses
- **Multi-step user profiling**: name, role, industry, company size, website status, goals, budget
- **Smart validation** for Arabic and Latin names, URLs, and user inputs
- **Contextual responses** based on user profile data
- **Persistent profile storage** in Supabase database

### 💬 Intelligent Chat System
- **Context-aware responses** using user profile data
- **Conversation history** tracking and management
- **Multi-language support** (Arabic primary, English secondary)
- **Smart query routing** to specialized tools
- **Error handling** with graceful fallbacks

### 🛠️ Specialized Marketing Tools
- **OpenAI Insights Tool**: Real-time marketing insights and recommendations
- **Marketing Strategy Analysis**: Comprehensive strategy development
- **Content Ideas Generator**: Platform-specific content suggestions
- **Competitor Analysis**: Market intelligence and competitive insights
- **ROI Calculator**: Campaign performance analysis
- **SEO Analysis**: Search engine optimization insights
- **Mentions Tracker**: Brand reputation monitoring
- **Posts Analyzer**: Social media content performance

## Technical Architecture

### Backend Stack
- **FastAPI**: High-performance web framework
- **LangGraph**: State management and workflow orchestration
- **OpenAI GPT-4o-mini**: AI language model for responses
- **Supabase**: Database and authentication
- **Python 3.8+**: Core programming language

### Key Components

#### 1. Onboarding System (`onboarding_graph.py`)
```python
# Smart onboarding with LangGraph
- State management with OBState
- AI-powered contextual responses
- Validation functions for user inputs
- Conditional workflow routing
- Database persistence
```

#### 2. Agent System (`agent.py`)
```python
# Enhanced agent with tool integration
- Query routing to specialized tools
- Profile-aware responses
- Conversation history management
- Error handling and fallbacks
```

#### 3. OpenAI Tools (`tools/openai_insights_tool.py`)
```python
# Specialized marketing tools
- fetch_openai_insight(): General marketing insights
- analyze_marketing_strategy(): Strategy development
- generate_content_ideas(): Content planning
- analyze_competitor_strategy(): Competitive analysis
- calculate_roi_metrics(): Performance analysis
```

#### 4. API Endpoints (`main.py`)
```python
# RESTful API endpoints
- /chat: Main conversation endpoint
- /onboarding/start: Start onboarding flow
- /onboarding/step: Continue onboarding
- /profile/status: Check user profile
- /reset: Reset conversation/profile
- /openai/chat: Direct OpenAI access
```

### Database Schema

#### Profiles Table
```sql
- user_id (UUID, primary key)
- user_role (text)
- industry (text)
- company_size (text)
- website_status (text)
- website_url (text)
- primary_goals (array)
- budget_range (text)
- marketing_experience (text)
- target_audience (text)
- current_challenges (text)
```

#### Messages Table
```sql
- user_id (UUID)
- role (text: 'user' or 'assistant')
- content (text)
- created_at (timestamp)
```

## User Experience Flow

### 1. Initial Interaction
- User greets or starts conversation
- System detects new user and initiates onboarding
- Smart greeting with personalized introduction

### 2. Onboarding Process
- **Step 1**: Name collection with validation
- **Step 2**: Role selection (marketing manager, entrepreneur, etc.)
- **Step 3**: Industry identification
- **Step 4**: Company size assessment
- **Step 5**: Website status and URL collection
- **Step 6**: Marketing goals definition
- **Step 7**: Budget range specification
- **Step 8**: Profile completion and welcome

### 3. Ongoing Conversations
- Profile-aware responses
- Specialized tool routing based on queries
- Conversation history maintenance
- Contextual recommendations

## Key Features for Saudi Market

### Cultural Considerations
- **Arabic language support** with proper RTL handling
- **Saudi business context** awareness
- **Local market trends** integration
- **Cultural sensitivity** in responses
- **Ramadan and holiday** awareness

### Business Intelligence
- **Saudi market insights** and trends
- **Local competitor analysis**
- **Regional marketing strategies**
- **Budget considerations** in Saudi Riyals
- **Platform preferences** for Saudi audience

## Development Environment

### Prerequisites
```bash
Python 3.8+
pip install -r requirements.txt
```

### Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

### Installation
```bash
# Clone repository
git clone <repository_url>
cd mona_agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the application
python main.py
```

## API Usage Examples

### Start Onboarding
```bash
curl -X POST "http://localhost:8000/onboarding/start" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

### Continue Onboarding
```bash
curl -X POST "http://localhost:8000/onboarding/step" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "value": "أحمد"}'
```

### Chat Conversation
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "message": "كيف أحسن استراتيجية التسويق الرقمي؟"}'
```

## Project Structure
```
mona_agent/
├── main.py                 # FastAPI application
├── agent.py               # Enhanced agent logic
├── onboarding_graph.py    # LangGraph onboarding system
├── schema.py              # Pydantic models
├── memory_store.py        # User state management
├── tools/
│   ├── openai_insights_tool.py    # Marketing insights
│   ├── mentions_tool.py           # Brand monitoring
│   ├── posts_tool.py              # Social media analysis
│   ├── seo_tool.py                # SEO analysis
│   ├── perplexity_tool.py         # Web search
│   ├── conversation_logger.py     # Logging utilities
│   └── supabase_client.py         # Database client
├── prompts/
│   ├── mona_intro_prompt.txt      # Introduction prompts
│   └── morvo_prompt.txt           # Main system prompts
├── requirements.txt               # Python dependencies
└── pyproject.toml                 # Project configuration
```

## Future Enhancements

### Planned Features
- **Multi-modal support** (images, documents)
- **Advanced analytics dashboard**
- **Integration with Saudi social platforms**
- **Voice interaction capabilities**
- **Advanced AI model fine-tuning**
- **Real-time market data integration**

### Technical Improvements
- **Microservices architecture**
- **Advanced caching strategies**
- **Real-time notifications**
- **Advanced security features**
- **Performance optimization**
- **Scalability improvements**

## Contributing

### Development Guidelines
- Follow Arabic-first design principles
- Maintain cultural sensitivity
- Use comprehensive error handling
- Write clear documentation
- Include unit tests for new features
- Follow PEP 8 coding standards

### Testing
```bash
# Run tests
python -m pytest tests/

# Run specific test
python test_enhanced_system.py
```

## Support and Maintenance

### Monitoring
- Application performance monitoring
- Error tracking and alerting
- User behavior analytics
- API usage metrics

### Maintenance
- Regular dependency updates
- Security patches
- Performance optimization
- Feature enhancements

## Contact and Support

For technical support, feature requests, or contributions:
- **Repository**: [GitHub Repository URL]
- **Documentation**: [Documentation URL]
- **Issues**: [GitHub Issues URL]

---

This project represents a comprehensive solution for Arabic marketing assistance, specifically tailored for the Saudi market with advanced AI capabilities, smart onboarding, and specialized marketing tools.
