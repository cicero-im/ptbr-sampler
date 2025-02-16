# 🇧🇷 Brazilian Realistic Data Generator

Generate names, addresses, CPFs, CNPJs, and other Brazilian documents that are **proportional to actual population distribution** and based **exclusively on existing, verified data**. Every generated name exists in Brazilian historical records, and locations are sampled proportionally to each region's population.

*Leia aqui em Português: [Português](README.md)*

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Key Features

- 📍 **Location Generation**: Realistic Brazilian addresses with population-weighted sampling
- 👤 **Name Generation**: Historically accurate Brazilian names with period-specific sampling
- 📄 **Document Generation**: Valid Brazilian documents (CPF, RG, PIS, CNPJ, CEI)
- 🎯 **Statistical Accuracy**: Based on real demographic data and historical statistics
- 🔧 **Flexible Output**: Structured data in various formats (CLI, Python dictionaries, API-ready)
- ⚡ **High Performance**: Efficient sampling with pre-calculated weights
- 🧪 **Thoroughly Tested**: Comprehensive test suite for reliability

## 🚀 Perfect For

- 🏢 **Enterprise Applications**: Generate realistic test data for Brazilian market applications
- 🧪 **Testing**: Create diverse datasets for thorough application testing
- 📊 **Data Science**: Generate statistically accurate samples for analysis and modeling
- 🎓 **Education**: Learn about Brazilian document formats and validation rules
- 🔄 **API Development**: Ready-to-use structured data for API responses

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ptbr-sampler.git
cd ptbr-sampler

# Install dependencies (recommended to use a virtual environment)
uv sync
```

## 🎯 Quick Start

### Command Line Interface

```bash
# Generate a complete profile (name, location, documents)
uv run src.cli sample --qty 1

# Generate specific documents only
uv run src.cli sample --only-cpf --only-rg --qty 3
```

### Python API

```python
from src.br_location_class import BrazilianLocationSampler
from src.br_name_class import BrazilianNameSampler, TimePeriod
from src.document_sampler import DocumentSampler

# Initialize samplers
location_sampler = BrazilianLocationSampler("data/cities_with_ceps.json")
name_sampler = BrazilianNameSampler("data/names_data.json", 
                                   middle_names_path="data/middle_names.json")
doc_sampler = DocumentSampler()

# Generate data
state_name, state_abbr, city_name = location_sampler.get_state_and_city()
name_components = name_sampler.get_random_name(
    time_period=TimePeriod.UNTIL_2010,
    return_components=True
)

# Get formatted output
result = {
    "name": name_components.first_name,
    "middle_name": name_components.middle_name,
    "surnames": name_components.surname,
    "city": city_name,
    "state": state_name,
    "state_abbr": state_abbr,
    "cep": location_sampler.format_full_location(
        city_name, state_name, state_abbr
    ).split(',')[-1].strip(),
    "cpf": doc_sampler.generate_cpf(),
    "rg": doc_sampler.generate_rg(state_abbr)
}
```

## 🎛️ Features In-Depth

### Location Generation
- Population-weighted selection of states and cities
- Realistic CEP (postal code) generation
- Flexible output formatting
- Support for specific region filtering

### Name Generation
- Historical period-based sampling
- Support for full names, middle names, and surnames
- Case formatting options (title case, uppercase)
- Top 40 surnames list option

### Document Generation
- CPF (Brazilian Individual Taxpayer ID)
- RG (Brazilian ID Card) with state-specific formats
- PIS (Social Integration Program Number)
- CNPJ (Brazilian Company ID)
- CEI (Employer Registration Number)

### Data Output
- Structured dictionary format
- CLI with rich formatting
- Batch generation support
- Customizable output fields

## 🏗️ Project Structure

```plaintext
src
├── br_location_class.py         # Location sampling
├── br_name_class.py             # Name sampling
├── br_rg_class.py              # RG generation
├── cli.py                      # Command-line interface
├── document_sampler.py         # Document generation
├── __init__.py                 # Package initialization
└── utils/                      # Utility functions
    ├── cpf.py                  # CPF handling
    ├── pis.py                  # PIS handling
    ├── cnpj.py                 # CNPJ handling
    ├── cei.py                  # CEI handling
    ├── util.py                 # Helper functions
    └── __init__.py
```

## 🧪 Testing

Comprehensive test suite covering all components:

```bash
uv run pytest
```

## 📚 Requirements

- Python 3.9+
- Dependencies:
  - Typer (CLI framework)
  - Rich (Terminal formatting)
  - pytest (Testing)

## 📖 Documentation

Detailed documentation for all features and components:

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Main Features](#main-features)
- [Command Line Interface](#command-line-interface)
- [Data Output](#data-output)
- [Testing and Validation](#testing)
- [Installation and Dependencies](#installation)
- [Usage Examples](#quick-start)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
