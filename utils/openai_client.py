import os
from dotenv import load_dotenv
from utils.logging import setup_logging

# Load environment variables
load_dotenv()

# Configure logger
logger = setup_logging()

def create_openai_client():
    """Create an OpenAI client instance if API key is available.
    
    Returns:
        OpenAI client instance or None if API key not found.
    """
    try:
        # Check if OpenAI API key is available
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OpenAI API key not found. AI features will be disabled.")
            return None
            
        # Import OpenAI library dynamically to avoid errors if not installed
        try:
            from openai import OpenAI
            
            # Monkey patch the httpx client wrapper to remove 'proxies' parameter
            try:
                from openai._base_client import SyncHttpxClientWrapper
                
                # Create custom wrapper class without proxies
                original_init = SyncHttpxClientWrapper.__init__
                
                def patched_init(self, *args, **kwargs):
                    # Remove proxies if present
                    if 'proxies' in kwargs:
                        del kwargs['proxies']
                    original_init(self, *args, **kwargs)
                
                # Apply the monkey patch
                SyncHttpxClientWrapper.__init__ = patched_init
                logger.info("Applied monkey patch for OpenAI client")
            except Exception as e:
                logger.warning(f"Could not apply monkey patch: {str(e)}")
            
            # Create client with only the api_key parameter
            client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully.")
            return client
        except ImportError:
            logger.warning("OpenAI Python package not installed. AI features will be disabled.")
            return None
            
    except Exception as e:
        logger.error(f"Error creating OpenAI client: {str(e)}")
        return None 