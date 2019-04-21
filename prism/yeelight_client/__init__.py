"""Yeelight protocol client.

Implements YeeLight protocol for prism.
"""

from .yeelight import get_lights, get_light

__all__ = ['get_light', 'get_lights']
