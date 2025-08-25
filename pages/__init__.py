"""
Pages module for the Text-to-Podcast Streamlit application.

This module contains all the page components for the multi-step podcast generation process:
- input_page: Handles file upload and URL input
- edit_page: Script editing and AI enhancement
- generate_page: Podcast generation and download
"""

# Import all page modules for easy access
from . import input_page
from . import edit_page
from . import generate_page

# Define what gets imported when someone does "from pages import *"
__all__ = [
    'input_page',
    'edit_page', 
    'generate_page'
]

# Version info
__version__ = '1.0.0'
__author__ = 'Your Name'

# Optional: Page registry for dynamic routing
PAGE_REGISTRY = {
    1: {
        'module': input_page,
        'name': 'Input Selection',
        'description': 'Choose input method and upload content'
    },
    2: {
        'module': edit_page,
        'name': 'Script Editing',
        'description': 'Edit and enhance your podcast script'
    },
    3: {
        'module': generate_page,
        'name': 'Generate Podcast',
        'description': 'Generate and download your podcast'
    }
}

def get_page_info(step_number):
    """Get information about a specific page step."""
    return PAGE_REGISTRY.get(step_number, None)

def get_all_pages():
    """Get all available pages."""
    return PAGE_REGISTRY