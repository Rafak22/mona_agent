# MORVO Backend

Java Spring Boot backend for the MORVO marketing analytics system.

## Features

- **SEO Data API**: Fetch keyword rankings and SEO performance data
- **Posts Data API**: Retrieve social media posts and engagement metrics
- **Mentions Data API**: Get brand mentions and sentiment analysis
- **Supabase Integration**: Direct connection to your existing database tables

## API Endpoints

- `GET /api/seo` - Fetch SEO data from `almarai_seo_examples`
- `GET /api/posts` - Fetch posts data from `almarai_posts_examples`
- `GET /api/mentions` - Fetch mentions data from `almarai_mentions_examples`
- `GET /api/health` - Health check endpoint

## Setup

### Prerequisites
- Java 17 or higher
- Maven 3.6+

### Environment Variables
Set these in Railway:
- `SUPABASE_DB_URL`: Your Supabase database URL
- `SUPABASE_DB_USERNAME`: Database username (usually 'postgres')
- `SUPABASE_DB_PASSWORD`: Database password
- `PORT`: Port number (Railway sets this automatically)

### Local Development
1. Clone the repository
2. Set environment variables
3. Run: `mvn spring-boot:run`
4. Access at: `http://localhost:8080`

### Railway Deployment
1. Connect your GitHub repo to Railway
2. Railway will automatically detect the Dockerfile
3. Set environment variables in Railway dashboard
4. Deploy!

## Database Tables

The backend connects to three main tables:
- `almarai_seo_examples` - SEO keyword tracking
- `almarai_posts_examples` - Social media posts
- `almarai_mentions_examples` - Brand mentions

## Next Steps

- Add LangGraph4j logic flows
- Implement data processing rules
- Add authentication and security
- Create scheduled jobs for data updates 