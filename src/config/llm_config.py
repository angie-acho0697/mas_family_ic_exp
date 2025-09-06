"""
Basic LLM Configuration for Google Gemini
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()

# Rate limiting for API calls
class APIRateLimiter:
    def __init__(self, delay_seconds=7.5):  # ~8 requests per minute
        self.delay_seconds = delay_seconds
        self.last_call_time = 0
    
    def wait_if_needed(self):
        current_time = time.time()
        time_since_last = current_time - self.last_call_time
        if time_since_last < self.delay_seconds:
            wait_time = self.delay_seconds - time_since_last
            print(f"⏳ API rate limiting: waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
        self.last_call_time = time.time()

# Global rate limiter
api_rate_limiter = APIRateLimiter()

class LLMConfig:
    """Simple configuration for Google Gemini"""
    
    def __init__(self):
        self.google_key = os.getenv("GOOGLE_API_KEY")
        if not self.google_key or self.google_key == "your_google_api_key_here":
            raise ValueError("GOOGLE_API_KEY not set or invalid")
        
        self.provider = "google"
        self.model = "gemini-1.5-flash"  # Updated model name
        # For litellm compatibility, we need the full model name with provider
        self.litellm_model = "gemini/gemini-1.5-flash"
    
    def get_llm(self):
        """Get Google Gemini LLM for CrewAI/litellm"""
        from crewai.llm import LLM
        
        # Apply rate limiting before creating LLM instance
        api_rate_limiter.wait_if_needed()
        
        # Set environment variables for CrewAI
        import os
        os.environ['GOOGLE_API_KEY'] = self.google_key
        # CrewAI expects the API key to be set as OPENAI_API_KEY for compatibility
        os.environ['OPENAI_API_KEY'] = self.google_key
        
        return LLM(
            model=self.litellm_model,
            api_key=self.google_key,
            temperature=0.7
        )
    
    def get_langchain_llm(self):
        """Get Google Gemini LLM for direct LangChain usage"""
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Apply rate limiting before creating LLM instance
        api_rate_limiter.wait_if_needed()
        
        return ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.google_key,
            temperature=0.7
            # Removed deprecated convert_system_message_to_human parameter
        )
    
    def get_provider_info(self):
        """Get provider information"""
        return {
            "provider": self.provider,
            "model": self.model,
            "litellm_model": self.litellm_model,
            "api_key_set": bool(self.google_key)
        }

# Global instance
llm_config = LLMConfig()
