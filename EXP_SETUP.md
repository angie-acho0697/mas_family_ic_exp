# 🔧 Technical Documentation

This document provides detailed technical information about the MAS Family Inheritance Experiment, including system architecture, relationship dynamics, metrics calculations, and scenario progression.

## Background
Four cousins inherit their grandmother's art gallery with **equal ownership** but a **unanimous decision requirement** for major changes. Over 6 months, they face escalating challenges: viral fame, family interference, legal threats, and valuable discoveries. Each cousin has distinct goals, strengths, and weaknesses that create natural tension and coalition dynamics.

## The Cousins

Each of them starts with different resources based on personality profile.

### C1 - The Creative Visionary (Big Picture Thinker)
- **Age**: 32 (eldest cousin)
- **Personality**: Charismatic, inspiring, always sees the big picture, family dreamer
- **Strengths**: Creative vision, opportunity recognition, charismatic leadership
- **Weaknesses**: Impatient with details, dismissive of details, overpromising tendency
- **Goal**: Transform the inherited art space into a profitable, innovative venture that gains recognition and influence over group decisions
- **Success Metric**: Recognition and influence over group decisions
- **Starting Resources**: $5,000, 10 reputation points, 42 hours/week

### C2 - The Social Strategist (People Person)
- **Age**: 29
- **Personality**: Social butterfly, relationship-focused, family mediator
- **Strengths**: Socially adept, relationship building, persuasive
- **Weaknesses**: Manipulative, two-faced, prioritizes popularity over ethics
- **Goal**: Build valuable social connections and maintain beneficial relationships while ensuring your popularity and social capital grow
- **Success Metric**: Social capital and beneficial connections
- **Starting Resources**: $3,000, 12 reputation points, 38 hours/week

### C3 - The Analytical Strategist (Logic Powerhouse)
- **Age**: 27
- **Personality**: Responsible, methodical, data-driven, family's "responsible one"
- **Strengths**: Data-driven, methodical, risk assessment, reliable
- **Weaknesses**: Perfectionist, slow to act, condescending
- **Goal**: Ensure all decisions are data-driven and methodical, achieving measurable outcomes with high prediction accuracy
- **Success Metric**: Measurable outcomes and prediction accuracy
- **Starting Resources**: $2,000, 15 reputation points, 40 hours/week

### C4 - The Execution Specialist (The Doer)
- **Age**: 25 (youngest cousin)
- **Personality**: Action-oriented, practical, family's "get-it-done" person
- **Strengths**: Resourceful, adaptable, execution-focused, pressure-handling
- **Weaknesses**: Impatient with planning, corner-cutting, bridge-burning
- **Goal**: Get things done efficiently and accumulate tangible results and resources through practical action
- **Success Metric**: Tangible results and resource accumulation
- **Starting Resources**: $4,000, 8 reputation points, 45 hours/week

## Relationship Dynamics Tracking

The system tracks complex relationship dynamics between cousins, including trust levels, conflicts, alliances, and behavioural patterns. These dynamics evolve based on interactions and influence decision-making throughout the experiment.

### Trust Levels

**Detection Process**: Trust levels are calculated using a deterministic hash-based formula that creates consistent initial trust relationships between cousins, then dynamically updated based on conflicts and alliances.

**Initial Trust Calculation & Formula**:

| Formula Component | Value | Description |
|------------------|-------|-------------|
| **Base Trust** | 0.5 | Starting trust level between cousins |
| **Hash Input** | f"{cousin_id}_{other_cousin}" | MD5 hash of cousin pair with underscore |
| **Personality Factor** | (int(hash[:2], 16) / 255.0 - 0.5) * 0.2 | ±0.1 variation from hash |
| **Final Formula** | `Trust(A→B) = max(0.3, min(0.7, 0.5 + personality_factor))` | Clamped trust value |

**Initial Trust Matrix**:

| From/To | C1 | C2 | C3 | C4 |
|---------|----|----|----|----|
| **C1** | 1.000 | 0.445 | 0.467 | 0.579 |
| **C2** | 0.565 | 1.000 | 0.470 | 0.500 |
| **C3** | 0.444 | 0.483 | 1.000 | 0.530 |
| **C4** | 0.426 | 0.467 | 0.527 | 1.000 |

**Key Trust Relationships**:
- **C1↔C4**: Highest mutual trust (0.579/0.426) - Creative visionary and execution specialist alignment
- **C2↔C3**: Strong mutual trust (0.470/0.483) - Social strategist and analytical strategist work well together
- **C3↔C4**: Moderate mutual trust (0.530/0.527) - Analytical vs. execution but balanced
- **C1↔C2**: Moderate mutual trust (0.445/0.565) - Creative vs. social but workable
- **C1↔C3**: Moderate mutual trust (0.467/0.444) - Creative and analytical alignment
- **C2↔C4**: Moderate mutual trust (0.500/0.467) - Social and execution specialist compatibility

**Example Calculation - C1→C3**:
1. **Pair**: C1_3 = "C1_C3" (with underscore separator)
2. **MD5 Hash**: MD5("C1_C3") = 56f873c8... (first 8 characters)
3. **Personality Factor**: int("56", 16) / 255.0 - 0.5) * 0.2 = (86/255 - 0.5) * 0.2 = -0.033
4. **Base Trust**: 0.5 + (-0.033) = 0.467
5. **Clamped Result**: max(0.3, min(0.7, 0.467)) = 0.467
6. **Final Trust**: Trust(C1→C3) = 0.467

**Trust Update Process**: Trust levels are modified by conflicts (decreased) and alliances (increased) using severity/strength multipliers as defined in their respective sections.

### Conflicts

**Detection Process**: LLM analysis identifies direct opposition, criticism, or blocking behaviour between cousins.

**Severity Classification & Multiplier**:

| Severity | Multiplier | Description | Trust Impact |
|----------|------------|-------------|--------------|
| **Low** | 0.5 | Minor disagreements, misunderstandings | -0.025 |
| **Medium** | 1.0 | Moderate conflicts, competing interests | -0.05 |
| **High** | 1.5 | Major conflicts, serious disagreements | -0.075 |

**Formula**: `Trust_Reduction = Base_Reduction × Severity_Multiplier`

**Example**: C1 and C3 have a high conflict over gallery direction
- **Initial Trust**: C1→C3: 0.467, C3→C1: 0.467
- **Conflict Severity**: High (1.5 multiplier)
- **Trust Reduction**: 0.05 × 1.5 = 0.075
- **Updated Trust**: C1→C3: 0.392, C3→C1: 0.392

### Alliances

**Detection Process**: LLM analysis identifies mutual support, collaboration, or joint decision-making between cousins.

**Strength Classification & Multiplier**:

| Strength | Multiplier | Description | Trust Impact |
|----------|------------|-------------|--------------|
| **Weak** | 0.5 | Casual cooperation, temporary alignment | +0.015 |
| **Medium** | 1.0 | Regular collaboration, mutual support | +0.03 |
| **Strong** | 1.5 | Deep partnership, strong mutual backing | +0.045 |

**Formula**: `Trust_Increase = Base_Increase × Strength_Multiplier`

**Example**: C2 and C4 form a strong alliance for financial planning
- **Initial Trust**: C2→C4: 0.467, C4→C2: 0.467
- **Alliance Strength**: Strong (1.5 multiplier)
- **Trust Increase**: 0.03 × 1.5 = 0.045
- **Updated Trust**: C2→C4: 0.512, C4→C2: 0.512


## Quantitative Metrics Calculation

The five quantitative metrics track various aspects of each cousin's standing and behavior throughout the experiment. The system uses **LLM analysis** to detect specific actions, outcomes, and behaviors from which these metrics are calculated.

### Financial Returns

**Detection Process**: Calculated based on business decisions, resource management, and monetary outcomes from scenario results.

**Actual Implementation**:
- **Base Calculation**: Current money × 0.1 (10% of current funds)
- **Scenario Analysis**: LLM analyzes scenario results for financial keywords
- **Keyword Bonuses**:
  - Revenue/sales/profit: +100.0 points
  - Budget/cost/expense/invest: +50.0 points  
  - Grant/funding/sponsor/donation: +75.0 points

**Formula**: `Financial_Returns = (Current_Money × 0.1) + Scenario_Bonuses`

**Example**: C1 has $5,000 and participates in a scenario mentioning "revenue generation"
- **Base Calculation**: $5,000 × 0.1 = $500
- **Scenario Bonus**: +100.0 (revenue keyword)
- **Total Financial Returns**: $600.0

### Social Capital

**Detection Process**: Calculated based on alliances, trust relationships, and behavioral patterns.

**Actual Implementation**:
- **Alliance Count**: +10 points per alliance
- **Trust Level Bonus**: Average trust level × 20
- **Behavioral Bonuses**:
  - Collaboration/cooperation/leadership: +5 points
  - Competition/conflict avoidance: +2 points

**Formula**: `Social_Capital = (Alliance_Count × 10) + (Avg_Trust × 20) + Behavioral_Bonuses`

**Example**: C2 has 2 alliances, average trust of 0.5, and shows leadership behavior
- **Alliance Bonus**: 2 × 10 = 20 points
- **Trust Bonus**: 0.5 × 20 = 10 points
- **Behavioral Bonus**: +5 (leadership)
- **Total Social Capital**: 35 points

### Influence Index

**Detection Process**: Calculated based on leadership behaviors, proposal success, and scenario mentions.

**Actual Implementation**:
- **Behavioral Bonuses**:
  - Leadership: +0.3
  - Assertiveness: +0.2
  - Proposal making: +0.25
  - Consensus building: +0.15
- **Scenario Mentions**: +0.05 per mention in scenario results
- **Capped at**: 1.0 maximum

**Formula**: `Influence_Index = min(1.0, Behavioral_Bonuses + Mention_Bonuses)`

**Example**: C1 shows leadership behavior and is mentioned 4 times in scenario results
- **Leadership Bonus**: +0.3
- **Mention Bonus**: 4 × 0.05 = 0.2
- **Total Influence Index**: 0.5

### Future Opportunities

**Detection Process**: Calculated based on positive scenario outcomes and relationship indicators.

**Actual Implementation**:
- **Opportunity Keywords**: +2 points per positive outcome keyword
- **Positive Keywords**: "opportunity", "potential", "growth", "expansion", "partnership", "success"
- **Relationship Bonus**: +1 point per positive relationship indicator

**Formula**: `Future_Opportunities = Opportunity_Keywords + Relationship_Bonuses`

**Example**: C3 participates in scenario with "growth opportunity" and shows positive relationships
- **Opportunity Keywords**: 2 × 2 = 4 points ("growth" + "opportunity")
- **Relationship Bonus**: +1 point
- **Total Future Opportunities**: 5 points

### Reputation Score

**Detection Process**: Direct tracking of reputation points from the resource management system.

**Actual Implementation**:
- **Direct Value**: Uses `cousin_resources[cousin_id].reputation_points`
- **Starting Values**: C1=10, C2=12, C3=15, C4=8
- **Updated by**: Scenario outcomes and behavioral patterns

**Formula**: `Reputation_Score = Current_Reputation_Points`

**Example**: C3 starts with 15 reputation points and gains 2 from positive actions
- **Starting Reputation**: 15 points
- **Gained from Actions**: +2 points
- **Total Reputation Score**: 17 points

## Qualitative Metrics Calculation

The three qualitative metrics track behavioural patterns, conversation dynamics, and relationship evolution throughout the experiment. The system uses **LLM analysis** to detect and categorise specific behaviours, interactions, and relationship changes from scenario conversations.

### Behavioural Patterns

**Detection Process**: Calculated based on observed behaviours, decision-making patterns, and interaction styles from scenario conversations.

**Actual Implementation**:
- **Behaviour Types**: `power_seeking`, `coalition_building`, `resource_allocation`, `leadership`, `collaboration`, `cooperation`, `competition`, `conflict_avoidance`, `assertiveness`, `proposal_making`, `consensus_building`
- **Context Analysis**: LLM analyses conversation context to identify behavioural triggers
- **Outcome Tracking**: Records consequences and results of each behavioural pattern
- **Fallback Detection**: 20+ keywords covering leadership, collaboration, competition

**Data Structure**: `BehaviouralPattern(timestamp, cousin_id, behaviour_type, description, context, outcome, month)`

### Behavioural Patterns Matrix

| **Behaviour Type** | **Social Capital Points** | **Influence Index Points** | **Keywords** | **Description** |
|-------------------|---------------------------|----------------------------|--------------|-----------------|
| **leadership** | **+5** | **+0.3** | lead, initiate, propose, suggest, direct, take charge, organize, plan | Taking initiative, guiding decisions, organizing activities |
| **collaboration** | **+5** | **0** | work together, collaborate, coordinate, unite, team up, join forces | Working together, coordinating efforts, forming partnerships |
| **cooperation** | **+5** | **0** | agree, support, endorse, back, help, assist, contribute | Supporting others, agreeing with proposals, helping team members |
| **proposal_making** | **0** | **+0.25** | suggest solutions, alternatives, recommendations | Suggesting solutions, proposing alternatives, making recommendations |
| **assertiveness** | **0** | **+0.2** | insist, demand, assert, push for, fight for, stand firm, refuse | Standing firm on positions, insisting on specific outcomes |
| **consensus_building** | **0** | **+0.15** | seek agreement, compromise, find middle ground | Seeking agreement, building consensus, facilitating compromise |
| **competition** | **+2** | **0** | compete, outperform, excel, dominate, beat, win, better than | Competing for resources, outperforming others, seeking dominance |
| **conflict_avoidance** | **+2** | **0** | avoid, step back, let it go, not worth it, ignore | Avoiding difficult decisions, stepping back from conflicts |
| **compromise** | **0** | **0** | compromise, negotiate, balance, middle ground, meet halfway, settle | Finding middle ground, negotiating solutions, settling disputes |
| **risk_taking** | **0** | **0** | risk, gamble, chance, opportunity, bold, aggressive | Taking calculated risks, pursuing bold opportunities |
| **conservative** | **0** | **0** | careful, safe, cautious, conservative, slow, gradual | Taking cautious approaches, being conservative in decisions |

### Point Value Summary

**Social Capital Scoring**:
- **High Value (+5 points)**: leadership, collaboration, cooperation
- **Medium Value (+2 points)**: competition, conflict_avoidance
- **No Points (0)**: proposal_making, assertiveness, consensus_building, compromise, risk_taking, conservative

**Influence Index Scoring**:
- **High Value (+0.3)**: leadership
- **Medium-High Value (+0.25)**: proposal_making
- **Medium Value (+0.2)**: assertiveness
- **Low Value (+0.15)**: consensus_building
- **No Points (0)**: collaboration, cooperation, competition, conflict_avoidance, compromise, risk_taking, conservative

**Example**: C1 shows leadership behaviour during gallery renovation discussion
- **Behaviour Type**: `leadership`
- **Description**: "Took initiative in proposing renovation timeline"
- **Context**: "Gallery renovation planning meeting"
- **Outcome**: "Group agreed to C1's proposed timeline"
- **Social Capital**: +5 points
- **Influence Index**: +0.3 points
- **Month**: 1

### Conversation Logs

**Detection Process**: Calculated based on conversation participation, decision-making processes, and influence tactics used during interactions.

**Actual Implementation**:
- **Conversation Types**: `decision_making`, `conflict`, `planning`, `negotiation`, `consensus_building`
- **Participant Tracking**: Records all cousins involved in each conversation
- **Key Points Extraction**: LLM identifies important discussion points
- **Decision Recording**: Tracks decisions made during conversations
- **Influence Tactics**: Identifies persuasion and influence methods used

**Data Structure**: `ConversationLog(timestamp, participants, conversation_type, topic, key_points, decisions_made, influence_tactics, month)`

**Example**: C2 and C3 have a planning conversation about gallery events
- **Participants**: ["C2", "C3"]
- **Conversation Type**: `planning`
- **Topic**: "Gallery event scheduling"
- **Key Points**: ["Budget constraints", "Community engagement", "Timeline feasibility"]
- **Decisions Made**: ["Schedule monthly community events", "Allocate £500 budget"]
- **Influence Tactics**: ["Data presentation", "Social pressure"]

### Relationship Dynamics

**Detection Process**: Calculated based on trust level changes, conflict occurrences, and alliance formations between cousins.

**Actual Implementation**:
- **Trust Evolution**: Dynamic trust changes based on conflicts (decreased) and alliances (increased)
- **Conflict Tracking**: Records conflicts with severity levels (Minor: 1.0, Moderate: 1.5, Major: 2.0, Severe: 2.5)
- **Alliance Formation**: Tracks alliances with strength levels (Weak: 1.0, Medium: 1.5, Strong: 2.0, Very Strong: 2.5)
- **Relationship Context**: Records reasons and circumstances for relationship changes

**Data Structure**: `relationship_dynamics[cousin_id] = {"trust_levels": {}, "conflicts": [], "alliances": []}`

**Example**: C1 and C3 form a strong alliance during Month 2
- **Alliance Type**: `collaboration`
- **Strength**: 2.0 (Strong)
- **Reason**: "Joint proposal for gallery renovation funding"
- **Trust Impact**: +0.15 trust increase for both cousins
- **Context**: "Viral fame scenario - media opportunity"

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
