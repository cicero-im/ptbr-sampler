"""
Brazilian Name and Location Generator

This package provides tools for generating realistic Brazilian names and locations
based on population data and historical naming patterns.

Classes:
    TimePeriod: Enum for different historical time periods
    BrazilianNameSampler: Generator for Brazilian names
    BrazilianLocationSampler: Generator for Brazilian locations

The package requires JSON files containing population data and name statistics.
"""

from src.br_location_class import BrazilianLocationSampler
from src.br_name_class import BrazilianNameSampler, TimePeriod
from src.cli import app, main

__all__ = ['TimePeriod', 'BrazilianNameSampler', 'BrazilianLocationSampler', 'app', 'main']

__version__ = '1.0.0'
