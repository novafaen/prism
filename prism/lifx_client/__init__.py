"""Lifx protocol client.

Implements Lifx protocol for prism.
"""

from .lifx import get_lights, get_light

__all__ = ['get_light', 'get_lights']
