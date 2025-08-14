# MORVO Agent - Technical Specification

## System Architecture Overview

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Supabase      │
│   (Client)      │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   LangGraph     │
                       │   Workflow      │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   OpenAI API    │
                       │   (GPT-4o-mini) │
                       └─────────────────┘
```

## Core Components Deep Dive

### 1. Onboarding System (`onboarding_graph.py`)

#### State Management
```python
class OBState(TypedDict, total=False):
    user_id: str
    profile: Dict[str, Any]        # Database fields
    ui: UIBlock                     # UI state
    user_name: Optional[str]
    preferred_name: Optional[str]
    preferred_choice: Optional[str]
    conversation_history: List[Dict[str, str]]
    current_step: str
    step_data: Dict[str, Any]
    ai_insights: Optional[str]
```

#### Workflow Nodes
1. **n_smart_intro**: Initial greeting and name collection
2. **n_smart_role**: Role selection with contextual options
3. **n_smart_industry**: Industry identification with suggestions
4. **n_smart_company_size**: Company size assessment
5. **n_smart_website_status**: Website status with conditional logic
6. **n_smart_website_url**: URL validation and collection
7. **n_smart_goals**: Marketing goals definition
8. **n_smart_budget**: Budget range specification
9. **n_complete_onboarding**: Profile completion and welcome

#### Validation Functions
```python
def validate_name(name: str) -> tuple[bool, str]:
    # Arabic and Latin name validation
    # Handles cultural considerations
    # Returns (is_valid, cleaned_name)

def validate_url(url: str) -> tuple[bool, str]:
    # URL format validation
    # Returns (is_valid, cleaned_url)

def validate_goals(goals: str) -> tuple[bool, List[str]]:
    # Goals parsing and validation
    # Returns (is_valid, goals_list)
```

### 2. Agent System (`agent.py`)

#### Query Routing Logic
```python
def route_query(message: str) -> Optional[str]:
    # Marketing strategy analysis
    if any(keyword in message_lower for keyword in ["استراتيجية", "خطة"]):
        return analyze_marketing_strategy(...)
    
    # Content ideas
    if any(keyword in message_lower for keyword in ["محتوى", "أفكار"]):
        return generate_content_ideas(...)
    
    # Competitor analysis
    if any(keyword in message_lower for keyword in ["منافسين", "منافس"]):
        return analyze_competitor_strategy(...)
    
    # ROI analysis
    if any(keyword in message_lower for keyword in ["roi", "عائد"]):
        return calculate_roi_metrics(...)
    
    # SEO analysis
    if any(keyword in message_lower for keyword in ["seo", "محركات البحث"]):
        return analyze_seo(...)
    
    # General insights
    return fetch_openai_insight(message)
```

#### Profile Integration
```python
def run_agent(message: str, user_profile: Dict[str, Any] = None, 
              conversation_history: List[Dict[str, str]] = None) -> str:
    # Try specialized tools first
    tool_response = route_query(message)
    if tool_response:
        return tool_response
    
    # Prepare context from user profile
    context = build_profile_context(user_profile)
    
    # Enhanced system prompt with context
    enhanced_system = MORVO_SYSTEM_PROMPT + context
    
    # Get response from OpenAI
    return answer_with_openai(message, enhanced_system, conversation_history)
```

### 3. OpenAI Tools (`tools/openai_insights_tool.py`)

#### Tool Functions
```python
@tool
def fetch_openai_insight(query: str, context: Optional[str] = None, 
                        profile_data: Optional[Dict[str, Any]] = None) -> str:
    # Real-time marketing insights
    # Context-aware responses
    # Profile-based personalization

@tool
def analyze_marketing_strategy(business_type: str, goals: List[str], 
                              budget: str, current_channels: Optional[List[str]] = None) -> str:
    # Comprehensive strategy development
    # Saudi market considerations
    # Budget optimization

@tool
def generate_content_ideas(content_type: str, industry: str, 
                          target_audience: str, platform: str) -> str:
    # Platform-specific content suggestions
    # Cultural considerations
    # Engagement strategies

@tool
def analyze_competitor_strategy(competitor_name: str, industry: str, 
                               focus_areas: Optional[List[str]] = None) -> str:
    # Competitive intelligence
    # Market positioning analysis
    # Differentiation opportunities

@tool
def calculate_roi_metrics(campaign_cost: float, revenue_generated: float, 
                         campaign_duration: str, channel: str) -> str:
    # ROI calculation
    # Performance analysis
    # Optimization recommendations
```

### 4. API Endpoints (`main.py`)

#### Core Endpoints
```python
@app.post("/chat")
def chat_with_mona(user_input: UserMessage, request: Request):
    # Main conversation endpoint
    # Handles onboarding and chat logic
    # Profile-aware responses

@app.post("/onboarding/start")
def onboarding_start(event: OBStartReq):
    # Initialize onboarding flow
    # Set user state to IN_ONBOARDING

@app.post("/onboarding/step")
def onboarding_step(event: OBStepReq):
    # Continue onboarding process
    # Validate user input
    # Update profile data

@app.get("/profile/status")
def profile_status(user_id: str):
    # Check if user has completed profile
    # Return profile status

@app.post("/reset")
def reset(req: ResetRequest):
    # Clear conversation history
    # Optionally clear profile
```

## Database Schema

### Profiles Table
```sql
CREATE TABLE profiles (
    user_id UUID PRIMARY KEY,
    user_role TEXT,
    industry TEXT,
    company_size TEXT,
    website_status TEXT,
    website_url TEXT,
    primary_goals TEXT[],
    budget_range TEXT,
    marketing_experience TEXT,
    target_audience TEXT,
    current_challenges TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES profiles(user_id),
    role TEXT CHECK (role IN ('user', 'assistant')),
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Data Flow

### 1. User Registration Flow
```
User Input → Validation → State Update → Database Save → Response
```

### 2. Chat Flow
```
User Message → Query Analysis → Tool Routing → OpenAI Response → Database Log → Response
```

### 3. Onboarding Flow
```
Start → Step 1 → Validation → Step 2 → ... → Complete → Profile Save
```

## Error Handling

### OpenAI API Errors
```python
try:
    response = openai.ChatCompletion.create(...)
except openai.error.AuthenticationError:
    return "🔑 خطأ في إعدادات API"
except openai.error.RateLimitError:
    return "⚠️ تم استنفاذ الحد المسموح"
except openai.error.APITimeoutError:
    return "⏰ انتهت مهلة الطلب"
except Exception as e:
    return f"❌ حدث خطأ: {str(e)}"
```

### Database Errors
```python
try:
    _sb.table("profiles").upsert(payload).execute()
except Exception as e:
    logging.error(f"Database error: {e}")
    # Continue without database save
```

### Validation Errors
```python
def validate_name(name: str) -> tuple[bool, str]:
    if not name.strip():
        return False, "الاسم مطلوب"
    
    if name.lower() in _NON_NAMES:
        return False, "هذا ليس اسماً صحيحاً"
    
    # Additional validation logic
    return True, cleaned_name
```

## Performance Considerations

### Caching Strategy
- User profile caching in memory
- Conversation history caching
- Tool response caching

### Rate Limiting
- OpenAI API rate limiting
- User request rate limiting
- Database query optimization

### Scalability
- Stateless API design
- Database connection pooling
- Async request handling

## Security Measures

### Input Validation
- SQL injection prevention
- XSS protection
- Input sanitization

### Authentication
- User ID validation
- Session management
- API key protection

### Data Protection
- Sensitive data encryption
- GDPR compliance
- Data retention policies

## Monitoring and Logging

### Application Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log user interactions
logger.info(f"User {user_id} sent message: {message[:50]}...")

# Log errors
logger.error(f"Error processing request: {e}")
```

### Performance Monitoring
- Response time tracking
- Error rate monitoring
- API usage metrics
- Database performance

### User Analytics
- User behavior tracking
- Feature usage statistics
- Conversion metrics
- User satisfaction scores

## Testing Strategy

### Unit Tests
```python
def test_name_validation():
    assert validate_name("أحمد") == (True, "أحمد")
    assert validate_name("") == (False, "الاسم مطلوب")
    assert validate_name("ايه") == (False, "هذا ليس اسماً صحيحاً")

def test_url_validation():
    assert validate_url("https://example.com") == (True, "https://example.com")
    assert validate_url("invalid-url") == (False, "الرابط غير صحيح")
```

### Integration Tests
```python
def test_onboarding_flow():
    # Test complete onboarding flow
    result = start_onboarding("test_user")
    assert result["done"] == False
    
    result = resume_onboarding("test_user", "أحمد")
    assert result["done"] == False
    
    # Continue through all steps...
```

### API Tests
```python
def test_chat_endpoint():
    response = client.post("/chat", json={
        "user_id": "test_user",
        "message": "مرحبا"
    })
    assert response.status_code == 200
    assert "reply" in response.json()
```

## Deployment Configuration

### Environment Variables
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Database Configuration
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:3000,https://app.example.com
```

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
- Load balancing
- Auto-scaling
- Health checks
- Backup strategies
- Disaster recovery
- SSL/TLS configuration

## Development Workflow

### Code Standards
- PEP 8 compliance
- Type hints usage
- Docstring documentation
- Error handling
- Logging standards

### Git Workflow
- Feature branches
- Pull request reviews
- Automated testing
- Deployment automation

### Code Review Checklist
- [ ] Functionality works as expected
- [ ] Error handling is comprehensive
- [ ] Performance is acceptable
- [ ] Security considerations addressed
- [ ] Documentation is updated
- [ ] Tests are included

This technical specification provides a comprehensive overview of the MORVO agent system architecture, implementation details, and development guidelines for building and maintaining the application.
