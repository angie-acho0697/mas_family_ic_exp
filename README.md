# 🏛️  A Multi-Agent Family Inheritance Experiment To Observe Instrumental Convergence Behaviour

This experiment simulates family inheritance dynamics through a multi-agent system. Using CrewAI and Google Gemini, it models how four distinct personalities navigate high-stakes decisions, form alliances, manage conflicts, and evolve relationships over time.

## Quick Start

### Prerequisites
- Python 3.10+ 
- Conda (Anaconda or Miniconda)
- **Google Gemini API Key** (Free tier available!)

### 1. Clone & Setup
```bash
git clone <repository-url>
cd mas_family_ic_exp
conda create -n mas_family_exp python=3.10
conda activate mas_family_exp
pip install -r requirements.txt
```

### 2. Get Your API Key
1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Sign in with Google account
3. Click "Get API Key" → "Create API Key"
4. Copy the key

### 3. Configure Environment
```bash
# Windows
copy env_example.txt .env

# macOS/Linux  
cp env_example.txt .env
```

Edit `.env` file:
```
GOOGLE_API_KEY=your_actual_api_key_here
LLM_PROVIDER=google
```

### 4. Run the Experiment
```bash
# Full 6-month drama
python run_experiment.py

# Just one month
python run_experiment.py --month 2

# Resume from where you left off
python run_experiment.py --resume
```

## Output Files

The experiment generates rich data files in the `output/` directory:

```
output/
├── logs/                    # Detailed conversation logs
├── results/                 # Metrics and analysis data  
└── state/                   # Experiment state for resuming
```


### Tech Specs

#### Technical Stack
- **CrewAI**: Multi-agent conversation orchestration
- **Google Gemini**: AI-powered relationship analysis  
- **Python 3.10+**: Core experiment framework

#### Capability:
- **Primary**: LLM analysis with detailed prompts and JSON parsing
- **Fallback**: Each LLM analysis method includes a comprehensive keyword-based fallback system that activates if:
- LLM API calls fail (503 Service Unavailable, overload errors)
- JSON parsing errors occur
- Network connectivity issues arise
- **Confidence Scoring**: All analyses include confidence levels (0.0-1.0)
- **Error Handling**: System continues data collection even during API failures

#### Fallback Features:
- **Conflict Detection**: 15+ keywords + regex patterns for direct opposition
- **Behavioural Patterns**: 20+ keywords covering leadership, collaboration, competition
- **Confidence Scoring**: Fallback analysis provides 0.3-0.4 confidence scores
- **Pattern Matching**: Advanced regex to detect cousin-to-cousin interactions

#### Rate Limiting & Error Handling:
- **Conservative Limits**: 4 requests/minute, 50 requests/hour
- **Exponential Backoff**: 30s → 60s → 120s → 300s max delay
- **Jitter**: Random delay variation to prevent thundering herd
- **Retry Logic**: Automatic retry for 503/overload errors
- **Graceful Degradation**: Fallback analysis ensures data collection continues


## Perfect For
- **Researchers** studying group dynamics and decision-making
- **Students** learning about multi-agent systems and AI
- **Developers** interested in CrewAI and LLM integration
- **Anyone** curious about family inheritance dynamics


## Contributing
This framework is designed to be extensible. Below can be added:
- New cousin personality types
- Additional scenario events  
- Custom analysis metrics
- Enhanced LLM prompts
- New relationship dynamics

## License
Research and educational use. Please follow LLM specific API usage policies.