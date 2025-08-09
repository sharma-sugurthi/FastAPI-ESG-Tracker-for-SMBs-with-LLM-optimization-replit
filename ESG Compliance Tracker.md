# ESG Compliance Tracker

A comprehensive FastAPI backend for ESG (Environmental, Social, Governance) compliance tracking designed specifically for retail SMBs (Small-Medium Businesses). Optimized for free LLM usage and cost-efficient deployment.

## 🌟 Features

### Core Functionality
- **User Authentication**: Firebase Auth or Supabase integration with JWT session management
- **ESG Questionnaire**: 10-question assessment with industry-specific defaults
- **CSV Data Upload**: Pandas-based parsing with LLM-powered missing value suggestions
- **Web Scraping**: GDPR-compliant ESG content extraction from public URLs
- **Regulatory Alerts**: Google News RSS integration with LLM summarization
- **AI Task Generator**: Personalized ESG improvement tasks with gamification
- **Enhanced Scoring**: Detailed ESG scoring with sub-categories and recommendations

### LLM Integration
- **Multi-Provider Support**: Groq, Gemini, OpenAI, Replicate, and Ollama
- **Cost-Optimized**: Prioritizes free/low-cost providers (Groq, Gemini)
- **Fallback System**: Automatic provider switching when APIs are unavailable
- **Configurable**: Switch providers via environment variables

### Deployment Ready
- **Docker Support**: Complete containerization with docker-compose
- **Render Integration**: One-click deployment to Render.com
- **Environment Configuration**: Comprehensive .env setup
- **GDPR Compliant**: Privacy-first design with user consent management

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional)
- API keys for LLM providers (Groq recommended for free tier)

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd esg-compliance-tracker
```

2. **Set up environment**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access the API**
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Docker Deployment

1. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

2. **Access the application**
- API: http://localhost:8000
- Database: PostgreSQL on port 5432

### Render Deployment

1. **Connect your GitHub repository to Render**
2. **Use the provided `render.yaml` configuration**
3. **Set environment variables in Render dashboard**
4. **Deploy automatically on git push**

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info
- `GET /auth/providers` - Available auth providers

### ESG Assessment
- `GET /esg/questions` - Get ESG questionnaire
- `POST /esg/questionnaire` - Submit questionnaire with LLM suggestions
- `POST /esg/score/enhanced` - Calculate detailed ESG score

### Data Upload
- `POST /upload/csv-upload` - Upload and process ESG CSV data
- `GET /upload/csv-template` - Download CSV template
- `POST /upload/validate-csv` - Validate CSV structure

### Web Scraping & Alerts
- `POST /scraping/scrape` - Scrape URL for ESG content (GDPR compliant)
- `GET /scraping/alerts` - Get regulatory alerts from news sources
- `GET /scraping/gdpr/privacy-notice` - GDPR privacy information

### AI Tasks & Gamification
- `POST /tasks/generate` - Generate personalized ESG tasks
- `GET /tasks/templates/{industry}` - Get task templates
- `POST /tasks/progress/{task_id}` - Update task progress
- `GET /tasks/badges` - Available achievement badges
- `GET /tasks/leaderboard` - ESG performance leaderboard

## 🔧 Configuration

### Environment Variables

#### Application Settings
```env
APP_NAME=ESG Compliance Tracker
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

#### Authentication
```env
SECRET_KEY=your-secret-key
# Firebase or Supabase credentials
FIREBASE_PROJECT_ID=your-project-id
SUPABASE_URL=your-supabase-url
```

#### LLM Configuration
```env
MODEL_PROVIDER=groq  # groq, gemini, openai, replicate, ollama
GROQ_API_KEY=your-groq-key
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
```

#### Database
```env
DATABASE_URL=postgresql://user:password@localhost:5432/esg_tracker
```

### LLM Provider Setup

#### Groq (Recommended - Free Tier)
1. Sign up at https://console.groq.com/
2. Get API key from dashboard
3. Set `MODEL_PROVIDER=groq` and `GROQ_API_KEY`

#### Google Gemini (Free Tier)
1. Get API key from Google AI Studio
2. Set `MODEL_PROVIDER=gemini` and `GEMINI_API_KEY`

#### OpenAI (Paid)
1. Get API key from OpenAI dashboard
2. Set `MODEL_PROVIDER=openai` and `OPENAI_API_KEY`

#### Local Ollama
1. Install Ollama locally
2. Run `ollama run llama3`
3. Set `MODEL_PROVIDER=ollama`

## 🏗️ Architecture

### Project Structure
```
esg-compliance-tracker/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Configuration and security
│   ├── models/        # Pydantic models
│   ├── services/      # Business logic
│   └── utils/         # Utility functions
├── deployment/        # Deployment configurations
├── docs/             # Documentation
├── tests/            # Test files
├── Dockerfile        # Docker configuration
├── docker-compose.yml
├── render.yaml       # Render deployment
└── requirements.txt
```

### Key Components

#### LLM Service (`app/services/llm_service.py`)
- Modular provider system
- Automatic fallback handling
- ESG-specific prompt engineering
- Cost optimization

#### Scoring Engine (`app/services/scoring_service.py`)
- Weighted ESG scoring
- Sub-category analysis
- Industry benchmarking
- Improvement recommendations

#### CSV Processing (`app/services/csv_service.py`)
- Pandas-based data validation
- LLM-powered missing value imputation
- Industry-specific templates
- Error handling and reporting

#### Web Scraping (`app/services/scraping_service.py`)
- GDPR-compliant data collection
- ESG keyword extraction
- Robots.txt compliance
- Rate limiting and error handling

## 🔒 Privacy & Compliance

### GDPR Compliance
- **User Consent**: Required for all web scraping operations
- **Data Minimization**: Only ESG-relevant content is extracted
- **Right to Erasure**: Users can delete their data
- **Retention Limits**: Data automatically deleted after 30 days
- **Privacy Notice**: Comprehensive privacy information available

### Security Features
- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Input validation and sanitization
- Rate limiting on scraping endpoints

## 🧪 Testing

### Run Tests
```bash
pytest tests/ -v
```

### Test Coverage
```bash
pytest --cov=app tests/
```

### API Testing
Use the interactive documentation at `/docs` to test all endpoints with sample data.

## 📊 ESG Scoring Methodology

### Scoring Categories
- **Environmental (40%)**: Emissions, energy, waste management
- **Social (30%)**: Diversity, employee satisfaction, community impact
- **Governance (30%)**: Ethics, transparency, compliance

### Badge System
- 🌱 **ESG Beginner** (0-49 points)
- 🌿 **ESG Starter** (50-59 points)
- 🌱 **Eco Improver** (60-69 points)
- ⭐ **Sustainability Star** (70-79 points)
- 🌍 **Green Leader** (80-89 points)
- 🏆 **ESG Champion** (90-100 points)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

#### LLM Provider Errors
- Check API key configuration
- Verify provider availability
- Try switching to a different provider

#### CSV Upload Issues
- Ensure CSV follows the template format
- Check file size limits (10MB max)
- Verify column mappings

#### Authentication Problems
- Verify Firebase/Supabase configuration
- Check JWT secret key
- Ensure CORS settings allow your frontend domain

### Getting Help
- Check the `/docs` endpoint for API documentation
- Review environment variable configuration
- Check application logs for detailed error messages

## 🔮 Roadmap

- [ ] Database integration (PostgreSQL/SQLite)
- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Mobile app integration
- [ ] Multi-language support
- [ ] Industry-specific modules
- [ ] Third-party ESG data integration
- [ ] Automated compliance reporting

---

**Built with ❤️ for sustainable business practices**

