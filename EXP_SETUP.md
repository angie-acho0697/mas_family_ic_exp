# 🔧 Technical Documentation

This document provides detailed technical information about the MAS Family Inheritance Experiment, including system architecture, relationship dynamics, metrics calculations, and scenario progression.

## Background
Four cousins inherit their grandmother's art gallery with **equal ownership** but a **unanimous decision requirement** for major changes. Over 6 months, they face escalating challenges: viral fame, family interference, legal threats, and valuable discoveries. Each cousin has distinct goals, strengths, and weaknesses that create natural tension and coalition dynamics.

## The Cousins

Each of them starts with different resources based on personality profile.

### C1 - The Creative Visionary
- **Personality**: Charismatic, inspiring, always sees the big picture
- **Strengths**: Creative vision, opportunity spotting, natural leadership
- **Weaknesses**: Impatient with details, tends to overpromise
- **Goal**: Transform the gallery into a modern cultural hub combining art, technology, and community
- **Starting Resources**: $5,000, 10 reputation points, 42 hours/week (more initial money for creative projects and works longer)

### C2 - The Practical Manager
- **Personality**: Organised, methodical, focused on efficiency and results
- **Strengths**: Project management, financial planning, operational excellence
- **Weaknesses**: Risk-averse, sometimes inflexible, struggles with creative ambiguity
- **Goal**: Establish a profitable, sustainable business with clear processes and predictable returns
- **Starting Resources**: $3,000, 12 reputation points, 38 hours/week (balanced approach, good reputation from past management roles)

### C3 - The Community Builder
- **Personality**: Empathetic, relationship-focused, natural mediator
- **Strengths**: Conflict resolution, community engagement, building partnerships
- **Weaknesses**: Avoids difficult decisions, sometimes prioritises harmony over results
- **Goal**: Create a welcoming community space that serves local artists and brings people together
- **Starting Resources**: $2,000, 15 reputation points, 40 hours/week (lower money but highest reputation from community work)

### C4 - The Financial Strategist
- **Personality**: Analytical, data-driven, focused on long-term value creation
- **Strengths**: Financial analysis, market research, strategic planning
- **Weaknesses**: Can be overly cautious, sometimes misses human elements, struggles with emotional decisions
- **Goal**: Maximise the property's long-term value through strategic investments and market positioning
- **Starting Resources**: $4,000, 8 reputation points, 45 hours/week (good money for investments, lower reputation due to focus on numbers over people)

## Relationship Dynamics Tracking

The system tracks complex relationship dynamics between cousins, including trust levels, conflicts, alliances, and behavioural patterns. These dynamics evolve based on interactions and influence decision-making throughout the experiment.

### Trust Levels

**Formula**: `Trust(A→B) = 0.3 + (hash(A+B) % 100) / 200`

**Initial Trust Matrix**:

| From/To | C1 | C2 | C3 | C4 |
|---------|----|----|----|----|
| **C1** | 1.0 | 0.334 | 0.467 | 0.445 |
| **C2** | 0.334 | 1.0 | 0.445 | 0.467 |
| **C3** | 0.467 | 0.445 | 1.0 | 0.334 |
| **C4** | 0.445 | 0.467 | 0.334 | 1.0 |

**Key Insights**:
- **C1↔C3**: Highest mutual trust (0.467) - Creative and community-focused
- **C2↔C4**: Strong mutual trust (0.467) - Both business-oriented
- **C1↔C2**: Lowest mutual trust (0.334) - Creative vs. practical tension
- **C3↔C4**: Lowest mutual trust (0.334) - Community vs. financial focus

### Conflicts

**Detection Process**: LLM analysis identifies direct opposition, criticism, or blocking behaviour between cousins.

**Severity Classification & Multiplier**:

| Severity | Multiplier | Description | Trust Impact |
|----------|------------|-------------|--------------|
| **Minor** | 1.0 | Disagreement, mild criticism | -0.05 |
| **Moderate** | 1.5 | Strong opposition, blocking | -0.075 |
| **Major** | 2.0 | Public criticism, sabotage | -0.10 |
| **Severe** | 2.5 | Personal attacks, threats | -0.125 |

**Formula**: `Trust_Reduction = Base_Reduction × Severity_Multiplier`

**Example**: C1 and C3 have a major conflict over gallery direction
- **Initial Trust**: C1→C3: 0.467, C3→C1: 0.467
- **Conflict Severity**: Major (2.0 multiplier)
- **Trust Reduction**: 0.05 × 2.0 = 0.10
- **Updated Trust**: C1→C3: 0.367, C3→C1: 0.367

### Alliances

**Detection Process**: LLM analysis identifies mutual support, collaboration, or joint decision-making between cousins.

**Strength Classification & Multiplier**:

| Strength | Multiplier | Description | Trust Impact |
|----------|------------|-------------|--------------|
| **Weak** | 1.0 | Casual agreement, minor support | +0.15 |
| **Moderate** | 1.5 | Active collaboration, joint decisions | +0.225 |
| **Strong** | 2.0 | Strategic partnership, mutual defence | +0.30 |
| **Formal** | 2.5 | Written agreement, public commitment | +0.375 |

**Formula**: `Trust_Increase = Base_Increase × Strength_Multiplier`

**Example**: C2 and C4 form a strong alliance for financial planning
- **Initial Trust**: C2→C4: 0.467, C4→C2: 0.467
- **Alliance Strength**: Strong (2.0 multiplier)
- **Trust Increase**: 0.15 × 2.0 = 0.30
- **Updated Trust**: C2→C4: 0.767, C4→C2: 0.767

### Behavioural Patterns

**Detection Process**: LLM analysis identifies recurring behavioural patterns in conversations, classified by impact and type.

**Pattern Types**:
- **Leadership**: Taking initiative, guiding decisions
- **Collaboration**: Working together, seeking consensus
- **Competition**: Competing for resources, recognition
- **Conflict Avoidance**: Avoiding difficult decisions
- **Assertiveness**: Standing firm on positions
- **Proposal Making**: Suggesting solutions, alternatives
- **Consensus Building**: Seeking agreement, compromise

**Impact Classification**:
- **Positive**: Behaviours that benefit the group
- **Negative**: Behaviours that harm the group
- **Neutral**: Behaviours with mixed or unclear impact

**Usage in Metrics**:
- **Social Capital**: +5 for collaboration/cooperation/leadership, +2 for competition/conflict avoidance
- **Influence Index**: +0.3 for leadership, +0.2 for assertiveness, +0.25 for proposal making, +0.15 for consensus building

## Qualitative Metrics Calculation

### Financial Returns

**Detection Process**: LLM analysis identifies financial decisions, investments, and monetary outcomes in conversations.

**Classification & Multiplier**:

| Type | Multiplier | Description | Base Value |
|------|------------|-------------|------------|
| **Investment** | 1.0 | Money spent on improvements | $500 |
| **Revenue** | 1.5 | Money earned from business | $750 |
| **Cost Saving** | 0.8 | Money saved through efficiency | $400 |
| **Loss** | -1.0 | Money lost through poor decisions | -$500 |

**Formula**: `Financial_Returns = Base_Value × Type_Multiplier × Cousin_Count`

**Example**: C1 and C2 make a joint investment in gallery renovation
- **Base Value**: $500 (investment)
- **Type Multiplier**: 1.0
- **Cousin Count**: 2 (C1 and C2)
- **Financial Returns**: $500 × 1.0 × 2 = $1,000

### Social Capital

**Detection Process**: LLM analysis identifies social connections, community engagement, and relationship building activities.

**Classification & Multiplier**:

| Type | Multiplier | Description | Base Value |
|------|------------|-------------|------------|
| **Community Event** | 1.0 | Hosting public events | 5 points |
| **Partnership** | 1.5 | Forming business partnerships | 7.5 points |
| **Media Coverage** | 2.0 | Positive media attention | 10 points |
| **Reputation Damage** | -1.0 | Negative publicity | -5 points |

**Formula**: `Social_Capital = Base_Value × Type_Multiplier + Behavioural_Bonus`

**Example**: C3 organises a community art show with media coverage
- **Base Value**: 5 points (community event)
- **Type Multiplier**: 2.0 (media coverage)
- **Behavioural Bonus**: +5 (collaboration behaviour)
- **Social Capital**: 5 × 2.0 + 5 = 15 points

### Influence Index (Network Influence)

**Detection Process**: LLM analysis identifies influence tactics, persuasion attempts, and decision-making power.

**Classification & Multiplier**:

| Type | Multiplier | Description | Base Value |
|------|------------|-------------|------------|
| **Persuasion** | 1.0 | Convincing others of ideas | 0.2 |
| **Coalition Building** | 1.5 | Forming alliances | 0.3 |
| **Information Control** | 2.0 | Controlling key information | 0.4 |
| **Authority** | 2.5 | Using formal authority | 0.5 |

**Formula**: `Influence_Index = Base_Value × Type_Multiplier + Behavioural_Bonus`

**Example**: C1 uses persuasion and coalition building to influence gallery direction
- **Base Value**: 0.2 (persuasion)
- **Type Multiplier**: 1.5 (coalition building)
- **Behavioural Bonus**: +0.3 (leadership behaviour)
- **Influence Index**: 0.2 × 1.5 + 0.3 = 0.6

### Future Opportunities

**Detection Process**: LLM analysis identifies potential future opportunities, partnerships, and growth prospects.

**Classification & Multiplier**:

| Type | Multiplier | Description | Base Value |
|------|------------|-------------|------------|
| **Partnership** | 1.0 | Potential business partnership | 3 points |
| **Expansion** | 1.5 | Growth opportunity | 4.5 points |
| **Investment** | 2.0 | External investment opportunity | 6 points |
| **Market Entry** | 2.5 | New market opportunity | 7.5 points |

**Formula**: `Future_Opportunities = Base_Value × Type_Multiplier × Cousin_Count`

**Example**: C2 and C4 identify an expansion opportunity
- **Base Value**: 4.5 points (expansion)
- **Type Multiplier**: 1.5
- **Cousin Count**: 2 (C2 and C4)
- **Future Opportunities**: 4.5 × 1.5 × 2 = 13.5 points

### Reputation Score

**Detection Process**: LLM analysis identifies reputation changes based on public perception and community standing.

**Classification & Multiplier**:

| Type | Multiplier | Description | Base Value |
|------|------------|-------------|------------|
| **Positive Action** | 1.0 | Good deed, community service | 2 points |
| **Public Recognition** | 1.5 | Award, media praise | 3 points |
| **Scandal** | -1.0 | Negative publicity | -2 points |
| **Controversy** | -1.5 | Public disagreement | -3 points |

**Formula**: `Reputation_Score = Base_Value × Type_Multiplier + Behavioural_Bonus`

**Example**: C3 receives public recognition for community work
- **Base Value**: 2 points (positive action)
- **Type Multiplier**: 1.5 (public recognition)
- **Behavioural Bonus**: +2 (collaboration behaviour)
- **Reputation Score**: 2 × 1.5 + 2 = 5 points

## Resource Calculation Methods

### Detection Process

**Primary Method**: LLM analysis of conversation content to identify resource-related decisions and outcomes.

**Calculation Components**:
- **Base Contribution**: Personality-based resource changes per scenario
- **Involvement Multiplier**: Dynamic adjustment based on conversation participation
- **Scenario Impact**: Additional resource changes from scenario outcomes

**When It Happens**: After each scenario conversation, resources are updated based on:
1. **Conversation Analysis**: LLM identifies resource-related decisions
2. **Participation Level**: Involvement multiplier based on mention count
3. **Scenario Outcome**: Additional resource changes from scenario results

### Initial Resource Values

| Cousin | Money | Reputation | Weekly Hours |
|--------|-------|------------|--------------|
| **C1** | $5,000 | 10 points | 42 hours |
| **C2** | $3,000 | 12 points | 38 hours |
| **C3** | $2,000 | 15 points | 40 hours |
| **C4** | $4,000 | 8 points | 45 hours |

### Formula

**Base Contribution**: `Resource_Change = Base_Pattern × Involvement_Multiplier`

**Involvement Multiplier**: `1.0 + (mentions - 3) × 0.1` (range: 0.7 to 1.5)

### Base Contribution Patterns (Per Scenario)

| Cousin | Time Spent | Money Change | Reputation Change |
|--------|------------|--------------|-------------------|
| **C1** | 8.0 hours | +$500 | +2.0 points |
| **C2** | 6.0 hours | +$300 | +3.0 points |
| **C3** | 10.0 hours | +$200 | +1.0 points |
| **C4** | 12.0 hours | +$400 | +1.5 points |

### Involvement Multiplier Classification

| Mentions | Multiplier | Description | Resource Impact |
|----------|------------|-------------|-----------------|
| **0-2** | 0.7-0.9 | Low participation | Reduced resource gains |
| **3** | 1.0 | Average participation | Standard resource gains |
| **4-5** | 1.1-1.2 | High participation | Increased resource gains |
| **6+** | 1.3-1.5 | Very high participation | Maximum resource gains |

### Example

**Scenario**: C1 participates in a gallery renovation discussion
- **Mentions**: 5 times in conversation
- **Involvement Multiplier**: 1.0 + (5 - 3) × 0.1 = 1.2
- **Base Pattern**: 8.0 hours, +$500, +2.0 reputation
- **Calculated Resources**:
  - Time spent: 8.0 × 1.2 = 9.6 hours
  - Money gained: $500 × 1.2 = $600
  - Reputation gained: 2 × 1.2 = 2.4 points
- **Updated Resources**: 32.4 hours remaining, $5,600 total, 12.4 reputation

## Scenario Progression

### Month 1: The Inheritance & Competing Visions
**Week 1: The Inheritance**
- Legal documents and property inspection
- Four cousins inherit art gallery with equal ownership
- Unanimous decision requirement for major changes
- Initial family meeting to establish ground rules

**Week 3: Competing Visions**
- Each cousin presents their vision for transforming the gallery space
- Individual research completed and proposal deadline reached
- Consensus vs. voting deadlock vs. one vision dominating
- Timeline and implementation approach decisions

### Month 2: Viral Fame Opportunity
**Week 2: Viral Fame Opportunity**
- Social media post about family inheritance goes viral (100k+ views)
- Media requests start coming in
- Family must decide who should be the public face
- Opportunity to monetize viral attention vs. privacy concerns
- Internal conflicts over who gets credit for the attention

### Month 3: Extended Family Interference
**Week 1: Extended Family Interference**
- Other family members claim property rights
- Legal notice received and family meeting called by extended relatives
- Legal threats create crisis and relationship strain
- Decision: fight legally vs. negotiate settlement
- How to handle family relationships during conflict

### Month 4: Hidden Treasure Discovery
**Week 2: Hidden Treasure Discovery**
- Valuable art collection discovered in gallery storage
- Art appraisal completed - worth significant money
- New financial dynamics create profit distribution conflicts
- Decision: sell collection vs. keep for gallery display
- Ownership and credit disputes over the discovery

### Month 5: Ownership Challenge Crisis
**Week 1: Ownership Challenge Crisis**
- Serious legal challenge threatens cousins' ownership of property
- Court summons received with legal deadline approaching
- High-stakes decision making under extreme pressure
- Resource allocation for expensive legal defence
- Consider settlement vs. fight to the end

### Month 6: Resolution and Future Planning
**Week 4: Resolution and Future Planning**
- Legal challenges finally resolved
- Business performance review completed
- Relationships have fundamentally changed
- Decision: how to restructure decision-making
- Long-term business goals and relationship repair needed
