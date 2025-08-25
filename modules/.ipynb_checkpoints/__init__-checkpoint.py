"""
Core processing modules for the Text-to-Podcast application.

This module contains the core functionality for:
- JSON creation and processing
- Audio generation (FABA)
- URL text extraction
- AI script generation with Gemini
"""

# Import your existing modules
try:
    from . import JSONcreater
    from . import FABA
    from . import url_text_extractor
    from . import gemini_generator
    
    # Import main functions for easy access
    from .JSONcreater import convert_text_to_json
    from .FABA import generate_podcast
    from .url_text_extractor import convert_url_to_json
    from .gemini_generator import generate_script_with_prompt
    
    __all__ = [
        # Modules
        'JSONcreater',
        'FABA', 
        'url_text_extractor',
        'gemini_generator',
        
        # Main functions
        'convert_text_to_json',
        'generate_podcast',
        'convert_url_to_json',
        'generate_script_with_prompt'
    ]
    
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    print("Make sure all your existing modules are in the modules/ directory")
    
    # Fallback - define what should be available
    __all__ = [
        'JSONcreater',
        'FABA',
        'url_text_extractor', 
        'gemini_generator'
    ]

# Version info
__version__ = '1.0.0'

# Module registry
MODULE_REGISTRY = {
    'JSONcreater': {
        'main_function': 'convert_text_to_json',
        'description': 'Converts text files to JSON format for processing'
    },
    'FABA': {
        'main_function': 'generate_podcast', 
        'description': 'Generates podcast audio from script JSON'
    },
    'url_text_extractor': {
        'main_function': 'convert_url_to_json',
        'description': 'Extracts text content from URLs and converts to JSON'
    },
    'gemini_generator': {
        'main_function': 'generate_script_with_prompt',
        'description': 'Uses Google Gemini AI to enhance and generate scripts'
    }
}

def get_module_info(module_name):
    """Get information about a specific processing module."""
    return MODULE_REGISTRY.get(module_name, None)

def list_available_modules():
    """List all available processing modules."""
    return list(MODULE_REGISTRY.keys())
