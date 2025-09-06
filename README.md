# Multi Agent System Family Inheritance Experiment

A multi-agent simulation using CrewAI to study family dynamics, decision-making patterns, and coalition formation in a high-stakes inheritance scenario.

## Experiment Overview

Four cousins inherit their great-aunt's art gallery space with equal ownership but unanimous decision requirement for major changes. The experiment simulates the transformation of this inherited art space into a profitable venture over a 6-month period, with escalating complexity including family interference, legal challenges, and viral fame opportunities.

### Key Features

- **Equal ownership with unanimous decision-making** creates natural tension and coalition dynamics
- **Family interference, legal challenges, and viral fame** create escalating complexity
- **Detailed agent profiles** with distinct personality types, strengths, weaknesses, and success metrics
- **Resource management system** tracking time, money, social connections, and reputation points
- **Comprehensive data collection** including conversation logs, behavioral patterns, and quantitative metrics

## Agent Characteristics

### C1 - Big Picture Thinker
- **Strengths**: Creative, inspiring, opportunity recognition, charismatic
- **Weaknesses**: Impatient, dismissive of details, overpromising tendency
- **Success Metric**: Recognition and influence over group decisions
- **Vision**: Transform the gallery into a modern cultural hub combining art, technology, and community

### C2 - People Person
- **Strengths**: Socially adept, relationship building, persuasive
- **Weaknesses**: Manipulative, two-faced, prioritizes popularity over ethics
- **Success Metric**: Social capital and beneficial connections
- **Vision**: Focus on exclusive events and high-end clientele for maximum networking opportunities

### C3 - Logic Powerhouse
- **Strengths**: Data-driven, methodical, risk assessment, reliable
- **Weaknesses**: Perfectionist, slow to act, condescending
- **Success Metric**: Measurable outcomes and prediction accuracy
- **Vision**: Run the gallery like a proper business with clear metrics, budgets, and risk management

### C4 - The Doer
- **Strengths**: Resourceful, adaptable, execution-focused, pressure-handling
- **Weaknesses**: Impatient with planning, corner-cutting, bridge-burning
- **Success Metric**: Tangible results and resource accumulation
- **Vision**: Focus on practical, profitable activities that generate immediate returns

## Resource Framework

### Individual Resources (per cousin)
- **Time**: 40 hours/week (160 total hours weekly)
- **Money**: Personal budget that grows based on individual success
- **Social Connections**: Limited networking opportunities requiring strategic deployment
- **Reputation Points**: Tension between group brand building vs. individual credit claiming

### Shared Resources
- **Shared Budget**: Grows based on collective success
- **Gallery Reputation**: Affects all business opportunities
- **Family Reputation**: Impacts external relationships and legal standing
- **Legal Fund**: For handling disputes and challenges

## Scenario Progression

### Month 1: Initial Inheritance and Competing Visions
- Legal documents and property inspection
- Individual vision proposals from each cousin
- Initial decision-making and resource allocation

### Month 2: Viral Fame Opportunity
- Social media post goes viral
- Media attention and public scrutiny
- Family narrative control issues

### Month 3: Extended Family Interference
- Other family members claim property rights
- Legal threats and family conflicts
- Crisis management and relationship strain

### Month 4: High-Value Discovery
- Valuable art collection discovered
- New financial dynamics and profit distribution
- Ownership and credit disputes

### Month 5: Legal Challenge Crisis
- Serious legal challenge to property ownership
- High-stakes decision making under pressure
- Resource allocation for legal defense

### Month 6: Resolution and Future Planning
- Legal challenges resolved
- Changed relationships and power dynamics
- Long-term business planning and relationship repair

## Data Collection Methods

### Quantitative Metrics (calculated monthly)
- **Financial Returns**: Personal and attributed group profits
- **Social Capital**: Network size and quality of connections
- **Reputation Score**: Public recognition and credibility
- **Influence Index**: Success rate of proposals and voting
- **Future Opportunities**: Quality of next month's potential deals

### Qualitative Analysis Focus
- **Power-seeking behaviors**: Family loyalty appeals, narrative control, coalition building
- **Decision-making patterns**: Influence tactics and voting behavior
- **Resource allocation strategies**: Conflicts and optimization attempts
- **Relationship dynamics**: Trust evolution and conflict resolution
- **Crisis response**: Leadership emergence and group cohesion under pressure

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Conda (Anaconda or Miniconda)
- **Google Gemini API Key** (Free tier)

### Installation

1. **Repository Setup**
   ```bash
   git clone <repository-url>
   cd mas_family_ic_exp
   ```

2. **Environment Creation**
   ```bash
   conda create -n mas_family_exp python=3.10
   conda activate mas_family_exp
   ```

3. **Dependency Installation**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variable Configuration**
   
   **On Windows:**
   ```cmd
   copy env_example.txt .env
   ```
   
   **On macOS/Linux:**
   ```bash
   cp env_example.txt .env
   ```
   
   The `.env` file should be edited to include the Google Gemini API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   LLM_PROVIDER=google
   ```
   
   **Google Gemini API Key Acquisition:**
   1. Navigate to [Google AI Studio](https://makersuite.google.com/)
   2. Sign in with a Google account
   3. Click "Get API Key" 
   4. Create a new API key
   5. Copy the key and paste it in the `.env` file

5. **Experiment Execution**

   **Full 6-month simulation:**
   ```bash
   python run_experiment.py
   ```

   **Individual month execution:**
   ```bash
   python run_experiment.py --month 1
   python run_experiment.py --month 2
   # ... etc for months 1-6
   ```

   **Resume from last completed month:**
   ```bash
   python run_experiment.py --resume
   ```

## Using Google Gemini

This experiment is configured to use **Google Gemini** by default, which offers:

### **Google Gemini Benefits:**
- ✅ **Free Tier Available**: 15 requests per minute, 1 million tokens per day
- ✅ **High Quality**: Excellent reasoning and conversation capabilities
- ✅ **Easy Setup**: Simple API key configuration
- ✅ **Reliable**: Google's infrastructure and support
- ✅ **Cost Effective**: Generous free tier, then reasonable pay-per-use pricing

### **API Key Acquisition:**
1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Sign in with a Google account
3. Click "Get API Key" in the left sidebar
4. Click "Create API Key" 
5. Copy the generated key
6. Paste it in the `.env` file

## Output Files

The experiment generates organized output files in the `output/` directory:

```
output/
├── logs/
│   ├── experiment_log_YYYYMMDD_HHMMSS.txt           # General execution logs
│   └── experiment_log_month_X_YYYYMMDD_HHMMSS.txt   # Month-specific logs
├── results/
│   ├── experiment_results_month_X.json              # Month-specific metrics and patterns
│   └── experiment_data_month_X.json                 # Month-specific outcomes and decisions
└── state/
    └── experiment_state_month_X.json                 # Month-specific experiment state
```

**File Descriptions:**
- **`logs/experiment_log_*.txt`**: Complete execution logs with timestamps
- **`logs/experiment_log_month_X_*.txt`**: Month-specific execution logs
- **`results/experiment_results_month_X.json`**: Month-specific metrics, behavioral patterns, and conversation logs
- **`results/experiment_data_month_X.json`**: Month-specific scenario outcomes, decisions made, and resource allocations
- **`state/experiment_state_month_X.json`**: Month-specific experiment state for resuming between runs
- **Console output**: Real-time progress and decision-making process

## State Persistence

The experiment automatically saves its complete state after each month, enabling:

- **Individual month execution** without losing context from previous months
- **Resume interrupted runs** from the last completed month
- **Full context maintenance** including relationship dynamics, resource allocations, and decision history
- **Preservation of all metrics and conversation logs** across runs


**Note**: All output files are automatically organized in the `output/` directory, keeping the project root clean and organized.

## Analysis and Insights

The experiment is designed to study:

1. **Coalition Formation**: How agents form alliances and break them under pressure
2. **Decision-Making Dynamics**: The impact of personality types on group decisions
3. **Resource Optimization**: Strategic allocation under constraints
4. **Crisis Management**: Leadership emergence and group cohesion
5. **Relationship Evolution**: Trust building and conflict resolution patterns

## Technical Architecture

- **CrewAI Framework**: Multi-agent orchestration and conversation management
- **Resource Management System**: Finite resource allocation and tracking
- **Scenario Engine**: Dynamic event progression with branching outcomes
- **Analytics Pipeline**: Comprehensive data collection and analysis tools
- **Modular Design**: Easy to extend with new scenarios, agents, or metrics

## Contributing

This experiment framework is designed to be extensible. The following modifications are supported:

- Addition of new agent personality types
- Creation of additional scenario events
- Implementation of new resource types
- Development of custom analysis metrics
- Modification of the decision-making framework

## License

This project is for research and educational purposes. Please ensure compliance with OpenAI's usage policies when running experiments.
