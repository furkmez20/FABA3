"""
Reusable UI components for the Text-to-Podcast application.

This module contains reusable Streamlit components that can be used across
different pages of the application.
"""

# Import all component modules
from . import progress_bar

# Export main functions for easy access
from .progress_bar import show_progress_bar

# Define what gets imported when someone does "from components import *"
__all__ = [
    'progress_bar',
    'show_progress_bar'
]

# Version info
__version__ = '1.0.0'

# Component registry for documentation
COMPONENT_REGISTRY = {
    'progress_bar': {
        'module': progress_bar,
        'main_function': 'show_progress_bar',
        'description': 'Displays step-by-step progress indicator'
    }
}

def get_component_info(component_name):
    """Get information about a specific component."""
    return COMPONENT_REGISTRY.get(component_name, None)