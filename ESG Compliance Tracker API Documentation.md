# ESG Compliance Tracker API Documentation

## Base URL
- Local Development: `http://localhost:8000`
- Production: `https://your-app.onrender.com`

## Authentication

All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Endpoints Overview

### Authentication (`/auth`)
- User registration and login
- JWT token management
- Provider information

### ESG Assessment (`/esg`)
- Questionnaire management
- ESG scoring and analysis
- Industry benchmarking

### Data Upload (`/upload`)
- CSV file processing
- Template downloads
- Data validation

### Web Scraping (`/scraping`)
- GDPR-compliant web scraping
- Regulatory alerts
- Privacy management

### AI Tasks (`/tasks`)
- Task generation
- Progress tracking
- Gamification features

---

## Authentication Endpoints

### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe",
  "company_name": "Green Retail Co.",
  "industry": "retail"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "user-123",
    "email": "user@example.com",
    "full_name": "John Doe",
    "company_name": "Green Retail Co.",
    "industry": "retail",
    "created_at": "2024-01-15T10:30:00Z",
    "is_active": true
  }
}
```

### POST /auth/login
Authenticate user and receive access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:** Same as registration response.

### GET /auth/me
Get current user information (requires authentication).

**Response:**
```json
{
  "id": "user-123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "company_name": "Green Retail Co.",
  "industry": "retail",
  "created_at": "2024-01-15T10:30:00Z",
  "is_active": true
}
```

### GET /auth/providers
Get available authentication providers.

**Response:**
```json
{
  "providers": ["firebase", "supabase"],
  "default": "firebase"
}
```

---

## ESG Assessment Endpoints

### GET /esg/questions
Get the standard ESG questionnaire (10 questions).

**Response:**
```json
[
  {
    "id": "energy_consumption",
    "category": "environmental",
    "question": "What is your annual energy consumption?",
    "question_type": "numeric",
    "unit": "kWh",
    "weight": 0.15,
    "industry_default": 50000,
    "help_text": "Include electricity, gas, and other energy sources",
    "required": true
  }
]
```

### POST /esg/questionnaire
Submit ESG questionnaire with optional LLM suggestions.

**Request Body:**
```json
{
  "answers": [
    {
      "question_id": "energy_consumption",
      "value": 45000,
      "is_llm_suggested": false,
      "source": "user_input"
    }
  ],
  "company_name": "Green Retail Co.",
  "industry": "retail",
  "use_llm_suggestions": true
}
```

**Response:**
```json
{
  "questionnaire": {
    "user_id": "user-123",
    "company_name": "Green Retail Co.",
    "industry": "retail",
    "answers": [...],
    "completed_at": "2024-01-15T10:30:00Z",
    "score": 72.5
  },
  "score": {
    "overall_score": 72.5,
    "environmental_score": 68.0,
    "social_score": 75.0,
    "governance_score": 74.0,
    "badge": "Sustainability Star",
    "improvement_areas": ["Energy efficiency"],
    "strengths": ["Good social impact"],
    "calculated_at": "2024-01-15T10:30:00Z"
  },
  "suggested_answers": [...],
  "tasks": [...]
}
```

### POST /esg/score/enhanced
Calculate enhanced ESG score with detailed breakdown.

**Request Body:**
```json
{
  "answers": [...],
  "industry": "retail",
  "company_size": "small"
}
```

**Response:**
```json
{
  "overall_score": 72.5,
  "environmental_score": 68.0,
  "social_score": 75.0,
  "governance_score": 74.0,
  "emissions_score": 65.0,
  "energy_score": 70.0,
  "waste_score": 69.0,
  "diversity_score": 78.0,
  "employee_score": 72.0,
  "community_score": 75.0,
  "ethics_score": 76.0,
  "transparency_score": 72.0,
  "badge": "Sustainability Star",
  "level": 8,
  "improvement_areas": ["Energy efficiency", "Waste management"],
  "strengths": ["Strong diversity practices"],
  "industry_percentile": 75.0,
  "trend": "improving",
  "calculated_at": "2024-01-15T10:30:00Z",
  "quick_wins": ["Switch to LED lighting"],
  "long_term_goals": ["Achieve carbon neutrality"]
}
```

---

## Data Upload Endpoints

### POST /upload/csv-upload
Upload and process ESG CSV file.

**Request (multipart/form-data):**
- `file`: CSV/Excel file
- `use_llm_for_missing`: boolean (default: true)
- `industry`: string (default: "retail")
- `company_name`: string (optional)
- `column_mapping`: JSON string (optional)

**Response:**
```json
{
  "upload_id": "upload-123",
  "filename": "esg_data.csv",
  "processing_result": {
    "status": "valid",
    "total_rows": 100,
    "valid_rows": 95,
    "invalid_rows": 5,
    "errors": [...],
    "warnings": [...],
    "processed_data": [...],
    "llm_suggestions": [...],
    "esg_score": 68.5
  },
  "download_url": "/upload/download/upload-123",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### GET /upload/csv-template
Get CSV template information.

**Response:**
```json
{
  "filename": "esg_data_template.csv",
  "headers": ["energy_consumption", "co2_emissions", ...],
  "sample_data": [...],
  "description": "ESG data template for retail SMBs",
  "mappings": [...]
}
```

### GET /upload/csv-template/download
Download CSV template file.

**Response:** CSV file download

### POST /upload/validate-csv
Validate CSV structure without processing.

**Request:** Same as csv-upload (file only)

**Response:**
```json
{
  "filename": "data.csv",
  "total_rows": 100,
  "total_columns": 15,
  "column_info": [...],
  "matched_esg_columns": ["energy_consumption", "co2_emissions"],
  "unmatched_columns": ["custom_field"],
  "suggested_mappings": {...}
}
```

---

## Web Scraping Endpoints

### POST /scraping/scrape
Scrape URL for ESG content (GDPR compliant).

**Request Body:**
```json
{
  "url": "https://example.com/sustainability",
  "user_consent": true,
  "extract_esg_only": true,
  "keywords": ["sustainability", "emissions"],
  "max_content_length": 10000
}
```

**Response:**
```json
{
  "request_id": "scrape-123",
  "status": "completed",
  "url": "https://example.com/sustainability",
  "scraped_content": {
    "url": "https://example.com/sustainability",
    "title": "Our Sustainability Commitment",
    "content": "We are committed to reducing our carbon footprint...",
    "esg_signals": ["carbon footprint reduction", "renewable energy"],
    "keywords_found": ["sustainability", "emissions"],
    "content_length": 5000,
    "scraped_at": "2024-01-15T10:30:00Z"
  },
  "gdpr_compliance": {
    "user_consent_given": true,
    "consent_timestamp": "2024-01-15T10:30:00Z",
    "data_retention_days": 30,
    "purpose_limitation": "ESG analysis only"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:31:00Z"
}
```

### GET /scraping/alerts
Get regulatory alerts from news sources.

**Query Parameters:**
- `keywords`: comma-separated keywords
- `max_results`: integer (default: 10)
- `days_back`: integer (default: 7)
- `min_relevance_score`: float (default: 0.5)

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert-123",
      "title": "New ESG Reporting Requirements",
      "summary": "Companies must report additional ESG metrics...",
      "source": "google_news",
      "source_url": "https://news.example.com/article",
      "category": "regulatory",
      "keywords": ["ESG", "reporting"],
      "relevance_score": 0.9,
      "published_at": "2024-01-15T08:00:00Z",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_found": 25,
  "search_keywords": ["ESG", "regulations"],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### GET /scraping/gdpr/privacy-notice
Get GDPR privacy notice for web scraping.

**Response:**
```json
{
  "privacy_notice": {
    "purpose": "ESG content analysis for compliance tracking",
    "data_collected": "Public web content, ESG-related text snippets",
    "retention_period": "30 days",
    "user_rights": [...],
    "legal_basis": "Legitimate interest for business compliance analysis"
  },
  "consent_form": {
    "required_fields": [...],
    "consent_text": "I consent to the collection..."
  }
}
```

---

## AI Tasks Endpoints

### POST /tasks/generate
Generate personalized ESG improvement tasks.

**Request Body:**
```json
{
  "user_esg_data": {
    "energy_consumption": 45000,
    "co2_emissions": 8.5,
    "diversity_percentage": 35
  },
  "industry": "retail",
  "company_size": "small",
  "max_tasks": 5,
  "difficulty_preference": "medium"
}
```

**Response:**
```json
{
  "tasks": [
    {
      "id": "task-123",
      "task": "Switch to LED lighting in all store locations",
      "description": "Replace traditional lighting with energy-efficient LEDs",
      "points": 25,
      "category": "environmental",
      "difficulty": "easy",
      "estimated_impact": "medium",
      "estimated_cost": "Low ($500-2000)",
      "timeline": "2-4 weeks",
      "resources_needed": ["LED bulbs", "electrician"],
      "success_metrics": ["Energy consumption reduction"],
      "industry_specific": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_points_available": 175,
  "recommendations": ["Focus on energy efficiency for quick wins"],
  "priority_order": ["task-123", "task-124"],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### POST /tasks/progress/{task_id}
Update progress on a specific task.

**Request Body:**
```json
{
  "status": "completed",
  "progress_percentage": 100.0,
  "notes": "Successfully installed LED lighting in main store"
}
```

**Response:**
```json
{
  "message": "Task progress updated successfully",
  "progress": {
    "task_id": "task-123",
    "user_id": "user-123",
    "status": "completed",
    "progress_percentage": 100.0,
    "notes": "Successfully installed LED lighting",
    "completed_at": "2024-01-15T10:30:00Z",
    "points_earned": 25
  },
  "points_earned": 25
}
```

### GET /tasks/badges
Get available ESG badges and achievements.

**Response:**
```json
{
  "badges": [
    {
      "name": "Green Starter",
      "description": "Completed your first environmental task",
      "icon": "🌱",
      "points_required": 25,
      "category": "environmental"
    }
  ],
  "total_badges": 6,
  "categories": ["environmental", "social", "governance", "overall"]
}
```

### GET /tasks/leaderboard
Get ESG performance leaderboard.

**Query Parameters:**
- `industry`: filter by industry
- `limit`: number of entries (default: 10)

**Response:**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "company_name": "Green Retail Co.",
      "score": 92.5,
      "badge": "ESG Champion",
      "industry": "retail"
    }
  ],
  "filter_industry": "retail",
  "total_entries": 50
}
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "status_code": 400
}
```

### Common HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `413`: Request Entity Too Large
- `422`: Validation Error
- `500`: Internal Server Error

---

## Rate Limiting

- Web scraping endpoints: 10 requests per minute
- LLM-powered endpoints: 20 requests per minute
- Other endpoints: 100 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

---

## Sample Data

### Sample ESG Questionnaire Response
```json
{
  "energy_consumption": 45000,
  "co2_emissions": 8.5,
  "packaging_recyclability": 70,
  "diversity_percentage": 35,
  "female_leadership": 30,
  "employee_satisfaction": 7.8,
  "data_privacy_compliance": true,
  "ethics_training": 85,
  "supplier_code": false,
  "transparency_reporting": false
}
```

### Sample CSV Data Format
```csv
energy_consumption,co2_emissions,packaging_recyclability,diversity_percentage
45000,8.5,70,35
52000,9.2,65,40
38000,7.1,75,45
```

---

## Testing with cURL

### Register User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User",
    "company_name": "Test Company",
    "industry": "retail"
  }'
```

### Submit Questionnaire
```bash
curl -X POST "http://localhost:8000/esg/questionnaire" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {"question_id": "energy_consumption", "value": 45000}
    ],
    "industry": "retail",
    "use_llm_suggestions": true
  }'
```

### Upload CSV
```bash
curl -X POST "http://localhost:8000/upload/csv-upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@esg_data.csv" \
  -F "use_llm_for_missing=true" \
  -F "industry=retail"
```

---

For more examples and interactive testing, visit the automatic API documentation at `/docs` when running the application.

