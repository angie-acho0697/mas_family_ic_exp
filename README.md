# 🏛️ Family Inheritance Experiment: A Multi-Agent Drama

**What happens when four cousins inherit an art gallery and must make unanimous decisions about its future?**

This experiment simulates the complex dynamics of family inheritance through an advanced multi-agent system. Using CrewAI and Google Gemini, it models how four distinct personalities navigate high-stakes decisions, form alliances, manage conflicts, and evolve relationships over time.

## 🎭 The Story

Four cousins inherit their great-aunt's art gallery with **equal ownership** but a **unanimous decision requirement** for major changes. Over 6 months, they face escalating challenges: viral fame, family interference, legal threats, and valuable discoveries. Each cousin has distinct goals, strengths, and weaknesses that create natural tension and coalition dynamics.

**The question**: Can they work together to transform the gallery into a profitable venture, or will family dynamics tear them apart?

## ✨ What Makes This Special

- 🧠 **AI-Powered Analysis**: Google Gemini analyzes every conversation to detect conflicts, alliances, and behavioral patterns
- 🎯 **Realistic Dynamics**: Each cousin has distinct personality traits that create authentic family tensions
- 📊 **Rich Data Collection**: Tracks trust levels, social connections, resource allocation, and decision-making patterns
- 🔄 **Dynamic Relationships**: Relationships evolve based on interactions, creating emergent storylines
- 🎪 **Escalating Drama**: 6 months of increasingly complex scenarios from viral fame to legal battles
- 🛡️ **Robust System**: Includes fallback analysis and error handling for reliable long-running experiments

## 👥 Meet the Cousins

### 🎨 C1 - The Creative Visionary
**"Let's make this gallery a cultural revolution!"**

- **Personality**: Charismatic, inspiring, always sees the big picture
- **Strengths**: Creative vision, opportunity spotting, natural leadership
- **Weaknesses**: Impatient with details, tends to overpromise
- **Goal**: Transform the gallery into a modern cultural hub combining art, technology, and community
- **Success Metric**: Recognition and influence over group decisions

### 🤝 C2 - The Social Strategist  
**"It's all about who you know and how you know them."**

- **Personality**: Socially adept, relationship-focused, persuasive
- **Strengths**: Network building, event planning, people management
- **Weaknesses**: Can be manipulative, prioritizes popularity over ethics
- **Goal**: Focus on exclusive events and high-end clientele for maximum networking
- **Success Metric**: Social capital and beneficial connections

### 📊 C3 - The Analytical Strategist
**"Let's run this like a proper business with data and metrics."**

- **Personality**: Methodical, risk-aware, detail-oriented
- **Strengths**: Data analysis, risk assessment, reliable planning
- **Weaknesses**: Perfectionist, slow to act, can be condescending
- **Goal**: Professional business operations with clear metrics and budgets
- **Success Metric**: Measurable outcomes and prediction accuracy

### ⚡ C4 - The Execution Specialist
**"Let's stop talking and start doing - time is money!"**

- **Personality**: Action-oriented, resourceful, results-driven
- **Strengths**: Quick execution, pressure handling, practical solutions
- **Weaknesses**: Impatient with planning, tends to cut corners
- **Goal**: Focus on profitable activities that generate immediate returns
- **Success Metric**: Tangible results and resource accumulation

## Relationship Dynamics System

### Trust Levels
- **Initialization**: Personality-based variation from 0.3 to 0.7 (base: 0.5 ± 0.1)
- **Calculation Formula**: `trust_level = base_trust + personality_factor`
- **Personality Factor**: `(hash(cousin_id + target_cousin) / 255.0 - 0.5) * 0.2`
- **Updates**: Based on LLM analysis of specific interactions between cousin pairs
- **Change Amount**: `base_change * confidence` where `base_change = 0.15`

### Conflicts
- **Detection**: LLM-powered analysis of conversation content
- **Severity Levels**: Low (0.2), Medium (0.5), High (0.8)
- **Confidence Threshold**: > 0.5 for inclusion
- **Impact**: Reduces trust levels between involved cousins
- **Fallback**: Keyword-based detection if LLM analysis fails

### Alliances
- **Detection**: LLM-powered analysis of collaboration patterns
- **Strength Levels**: Weak (0.3), Medium (0.6), Strong (0.9)
- **Confidence Threshold**: > 0.5 for inclusion
- **Impact**: Increases trust levels and creates social connections
- **Fallback**: Keyword-based detection if LLM analysis fails

### Social Connection Strength
- **Initialization**: 0.5 for new connections
- **Calculation Formula**: 
  ```
  strength = (trust_level × 0.6) + (alliance_bonus × 0.25) - (conflict_penalty × 0.15) + (context_bonus × 0.1) + personality_factor
  ```
- **Personality Factor**: `±0.05` variation based on cousin pair hash
- **Strengthening**: +0.1 per interaction (capped at 1.0)
- **Bounds**: [0.0, 1.0]

### Behavioral Patterns
- **Types**: Leadership, Collaboration, Competition, Compromise, Assertiveness, Cooperation, Passive, Analytical
- **Detection**: LLM-powered analysis of conversation context
- **Confidence Threshold**: > 0.5 for inclusion
- **Impact Assessment**: Positive, Negative, or Neutral
- **Fallback**: Keyword-based detection if LLM analysis fails

## Resource Framework

### Individual Resources (per cousin)
- **Time**: 40 hours/week (160 total hours weekly)
- **Money**: Personal budget that grows based on individual success
- **Social Connections**: Dynamic strength-based connections with other cousins
- **Reputation Points**: Tension between group brand building vs. individual credit claiming

### Shared Resources
- **Shared Budget**: Grows based on collective success
- **Gallery Reputation**: Affects all business opportunities
- **Family Reputation**: Impacts external relationships and legal standing
- **Legal Fund**: For handling disputes and challenges

## 📅 The 6-Month Journey

### 🌱 Month 1: The Inheritance
**"We're all equal owners now - but what do we actually want to do?"**
- Legal documents and property inspection
- Each cousin presents their vision for the gallery
- Initial tensions emerge as competing priorities clash

### 📱 Month 2: Viral Fame
**"We're internet famous - but is this good or bad for business?"**
- A social media post about the inheritance goes viral
- Media attention brings both opportunities and scrutiny
- Family must decide how to handle their newfound fame

### ⚖️ Month 3: Family Interference  
**"Aunt Millie says the property should be hers - and she's threatening legal action!"**
- Extended family members claim property rights
- Legal threats create crisis and relationship strain
- The cousins must decide: fight or negotiate?

### 💎 Month 4: Hidden Treasure
**"There's a valuable art collection in the basement - who gets credit for finding it?"**
- Discovery of valuable art collection changes everything
- New financial dynamics create profit distribution conflicts
- Ownership and credit disputes emerge

### 🚨 Month 5: Legal Crisis
**"This is serious - we could lose everything if we don't act fast!"**
- Major legal challenge threatens property ownership
- High-stakes decision making under extreme pressure
- Resource allocation for expensive legal defense

### 🎯 Month 6: Resolution
**"After everything we've been through, what does the future hold?"**
- Legal challenges finally resolved
- Relationships have fundamentally changed
- Long-term planning and relationship repair needed

## LLM-Powered Analysis System

### Analysis Methods
All relationship dynamics are analyzed using **Google Gemini** with sophisticated prompts:

1. **Trust Change Analysis**
   - Detects specific trust changes between individual cousin pairs
   - Identifies positive/negative trust indicators
   - Provides confidence scores and detailed reasoning

2. **Conflict Detection**
   - Identifies disagreements, tensions, and opposition between cousins
   - Categorizes conflict types and severity levels
   - Excludes self-conflicts and duplicate entries

3. **Alliance Formation**
   - Detects collaboration, support, and partnership patterns
   - Categorizes alliance strength and type
   - Tracks coalition building and mutual backing

4. **Behavioral Pattern Recognition**
   - Identifies leadership, collaboration, competition, and other behavioral patterns
   - Assesses impact (positive/negative/neutral) on group dynamics
   - Provides detailed descriptions of observed behaviors

### Fallback System
Each LLM analysis method includes a keyword-based fallback system that activates if:
- LLM API calls fail
- JSON parsing errors occur
- Network connectivity issues arise

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

## 🚀 Quick Start

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

**That's it!** The experiment will run automatically and generate detailed logs and analysis files.

## 🤖 Why Google Gemini?

This experiment uses **Google Gemini** for AI-powered relationship analysis:

- 🆓 **Free Tier**: 15 requests/minute, 1M tokens/day
- 🧠 **High Quality**: Excellent reasoning and conversation analysis
- 🛡️ **Built-in Rate Limiting**: Automatic API quota management
- 🔄 **Retry Logic**: Handles overload errors with exponential backoff
- 📊 **Reliable Analysis**: Sophisticated conflict, alliance, and behavioral pattern detection

The system includes robust error handling and fallback analysis to ensure reliable long-running experiments.

## 📁 What You'll Get

The experiment generates rich data files in the `output/` directory:

```
output/
├── logs/                    # Detailed conversation logs
├── results/                 # Metrics and analysis data  
└── state/                   # Experiment state for resuming
```

**Key Outputs:**
- 📝 **Conversation Logs**: Every family discussion with AI analysis
- 📊 **Relationship Data**: Trust levels, conflicts, alliances over time
- 🎭 **Behavioral Patterns**: Leadership, collaboration, competition patterns
- 💰 **Resource Tracking**: Money, time, reputation, social connections
- 🔄 **State Files**: Resume experiments from any point

## State Persistence

The experiment automatically saves its complete state after each month, enabling:

- **Individual month execution** without losing context from previous months
- **Resume interrupted runs** from the last completed month
- **Full context maintenance** including relationship dynamics, resource allocations, and decision history
- **Preservation of all metrics and conversation logs** across runs

**Note**: All output files are automatically organized in the `output/` directory, keeping the project root clean and organized.

## 🔬 Research Insights

This experiment studies fascinating questions about human behavior:

- 🤝 **How do alliances form and break under pressure?**
- 🧠 **Which personality types emerge as leaders in crises?**
- ⚖️ **How do groups make decisions when everyone has equal power?**
- 💰 **What happens when resources are limited and stakes are high?**
- 🔄 **How do relationships evolve through conflict and cooperation?**
- 🤖 **How effective is AI at analyzing human social dynamics?**

## 🛠️ Technical Stack

- **CrewAI**: Multi-agent conversation orchestration
- **Google Gemini**: AI-powered relationship analysis  
- **Python 3.10+**: Core experiment framework
- **Rate Limiting**: Smart API quota management
- **Error Handling**: Robust fallback systems
- **State Persistence**: Resume experiments from any point

## 🎯 Perfect For

- **Researchers** studying group dynamics and decision-making
- **Students** learning about multi-agent systems and AI
- **Developers** interested in CrewAI and LLM integration
- **Anyone** curious about family inheritance drama! 😄

## 🤝 Contributing

This framework is designed to be extensible. You can easily add:
- New cousin personality types
- Additional scenario events  
- Custom analysis metrics
- Enhanced LLM prompts
- New relationship dynamics

## 📄 License

Research and educational use. Please follow Google's API usage policies.

---

**Ready to see what happens when family meets inheritance?** 🏛️✨