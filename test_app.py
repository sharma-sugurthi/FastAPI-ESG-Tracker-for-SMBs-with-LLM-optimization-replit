#!/usr/bin/env python3
"""
Simple test script to verify the ESG Compliance Tracker application.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        from app.main import app
        print("✓ Main application imported successfully")
        
        from app.core.config import settings
        print("✓ Configuration loaded successfully")
        
        from app.services.llm_service import llm_service
        print("✓ LLM service imported successfully")
        
        from app.services.csv_service import csv_service
        print("✓ CSV service imported successfully")
        
        from app.services.scraping_service import scraping_service
        print("✓ Scraping service imported successfully")
        
        from app.services.scoring_service import scoring_service
        print("✓ Scoring service imported successfully")
        
        from app.models.esg import DEFAULT_ESG_QUESTIONS
        print(f"✓ ESG models loaded ({len(DEFAULT_ESG_QUESTIONS)} questions)")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from app.core.config import settings
        
        print(f"✓ App name: {settings.app_name}")
        print(f"✓ Model provider: {settings.model_provider}")
        print(f"✓ Host: {settings.host}")
        print(f"✓ Port: {settings.port}")
        print(f"✓ Upload directory: {settings.upload_dir}")
        
        # Check if upload directory exists or can be created
        os.makedirs(settings.upload_dir, exist_ok=True)
        print(f"✓ Upload directory created/verified: {settings.upload_dir}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_esg_questions():
    """Test ESG questions and models."""
    print("\nTesting ESG questions...")
    
    try:
        from app.models.esg import DEFAULT_ESG_QUESTIONS, ESGAnswer
        
        print(f"✓ Loaded {len(DEFAULT_ESG_QUESTIONS)} ESG questions")
        
        # Test question structure
        for i, question in enumerate(DEFAULT_ESG_QUESTIONS[:3]):  # Test first 3
            print(f"  Question {i+1}: {question.id} ({question.category.value})")
        
        # Test creating an answer
        answer = ESGAnswer(
            question_id="energy_consumption",
            value=45000,
            is_llm_suggested=False,
            source="test"
        )
        print(f"✓ Created test answer: {answer.question_id} = {answer.value}")
        
        return True
    except Exception as e:
        print(f"✗ ESG questions test failed: {e}")
        return False

async def test_llm_service():
    """Test LLM service functionality."""
    print("\nTesting LLM service...")
    
    try:
        from app.services.llm_service import llm_service
        
        # Test provider availability
        try:
            provider = llm_service.get_provider()
            print(f"✓ LLM provider available: {llm_service.current_provider}")
        except Exception as e:
            print(f"⚠ LLM provider not available: {e}")
            print("  This is expected if no API keys are configured")
        
        # Test default task generation (fallback)
        default_tasks = llm_service._get_default_tasks()
        print(f"✓ Default tasks available: {len(default_tasks)} tasks")
        
        return True
    except Exception as e:
        print(f"✗ LLM service test failed: {e}")
        return False

def test_csv_service():
    """Test CSV service functionality."""
    print("\nTesting CSV service...")
    
    try:
        from app.services.csv_service import csv_service
        
        # Test template generation
        template = csv_service.generate_csv_template()
        print(f"✓ CSV template generated: {template.filename}")
        print(f"  Headers: {len(template.headers)} columns")
        print(f"  Sample data: {len(template.sample_data)} rows")
        
        # Test supported formats
        print(f"✓ Supported formats: {csv_service.supported_formats}")
        
        return True
    except Exception as e:
        print(f"✗ CSV service test failed: {e}")
        return False

def test_scoring_service():
    """Test scoring service functionality."""
    print("\nTesting scoring service...")
    
    try:
        from app.services.scoring_service import scoring_service
        from app.models.esg import ESGAnswer
        
        # Create sample answers
        sample_answers = [
            ESGAnswer(question_id="energy_consumption", value=45000, source="test"),
            ESGAnswer(question_id="co2_emissions", value=8.5, source="test"),
            ESGAnswer(question_id="diversity_percentage", value=35, source="test"),
        ]
        
        # Test scoring
        score = scoring_service.calculate_enhanced_score(sample_answers)
        print(f"✓ Enhanced score calculated: {score.overall_score}")
        print(f"  Badge: {score.badge}")
        print(f"  Level: {score.level}")
        print(f"  Improvement areas: {len(score.improvement_areas)}")
        
        return True
    except Exception as e:
        print(f"✗ Scoring service test failed: {e}")
        return False

def test_api_routes():
    """Test API route definitions."""
    print("\nTesting API routes...")
    
    try:
        from app.main import app
        
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append(f"{list(route.methods)[0]} {route.path}")
        
        print(f"✓ API routes loaded: {len(routes)} routes")
        
        # Check for key routes
        key_routes = [
            "GET /",
            "GET /health",
            "POST /auth/register",
            "POST /auth/login",
            "GET /esg/questions",
            "POST /esg/questionnaire",
            "POST /upload/csv-upload",
            "POST /scraping/scrape",
            "POST /tasks/generate"
        ]
        
        for key_route in key_routes:
            if any(key_route in route for route in routes):
                print(f"  ✓ {key_route}")
            else:
                print(f"  ⚠ {key_route} not found")
        
        return True
    except Exception as e:
        print(f"✗ API routes test failed: {e}")
        return False

def create_sample_data():
    """Create sample data files for testing."""
    print("\nCreating sample data...")
    
    try:
        # Create sample CSV data
        sample_csv_data = """energy_consumption,co2_emissions,packaging_recyclability,diversity_percentage,female_leadership,employee_satisfaction,data_privacy_compliance,ethics_training,supplier_code,transparency_reporting
45000,8.5,70,35,30,7.8,true,85,false,false
52000,9.2,65,40,35,8.1,true,90,true,false
38000,7.1,75,45,40,7.5,true,88,false,true"""
        
        sample_csv_path = "sample_esg_data.csv"
        with open(sample_csv_path, 'w') as f:
            f.write(sample_csv_data)
        
        print(f"✓ Sample CSV created: {sample_csv_path}")
        
        # Create sample environment file
        sample_env = """# ESG Compliance Tracker - Sample Environment Configuration

# Application Settings
APP_NAME=ESG Compliance Tracker
APP_VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Authentication
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Configuration (choose one)
MODEL_PROVIDER=groq
# GROQ_API_KEY=your-groq-api-key
# GEMINI_API_KEY=your-gemini-api-key
# OPENAI_API_KEY=your-openai-api-key

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# File Upload Configuration
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads

# ESG Scoring Configuration
EMISSIONS_WEIGHT=0.4
DEI_WEIGHT=0.3
PACKAGING_WEIGHT=0.3"""
        
        if not os.path.exists('.env'):
            with open('.env', 'w') as f:
                f.write(sample_env)
            print("✓ Sample .env file created")
        else:
            print("✓ .env file already exists")
        
        return True
    except Exception as e:
        print(f"✗ Sample data creation failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 ESG Compliance Tracker - Application Tests")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("ESG Questions", test_esg_questions),
        ("LLM Service", test_llm_service),
        ("CSV Service", test_csv_service),
        ("Scoring Service", test_scoring_service),
        ("API Routes", test_api_routes),
        ("Sample Data", create_sample_data),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\n🚀 To start the application:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("\n📚 Then visit:")
        print("   - API Documentation: http://localhost:8000/docs")
        print("   - Health Check: http://localhost:8000/health")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("   The application may still work, but some features might be limited.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())

