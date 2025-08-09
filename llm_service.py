"""
Modular LLM service supporting multiple providers.
Supports Groq, Gemini, OpenAI, Replicate, and Ollama.
"""

from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import json
import requests
try:
    from app.core.config import settings
except Exception:
    from config import settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate_text(self, prompt: str, max_tokens: int = 150) -> str:
        """Generate text using the LLM provider."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured."""
        pass


class GroqProvider(LLMProvider):
    """Groq LLM provider."""
    
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama3-8b-8192"  # Fast and free model
    
    async def generate_text(self, prompt: str, max_tokens: int = 150) -> str:
        """Generate text using Groq API."""
        if not self.is_available():
            raise ValueError("Groq API key not configured")
        
        try:
            import groq
            client = groq.Groq(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Groq is available."""
        return bool(self.api_key)


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = "gemini-pro"
    
    async def generate_text(self, prompt: str, max_tokens: int = 150) -> str:
        """Generate text using Gemini API."""
        if not self.is_available():
            raise ValueError("Gemini API key not configured")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7
                )
            )
            
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return bool(self.api_key)


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider (fallback)."""
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = "gpt-3.5-turbo"
    
    async def generate_text(self, prompt: str, max_tokens: int = 150) -> str:
        """Generate text using OpenAI API."""
        if not self.is_available():
            raise ValueError("OpenAI API key not configured")
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return bool(self.api_key)


class ReplicateProvider(LLMProvider):
    """Replicate LLM provider."""
    
    def __init__(self):
        self.api_token = settings.replicate_api_token
        self.model = "meta/llama-2-7b-chat"
    
    async def generate_text(self, prompt: str, max_tokens: int = 150) -> str:
        """Generate text using Replicate API."""
        if not self.is_available():
            raise ValueError("Replicate API token not configured")
        
        try:
            headers = {
                "Authorization": f"Token {self.api_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "version": "13c3cdee13ee059ab779f0291d29054dab00a47dad8261375654de5540165fb0",
                "input": {
                    "prompt": prompt,
                    "max_new_tokens": max_tokens,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(
                "https://api.replicate.com/v1/predictions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                prediction = response.json()
                # Note: Replicate is async, you'd need to poll for results
                # For simplicity, returning a placeholder
                return "Replicate response (async processing)"
            else:
                raise Exception(f"Replicate API error: {response.text}")
        except Exception as e:
            raise Exception(f"Replicate API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Replicate is available."""
        return bool(self.api_token)


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = "llama3"
    
    async def generate_text(self, prompt: str, max_tokens: int = 150) -> str:
        """Generate text using Ollama local API."""
        if not self.is_available():
            raise ValueError("Ollama not available")
        
        try:
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                raise Exception(f"Ollama API error: {response.text}")
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


class LLMService:
    """Main LLM service with provider switching."""
    
    def __init__(self):
        self.providers = {
            "groq": GroqProvider(),
            "gemini": GeminiProvider(),
            "openai": OpenAIProvider(),
            "replicate": ReplicateProvider(),
            "ollama": OllamaProvider()
        }
        self.current_provider = settings.model_provider
    
    def get_provider(self) -> LLMProvider:
        """Get the current LLM provider."""
        provider = self.providers.get(self.current_provider)
        if not provider:
            raise ValueError(f"Unknown provider: {self.current_provider}")
        
        if not provider.is_available():
            # Try fallback providers
            for fallback_name, fallback_provider in self.providers.items():
                if fallback_name != self.current_provider and fallback_provider.is_available():
                    print(f"Falling back to {fallback_name} provider")
                    return fallback_provider
            
            raise ValueError(f"No available LLM providers configured")
        
        return provider
    
    async def generate_esg_suggestion(self, question: str, industry: str = "retail", 
                                    question_type: str = "numeric") -> Dict[str, Any]:
        """Generate ESG metric suggestion based on industry norms."""
        prompt = f"""
        You are an ESG (Environmental, Social, Governance) expert for retail SMBs.
        
        Question: {question}
        Industry: {industry}
        Question Type: {question_type}
        
        Provide a realistic default value for this ESG metric based on industry norms for small-medium retail businesses.
        
        Respond with ONLY a JSON object in this format:
        {{
            "suggested_value": <value>,
            "confidence": <0.0-1.0>,
            "explanation": "<brief explanation>",
            "source": "industry_average"
        }}
        
        For numeric values, provide reasonable numbers.
        For percentages, provide values between 0-100.
        For boolean values, use true/false.
        """
        
        try:
            provider = self.get_provider()
            response = await provider.generate_text(prompt, max_tokens=200)
            
            # Try to parse JSON response
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                # If JSON parsing fails, extract value manually
                return {
                    "suggested_value": self._extract_default_value(question_type),
                    "confidence": 0.5,
                    "explanation": "Default industry average",
                    "source": "fallback"
                }
        except Exception as e:
            print(f"LLM suggestion failed: {e}")
            return {
                "suggested_value": self._extract_default_value(question_type),
                "confidence": 0.3,
                "explanation": "System default due to LLM unavailability",
                "source": "system_default"
            }
    
    def _extract_default_value(self, question_type: str) -> Any:
        """Extract default values based on question type."""
        defaults = {
            "numeric": 0,
            "percentage": 50,
            "boolean": False,
            "text": "Not specified"
        }
        return defaults.get(question_type, 0)
    
    async def summarize_news(self, news_content: str) -> str:
        """Summarize ESG-related news content."""
        prompt = f"""
        Summarize the following ESG-related news for retail SMBs in 2-3 sentences.
        Focus on actionable insights and regulatory changes.
        
        News content: {news_content}
        
        Summary:
        """
        
        try:
            provider = self.get_provider()
            return await provider.generate_text(prompt, max_tokens=150)
        except Exception as e:
            return f"Summary unavailable: {str(e)}"
    
    async def generate_esg_tasks(self, user_answers: List[Dict], industry: str = "retail") -> List[Dict]:
        """Generate gamified ESG improvement tasks."""
        prompt = f"""
        Based on the following ESG responses from a {industry} SMB, generate 3-5 actionable improvement tasks.
        Each task should be gamified with points and be specific to retail businesses.
        
        User ESG Data: {json.dumps(user_answers, indent=2)}
        
        Respond with ONLY a JSON array of tasks in this format:
        [
            {{
                "task": "<specific action>",
                "points": <10-50>,
                "category": "<environmental|social|governance>",
                "difficulty": "<easy|medium|hard>",
                "estimated_impact": "<low|medium|high>"
            }}
        ]
        """
        
        try:
            provider = self.get_provider()
            response = await provider.generate_text(prompt, max_tokens=300)
            
            try:
                tasks = json.loads(response)
                return tasks if isinstance(tasks, list) else []
            except json.JSONDecodeError:
                # Return default tasks if parsing fails
                return self._get_default_tasks()
        except Exception as e:
            print(f"Task generation failed: {e}")
            return self._get_default_tasks()
    
    def _get_default_tasks(self) -> List[Dict]:
        """Get default ESG improvement tasks."""
        return [
            {
                "task": "Switch to LED lighting in all store locations",
                "points": 25,
                "category": "environmental",
                "difficulty": "easy",
                "estimated_impact": "medium"
            },
            {
                "task": "Implement employee diversity training program",
                "points": 30,
                "category": "social",
                "difficulty": "medium",
                "estimated_impact": "high"
            },
            {
                "task": "Create a supplier code of conduct",
                "points": 20,
                "category": "governance",
                "difficulty": "easy",
                "estimated_impact": "medium"
            }
        ]


# Global LLM service instance
llm_service = LLMService()

