# Gerador de Nomes, Localizações e Documentos Brasileiros Realistas

Este pacote fornece uma solução completa para gerar amostras realísticas de nomes, localizações e documentos brasileiros com base em dados populacionais e estatísticas históricas.

---

## Sumário

- [Visão Geral](#visão-geral)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Funcionalidades Principais](#funcionalidades-principais)
  - [Amostrador de Localizações Brasileiras](#amostrador-de-localizações-brasileiras)
  - [Amostrador de Nomes Brasileiros](#amostrador-de-nomes-brasileiros)
  - [Gerador de RG](#gerador-de-rg)
  - [Amostrador de Documentos](#amostrador-de-documentos)
  - [Utilitários para Documentos](#utilitários-para-documentos)
- [Interface de Linha de Comando (CLI)](#interface-de-linha-de-comando-cli)
- [Retorno de Dados em Dicionários](#retorno-de-dados-em-dicionários)
- [Testes e Validação](#testes-e-validação)
- [Instalação e Dependências](#instalação-e-dependências)
- [Exemplos de Uso](#exemplos-de-uso)
- [Licença](#licença)

---

## Visão Geral

O pacote permite gerar:
- **Localizações brasileiras:** Seleciona estados e cidades com base em porcentagens populacionais; gera CEPs aleatórios ou a partir de intervalos pré-definidos; formata a saída de maneira flexível.
- **Nomes brasileiros:** Seleciona nomes e sobrenomes (inclusive com opções para incluir nomes do meio ou usar somente sobrenomes) com base em dados históricos e estatísticos.
- **Documentos brasileiros:** Gera números válidos para CPF, PIS, CNPJ, CEI e RG, utilizando funções utilitárias e regras específicas para cada documento.
- **Saída estruturada:** As funções de amostragem, especialmente através da CLI, retornam os resultados em dicionários contendo vários itens (nome, local, documentos, etc.), facilitando o uso em scripts e sistemas automatizados.

---

## Estrutura do Projeto

```plaintext
src
├── br_location_class.py         # Classe para amostragem de localizações brasileiras
├── br_name_class.py             # Classe para amostragem de nomes brasileiros e enumeração de períodos
├── br_rg_class.py               # Geração de números de RG conforme os padrões estaduais
├── cli.py                       # Interface de linha de comando (Typer + Rich)
├── document_sampler.py          # Classe para geração de documentos (CPF, PIS, CNPJ, CEI, RG)
├── __init__.py                  # Inicialização do pacote e exportação das principais classes e funções
└── utils
    ├── cpf.py                   # Funções para CPF (validação, formatação, geração)
    ├── pis.py                   # Funções para PIS/PASEP
    ├── cnpj.py                  # Funções para CNPJ
    ├── cei.py                   # Funções para CEI
    ├── util.py                  # Funções auxiliares (limpeza e padding de IDs)
    └── __init__.py
```

Além dos módulos de código, o diretório **tests** contém diversos testes unitários (utilizando `pytest`) que garantem o funcionamento correto de cada componente do pacote.

---

## Funcionalidades Principais

### Amostrador de Localizações Brasileiras

- **Classe:** `BrazilianLocationSampler`
- **Funcionalidades:**
  - Carrega dados de cidades e estados a partir de um arquivo JSON.
  - Pré-calcula pesos com base na porcentagem populacional para amostragem eficiente.
  - Métodos para retornar:
    - Um estado aleatório (nome e abreviação) com base no peso populacional.
    - Uma cidade aleatória, podendo restringir por estado.
    - Combinações completas (estado, abreviação e cidade).
    - Geração e formatação de CEPs, com opções para incluir ou omitir o hífen.
  - **Exemplo de saída (localização completa):**
    ```plaintext
    São Paulo, São Paulo (SP), 01000-000
    ```

### Amostrador de Nomes Brasileiros

- **Classe:** `BrazilianNameSampler`
- **Funcionalidades:**
  - Carrega dados de nomes e sobrenomes (e, opcionalmente, nomes do meio) a partir de arquivos JSON.
  - Permite selecionar nomes baseados em diferentes períodos históricos (por exemplo, `ate2010`).
  - Suporta opções como:
    - Geração de nomes em caixa alta (raw) ou no formato de título.
    - Inclusão ou exclusão de sobrenomes.
    - Seleção de apenas sobrenomes, ou somente nomes do meio.
    - Uso de uma lista "top 40" de sobrenomes.
  - **Retorno:**
    - Pode retornar o nome completo como string ou os componentes do nome como uma instância do `NameComponents` (contendo `first_name`, `middle_name` e `surname`).

### Gerador de RG

- **Classe:** `BrazilianRG`
- **Funcionalidades:**
  - Gera números de RG de acordo com os padrões específicos de cada estado (ex.: inclusão de pontos, hífens e, em alguns casos, o prefixo do estado ou emissor).
  - Permite opções para:
    - Incluir ou não a informação do emissor (ex.: `SSP-SP` ou `DETRAN-RJ`).
    - Gerar somente o número do RG sem formatação adicional.

### Amostrador de Documentos

- **Classe:** `DocumentSampler`
- **Funcionalidades:**
  - Utiliza os utilitários para gerar números válidos para:
    - **CPF:** Com formatação padrão (XXX.XXX.XXX-XX).
    - **PIS:** No formato típico (XXX.XXXXX.XX-X).
    - **CNPJ:** No formato (XX.XXX.XXX/XXXX-XX).
    - **CEI:** No formato (XX.XXX.XXXXX/XX).
    - **RG:** Chamando o gerador de RG, podendo incluir o emissor.

### Utilitários para Documentos

Cada documento possui seu próprio módulo em `src/utils/`:
- **CPF, PIS, CNPJ e CEI:** Possuem funções para limpeza, validação, cálculo de dígitos verificadores, formatação e geração aleatória de números válidos.

---

## Interface de Linha de Comando (CLI)

- **Arquivo:** `cli.py`
- **Descrição:**
  - Utiliza o framework **Typer** para criar uma CLI robusta.
  - Exibe os resultados utilizando a biblioteca **Rich** para formatação de tabelas.
  - Aceita diversas opções e flags para controlar a saída, como:
    - Geração apenas de nomes, apenas de localizações, apenas de documentos ou combinações destes.
    - Formatação personalizada do CEP (com ou sem hífen).
    - Escolha do período histórico para amostragem de nomes.
    - Opções para incluir ou omitir detalhes dos documentos.
  - **Saída:** Os resultados podem ser apresentados em uma tabela interativa e, internamente, convertidos em dicionários padronizados para facilitar a integração.  
  - A função `parse_result` converte os dados brutos em um dicionário com chaves como:
    - `name`
    - `middle_name`
    - `surnames`
    - `city`
    - `state`
    - `state_abbr`
    - `cep`
    - `cpf`
    - `rg`
    - (e possivelmente outros documentos, como `pis`, `cnpj` e `cei`)

---

## Retorno de Dados em Dicionários

Uma das características centrais do pacote é a capacidade de retornar **vários itens em dicionários**. Isso é particularmente útil para:
- Integração com sistemas que consumam APIs.
- Processamento e manipulação posterior dos dados gerados.
- Automatização de fluxos de trabalho.

Quando a função CLI é chamada (por exemplo, através do comando `sample`), os resultados são convertidos usando a função `parse_result`, que estrutura a saída da seguinte forma:

```python
{
    "name": "João",
    "middle_name": "Pedro",
    "surnames": "da Silva",
    "city": "São Paulo",
    "state": "São Paulo",
    "state_abbr": "SP",
    "cep": "01000-000",
    "cpf": "123.456.789-00",
    "rg": "SSP-SP 12.345.678-9"
    // Possíveis entradas adicionais para PIS, CNPJ, CEI, etc.
}
```

- **Quantidade de Amostras:**
  - Se gerar apenas uma amostra (qty=1), a função retornará um único dicionário.
  - Para múltiplas amostras (qty>1), o retorno será uma lista de dicionários.

Essa abordagem facilita o consumo dos dados tanto em scripts automatizados quanto em aplicações que requerem uma API de dados estruturados.

---

## Testes e Validação

O diretório `tests/` contém diversos casos de teste que validam:
- A correta amostragem de nomes, localizações e documentos.
- A validação dos formatos dos documentos (CPF, PIS, CNPJ, CEI, RG).
- O comportamento da CLI e a formatação das tabelas de resultados.
- Recomenda-se executar os testes com o comando:

```sh
pytest
```

---

## Instalação e Dependências

### Requisitos

- Python 3.9+
- Dependências externas:
  - Typer
  - Rich
  - pytest (para execução dos testes)

### Instalação

1. Clone o repositório:

```sh
git clone https://github.com/seu-usuario/ptbr-sampler.git
cd ptbr-sampler
```

2. Instale as dependências (recomenda-se usar um ambiente virtual):

```sh
uv sync
```

---

## Exemplos de Uso

### Via Linha de Comando

Para gerar uma amostra completa (localização, nome e documentos) e exibi-la em uma tabela:

```sh
uv run src.cli sample --qty 1
```

Para gerar apenas documentos (por exemplo, somente CPF e RG):

```sh
uv run src.cli sample --only-cpf --only-rg --qty 3
```

### Via Código Python

Você pode utilizar as classes diretamente em seus scripts:

```python
from src.br_location_class import BrazilianLocationSampler
from src.br_name_class import BrazilianNameSampler, TimePeriod
from src.document_sampler import DocumentSampler

# Inicializar os amostradores com os respectivos arquivos JSON
location_sampler = BrazilianLocationSampler("data/cities_with_ceps.json")
name_sampler = BrazilianNameSampler("data/names_data.json", middle_names_path="data/middle_names.json")
doc_sampler = DocumentSampler()

# Gerar uma amostra
state_name, state_abbr, city_name = location_sampler.get_state_and_city()
name_components = name_sampler.get_random_name(time_period=TimePeriod.UNTIL_2010, return_components=True)
documents = {
    "cpf": doc_sampler.generate_cpf(),
    "rg": doc_sampler.generate_rg(state_abbr)
}

# Estruturar o resultado em um dicionário
result = {
    "name": name_components.first_name,
    "middle_name": name_components.middle_name,
    "surnames": name_components.surname,
    "city": city_name,
    "state": state_name,
    "state_abbr": state_abbr,
    "cep": location_sampler.format_full_location(city_name, state_name, state_abbr).split(',')[-1].strip(),
    "cpf": documents["cpf"],
    "rg": documents["rg"]
}

print(result)
```

---

## Licença

Este projeto está licenciado sob a MIT License.
---

# Brazilian Names, Locations and Documents Generator

This package provides a complete solution for generating realistic Brazilian names, locations, and documents based on population data and historical naming statistics. It is designed to be used by developers looking to generate sample data for testing and development purposes.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Main Features](#main-features)
  - [Brazilian Location Sampler](#brazilian-location-sampler)
  - [Brazilian Name Sampler](#brazilian-name-sampler)
  - [RG Generator](#rg-generator)
  - [Document Sampler](#document-sampler)
  - [Document Utilities](#document-utilities)
- [Command-Line Interface (CLI)](#command-line-interface-cli)
- [Returning Data as Dictionaries](#returning-data-as-dictionaries)
- [Testing and Validation](#testing-and-validation)
- [Installation and Dependencies](#installation-and-dependencies)
- [Usage Examples](#usage-examples)
- [License](#license)

---

## Overview

The package enables you to generate:
- **Brazilian Locations:** Randomly select states and cities based on population percentages; generate CEPs (postal codes) either randomly or from specified ranges; and format the output flexibly.
- **Brazilian Names:** Select first names and surnames (with options to include middle names or use only surnames) based on historical and statistical data.
- **Brazilian Documents:** Generate valid numbers for CPF, PIS, CNPJ, CEI, and RG using dedicated utility functions and state-specific rules.
- **Structured Output:** Many functions, especially via the CLI, return results as standardized dictionaries with keys like name, middle_name, surnames, city, state, state_abbr, cep, cpf, rg, etc.

---

## Project Structure

```plaintext
src
├── br_location_class.py         # Class for sampling Brazilian locations
├── br_name_class.py             # Class for sampling Brazilian names and time period enumeration
├── br_rg_class.py               # Generates state-specific Brazilian RG numbers
├── cli.py                       # Command-line interface (Typer + Rich)
├── document_sampler.py          # Class for generating documents (CPF, PIS, CNPJ, CEI, RG)
├── __init__.py                  # Package initialization and exports
└── utils
    ├── cpf.py                   # CPF functions (validation, formatting, generation)
    ├── pis.py                   # PIS/PASEP functions
    ├── cnpj.py                  # CNPJ functions
    ├── cei.py                   # CEI functions
    ├── util.py                  # Helper functions for cleaning and padding IDs
    └── __init__.py
```

The `tests/` directory includes unit tests (using `pytest`) to ensure the correct functionality of every component.

---

## Main Features

### Brazilian Location Sampler

- **Class:** `BrazilianLocationSampler`
- **Features:**
  - Loads city and state data from a JSON file.
  - Pre-calculates weights based on population percentages for efficient sampling.
  - Methods to return:
    - A random state (name and abbreviation) based on population weights.
    - A random city, optionally restricted to a given state.
    - A complete combination (state, abbreviation, and city).
    - Generation and formatting of CEPs with options to include or omit the dash.
  - **Example Output (Complete Location):**
    ```plaintext
    São Paulo, São Paulo (SP), 01000-000
    ```

### Brazilian Name Sampler

- **Class:** `BrazilianNameSampler`
- **Features:**
  - Loads first names, surnames, and optionally middle names from JSON files.
  - Supports selection of names based on different historical time periods (e.g., `ate2010`).
  - Offers options such as:
    - Generating names in uppercase (raw) or in title case.
    - Including or excluding surnames.
    - Generating only surnames or only middle names.
    - Utilizing a "top 40" list of surnames.
  - **Return Options:**
    - Returns the full name as a string or as a `NameComponents` instance containing `first_name`, `middle_name`, and `surname`.

### RG Generator

- **Class:** `BrazilianRG`
- **Features:**
  - Generates RG numbers following state-specific formats (e.g., inclusion of dots, dashes, and optional state prefixes or issuer codes).
  - Options to include the issuing authority (e.g., `SSP-SP` or `DETRAN-RJ`) or to generate only the raw RG number.

### Document Sampler

- **Class:** `DocumentSampler`
- **Features:**
  - Uses utility functions to generate valid numbers for:
    - **CPF:** Formatted as XXX.XXX.XXX-XX.
    - **PIS:** In the format XXX.XXXXX.XX-X.
    - **CNPJ:** Formatted as XX.XXX.XXX/XXXX-XX.
    - **CEI:** Formatted as XX.XXX.XXXXX/XX.
    - **RG:** Generated using the state-specific generator.

### Document Utilities

Each document type has its own module in `src/utils/`:
- **CPF, PIS, CNPJ, CEI:** Contain functions for cleaning, validating, calculating check digits, formatting, and generating random valid numbers.

---

## Command-Line Interface (CLI)

- **File:** `cli.py`
- **Description:**
  - Built with Typer to create a robust CLI.
  - Displays results in well-formatted tables using Rich.
  - Offers a wide range of options/flags to control output, such as:
    - Generating only names, only locations, only documents, or combinations thereof.
    - Customizing CEP formatting (with or without dash).
    - Selecting the historical time period for name sampling.
    - Including or excluding details in document outputs.
  - **Output:** Results are displayed in an interactive table and internally converted to standardized dictionaries via the `parse_result` function.

---

## Returning Data as Dictionaries

A core feature of the package is its ability to return multiple items as dictionaries. This is especially useful for:
- Integration with APIs and external systems.
- Further processing or automation workflows.

When the CLI function is called (e.g., through the command `sample`), the results are converted using the `parse_result` function, structuring the output as follows:

```python
{
    "name": "João",
    "middle_name": "Pedro",
    "surnames": "da Silva",
    "city": "São Paulo",
    "state": "São Paulo",
    "state_abbr": "SP",
    "cep": "01000-000",
    "cpf": "123.456.789-00",
    "rg": "SSP-SP 12.345.678-9"
    // Additional entries may include PIS, CNPJ, CEI, etc.
}
```

- **Sample Quantity:**
  - If a single sample is generated (`qty=1`), the function returns one dictionary.
  - If multiple samples are generated (`qty>1`), a list of dictionaries is returned.

This structured approach simplifies the consumption and further processing of the generated data.

---

## Testing and Validation

The `tests/` directory contains comprehensive unit tests to verify:
- Correct sampling of names, locations, and documents.
- Proper formatting and validation of document numbers (CPF, PIS, CNPJ, CEI, RG).
- The behavior and output formatting of the CLI.
- Run tests using:

```sh
pytest
```

---

## Installation and Dependencies

### Requirements

- Python 3.9+
- External dependencies:
  - Typer
  - Rich
  - pytest (for running tests)

### Installation

1. Clone the repository:

```sh
git clone https://github.com/your-username/ptbr-sampler.git
cd ptbr-sampler
```

2. Install the dependencies (using a virtual environment is recommended):

```sh
uv sync
```

---

## Usage Examples

### Via Command-Line Interface

Generate a complete sample (location, name, and documents) and display it in a table:

```sh
uv run src.cli sample --qty 1
```

Generate only documents (e.g., only CPF and RG) for 3 samples:

```sh
uv run src.cli sample --only-cpf --only-rg --qty 3
```

### Via Python Code

You can use the classes directly in your scripts:

```python
from src.br_location_class import BrazilianLocationSampler
from src.br_name_class import BrazilianNameSampler, TimePeriod
from src.document_sampler import DocumentSampler

# Initialize samplers with respective JSON data files
location_sampler = BrazilianLocationSampler("data/cities_with_ceps.json")
name_sampler = BrazilianNameSampler("data/names_data.json", middle_names_path="data/middle_names.json")
doc_sampler = DocumentSampler()

# Generate a sample
state_name, state_abbr, city_name = location_sampler.get_state_and_city()
name_components = name_sampler.get_random_name(time_period=TimePeriod.UNTIL_2010, return_components=True)
documents = {
    "cpf": doc_sampler.generate_cpf(),
    "rg": doc_sampler.generate_rg(state_abbr)
}

# Structure the result as a dictionary
result = {
    "name": name_components.first_name,
    "middle_name": name_components.middle_name,
    "surnames": name_components.surname,
    "city": city_name,
    "state": state_name,
    "state_abbr": state_abbr,
    "cep": location_sampler.format_full_location(city_name, state_name, state_abbr).split(',')[-1].strip(),
    "cpf": documents["cpf"],
    "rg": documents["rg"]
}

print(result)
```

---

## License

This project is licensed under the MIT License.
