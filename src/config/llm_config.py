"""
Basic LLM Configuration for Google Gemini
"""

import os
import time
import random
from dotenv import load_dotenv

load_dotenv()

# Rate limiting for API calls with retry mechanism
class APIRateLimiter:
    def __init__(self, delay_seconds=15.0):  # More conservative: ~4 requests per minute
        self.delay_seconds = delay_seconds
        self.last_call_time = 0
        self.request_count = 0
        self.hourly_requests = []
    
    def wait_if_needed(self):
        current_time = time.time()
        
        # Clean up old hourly requests (older than 1 hour)
        self.hourly_requests = [t for t in self.hourly_requests if current_time - t < 3600]
        
        # Check hourly limit (more conservative for free tier)
        if len(self.hourly_requests) >= 50:  # Reduced from 80 to 50
            wait_time = 3600 - (current_time - self.hourly_requests[0])
            if wait_time > 0:
                print(f"⏳ Hourly rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                current_time = time.time()
        
        # Check minimum delay between requests
        time_since_last = current_time - self.last_call_time
        if time_since_last < self.delay_seconds:
            wait_time = self.delay_seconds - time_since_last
            print(f"⏳ API rate limiting: waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
        
        # Record this request
        self.last_call_time = time.time()
        self.hourly_requests.append(current_time)
        self.request_count += 1
        
        # Log progress every 3 requests
        if self.request_count % 3 == 0:
            print(f"📊 API Requests made: {self.request_count} (Hourly: {len(self.hourly_requests)}/50)")

# Global rate limiter with more conservative settings
api_rate_limiter = APIRateLimiter(delay_seconds=15.0)

# Retry mechanism for handling API overload errors
def retry_with_exponential_backoff(func, max_retries=5, base_delay=30, max_delay=300):
    """
    Retry a function with exponential backoff for handling 503 errors
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for first retry
        max_delay: Maximum delay in seconds
    """
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            error_str = str(e).lower()
            
            # Check if it's a 503 or overload error
            if "503" in error_str or "overloaded" in error_str or "unavailable" in error_str:
                if attempt < max_retries:
                    # Calculate delay with exponential backoff and jitter
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = random.uniform(0.1, 0.3) * delay  # Add 10-30% jitter
                    total_delay = delay + jitter
                    
                    print(f"🔄 API overload detected (attempt {attempt + 1}/{max_retries + 1})")
                    print(f"⏳ Retrying in {total_delay:.1f} seconds...")
                    time.sleep(total_delay)
                    continue
                else:
                    print(f"❌ Max retries ({max_retries}) exceeded. Giving up.")
                    raise e
            else:
                # Not a retryable error, re-raise immediately
                raise e
    
    return None

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
        """Get Google Gemini LLM for CrewAI/litellm with retry mechanism"""
        from crewai.llm import LLM
        
        def _create_llm():
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
        
        # Use retry mechanism for LLM creation
        return retry_with_exponential_backoff(_create_llm)
    
    def get_langchain_llm(self):
        """Get Google Gemini LLM for direct LangChain usage with retry mechanism"""
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        def _create_langchain_llm():
            # Apply rate limiting before creating LLM instance
            api_rate_limiter.wait_if_needed()
            
            return ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self.google_key,
                temperature=0.7
                # Removed deprecated convert_system_message_to_human parameter
            )
        
        # Use retry mechanism for LLM creation
        return retry_with_exponential_backoff(_create_langchain_llm)
    
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