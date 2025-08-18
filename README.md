# ESKAI - Evolved Strategic Knowledge and AI Framework

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

ESKAI is a sophisticated multi-layered AGI (Artificial General Intelligence) framework that processes complex user inputs through six distinct layers, from intent assessment to final result rendering. It leverages multiple AI providers for robustness and includes dynamic tool creation capabilities.

## 🚀 Features

- **Multi-Layer Processing**: 6-layer architecture for comprehensive task handling
- **Multi-Provider AI**: Integrates Groq, OpenAI, and Gemini for robust decision-making
- **Dynamic Tool Creation**: Automatically creates and persists tools as needed
- **Smart Agent Orchestration**: Dependency-aware execution with parallel processing
- **Comprehensive Logging**: Full traceability from input to output
- **Adaptive Response**: Different processing paths based on intent
- **Safety & Security**: Built-in safeguards and error recovery

## 🏗️ Architecture

```
┌─────────────────┐
│ Layer 1: Prompt │  Intent Classification (Chat vs Objective)
│ Assessment      │
├─────────────────┤
│ Layer 2: Objective│ Multi-provider objective extraction
│ Formulation     │
├─────────────────┤
│ Layer 3: Work   │  Workflow generation and optimization
│ Plan Generation │
├─────────────────┤
│ Layer 4: Agent  │  Agent specification and orchestration
│ Orchestration   │
├─────────────────┤
│ Layer 5:        │  Agent execution with monitoring
│ Execution       │
├─────────────────┤
│ Layer 6: Final  │  Result synthesis and validation
│ Result Rendering│
└─────────────────┘
```

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/kamyasamuel/eskai.git
cd eskai
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required API keys:
- `OPENAI_API_KEY`: Your OpenAI API key
- `GROQ_API_KEY`: Your Groq API key  
- `GEMINI_API_KEY`: Your Google Gemini API key

## 🚀 Quick Start

### Basic Usage

```python
from eskai import ESKAI

# Initialize the AGI framework
agi = ESKAI()

# Simple chat interaction
response = agi.process("Hello, how are you?")
print(response)

# Complex objective-driven task
result = agi.process("Create a comprehensive market analysis for electric vehicles in 2025")
print(result)
```

### Command Line Interface

```bash
# Interactive mode
python -m eskai.cli --interactive

# Single command
python -m eskai.cli "Analyze the latest trends in AI and create a report"

# With specific configuration
python -m eskai.cli --config custom_config.yaml "Your task here"
```

### Advanced Usage

```python
from eskai import ESKAI
from eskai.config import ESKAIConfig

# Custom configuration
config = ESKAIConfig(
    max_concurrent_agents=5,
    enable_parallel_execution=True,
    log_level="DEBUG"
)

agi = ESKAI(config=config)

# Process with custom parameters
result = agi.process(
    prompt="Build a web scraper for job listings",
    max_execution_time=3600,  # 1 hour timeout
    enable_internet=True,
    enable_code_execution=True
)
```

## 🎯 Problem Categories ESKAI Can Solve

### 1. Data Analysis & Research
- **Market Research**: Comprehensive market analysis with competitor research, trend analysis, and forecasting
- **Scientific Literature Review**: Automated literature surveys with synthesis and gap analysis
- **Financial Analysis**: Stock analysis, portfolio optimization, risk assessment
- **Social Media Analytics**: Sentiment analysis, trend detection, influence mapping

### 2. Content Creation & Documentation
- **Technical Documentation**: API docs, user manuals, system architecture documents
- **Creative Writing**: Stories, scripts, marketing copy with market research backing
- **Educational Content**: Course materials, tutorials, assessment tools
- **Report Generation**: Executive summaries, research reports, compliance documents

### 3. Software Development
- **Full-Stack Application Development**: Web apps, APIs, databases with deployment
- **Code Analysis & Optimization**: Performance analysis, security auditing, refactoring
- **Test Suite Creation**: Unit tests, integration tests, performance tests
- **DevOps Automation**: CI/CD pipelines, infrastructure as code, monitoring

### 4. Business Strategy & Operations
- **Business Plan Development**: Market analysis, financial projections, risk assessment
- **Process Optimization**: Workflow analysis, automation opportunities, efficiency improvements
- **Competitive Intelligence**: Competitor analysis, market positioning, strategic recommendations
- **Digital Transformation**: Technology roadmaps, implementation strategies, change management

### 5. Academic & Scientific Projects
- **Research Proposal Writing**: Literature review, methodology design, grant applications
- **Data Analysis Projects**: Statistical analysis, visualization, hypothesis testing
- **Academic Paper Writing**: Research papers, systematic reviews, meta-analyses
- **Experiment Design**: Protocol development, statistical power analysis, controls

### 6. Creative & Media Projects
- **Multimedia Content Creation**: Video scripts, podcast outlines, social media campaigns
- **Brand Development**: Logo concepts, brand guidelines, marketing strategies
- **Event Planning**: Comprehensive event planning with logistics, marketing, and execution
- **Product Design**: User research, prototyping, testing, iteration

## 📁 Project Structure

```
eskai/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── setup.py                 # Package setup
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore rules
├── docs/                   # Documentation
│   ├── API.md              # API documentation
│   ├── EXAMPLES.md         # Usage examples
│   └── ARCHITECTURE.md     # Detailed architecture
├── eskai/                  # Main package
│   ├── __init__.py         # Package initialization
│   ├── core/               # Core framework components
│   │   ├── __init__.py
│   │   ├── eskai_main.py   # Main ESKAI class
│   │   ├── layer1.py       # Prompt assessment
│   │   ├── layer2.py       # Objective formulation
│   │   ├── layer3.py       # Work plan generation
│   │   ├── layer4.py       # Agent orchestration
│   │   ├── layer5.py       # Execution engine
│   │   └── layer6.py       # Result rendering
│   ├── agents/             # Agent implementations
│   │   ├── __init__.py
│   │   ├── base_agent.py   # Base agent class
│   │   ├── researcher.py   # Research agent
│   │   ├── analyst.py      # Analysis agent
│   │   ├── creator.py      # Content creation agent
│   │   └── executor.py     # Code execution agent
│   ├── tools/              # Tool management
│   │   ├── __init__.py
│   │   ├── tool_manager.py # Dynamic tool creation
│   │   ├── internet_tool.py # Web access
│   │   ├── code_tool.py    # Code execution
│   │   └── analysis_tool.py # Data analysis
│   ├── providers/          # AI provider integrations
│   │   ├── __init__.py
│   │   ├── openai_client.py
│   │   ├── groq_client.py
│   │   └── gemini_client.py
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py       # Comprehensive logging
│   │   ├── config.py       # Configuration management
│   │   └── security.py     # Security utilities
│   └── cli/                # Command line interface
│       ├── __init__.py
│       └── main.py         # CLI implementation
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── conftest.py         # Test configuration
│   ├── test_core/          # Core tests
│   ├── test_agents/        # Agent tests
│   ├── test_tools/         # Tool tests
│   └── test_integration/   # Integration tests
└── examples/               # Usage examples
    ├── basic_usage.py
    ├── advanced_usage.py
    ├── custom_agents.py
    └── batch_processing.py
```

## 🔧 Configuration

ESKAI uses YAML configuration files for customization:

```yaml
# config.yaml
eskai:
  providers:
    openai:
      model: "gpt-4"
      temperature: 0.7
    groq:
      model: "mixtral-8x7b-32768"
    gemini:
      model: "gemini-2.5-flash"
  
  execution:
    max_concurrent_agents: 3
    timeout_seconds: 3600
    enable_parallel_execution: true
  
  tools:
    enable_internet: true
    enable_code_execution: true
    enable_file_operations: true
  
  logging:
    level: "INFO"
    file: "eskai.log"
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=eskai

# Run specific test category
pytest tests/test_core/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Groq for fast inference
- Google for Gemini API
- The open-source community for various tools and libraries

## 📞 Support

- 📧 Email: support@eskai.ai
- 💬 Discord: [ESKAI Community](https://discord.gg/eskai)
- 🐛 Issues: [GitHub Issues](https://github.com/kamyasamuel/eskai/issues)
- 📖 Documentation: [Full Documentation](https://docs.eskaen.com)

## 🗺️ Roadmap

- [ ] Web interface for ESKAI
- [ ] Plugin system for custom tools
- [ ] Multi-modal support (images, audio, video)
- [ ] Distributed execution across multiple machines
- [ ] Learning memory system
- [ ] Advanced security features
- [ ] Real-time collaboration between agents

---

**ESKAI** - *Evolved Strategic Knowledge and AI Framework* - Making AGI accessible and practical for complex problem-solving.
