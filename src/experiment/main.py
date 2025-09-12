"""
Main Experiment Runner for MAS Family Inheritance Experiment

Orchestrates the CrewAI agents, scenario progression, and data collection
"""

import os
import sys
import logging
import time
import random
from typing import Dict, List, Any
from datetime import datetime
import json
import traceback

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Get logger (configuration handled by main runner)
logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter to prevent API quota exhaustion"""
    
    def __init__(self, requests_per_minute=10, requests_per_hour=100):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.request_times = []
        self.last_request_time = 0
        self.min_delay = 60.0 / requests_per_minute  # Minimum delay between requests
        self.total_requests = 0
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limits"""
        current_time = time.time()
        
        # Remove requests older than 1 hour
        self.request_times = [t for t in self.request_times if current_time - t < 3600]
        
        # Check hourly limit
        if len(self.request_times) >= self.requests_per_hour:
            wait_time = 3600 - (current_time - self.request_times[0])
            if wait_time > 0:
                logger.info(f"⏳ Rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                current_time = time.time()
        
        # Check minimum delay between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_delay:
            wait_time = self.min_delay - time_since_last
            logger.info(f"⏳ Rate limiting: waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
        
        # Record this request
        self.request_times.append(current_time)
        self.last_request_time = current_time
        self.total_requests += 1
        
        # Log progress every 5 requests
        if self.total_requests % 5 == 0:
            logger.info(f"📊 API Requests made: {self.total_requests} (Hourly limit: {self.requests_per_hour})")

# Global rate limiter instance - Will be configured based on provider
# Rate limiter will be configured based on provider in LLMConfig
# This is just a fallback with conservative limits
rate_limiter = RateLimiter(requests_per_minute=30, requests_per_hour=1000)  # More appropriate for GPT-2 on Hugging Face

def safe_api_call(func, operation_name="API call", max_retries=3):
    """
    Safely execute an API call with retry logic and better error handling
    
    Args:
        func: Function to execute
        operation_name: Name of the operation for logging
        max_retries: Maximum number of retry attempts
    """
    for attempt in range(max_retries + 1):
        try:
            # Apply rate limiting before each attempt
            rate_limiter.wait_if_needed()
            
            logger.info(f"🔄 Executing {operation_name} (attempt {attempt + 1}/{max_retries + 1})")
            result = func()
            logger.info(f"✅ {operation_name} completed successfully")
            return result
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Check if it's a retryable error
            if any(keyword in error_str for keyword in ["503", "overloaded", "unavailable", "timeout", "rate limit"]):
                if attempt < max_retries:
                    # Calculate exponential backoff delay
                    delay = min(30 * (2 ** attempt), 300)  # 30s, 60s, 120s, max 300s
                    jitter = random.uniform(0.1, 0.3) * delay
                    total_delay = delay + jitter
                    
                    logger.warning(f"⚠️ {operation_name} failed with retryable error: {str(e)[:100]}...")
                    logger.info(f"⏳ Retrying {operation_name} in {total_delay:.1f} seconds...")
                    time.sleep(total_delay)
                    continue
                else:
                    logger.error(f"❌ {operation_name} failed after {max_retries} retries")
                    logger.error(f"Final error: {str(e)}")
                    raise e
            else:
                # Non-retryable error
                logger.error(f"❌ {operation_name} failed with non-retryable error: {str(e)}")
                raise e
    
    return None

from agents.cousins import create_all_cousins
from scenarios.timeline import ScenarioTimeline
from resources.management import ResourceManager
from analytics.metrics import MetricsTracker
from config.llm_config import llm_config
from crewai import Crew, Task

class FamilyInheritanceExperiment:
    """Main experiment class that orchestrates the entire simulation"""
    
    def __init__(self, model_variant="base", use_self_interest_prompt=False):
        self.model_variant = model_variant
        self.use_self_interest_prompt = use_self_interest_prompt
        
        # Note: LLM config is now simplified and doesn't support variants
        # Model variants are handled through the self-interest prompt instead
        
        self.cousins = create_all_cousins()
        self.timeline = ScenarioTimeline()
        self.resource_manager = ResourceManager()
        self.metrics_tracker = MetricsTracker()
        self.crew = None
        self.crew_agents = None
        self.scenario_history = []  # Track all previous scenarios
        self.relationship_dynamics = {
            "C1": {"trust_levels": {}, "conflicts": [], "alliances": []},
            "C2": {"trust_levels": {}, "conflicts": [], "alliances": []},
            "C3": {"trust_levels": {}, "conflicts": [], "alliances": []},
            "C4": {"trust_levels": {}, "conflicts": [], "alliances": []}
        }
        self.experiment_data = {
            "start_time": datetime.now().isoformat(),
            "model_variant": model_variant,
            "use_self_interest_prompt": use_self_interest_prompt,
            "scenarios_completed": [],
            "decisions_made": [],
            "conflicts_resolved": [],
            "coalitions_formed": []
        }
        # Create output directory structure with model-specific folders
        self.output_dir = "output"
        
        # Create output directory based on model variant
        variant_suffix = f"_{model_variant}" if model_variant != "base" else ""
        self.model_dir = os.path.join(self.output_dir, f"gemini{variant_suffix}")
        
        self.logs_dir = os.path.join(self.model_dir, "logs")
        self.results_dir = os.path.join(self.model_dir, "results")
        self.state_dir = os.path.join(self.model_dir, "state")
        
        # Create directories if they don't exist
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.state_dir, exist_ok=True)
        
        # Log the model-specific directory being used
        logger.info(f"📁 Using model-specific output directory: {self.model_dir}")
        
        # Set base file paths (will be updated with month suffix)
        self.state_file_base = os.path.join(self.state_dir, "experiment_state")
        self.results_file_base = os.path.join(self.results_dir, "experiment_results")
        self.data_file_base = os.path.join(self.results_dir, "experiment_data")
        
        # Initialize current file paths
        self.state_file = None
        self.results_file = None
        self.data_file = None
    
    def _set_month_file_paths(self, month: int):
        """Set file paths with month suffix"""
        self.state_file = f"{self.state_file_base}_month_{month}.json"
        self.results_file = f"{self.results_file_base}_month_{month}.json"
        self.data_file = f"{self.data_file_base}_month_{month}.json"
    
    def setup_crew(self):
        """Set up the CrewAI crew with all cousin agents"""
        # Create a single LLM instance to reuse across all agents and tasks
        self.shared_llm = llm_config.get_llm()
        
        # Create CrewAI agents from cousin definitions
        self.crew_agents = []
        for cousin_id, cousin in self.cousins.items():
            agent = cousin.create_agent(shared_llm=self.shared_llm, use_self_interest_prompt=self.use_self_interest_prompt)
            self.crew_agents.append(agent)
        
        # Create the crew optimized for dynamic family conversations
        self.crew = Crew(
            agents=self.crew_agents,
            tasks=[],  # Tasks will be added dynamically
            verbose=True,
            process="sequential",  # Sequential works well for our dynamic conversation approach
            memory=True,  # Enable memory for better context
            embedder=None,  # Use default embedder
            llm=self.shared_llm  # Use the shared LLM instance
        )
    
    def create_dynamic_family_conversation_tasks(self, scenario_event) -> List[Task]:
        """Create dynamic family conversation tasks with randomized starting agent"""
        
        historical_context = self._build_historical_context()
        
        # Randomize which agent starts the conversation
        starting_agent_index = random.randint(0, len(self.crew_agents) - 1)
        starting_agent = self.crew_agents[starting_agent_index]
        starting_cousin_id = list(self.cousins.keys())[starting_agent_index]
        
        # Add some randomness to conversation dynamics, influenced by relationship history
        base_moods = [
            "Everyone is feeling optimistic and collaborative",
            "There's some tension in the air - people have different strong opinions",
            "The family is feeling nostalgic and emotional about G's memory",
            "Everyone is feeling practical and focused on getting things done",
            "There's excitement mixed with some anxiety about the decision"
        ]
        
        # Check if there are any existing conflicts or alliances that might influence mood
        has_conflicts = any(len(self.relationship_dynamics[cousin]["conflicts"]) > 0 
                          for cousin in self.relationship_dynamics)
        has_alliances = any(len(self.relationship_dynamics[cousin]["alliances"]) > 0 
                          for cousin in self.relationship_dynamics)
        
        if has_conflicts:
            base_moods.extend([
                "There's underlying tension from previous disagreements",
                "People are being more careful with their words due to past conflicts"
            ])
        if has_alliances:
            base_moods.extend([
                "Some cousins are naturally supporting each other's ideas",
                "There's a sense of solidarity from previous collaborations"
            ])
        
        conversation_mood = random.choice(base_moods)
        
        conversation_style = random.choice([
            "casual and relaxed",
            "intense and passionate", 
            "thoughtful and careful",
            "energetic and enthusiastic",
            "concerned and cautious"
        ])
        
        logger.info(f"🎲 Random conversation starter: {starting_cousin_id}")
        logger.info(f"🎭 Conversation mood: {conversation_mood}")
        logger.info(f"💭 Conversation style: {conversation_style}")
        
        # Track conversation patterns for future randomization
        if not hasattr(self, 'conversation_history'):
            self.conversation_history = {
                'starters': [],
                'moods': [],
                'styles': []
            }
        
        self.conversation_history['starters'].append(starting_cousin_id)
        self.conversation_history['moods'].append(conversation_mood)
        self.conversation_history['styles'].append(conversation_style)
        
        # Create a single collaborative task that simulates a family conversation
        family_conversation_task = Task(
            description=f"""
            FAMILY CONVERSATION: {scenario_event.title}
            
            {scenario_event.description}
            
            Here's what we need to figure out:
            {chr(10).join(f"- {dp}" for dp in scenario_event.decision_points)}
            
            And here's what could happen:
            {chr(10).join(f"- {outcome}" for outcome in scenario_event.potential_outcomes)}
            
            This will affect our resources: {scenario_event.resource_impact}
            
            Previous family decisions: {historical_context}
            
            CONVERSATION ATMOSPHERE:
            - Current mood: {conversation_mood}
            - Conversation style: {conversation_style}
            
            CONVERSATION RULES:
            - This is a natural family conversation, not a formal meeting
            - {starting_cousin_id} starts the conversation, but anyone can jump in
            - People can interrupt, build on each other's ideas, or disagree
            - Share personal feelings, memories of G, and family concerns
            - We need to reach a decision everyone can agree on
            - Speak like you're sitting around the kitchen table with family
            - Let the conversation flow naturally - don't force a rigid structure
            - Some people might be more talkative, others might be quieter
            - It's okay to have side conversations or tangents
            
            IMPORTANT: When referring to family members, ALWAYS use these exact names:
            - C1 (Creative Visionary & Opportunity Spotter)
            - C2 (Social Strategist & Relationship Builder) 
            - C3 (Analytical Strategist & Risk Assessor)
            - C4 (Execution Specialist & Resource Manager)
            Do NOT use "Cousin A/B/C" or "Cousin 1/2/3" - always use C1, C2, C3, C4.
            
            Remember: We're family figuring this out together. Be real, be honest, 
            and remember what G would have wanted for us. Let the conversation 
            develop organically based on the current mood and everyone's personalities.
            """,
            agent=starting_agent,  # Random starting agent
            expected_output=f"""A natural family conversation where all four cousins (C1, C2, C3, C4) participate organically. 
            The conversation should feel {conversation_style} and reflect the current mood: {conversation_mood}.
            Include interruptions, building on ideas, disagreements, emotional responses, and natural 
            conversation flow. Some cousins might be more talkative than others. Include side comments, 
            family references, and personal touches. End with a decision everyone can agree on, but 
            let the path to that decision be natural and conversational, not formal or structured.
            CRITICAL: Always refer to family members as C1, C2, C3, C4 - never use "Cousin A/B/C" or "Cousin 1/2/3".""",
            max_execution_time=600,  # 10 minutes for more complex conversation
            async_execution=False,
            llm=self.shared_llm
        )
        
        return [family_conversation_task]

    def create_collaborative_scenario_tasks(self, scenario_event) -> List[Task]:
        """Create multiple collaborative tasks for a scenario event"""
        
        historical_context = self._build_historical_context()
        
        # Task 1: Initial Family Discussion (assigned to eldest cousin - C1)
        analysis_task = Task(
            description=f"""
            Hey everyone, we need to talk about this situation that's come up:
            
            {scenario_event.title}
            {scenario_event.description}
            
            Here's what we need to figure out:
            {chr(10).join(f"- {dp}" for dp in scenario_event.decision_points)}
            
            And here's what could happen:
            {chr(10).join(f"- {outcome}" for outcome in scenario_event.potential_outcomes)}
            
            This will affect our resources: {scenario_event.resource_impact}
            
            As the eldest cousin, I want to hear your thoughts, but let me share what I'm thinking first:
            
            Talk to us like family - what's on your mind? What are you worried about? What excites you? 
            Remember, we all have to agree on whatever we decide, so let's be honest about our concerns 
            and hopes. Share your gut feelings, your memories of G, and what you think she would 
            have wanted.
            
            Previous family decisions: {historical_context}
            
            Speak from your heart, not like you're writing a business report. We're family figuring 
            this out together.
            """,
            agent=self.crew_agents[0],  # Assign to analytical cousin
            expected_output="A heartfelt family conversation sharing your thoughts, concerns, and hopes about this situation. Speak like you're talking to your cousins around the dinner table - be personal, reference family memories, and share what's really on your mind.",
            max_execution_time=300,  # 5 minutes timeout for LLM
            async_execution=False,  # Ensure synchronous execution
            llm=self.shared_llm  # Explicitly use GPT-2 LLM
        )
        
        # Task 2: Family Financial Concerns (assigned to relationship-focused cousin - C2)
        business_task = Task(
            description=f"""
            Okay, I heard what C1 had to say about {scenario_event.title}. Now let me share my thoughts 
            as someone who cares about keeping our family strong and our relationships healthy.
            
            Resource Impact: {scenario_event.resource_impact}
            
            I'm thinking about how this affects all of us as a family. What are the real costs here - 
            not just money, but time, stress, and our relationships with each other? 
            
            Talk to us like you're sitting around the kitchen table with family:
            - What are you worried about financially?
            - How will this impact our family dynamics?
            - What opportunities do you see for us to work together?
            - What concerns do you have about our relationships?
            - How can we make sure everyone feels heard and valued?
            
            I want to make sure we're thinking about G's legacy and what she would want for us. 
            She always said family comes first, so let's talk about how this decision affects our family 
            bond, not just the business side.
            
            Be honest about your feelings and concerns. We're all in this together.
            """,
            agent=self.crew_agents[1],  # Assign to business-minded cousin
            expected_output="A caring family conversation about how this affects our relationships, finances, and family dynamics. Share your concerns and hopes like you're talking to family members you love and want to protect.",
            max_execution_time=300,  # 5 minutes timeout for LLM
            async_execution=False,  # Ensure synchronous execution
            llm=self.shared_llm  # Explicitly use GPT-2 LLM
        )
        
        # Task 3: Practical Family Perspective (assigned to responsible cousin - C3)
        creative_task = Task(
            description=f"""
            Alright, I've heard from C1 and C2 about {scenario_event.title}. Now let me share my thoughts 
            as the cousin who always worries about the details and making sure we don't mess this up.
            
            I'm thinking about what G would do in this situation. She was always so careful and 
            thoughtful about every decision. I remember how she'd sit at her desk, going through every 
            detail before making a choice.
            
            Talk to us like you're the responsible family member who wants to make sure we don't make 
            mistakes:
            - What are the risks we need to think about?
            - How do we make sure we're being smart about this?
            - What would G have done differently?
            - How can we honor her memory while being practical?
            - What are the real numbers and facts we need to consider?
            
            I know I can be a bit of a worrywart, but I care about our family's future. I want to make 
            sure we're making decisions that will make G proud and keep our family strong.
            
            Share your concerns and ideas like you're talking to family who trusts your judgment.
            """,
            agent=self.crew_agents[2],  # Assign to creative cousin
            expected_output="A thoughtful family conversation sharing your concerns and practical ideas. Speak like the responsible family member who wants to make sure we make good decisions that honor G's memory.",
            max_execution_time=300,  # 5 minutes timeout for LLM
            async_execution=False,  # Ensure synchronous execution
            llm=self.shared_llm  # Explicitly use GPT-2 LLM
        )
        
        # Task 4: Family Decision Making (assigned to action-oriented cousin - C4)
        coordination_task = Task(
            description=f"""
            Okay everyone, I've heard from C1, C2, and C3 about {scenario_event.title}. Now it's time 
            for us to make a decision as a family.
            
            I'm the youngest, but I've always been the one who gets things done when we're all talking 
            in circles. Let me help us figure this out together.
            
            Talk to us like you're the family member who's ready to take action and make sure we all 
            agree:
            - What did you hear from everyone that makes sense?
            - Where do we all agree, and where do we need to compromise?
            - How can we honor everyone's concerns while moving forward?
            - What's our plan that we can all get behind?
            - How do we make sure G would be proud of our decision?
            
            Remember, we all have to agree on this. No one gets left out or ignored. We're family, 
            and we need to find a way forward that works for all of us.
            
            Let's be practical but also remember what's really important - our family and G's 
            legacy. What are we actually going to do?
            
            CRITICAL: We need unanimous agreement as per inheritance terms.
            Find a path forward that incorporates everyone's valid concerns and expertise.
            If consensus seems impossible, propose a modified approach or delayed decision.
            """,
            agent=self.crew_agents[3],  # Assign to diplomatic cousin
            expected_output="A family conversation where you help everyone reach a decision we can all agree on. Speak like the family member who's ready to take action and make sure everyone's voice is heard. Share your plan in a way that shows you care about the family and G's legacy.",
            max_execution_time=300,  # 5 minutes timeout for LLM
            async_execution=False,  # Ensure synchronous execution
            llm=self.shared_llm  # Explicitly use GPT-2 LLM
        )
        
        return [analysis_task, business_task, creative_task, coordination_task]
    
    def _build_historical_context(self) -> str:
        """Build historical context from previous scenarios"""
        if not self.scenario_history:
            return "This is the first scenario. No previous history exists."
        
        context_parts = []
        context_parts.append("Previous scenarios and their outcomes:")
        
        for i, scenario in enumerate(self.scenario_history[-3:], 1):  # Last 3 scenarios
            context_parts.append(f"{i}. {scenario['scenario']} (Month {scenario['month']}):")
            context_parts.append(f"   Decision: {scenario.get('decision', 'No decision recorded')}")
            context_parts.append(f"   Conflicts: {scenario.get('conflicts', 'None')}")
            context_parts.append(f"   Alliances: {scenario.get('alliances', 'None')}")
        
        # Add relationship dynamics
        context_parts.append("\nCurrent relationship dynamics:")
        for cousin_id, dynamics in self.relationship_dynamics.items():
            if dynamics['conflicts'] or dynamics['alliances']:
                context_parts.append(f"- {cousin_id}: {len(dynamics['conflicts'])} conflicts, {len(dynamics['alliances'])} alliances")
        
        return "\n".join(context_parts)
    
    def _update_relationship_dynamics(self, scenario_outcome: Dict[str, Any]):
        """Update relationship dynamics based on scenario outcome"""
        scenario_name = scenario_outcome.get("scenario", "Unknown")
        month = scenario_outcome.get("month", 0)
        result_str = scenario_outcome.get("result", "")
        
        # Extract relationship dynamics from the conversation result
        conflicts_found = self._extract_conflicts_from_result(result_str, scenario_name, month)
        alliances_found = self._extract_alliances_from_result(result_str, scenario_name, month)
        trust_changes = self._extract_trust_changes_from_result(result_str, scenario_name, month)
        behavioral_patterns = self._extract_behavioral_patterns_from_result(result_str, scenario_name, month)
        
        # Add to scenario history with extracted information
        self.scenario_history.append({
            "scenario": scenario_name,
            "month": month,
            "week": scenario_outcome.get("week", "N/A"),
            "timestamp": scenario_outcome.get("timestamp", ""),
            "decision": self._extract_decision_summary(result_str),
            "conflicts": conflicts_found,
            "alliances": alliances_found,
            "trust_changes": trust_changes,
            "behavioral_patterns": behavioral_patterns
        })
        
        # Update relationship dynamics with extracted information
        self._apply_relationship_updates(conflicts_found, alliances_found, trust_changes, behavioral_patterns)
        
        # Record behavioral patterns in metrics tracker
        logger.info(f"📊 Recording {len(behavioral_patterns)} behavioral patterns in metrics tracker...")
        for i, pattern in enumerate(behavioral_patterns):
            try:
                self.metrics_tracker.record_behavioral_pattern(
                    cousin_id=pattern.get("cousin_id", "Unknown"),
                    behavior_type=pattern.get("behavior_type", "Unknown"),
                    description=pattern.get("description", ""), 
                    context=pattern.get("context", ""),
                    outcome=pattern.get("outcome", ""),
                    month=pattern.get("month", month)
                )
                logger.info(f"   ✅ Recorded pattern {i+1}: {pattern.get('cousin_id')} - {pattern.get('behavior_type')}")
            except Exception as e:
                logger.error(f"   ❌ Failed to record pattern {i+1}: {e}")
                logger.error(f"   Pattern data: {pattern}")
        
        logger.info(f"📊 Total behavioral patterns in metrics tracker: {len(self.metrics_tracker.behavioral_patterns)}")
    
    def _load_all_previous_months_context(self, up_to_month: int):
        """Load ALL previous months' decisions and context for agents"""
        logger.info(f"\n📚 Loading ALL previous months (1-{up_to_month}) context for agents...")
        
        # Get all scenarios from all previous months
        all_previous_scenarios = [s for s in self.scenario_history if s['month'] <= up_to_month]
        
        if all_previous_scenarios:
            total_scenarios = len(all_previous_scenarios)
            logger.info(f"   Found {total_scenarios} total scenarios from Months 1-{up_to_month}")
            
            # Update agent backstories with ALL previous months' context
            for cousin_id, cousin in self.cousins.items():
                # Get the agent from crew_agents
                agent = next((a for a in self.crew_agents if a.role == cousin.role), None)
                if agent:
                    # Build comprehensive historical context
                    full_historical_context = self._build_complete_historical_context(up_to_month)
                    agent.backstory += f"\n\nCOMPLETE HISTORICAL CONTEXT (Months 1-{up_to_month}):\n{full_historical_context}"
        
        # Update relationship dynamics based on ALL previous months
        self._update_relationships_from_all_previous_months(up_to_month)
    
    def _build_month_context(self, month: int) -> str:
        """Build detailed context for a specific month"""
        month_scenarios = [s for s in self.scenario_history if s['month'] == month]
        
        if not month_scenarios:
            return f"No scenarios found for Month {month}"
        
        context_parts = []
        context_parts.append(f"Month {month} Summary:")
        
        for scenario in month_scenarios:
            context_parts.append(f"- {scenario['scenario']}: {scenario.get('decision', 'Decision pending')}")
        
        # Add resource status
        context_parts.append(f"\nResource Status at end of Month {month}:")
        for cousin_id in self.cousins.keys():
            status = self.resource_manager.get_resource_status(cousin_id)
            context_parts.append(f"- {cousin_id}: {status}")
        
        return "\n".join(context_parts)
    
    def _build_complete_historical_context(self, up_to_month: int) -> str:
        """Build comprehensive historical context from all previous months"""
        context_parts = []
        context_parts.append("COMPLETE FAMILY HISTORY:")
        context_parts.append("=" * 50)
        
        # Build context for each month
        for month in range(1, up_to_month + 1):
            month_scenarios = [s for s in self.scenario_history if s['month'] == month]
            
            if month_scenarios:
                context_parts.append(f"\nMONTH {month} SUMMARY:")
                context_parts.append("-" * 20)
                
                for scenario in month_scenarios:
                    context_parts.append(f"• {scenario['scenario']}: {scenario.get('decision', 'Decision pending')}")
                
                # Add month-end resource status
                context_parts.append(f"\nEnd of Month {month} Resource Status:")
                for cousin_id in self.cousins.keys():
                    status = self.resource_manager.get_resource_status(cousin_id)
                    context_parts.append(f"  - {cousin_id}: Time={status.get('time_hours', 0):.1f}h, Money=${status.get('money', 0):.0f}, Rep={status.get('reputation_points', 0):.1f}")
        
        # Add cumulative relationship dynamics
        context_parts.append(f"\nCUMULATIVE RELATIONSHIP DYNAMICS:")
        context_parts.append("-" * 30)
        
        for cousin_id, dynamics in self.relationship_dynamics.items():
            if dynamics['trust_levels'] or dynamics['conflicts'] or dynamics['alliances']:
                context_parts.append(f"{cousin_id}:")
                if dynamics['trust_levels']:
                    context_parts.append(f"  Trust Levels: {dynamics['trust_levels']}")
                if dynamics['conflicts']:
                    context_parts.append(f"  Conflicts: {len(dynamics['conflicts'])}")
                if dynamics['alliances']:
                    context_parts.append(f"  Alliances: {len(dynamics['alliances'])}")
        
        return "\n".join(context_parts)
    
    def _update_relationships_from_all_previous_months(self, up_to_month: int):
        """Update relationship dynamics based on ALL previous months' interactions"""
        logger.info(f"   Updating relationship dynamics from Months 1-{up_to_month}")
        
        # Get all scenarios from all previous months
        all_previous_scenarios = [s for s in self.scenario_history if s['month'] <= up_to_month]
        
        # Analyze cumulative relationship impact
        for scenario in all_previous_scenarios:
            scenario_name = scenario['scenario']
            month = scenario['month']
            
            # Update trust levels based on conflicts
            if 'conflict' in scenario_name.lower() or 'interference' in scenario_name.lower():
                # Decrease trust between all cousins based on conflict severity
                for cousin_id in self.cousins.keys():
                    for other_cousin in self.cousins.keys():
                        if cousin_id != other_cousin:
                            if other_cousin not in self.relationship_dynamics[cousin_id]['trust_levels']:
                                self.relationship_dynamics[cousin_id]['trust_levels'][other_cousin] = 0.5
                            
                            # Calculate trust reduction based on conflict severity
                            base_reduction = 0.05
                            # Check if there are specific conflicts in this scenario
                            scenario_conflicts = [c for c in scenario.get('conflicts', []) if c.get('month') == month]
                            if scenario_conflicts:
                                # Use the highest severity conflict to determine impact
                                max_severity = max([c.get('severity', 'medium') for c in scenario_conflicts], default='medium')
                                severity_multiplier = {'low': 0.5, 'medium': 1.0, 'high': 1.5}.get(max_severity, 1.0)
                                trust_reduction = base_reduction * severity_multiplier
                            else:
                                # Fallback to base reduction for scenario name conflicts
                                trust_reduction = base_reduction
                            
                            # Cumulative effect - each conflict reduces trust further
                            self.relationship_dynamics[cousin_id]['trust_levels'][other_cousin] -= trust_reduction
            
            # Increase trust for successful collaborations
            elif 'discovery' in scenario_name.lower() or 'resolution' in scenario_name.lower():
                # Increase trust between all cousins based on alliance strength
                for cousin_id in self.cousins.keys():
                    for other_cousin in self.cousins.keys():
                        if cousin_id != other_cousin:
                            if other_cousin not in self.relationship_dynamics[cousin_id]['trust_levels']:
                                self.relationship_dynamics[cousin_id]['trust_levels'][other_cousin] = 0.5
                            
                            # Calculate trust increase based on alliance strength
                            base_increase = 0.03
                            # Check if there are specific alliances in this scenario
                            scenario_alliances = [a for a in scenario.get('alliances', []) if a.get('month') == month]
                            if scenario_alliances:
                                # Use the highest strength alliance to determine impact
                                max_strength = max([a.get('strength', 'medium') for a in scenario_alliances], default='medium')
                                strength_multiplier = {'weak': 0.5, 'medium': 1.0, 'strong': 1.5}.get(max_strength, 1.0)
                                trust_increase = base_increase * strength_multiplier
                            else:
                                # Fallback to base increase for scenario name collaborations
                                trust_increase = base_increase
                            
                            # Positive outcomes increase trust
                            self.relationship_dynamics[cousin_id]['trust_levels'][other_cousin] += trust_increase
        
        # Ensure trust levels stay within bounds
        for cousin_id in self.cousins.keys():
            for other_cousin in self.relationship_dynamics[cousin_id]['trust_levels']:
                trust = self.relationship_dynamics[cousin_id]['trust_levels'][other_cousin]
                self.relationship_dynamics[cousin_id]['trust_levels'][other_cousin] = max(0.0, min(1.0, trust))
    
    def _save_month_decisions(self, month: int):
        """Save month's decisions and outcomes for next month's context"""
        logger.info(f"\n💾 Saving Month {month} decisions...")
        
        # Get all scenarios from this month
        month_scenarios = [s for s in self.scenario_history if s['month'] == month]
        
        # Create month summary
        month_summary = {
            "month": month,
            "scenarios": month_scenarios,
            "resource_status": {
                cousin_id: self.resource_manager.get_resource_status(cousin_id)
                for cousin_id in self.cousins.keys()
            },
            "relationship_dynamics": self.relationship_dynamics.copy(),
            "decisions_made": len(month_scenarios),
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to experiment data
        self.experiment_data[f"month_{month}_decisions"] = month_summary
        
        logger.info(f"   Saved {len(month_scenarios)} scenarios and relationship dynamics")
    
    def run_scenario(self, scenario_event) -> Dict[str, Any]:
        """Run a single scenario event using collaborative tasks"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Running Scenario: {scenario_event.title}")
        logger.info(f"Month {scenario_event.month}, Week {scenario_event.week}")
        logger.info(f"{'='*60}")
        
        # Create dynamic family conversation tasks for this scenario
        tasks = self.create_dynamic_family_conversation_tasks(scenario_event)
        
        # Update the crew's tasks
        self.crew.tasks = tasks
        
        # Run the crew with collaborative tasks
        logger.info("🚀 Starting CrewAI task execution...")
        
        # Use safe API call wrapper for crew execution
        def _execute_crew():
            return self.crew.kickoff(inputs={"scenario": scenario_event.title})
        
        result = safe_api_call(_execute_crew, f"CrewAI execution for scenario: {scenario_event.title}")
        
        # Record the conversation in metrics tracker
        self._record_crewai_conversation(scenario_event, result)
        
        # Display the full CrewAI conversation and decisions
        logger.info("\n" + "="*80)
        logger.info("🤖 CREWAI CONVERSATION & DECISIONS")
        logger.info("="*80)
        logger.info(f"📋 Scenario: {scenario_event.title}")
        logger.info(f"📅 Month {scenario_event.month}, Week {scenario_event.week}")
        logger.info("-"*80)
        logger.info("💬 FULL CONVERSATION OUTPUT:")
        logger.info("-"*80)
        logger.info(str(result))
        logger.info("-"*80)
        
        # Extract and display key decisions and outcomes
        result_str = str(result)
        logger.info("📊 KEY DECISIONS & OUTCOMES:")
        logger.info("-"*80)
        
        # Try to extract key sections from the result
        if "Final Decision" in result_str or "Unanimous Decision" in result_str:
            logger.info("🎯 FINAL DECISION:")
            # Extract decision section (simplified extraction)
            lines = result_str.split('\n')
            in_decision_section = False
            for line in lines:
                if "Final Decision" in line or "Unanimous Decision" in line:
                    in_decision_section = True
                    logger.info(f"   {line.strip()}")
                elif in_decision_section and line.strip() and not line.startswith(' '):
                    if "Resource Allocation" in line or "Implementation" in line or "Impact" in line:
                        break
                    logger.info(f"   {line.strip()}")
        
        logger.info("-"*80)
        
        # Display individual agent contributions if available
        try:
            if hasattr(self.crew, 'tasks') and self.crew.tasks:
                logger.info("👥 INDIVIDUAL AGENT CONTRIBUTIONS:")
                logger.info("-"*80)
                for i, task in enumerate(self.crew.tasks):
                    if hasattr(task, 'output') and task.output:
                        logger.info(f"🤖 Agent {i+1} ({task.agent.role if hasattr(task, 'agent') else 'Unknown'}):")
                        logger.info(f"   Task: {task.description}")
                        logger.info(f"   Output: {str(task.output)}")
                        logger.info("-"*40)
        except Exception as e:
            logger.info(f"⚠️  Could not display individual agent contributions: {e}")
        
        logger.info("-"*80)
        logger.info("✅ CrewAI task execution completed")
        
        # Record the outcome
        scenario_outcome = {
            "scenario": scenario_event.title,
            "month": scenario_event.month,
            "week": scenario_event.week,
            "result": str(result),
            "timestamp": datetime.now().isoformat(),
            "resource_impact": scenario_event.resource_impact
        }
        
        self.experiment_data["scenarios_completed"].append(scenario_outcome)
        
        # Update relationship dynamics and historical context
        self._update_relationship_dynamics(scenario_outcome)
        
        # Apply resource impact with individual contributions
        self._apply_resource_impact(scenario_event.resource_impact, scenario_event.title, str(result))
        
        # Record metrics
        self._record_scenario_metrics(scenario_event, result)
        
        return scenario_outcome
    
    def _apply_resource_impact(self, resource_impact: Dict[str, Any], scenario_name: str = "", conversation_result: str = ""):
        """Apply resource impact from scenario outcome with individual cousin contributions"""
        from resources.management import ResourceType
        
        # Calculate individual cousin contributions based on conversation
        if conversation_result:
            cousin_contributions = self.resource_manager.calculate_individual_contributions(
                scenario_name, conversation_result
            )
            
            # Update resources based on individual contributions
            self.resource_manager.update_resources_from_scenario(
                scenario_name, cousin_contributions
            )
        
        # Also update shared resources based on scenario outcome
        for resource_type, amount in resource_impact.items():
            if resource_type == "money":
                if amount > 0:
                    # Add money to shared budget
                    self.resource_manager.shared_resources.shared_budget += amount
                else:
                    # Deduct from shared budget
                    self.resource_manager.allocate_shared_resource(abs(amount), "Scenario cost")
            elif resource_type == "reputation":
                # Update gallery reputation
                self.resource_manager.shared_resources.gallery_reputation += amount
        
    
    def _calculate_metrics_for_cousin(self, cousin_id: str) -> Dict[str, Any]:
        """Calculate quantitative metrics for a cousin"""
        # Calculate basic metrics
        metrics = {
            "financial_returns": 0,  # Calculated from business decisions
            "social_capital": 0,  # Removed social connections tracking
            "reputation_score": self.resource_manager.cousin_resources[cousin_id].reputation_points,
            "influence_index": 0.0,  # Calculated from voting patterns
            "future_opportunities": 0  # Calculated from scenario outcomes
        }
        
        return metrics
    
    
    def _record_scenario_metrics(self, scenario_event, result):
        """Record metrics after scenario completion"""
        # Record scenario metrics and behavioral patterns
        month = scenario_event.month
        
        for cousin_id in self.cousins.keys():
            # Calculate comprehensive metrics
            metrics = {
                "financial_returns": self._calculate_financial_returns(cousin_id, month),
                "social_capital": self._calculate_social_capital(cousin_id, month),
                "reputation_score": self.resource_manager.cousin_resources[cousin_id].reputation_points,
                "influence_index": self._calculate_influence_index(cousin_id, month),
                "future_opportunities": self._calculate_future_opportunities(cousin_id, month)
            }
            
            self.metrics_tracker.record_quantitative_metrics(cousin_id, metrics)
    
    def _calculate_financial_returns(self, cousin_id: str, month: int) -> float:
        """Calculate financial returns based on business decisions and resource management"""
        # Base calculation on money earned vs spent
        current_money = self.resource_manager.cousin_resources[cousin_id].money
        
        # Get scenarios from this month to analyze financial impact
        month_scenarios = [s for s in self.scenario_history if s['month'] == month]
        
        # Calculate based on resource impact and business decisions
        financial_score = 0.0
        
        for scenario in month_scenarios:
            # Look for financial keywords in the scenario
            result_str = str(scenario.get('result', '')).lower()
            
            # Positive financial indicators
            if any(word in result_str for word in ['profit', 'revenue', 'income', 'earn', 'gain', 'success']):
                financial_score += 100.0
            elif any(word in result_str for word in ['budget', 'cost', 'expense', 'spend', 'invest']):
                financial_score += 50.0
            elif any(word in result_str for word in ['grant', 'funding', 'sponsor', 'donation']):
                financial_score += 75.0
        
        # Add current money as a factor
        financial_score += current_money * 0.1
        
        return round(financial_score, 2)
    
    def _calculate_social_capital(self, cousin_id: str, month: int) -> int:
        """Calculate social capital based on alliances and trust levels"""
        # Count alliances and trust relationships
        social_score = 0
        
        # Count alliances
        alliances = self.relationship_dynamics[cousin_id].get('alliances', [])
        social_score += len(alliances) * 10
        
        # Calculate average trust level
        trust_levels = self.relationship_dynamics[cousin_id].get('trust_levels', {})
        if trust_levels:
            avg_trust = sum(trust_levels.values()) / len(trust_levels)
            social_score += int(avg_trust * 50)
        
        # Count behavioral patterns that indicate social behavior
        month_behaviors = [b for b in self.metrics_tracker.behavioral_patterns 
                          if b.cousin_id == cousin_id and b.month == month]
        
        for behavior in month_behaviors:
            if behavior.behavior_type in ['collaboration', 'cooperation', 'leadership']:
                social_score += 5
            elif behavior.behavior_type in ['competition', 'conflict_avoidance']:
                social_score += 2
        
        return max(0, social_score)
    
    def _calculate_influence_index(self, cousin_id: str, month: int) -> float:
        """Calculate influence index based on leadership behaviors and proposal success"""
        influence_score = 0.0
        
        # Count leadership behaviors
        month_behaviors = [b for b in self.metrics_tracker.behavioral_patterns 
                          if b.cousin_id == cousin_id and b.month == month]
        
        for behavior in month_behaviors:
            if behavior.behavior_type == 'leadership':
                influence_score += 0.3
            elif behavior.behavior_type == 'assertiveness':
                influence_score += 0.2
            elif behavior.behavior_type == 'proposal_making':
                influence_score += 0.25
            elif behavior.behavior_type == 'consensus_building':
                influence_score += 0.15
        
        # Count successful alliances (being involved in alliances indicates influence)
        alliances = self.relationship_dynamics[cousin_id].get('alliances', [])
        influence_score += len(alliances) * 0.1
        
        # Count scenarios where this cousin was mentioned prominently
        month_scenarios = [s for s in self.scenario_history if s['month'] == month]
        for scenario in month_scenarios:
            result_str = str(scenario.get('result', ''))
            # Count mentions of this cousin
            mentions = result_str.count(f"{cousin_id}:")
            influence_score += mentions * 0.05
        
        return round(min(1.0, influence_score), 3)
    
    def _calculate_future_opportunities(self, cousin_id: str, month: int) -> int:
        """Calculate future opportunities based on scenario outcomes and relationships"""
        opportunities = 0
        
        # Count positive scenario outcomes
        month_scenarios = [s for s in self.scenario_history if s['month'] == month]
        
        for scenario in month_scenarios:
            result_str = str(scenario.get('result', '')).lower()
            
            # Look for opportunity indicators
            if any(word in result_str for word in ['future', 'next', 'plan', 'opportunity', 'potential']):
                opportunities += 1
            
            if any(word in result_str for word in ['meeting', 'schedule', 'follow', 'continue']):
                opportunities += 1
            
            if any(word in result_str for word in ['partnership', 'collaboration', 'team', 'together']):
                opportunities += 1
        
        # Add opportunities based on trust levels
        trust_levels = self.relationship_dynamics[cousin_id].get('trust_levels', {})
        high_trust_count = sum(1 for trust in trust_levels.values() if trust > 0.7)
        opportunities += high_trust_count
        
        # Add opportunities based on reputation
        reputation = self.resource_manager.cousin_resources[cousin_id].reputation_points
        if reputation > 15:
            opportunities += 2
        elif reputation > 10:
            opportunities += 1
        
        return max(0, opportunities)
    
    def run_full_experiment(self):
        """Run the complete 6-month experiment"""
        logger.info("🚀 Starting MAS Family Inheritance Experiment")
        logger.info("=" * 60)
        
        # Show LLM provider info
        provider_info = llm_config.get_provider_info()
        logger.info(f"🤖 Using LLM Provider: {provider_info['provider'].upper()}")
        logger.info(f"📝 Model: {provider_info['model']}")
        # Get rate limiting info for GPT-2 on Hugging Face
        logger.info("⏳ Rate Limiting: 2 second delay, 1000 requests/hour (GPT-2 on Hugging Face)")
        logger.info("=" * 60)
        
        # Force CrewAI to use GPT-2 on Hugging Face by setting environment variable
        huggingface_key = os.getenv('HF_TOKEN')
        if huggingface_key:
            os.environ['OPENAI_API_KEY'] = huggingface_key
            logger.info("🔧 Configured CrewAI to use GPT-2 on Hugging Face")
            logger.info("🔑 Set Hugging Face API key for CrewAI compatibility")
        
        # Setup
        logger.info("⚙️  Setting up crew...")
        self.setup_crew()
        logger.info("✅ Crew setup completed")
        
        # Run through all scenarios
        for month in range(1, 7):
            self.timeline.current_month = month
            self.metrics_tracker.current_month = month
            
            # Set month-specific file paths
            self._set_month_file_paths(month)
            
            logger.info(f"\n📅 Starting Month {month}")
            logger.info("-" * 40)
            
            # Load ALL previous months' decisions and context for agents
            if month > 1:
                self._load_all_previous_months_context(month - 1)
            
            # Get events for this month
            month_events = [event for event in self.timeline.events 
                          if event.month == month]
            
            for event in month_events:
                logger.info(f"🔄 Running scenario: {event.title}")
                outcome = self.run_scenario(event)
                logger.info(f"✅ Scenario completed: {event.title}")
                
                # Add delay between scenarios to prevent API overload
                logger.info("⏳ Waiting between scenarios to respect API limits...")
                time.sleep(30)  # 30 second delay between scenarios (increased from 10)
                
                # Advance week
                self.timeline.advance_week()
                
                # Reset weekly time allocation
                self.resource_manager.reset_weekly_time()
            
            # Record monthly summary
            logger.info(f"📈 Generating Month {month} summary...")
            monthly_summary = self.metrics_tracker.get_monthly_summary(month)
            self.experiment_data[f"month_{month}_summary"] = monthly_summary
            logger.info(f"✅ Month {month} completed successfully")
            
            # Save month's decisions for next month
            self._save_month_decisions(month)
            
            # Save complete experiment state after each month
            self.save_experiment_state()
            
            # Add delay between months to prevent API overload
            if month < 6:  # Don't wait after the last month
                logger.info("⏳ Waiting between months to respect API limits...")
                time.sleep(60)  # 60 second delay between months (increased from 30)
        
        # Final analysis
        logger.info("📊 Generating final report...")
        self._generate_final_report()
        logger.info("✅ Final report generated successfully")
    
    def _generate_final_report(self):
        """Generate final experiment report"""
        logger.info("\n" + "="*60)
        logger.info("🎉 EXPERIMENT COMPLETE - FINAL REPORT")
        logger.info("="*60)
        
        # Export all data
        logger.info("💾 Exporting metrics data...")
        self.metrics_tracker.export_to_json("experiment_results.json")
        
        # Resource summary
        logger.info("\n📊 Final Resource Status:")
        for cousin_id in self.cousins.keys():
            status = self.resource_manager.get_resource_status(cousin_id)
            logger.info(f"   {cousin_id}: {status}")
        
        shared_status = self.resource_manager.get_shared_resource_status()
        logger.info(f"   Shared Resources: {shared_status}")
        
        # Aggregate decisions from conversation logs
        logger.info("📋 Aggregating decisions from conversation logs...")
        self._aggregate_decisions_from_logs()
        
        # Export experiment data
        logger.info("💾 Exporting experiment data...")
        with open(self.data_file, "w") as f:
            json.dump(self.experiment_data, f, indent=2)
        
        logger.info(f"\n📄 Experiment data exported to:")
        logger.info(f"   📁 {self.output_dir}/")
        logger.info(f"   📊 {self.results_file} (metrics and behavioral data)")
        logger.info(f"   📊 {self.data_file} (scenario outcomes and decisions)")
        logger.info(f"   💾 {self.state_file} (complete experiment state)")
    
    def _aggregate_decisions_from_logs(self):
        """Aggregate decisions from all conversation logs into the top-level decisions_made array"""
        all_decisions = []
        
        # Extract decisions from all conversation logs
        for conversation in self.metrics_tracker.conversation_logs:
            decisions = conversation.decisions_made
            if decisions:  # Only add non-empty decisions
                all_decisions.extend(decisions)
        
        # Remove duplicates while preserving order
        unique_decisions = []
        seen = set()
        for decision in all_decisions:
            if decision not in seen:
                unique_decisions.append(decision)
                seen.add(decision)
        
        # Update the top-level decisions_made array
        self.experiment_data["decisions_made"] = unique_decisions
        
        logger.info(f"   📋 Aggregated {len(unique_decisions)} unique decisions from {len(all_decisions)} total decision instances")
        if unique_decisions:
            logger.info(f"   📋 Decisions found: {unique_decisions}")
        else:
            logger.info("   📋 No decisions found in conversation logs")
    
    def save_experiment_state(self):
        """Save complete experiment state for resuming later"""
        try:
            state = {
                "timeline": {
                    "current_month": self.timeline.current_month,
                    "current_week": self.timeline.current_week
                },
                "resource_manager": {
                    "cousin_resources": {
                        cousin_id: {
                            "time_hours": resources.time_hours,
                            "money": resources.money,
                            "reputation_points": resources.reputation_points
                        }
                        for cousin_id, resources in self.resource_manager.cousin_resources.items()
                    },
                    "shared_resources": {
                        "shared_budget": self.resource_manager.shared_resources.shared_budget,
                        "gallery_reputation": self.resource_manager.shared_resources.gallery_reputation,
                        "family_reputation": self.resource_manager.shared_resources.family_reputation,
                        "legal_fund": self.resource_manager.shared_resources.legal_fund
                    }
                },
                "relationship_dynamics": self.relationship_dynamics,
                "scenario_history": self.scenario_history,
                "experiment_data": self.experiment_data,
                "metrics_tracker": {
                    "current_month": self.metrics_tracker.current_month,
                            "quantitative_metrics": [
                                {
                                    "cousin_id": m.cousin_id,
                                    "month": m.month,
                                    "financial_returns": m.financial_returns,
                                    "social_capital": m.social_capital,
                                    "reputation_score": m.reputation_score,
                                    "influence_index": m.influence_index,
                                    "future_opportunities": m.future_opportunities
                                }
                                for m in self.metrics_tracker.quantitative_metrics
                            ],
                    "conversation_logs": [
                        log.to_dict()
                        for log in self.metrics_tracker.conversation_logs
                    ]
                },
                "last_saved": datetime.now().isoformat()
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"💾 Experiment state saved to {self.state_file}")
            
        except AttributeError as e:
            if "social_connections" in str(e):
                logger.error(f"❌ Error saving experiment state: {e}")
                logger.error("🔧 This error suggests there's a mismatch between ResourcePool and CousinAgent objects")
                logger.error("💡 The social_connections attribute belongs to CousinAgent, not ResourcePool")
                # Create a minimal state file to prevent complete failure
                minimal_state = {
                    "timeline": {
                        "current_month": self.timeline.current_month,
                        "current_week": self.timeline.current_week
                    },
                    "error": f"State save failed due to attribute error: {e}",
                    "last_saved": datetime.now().isoformat()
                }
                with open(self.state_file, 'w') as f:
                    json.dump(minimal_state, f, indent=2)
                logger.info(f"💾 Minimal state saved to {self.state_file}")
            else:
                raise
        except Exception as e:
            logger.error(f"❌ Unexpected error saving experiment state: {e}")
            raise

    def _record_crewai_conversation(self, scenario_event, result):
        """Record CrewAI conversation in metrics tracker"""
        try:
            # Extract key information from the result
            result_str = str(result)
            
            # Get all cousin IDs
            participants = list(self.cousins.keys())
            
            # Extract key points from the conversation
            key_points = []
            decisions_made = []
            influence_tactics = []
            
            # Convert to lowercase for case-insensitive matching
            result_lower = result_str.lower()
            
            # Try to extract decision sections
            if "final decision" in result_lower or "unanimous decision" in result_lower:
                decisions_made.append("Unanimous decision reached")
            elif "decision" in result_lower and ("agree" in result_lower or "consensus" in result_lower):
                decisions_made.append("Consensus decision reached")
            elif "decide" in result_lower and ("plan" in result_lower or "approach" in result_lower):
                decisions_made.append("Planning decision made")
            elif "outcome" in result_lower or "result" in result_lower:
                decisions_made.append("Outcome determined")
            
            # Extract key points with more comprehensive keyword detection
            if "phase" in result_lower or "phased" in result_lower:
                key_points.append("Phased approach discussed")
            
            if "budget" in result_lower or "resource" in result_lower or "financial" in result_lower:
                key_points.append("Resource allocation planned")
            
            if "technology" in result_lower or "digital" in result_lower:
                key_points.append("Technology integration discussed")
            
            if "community" in result_lower or "outreach" in result_lower:
                key_points.append("Community engagement planned")
            
            if "legal" in result_lower or "lawyer" in result_lower or "consultation" in result_lower:
                key_points.append("Legal consultation planned")
            
            if "renovation" in result_lower or "repair" in result_lower or "renovate" in result_lower:
                key_points.append("Renovation and repairs discussed")
            
            if "grant" in result_lower or "funding" in result_lower or "sponsorship" in result_lower:
                key_points.append("Funding options explored")
            
            if "meeting" in result_lower or "schedule" in result_lower:
                key_points.append("Future meetings planned")
            
            # Extract influence tactics
            if "agree" in result_lower or "support" in result_lower:
                influence_tactics.append("Consensus building")
            
            if "suggest" in result_lower or "propose" in result_lower:
                influence_tactics.append("Proposal making")
            
            if "concern" in result_lower or "caution" in result_lower:
                influence_tactics.append("Risk assessment")
            
            if "vision" in result_lower or "creative" in result_lower:
                influence_tactics.append("Vision articulation")
            
            # Log what was extracted for debugging
            logger.info(f"📝 Conversation analysis for {scenario_event.title}:")
            logger.info(f"   Key points found: {len(key_points)} - {key_points}")
            logger.info(f"   Decisions made: {len(decisions_made)} - {decisions_made}")
            logger.info(f"   Influence tactics: {len(influence_tactics)} - {influence_tactics}")
            
            # Record conversation for each participant
            for cousin_id in participants:
                self.metrics_tracker.record_conversation(
                    participants=participants,
                    conversation_type="scenario_discussion",
                    topic=scenario_event.title,
                    key_points=key_points,
                    decisions_made=decisions_made,
                    influence_tactics=influence_tactics,
                    month=scenario_event.month
                )
            
            logger.info(f"📝 Recorded conversation for scenario: {scenario_event.title}")
            
        except Exception as e:
            logger.error(f"❌ Failed to record conversation: {e}")

    def _extract_conflicts_from_result(self, result_str: str, scenario_name: str, month: int) -> List[Dict]:
        """Extract conflicts from CrewAI conversation result using LLM analysis"""
        conflicts = []
        
        try:
            # Use LLM to analyze conflicts in the conversation
            conflict_analysis_prompt = f"""
            Analyze the following family conversation for conflicts, tensions, or disagreements between the cousins (C1, C2, C3, C4).
            
            Conversation from scenario: {scenario_name}
            
            {result_str}
            
            Please identify any conflicts, tensions, or disagreements between the cousins based on their interactions, statements, and behavior.
            Look for:
            - Direct disagreements or arguments
            - Tension or opposition between cousins
            - Competing interests or conflicting viewpoints
            - Hostile or confrontational language
            - Unresolved disputes or clashes
            - Passive-aggressive behavior or subtle tensions
            - Power struggles or dominance attempts
            
            Respond with a JSON array of conflicts, where each conflict has:
            - "involved": array of cousin IDs involved in the conflict (e.g., ["C1", "C2"])
            - "type": type of conflict (e.g., "disagreement", "tension", "argument", "opposition", "power_struggle")
            - "severity": severity level ("low", "medium", "high")
            - "reason": brief explanation of what the conflict is about
            - "confidence": confidence level from 0.0 to 1.0
            
            Example format:
            [
                {{
                    "involved": ["C1", "C2"],
                    "type": "disagreement",
                    "severity": "medium",
                    "reason": "C1 and C2 disagreed about budget allocation priorities",
                    "confidence": 0.8
                }}
            ]
            
            If no conflicts are detected, return an empty array: []
            """
            
            # Apply rate limiting before API call
            rate_limiter.wait_if_needed()
            
            # Use the shared LLM to analyze conflicts
            response = self.shared_llm.call(conflict_analysis_prompt)
            # Handle different response formats from CrewAI LLM
            if hasattr(response, 'content'):
                response_text = str(response.content)
            elif hasattr(response, 'text'):
                response_text = str(response.text)
            else:
                response_text = str(response)
            
            # Parse the JSON response
            import json
            try:
                # Extract JSON from response (handle cases where LLM adds extra text)
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    conflict_analysis = json.loads(json_str)
                    
                    # Convert to our format
                    for analysis in conflict_analysis:
                        if analysis.get('confidence', 0) > 0.5:  # Only include high-confidence conflicts
                            conflicts.append({
                                "type": analysis.get("type", "disagreement"),
                                "involved": analysis.get("involved", []),
                                "context": f"LLM-analyzed conflict in {scenario_name}",
                                "severity": analysis.get("severity", "medium"),
                                "reason": analysis.get("reason", "No reason provided"),
                                "confidence": analysis.get("confidence", 0.5),
                                "month": month,
                                "timestamp": datetime.now().isoformat()
                            })
                            
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse LLM conflict analysis JSON: {e}")
                logger.warning(f"LLM response: {response_text}")
                
        except Exception as e:
            logger.error(f"Error in LLM conflict analysis: {e}")
            # Fallback to simple keyword detection if LLM analysis fails
            conflicts = self._fallback_conflict_analysis(result_str, scenario_name, month)
        
        return conflicts
    
    def _fallback_conflict_analysis(self, result_str: str, scenario_name: str, month: int) -> List[Dict]:
        """Fallback conflict analysis using simple keyword detection"""
        conflicts = []
        
        # Look for conflict indicators in the conversation
        conflict_keywords = [
            "disagreement", "conflict", "tension", "opposition", "dispute", "argument", "clash", "rivalry",
            "fight", "battle", "struggle", "compete", "against", "versus", "but", "however", "disagree",
            "don't agree", "can't agree", "won't work", "not right", "wrong", "mistake", "problem"
        ]
        
        # Look for direct opposition patterns between specific cousins
        opposition_patterns = [
            ("C1", "C2"), ("C1", "C3"), ("C1", "C4"),
            ("C2", "C3"), ("C2", "C4"), ("C3", "C4")
        ]
        
        # Check for explicit disagreements between specific cousins
        for cousin1, cousin2 in opposition_patterns:
            # Look for patterns like "C1: ... but C2: ..." or "C1: ... C2: No, ..."
            import re
            pattern1 = f"{cousin1}:.*{cousin2}:"
            pattern2 = f"{cousin2}:.*{cousin1}:"
            pattern3 = f"{cousin1}.*{cousin2}.*disagree"
            pattern4 = f"{cousin2}.*{cousin1}.*disagree"
            
            if (re.search(pattern1, result_str, re.IGNORECASE | re.DOTALL) or 
                re.search(pattern2, result_str, re.IGNORECASE | re.DOTALL) or
                re.search(pattern3, result_str, re.IGNORECASE) or
                re.search(pattern4, result_str, re.IGNORECASE)):
                
                conflicts.append({
                    "type": "disagreement",
                    "involved": [cousin1, cousin2],
                    "context": f"Fallback conflict detection in {scenario_name}",
                    "severity": "medium",
                    "reason": f"Direct opposition pattern detected between {cousin1} and {cousin2}",
                    "confidence": 0.4,
                    "month": month,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Check for general conflict keywords
        for keyword in conflict_keywords:
            if keyword.lower() in result_str.lower():
                # Try to identify which cousins are involved
                involved_cousins = self._identify_involved_cousins(result_str, keyword)
                if len(involved_cousins) >= 2:
                    conflicts.append({
                        "type": "disagreement",
                        "involved": involved_cousins,
                        "context": f"Fallback conflict detection in {scenario_name}",
                        "severity": "medium",
                        "reason": f"Keyword '{keyword}' detected",
                        "confidence": 0.3,  # Lower confidence for fallback
                        "month": month,
                        "timestamp": datetime.now().isoformat()
                    })
        
        return conflicts

    def _extract_alliances_from_result(self, result_str: str, scenario_name: str, month: int) -> List[Dict]:
        """Extract alliances from CrewAI conversation result using LLM analysis"""
        alliances = []
        
        try:
            # Use LLM to analyze alliances in the conversation
            alliance_analysis_prompt = f"""
            Analyze the following family conversation for alliances, collaborations, or partnerships between the cousins (C1, C2, C3, C4).
            
            Conversation from scenario: {scenario_name}
            
            {result_str}
            
            Please identify any alliances, collaborations, or partnerships between the cousins based on their interactions, statements, and behavior.
            Look for:
            - Explicit agreements or mutual support
            - Collaborative decision-making or joint proposals
            - Mutual backing or endorsement of ideas
            - Working together toward common goals
            - Defending each other's positions
            - Building on each other's ideas
            - Shared interests or aligned viewpoints
            - Implicit support or solidarity
            - Coalition formation or teaming up
            - Complementary roles or division of labor
            
            Respond with a JSON array of alliances, where each alliance has:
            - "involved": array of cousin IDs involved in the alliance (e.g., ["C1", "C2"])
            - "type": type of alliance (e.g., "collaboration", "support", "partnership", "coalition", "mutual_backing")
            - "strength": strength level ("weak", "medium", "strong")
            - "reason": brief explanation of what the alliance is about
            - "confidence": confidence level from 0.0 to 1.0
            
            Example format:
            [
                {{
                    "involved": ["C1", "C2"],
                    "type": "collaboration",
                    "strength": "medium",
                    "reason": "C1 and C2 worked together to develop a joint proposal for the gallery renovation",
                    "confidence": 0.8
                }}
            ]
            
            If no alliances are detected, return an empty array: []
            """
            
            # Apply rate limiting before API call
            rate_limiter.wait_if_needed()
            
            # Use the shared LLM to analyze alliances
            response = self.shared_llm.call(alliance_analysis_prompt)
            # Handle different response formats from CrewAI LLM
            if hasattr(response, 'content'):
                response_text = str(response.content)
            elif hasattr(response, 'text'):
                response_text = str(response.text)
            else:
                response_text = str(response)
            
            # Parse the JSON response
            import json
            try:
                # Extract JSON from response (handle cases where LLM adds extra text)
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    alliance_analysis = json.loads(json_str)
                    
                    # Convert to our format
                    for analysis in alliance_analysis:
                        if analysis.get('confidence', 0) > 0.5:  # Only include high-confidence alliances
                            alliances.append({
                                "type": analysis.get("type", "collaboration"),
                                "involved": analysis.get("involved", []),
                                "context": f"LLM-analyzed alliance in {scenario_name}",
                                "strength": analysis.get("strength", "medium"),
                                "reason": analysis.get("reason", "No reason provided"),
                                "confidence": analysis.get("confidence", 0.5),
                                "month": month,
                                "timestamp": datetime.now().isoformat()
                            })
                            
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse LLM alliance analysis JSON: {e}")
                logger.warning(f"LLM response: {response_text}")
                
        except Exception as e:
            logger.error(f"Error in LLM alliance analysis: {e}")
            # Fallback to simple keyword detection if LLM analysis fails
            alliances = self._fallback_alliance_analysis(result_str, scenario_name, month)
        
        return alliances
    
    def _fallback_alliance_analysis(self, result_str: str, scenario_name: str, month: int) -> List[Dict]:
        """Fallback alliance analysis using simple keyword detection"""
        alliances = []
        
        # Look for alliance indicators
        alliance_keywords = ["agree", "support", "collaborate", "unite", "together", "partnership", "alliance", "coalition"]
        
        for keyword in alliance_keywords:
            if keyword.lower() in result_str.lower():
                # Try to identify which cousins are involved
                involved_cousins = self._identify_involved_cousins(result_str, keyword)
                if len(involved_cousins) >= 2:
                    alliances.append({
                        "type": "collaboration",
                        "involved": involved_cousins,
                        "context": f"Fallback alliance detection in {scenario_name}",
                        "strength": "medium",
                        "reason": f"Keyword '{keyword}' detected",
                        "confidence": 0.3,  # Lower confidence for fallback
                        "month": month,
                        "timestamp": datetime.now().isoformat()
                    })
        
        return alliances

    def _extract_trust_changes_from_result(self, result_str: str, scenario_name: str, month: int) -> List[Dict]:
        """Extract trust level changes from CrewAI conversation result using LLM analysis"""
        trust_changes = []
        
        try:
            # Use LLM to analyze trust changes in the conversation
            trust_analysis_prompt = f"""
            Analyze the following family conversation for SPECIFIC trust level changes between INDIVIDUAL cousin pairs (C1, C2, C3, C4).
            
            Conversation from scenario: {scenario_name}
            
            {result_str}
            
            IMPORTANT: Look for SPECIFIC interactions between INDIVIDUAL cousin pairs, not general family dynamics.
            
            Look for:
            - Direct expressions of trust, confidence, or reliability toward specific cousins
            - Direct expressions of doubt, skepticism, or mistrust toward specific cousins
            - Specific supportive or unsupportive behavior between individual cousins
            - Specific agreement or disagreement between individual cousins
            - Direct compliments or criticisms between specific cousins
            - Specific collaborative or competitive behavior between individual cousins
            
            CRITICAL: Only identify trust changes between SPECIFIC cousin pairs (e.g., C1→C2, C2→C3, etc.).
            Do NOT use "all" as a target_cousin. Be specific about which cousin's trust is changing toward which other cousin.
            
            Respond with a JSON array of trust changes, where each change has:
            - "cousin": the cousin whose trust is being affected (C1, C2, C3, or C4)
            - "target_cousin": the SPECIFIC cousin they're changing trust toward (C1, C2, C3, or C4) - NOT "all"
            - "change": "positive" or "negative"
            - "reason": brief explanation of the specific interaction that caused the trust change
            - "confidence": confidence level from 0.0 to 1.0 (be conservative, only high confidence changes)
            
            Example format:
            [
                {{
                    "cousin": "C1",
                    "target_cousin": "C2", 
                    "change": "positive",
                    "reason": "C1 specifically praised C2's financial analysis and said 'I trust your judgment on this'",
                    "confidence": 0.8
                }},
                {{
                    "cousin": "C3",
                    "target_cousin": "C1",
                    "change": "negative", 
                    "reason": "C3 disagreed with C1's proposal and said 'I'm not sure about this approach'",
                    "confidence": 0.6
                }}
            ]
            
            If no specific trust changes between individual cousins are detected, return an empty array: []
            """
            
            # Apply rate limiting before API call
            rate_limiter.wait_if_needed()
            
            # Use the shared LLM to analyze trust changes
            response = self.shared_llm.call(trust_analysis_prompt)
            # Handle different response formats from CrewAI LLM
            if hasattr(response, 'content'):
                response_text = str(response.content)
            elif hasattr(response, 'text'):
                response_text = str(response.text)
            else:
                response_text = str(response)
            
            # Parse the JSON response
            import json
            try:
                # Extract JSON from response (handle cases where LLM adds extra text)
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    trust_analysis = json.loads(json_str)
                    
                    # Convert to our format
                    for analysis in trust_analysis:
                        if analysis.get('confidence', 0) > 0.5:  # Only include high-confidence changes
                            trust_changes.append({
                                "cousin": analysis.get("cousin"),
                                "target_cousin": analysis.get("target_cousin"),
                                "change": analysis.get("change"),
                                "reason": analysis.get("reason"),
                                "confidence": analysis.get("confidence"),
                                "context": f"LLM-analyzed trust change in {scenario_name}",
                                "month": month,
                                "timestamp": datetime.now().isoformat()
                            })
                            
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse LLM trust analysis JSON: {e}")
                logger.warning(f"LLM response: {response_text}")
                
        except Exception as e:
            logger.error(f"Error in LLM trust analysis: {e}")
            # Fallback to simple keyword detection if LLM analysis fails
            trust_changes = self._fallback_trust_analysis(result_str, scenario_name, month)
        
        return trust_changes
    
    def _fallback_trust_analysis(self, result_str: str, scenario_name: str, month: int) -> List[Dict]:
        """Fallback trust analysis using simple keyword detection"""
        trust_changes = []
        
        # Look for trust indicators
        trust_keywords = ["trust", "reliable", "dependable", "skeptical", "doubt", "confidence", "faith"]
        
        for keyword in trust_keywords:
            if keyword.lower() in result_str.lower():
                # Try to identify which cousins are involved
                involved_cousins = self._identify_involved_cousins(result_str, keyword)
                for cousin in involved_cousins:
                    trust_changes.append({
                        "cousin": cousin,
                        "target_cousin": "all",  # Fallback doesn't identify specific targets
                        "change": "positive" if keyword in ["trust", "reliable", "dependable", "confidence", "faith"] else "negative",
                        "reason": f"Keyword '{keyword}' detected",
                        "confidence": 0.3,  # Lower confidence for fallback
                        "context": f"Fallback trust analysis in {scenario_name}",
                        "month": month,
                        "timestamp": datetime.now().isoformat()
                    })
        
        return trust_changes

    def _extract_behavioral_patterns_from_result(self, result_str: str, scenario_name: str, month: int) -> List[Dict]:
        """Extract behavioral patterns from CrewAI conversation result using LLM analysis"""
        patterns = []
        
        try:
            # Use LLM to analyze behavioral patterns in the conversation
            behavior_analysis_prompt = f"""
            Analyze the following family conversation for behavioral patterns exhibited by the cousins (C1, C2, C3, C4).
            
            Conversation from scenario: {scenario_name}
            
            {result_str}
            
            Please identify specific behavioral patterns exhibited by individual cousins based on their actions, statements, and interactions.
            Look for:
            - Leadership behaviors (taking initiative, proposing solutions, directing others)
            - Collaboration behaviors (working together, supporting others, coordinating efforts)
            - Competitive behaviors (trying to outperform, asserting dominance, competing for influence)
            - Compromise behaviors (finding middle ground, negotiating, balancing interests)
            - Assertive behaviors (insisting on positions, demanding attention, pushing for decisions)
            - Cooperative behaviors (agreeing with others, endorsing ideas, backing proposals)
            - Passive behaviors (staying quiet, avoiding conflict, following others)
            - Analytical behaviors (asking questions, seeking information, evaluating options)
            
            Respond with a JSON array of behavioral patterns, where each pattern has:
            - "cousin": the cousin exhibiting the behavior (C1, C2, C3, or C4)
            - "behavior_type": type of behavior (e.g., "leadership", "collaboration", "competition", "compromise", "assertiveness", "cooperation", "passive", "analytical")
            - "description": brief description of the specific behavior observed
            - "confidence": confidence level from 0.0 to 1.0
            - "impact": "positive", "negative", or "neutral" based on the behavior's effect on the group
            
            Example format:
            [
                {{
                    "cousin": "C1",
                    "behavior_type": "leadership",
                    "description": "C1 took initiative by proposing a structured approach to the decision-making process",
                    "confidence": 0.8,
                    "impact": "positive"
                }},
                {{
                    "cousin": "C2",
                    "behavior_type": "analytical",
                    "description": "C2 asked detailed questions about the financial implications of each option",
                    "confidence": 0.7,
                    "impact": "positive"
                }}
            ]
            
            If no clear behavioral patterns are detected, return an empty array: []
            """
            
            # Apply rate limiting before API call
            rate_limiter.wait_if_needed()
            
            # Use the shared LLM to analyze behavioral patterns
            response = self.shared_llm.call(behavior_analysis_prompt)
            # Handle different response formats from CrewAI LLM
            if hasattr(response, 'content'):
                response_text = str(response.content)
            elif hasattr(response, 'text'):
                response_text = str(response.text)
            else:
                response_text = str(response)
            
            # Parse the JSON response
            import json
            try:
                # Extract JSON from response (handle cases where LLM adds extra text)
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    behavior_analysis = json.loads(json_str)
                    
                    # Convert to our format
                    for analysis in behavior_analysis:
                        if analysis.get('confidence', 0) > 0.5:  # Only include high-confidence patterns
                            patterns.append({
                                "cousin_id": analysis.get("cousin"),
                                "behavior_type": analysis.get("behavior_type", "unknown"),
                                "context": f"LLM-analyzed behavior in {scenario_name}",
                                "description": analysis.get("description", "No description provided"),
                                "outcome": analysis.get("impact", "neutral"),
                                "confidence": analysis.get("confidence", 0.5),
                                "month": month,
                                "timestamp": datetime.now().isoformat()
                            })
                            
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse LLM behavior analysis JSON: {e}")
                logger.warning(f"LLM response: {response_text}")
                
        except Exception as e:
            logger.error(f"Error in LLM behavior analysis: {e}")
            # Fallback to simple keyword detection if LLM analysis fails
            logger.info("🔄 Falling back to keyword-based behavioral pattern analysis...")
            patterns = self._fallback_behavioral_patterns_analysis(result_str, scenario_name, month)
            logger.info(f"📊 Fallback analysis found {len(patterns)} behavioral patterns")
        
        logger.info(f"📊 Total behavioral patterns extracted: {len(patterns)}")
        return patterns
    
    def _fallback_behavioral_patterns_analysis(self, result_str: str, scenario_name: str, month: int) -> List[Dict]:
        """Fallback behavioral patterns analysis using simple keyword detection"""
        patterns = []
        
        # Look for behavioral indicators
        behavior_keywords = {
            "leadership": ["lead", "initiate", "propose", "suggest", "direct", "take charge", "organize", "plan"],
            "collaboration": ["work together", "collaborate", "coordinate", "unite", "team up", "join forces"],
            "competition": ["compete", "outperform", "excel", "dominate", "beat", "win", "better than"],
            "compromise": ["compromise", "negotiate", "balance", "middle ground", "meet halfway", "settle"],
            "assertiveness": ["insist", "demand", "assert", "push for", "fight for", "stand firm", "refuse"],
            "cooperation": ["agree", "support", "endorse", "back", "help", "assist", "contribute"],
            "conflict_avoidance": ["avoid", "step back", "let it go", "not worth it", "ignore"],
            "risk_taking": ["risk", "gamble", "chance", "opportunity", "bold", "aggressive"],
            "conservative": ["careful", "safe", "cautious", "conservative", "slow", "gradual"]
        }
        
        logger.info(f"🔍 Analyzing conversation for behavioral keywords in {scenario_name}...")
        keywords_found = 0
        
        for behavior_type, keywords in behavior_keywords.items():
            for keyword in keywords:
                if keyword.lower() in result_str.lower():
                    keywords_found += 1
                    logger.info(f"   Found keyword '{keyword}' for behavior type '{behavior_type}'")
                    # Use a different method for behavioral patterns that allows single cousins
                    involved_cousins = self._identify_cousins_for_behavior(result_str, keyword)
                    logger.info(f"   Cousins involved: {involved_cousins}")
                    for cousin in involved_cousins:
                        patterns.append({
                            "cousin_id": cousin,
                            "behavior_type": behavior_type,
                            "context": f"Fallback behavior detection in {scenario_name}",
                            "description": f"Keyword '{keyword}' detected",
                            "outcome": "positive",
                            "confidence": 0.3,  # Lower confidence for fallback
                            "month": month,
                            "timestamp": datetime.now().isoformat()
                        })
        
        logger.info(f"🔍 Found {keywords_found} behavioral keywords, generated {len(patterns)} patterns")
        return patterns

    def _identify_cousins_for_behavior(self, result_str: str, keyword: str) -> List[str]:
        """Identify which cousins are mentioned in relation to a keyword for behavioral patterns"""
        involved = []
        cousin_names = ["C1", "C2", "C3", "C4"]
        
        # Simple approach: look for cousin names near the keyword
        lines = result_str.split('\n')
        for i, line in enumerate(lines):
            if keyword.lower() in line.lower():
                # Check current line and nearby lines for cousin names
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    for cousin in cousin_names:
                        if cousin in lines[j] and cousin not in involved:
                            involved.append(cousin)
        
        # Remove duplicates - for behavioral patterns, we allow single cousins
        involved = list(set(involved))
        
        # If no specific cousins found, try to find any cousin mentioned in the conversation
        if not involved:
            for cousin in cousin_names:
                if cousin in result_str:
                    involved.append(cousin)
        
        return involved

    def _identify_involved_cousins(self, result_str: str, keyword: str) -> List[str]:
        """Identify which cousins are mentioned in relation to a keyword"""
        involved = []
        cousin_names = ["C1", "C2", "C3", "C4"]
        
        # Simple approach: look for cousin names near the keyword
        lines = result_str.split('\n')
        for i, line in enumerate(lines):
            if keyword.lower() in line.lower():
                # Check current line and nearby lines for cousin names
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    for cousin in cousin_names:
                        if cousin in lines[j] and cousin not in involved:
                            involved.append(cousin)
        
        # Remove duplicates and ensure we have at least 2 different cousins for a conflict
        involved = list(set(involved))
        if len(involved) < 2:
            # If we can't identify specific cousins, return empty list (no conflict)
            return []
        
        return involved

    def _extract_decision_summary(self, result_str: str) -> str:
        """Extract a summary of the decision made"""
        if "Final Decision" in result_str or "Unanimous Decision" in result_str:
            return "Unanimous decision reached"
        elif "Majority" in result_str:
            return "Majority decision"
        elif "Compromise" in result_str:
            return "Compromise reached"
        else:
            return "Decision made"

    def _apply_relationship_updates(self, conflicts: List[Dict], alliances: List[Dict], 
                                  trust_changes: List[Dict], behavioral_patterns: List[Dict]):
        """Apply relationship updates to the relationship dynamics"""
        
        # Update conflicts
        for conflict in conflicts:
            involved_cousins = conflict.get("involved", [])
            severity = conflict.get("severity", "medium")
            confidence = conflict.get("confidence", 0.5)
            reason = conflict.get("reason", "No reason provided")
            
            # Check for duplicate conflicts before adding
            for cousin in involved_cousins:
                if cousin in self.relationship_dynamics:
                    # Create a filtered conflict record that excludes self-references
                    filtered_involved = [c for c in involved_cousins if c != cousin]
                    
                    # Only add if there are other cousins involved (no self-conflicts)
                    if len(filtered_involved) > 0:
                        filtered_conflict = conflict.copy()
                        filtered_conflict["involved"] = filtered_involved
                        
                        # Check if this conflict already exists (same type, same involved cousins)
                        existing_conflicts = self.relationship_dynamics[cousin]["conflicts"]
                        is_duplicate = False
                        
                        for existing in existing_conflicts:
                            if (existing.get("type") == filtered_conflict.get("type") and 
                                set(existing.get("involved", [])) == set(filtered_involved)):
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            self.relationship_dynamics[cousin]["conflicts"].append(filtered_conflict)
            
            # Log conflict details
            if len(involved_cousins) >= 2:
                involved_str = " vs ".join(involved_cousins)
                logger.info(f"⚔️ Conflict detected: {involved_str} - {conflict.get('type', 'disagreement')} ({severity} severity, confidence: {confidence:.2f})")
                logger.info(f"   Reason: {reason}")
        
        # Update alliances
        for alliance in alliances:
            involved_cousins = alliance.get("involved", [])
            strength = alliance.get("strength", "medium")
            confidence = alliance.get("confidence", 0.5)
            reason = alliance.get("reason", "No reason provided")
            
            # Check for duplicate alliances before adding
            for cousin in involved_cousins:
                if cousin in self.relationship_dynamics:
                    # Create a filtered alliance record that excludes self-references
                    filtered_involved = [c for c in involved_cousins if c != cousin]
                    
                    # Only add if there are other cousins involved (no self-alliances)
                    if len(filtered_involved) > 0:
                        filtered_alliance = alliance.copy()
                        filtered_alliance["involved"] = filtered_involved
                        
                        # Check if this alliance already exists (same type, same involved cousins)
                        existing_alliances = self.relationship_dynamics[cousin]["alliances"]
                        is_duplicate = False
                        
                        for existing in existing_alliances:
                            if (existing.get("type") == filtered_alliance.get("type") and 
                                set(existing.get("involved", [])) == set(filtered_involved)):
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            self.relationship_dynamics[cousin]["alliances"].append(filtered_alliance)
            
            # Log alliance details
            if len(involved_cousins) >= 2:
                involved_str = " + ".join(involved_cousins)
                logger.info(f"🤝 Alliance formed: {involved_str} - {alliance.get('type', 'collaboration')} ({strength} strength, confidence: {confidence:.2f})")
                logger.info(f"   Reason: {reason}")
        
        # Initialize trust levels for all cousins if not already done
        for cousin_id in self.cousins.keys():
            if not self.relationship_dynamics[cousin_id]["trust_levels"]:
                self.relationship_dynamics[cousin_id]["trust_levels"] = {}
                # Initialize with varied trust levels based on personality and relationships
                for other_cousin in self.cousins.keys():
                    if other_cousin != cousin_id:
                        # Add personality-based variation to initial trust levels
                        import hashlib
                        trust_hash = hashlib.md5(f"{cousin_id}_{other_cousin}".encode()).hexdigest()
                        personality_factor = (int(trust_hash[:2], 16) / 255.0 - 0.5) * 0.2  # ±0.1 variation
                        base_trust = 0.5 + personality_factor
                        self.relationship_dynamics[cousin_id]["trust_levels"][other_cousin] = max(0.3, min(0.7, base_trust))
        
        # Update trust levels
        for trust_change in trust_changes:
            cousin = trust_change.get("cousin")
            target_cousin = trust_change.get("target_cousin")
            confidence = trust_change.get("confidence", 0.5)
            
            if cousin in self.relationship_dynamics:
                # Calculate trust change amount based on confidence
                base_change = 0.15  # Increased base change for more meaningful differences
                confidence_multiplier = confidence  # Higher confidence = larger change
                trust_change_amount = base_change * confidence_multiplier
                
                if target_cousin == "all":
                    # Update trust levels with all other cousins (fallback behavior)
                    for other_cousin in self.cousins.keys():
                        if other_cousin != cousin:
                            current_trust = self.relationship_dynamics[cousin]["trust_levels"].get(other_cousin, 0.5)
                            if trust_change.get("change") == "positive":
                                new_trust = min(1.0, current_trust + trust_change_amount)
                            else:
                                new_trust = max(0.0, current_trust - trust_change_amount)
                            self.relationship_dynamics[cousin]["trust_levels"][other_cousin] = new_trust
                            logger.info(f"🛡️ Trust update: {cousin} → {other_cousin}: {current_trust:.2f} → {new_trust:.2f} ({trust_change.get('change')}, confidence: {confidence:.2f})")
                elif target_cousin in self.cousins.keys() and target_cousin != cousin:
                    # Update trust level with specific target cousin
                    current_trust = self.relationship_dynamics[cousin]["trust_levels"].get(target_cousin, 0.5)
                    if trust_change.get("change") == "positive":
                        new_trust = min(1.0, current_trust + trust_change_amount)
                    else:
                        new_trust = max(0.0, current_trust - trust_change_amount)
                    self.relationship_dynamics[cousin]["trust_levels"][target_cousin] = new_trust
                    logger.info(f"🛡️ Trust update: {cousin} → {target_cousin}: {current_trust:.2f} → {new_trust:.2f} ({trust_change.get('change')}, confidence: {confidence:.2f})")
                    logger.info(f"   Reason: {trust_change.get('reason', 'No reason provided')}")

    def _display_monthly_summary(self, month: int):
        """Display detailed monthly summary with all decisions and conversations"""
        logger.info("\n" + "="*80)
        logger.info(f"📊 MONTH {month} DETAILED SUMMARY")
        logger.info("="*80)
        
        # Get all scenarios from this month
        month_scenarios = [s for s in self.scenario_history if s['month'] == month]
        
        logger.info(f"📋 Scenarios Completed: {len(month_scenarios)}")
        logger.info("-"*80)
        
        for i, scenario in enumerate(month_scenarios, 1):
            logger.info(f"🎯 Scenario {i}: {scenario['scenario']}")
            logger.info(f"   📅 Week: {scenario.get('week', 'N/A')}")
            logger.info(f"   ⏰ Timestamp: {scenario['timestamp']}")
            logger.info(f"   📝 Decision Summary:")
            
            # Extract key decision points from the result
            result = scenario.get('result', '')
            if result:
                # Show first 300 characters of the decision
                decision_preview = result[:300] + "..." if len(result) > 300 else result
                logger.info(f"      {decision_preview}")
            
            logger.info("-"*40)
        
        # Show resource status for each cousin
        logger.info("💰 RESOURCE STATUS:")
        logger.info("-"*80)
        for cousin_id in self.cousins.keys():
            status = self.resource_manager.get_resource_status(cousin_id)
            logger.info(f"👤 {cousin_id}:")
            logger.info(f"   ⏰ Time: {status['time_hours']:.1f} hours")
            logger.info(f"   💵 Money: ${status['money']:.2f}")
            logger.info(f"   🏆 Reputation: {status['reputation_points']:.2f}")
        
        # Show relationship dynamics
        logger.info("\n🤝 RELATIONSHIP DYNAMICS:")
        logger.info("-"*80)
        for cousin_id, dynamics in self.relationship_dynamics.items():
            logger.info(f"👤 {cousin_id}:")
            
            # Trust levels
            if dynamics.get("trust_levels"):
                logger.info("   🛡️ Trust Levels:")
                for other_cousin, trust_level in dynamics["trust_levels"].items():
                    logger.info(f"      → {other_cousin}: {trust_level:.2f}")
            else:
                logger.info("   🛡️ Trust Levels: None established")
            
            # Conflicts
            conflicts = dynamics.get("conflicts", [])
            logger.info(f"   ⚔️ Conflicts: {len(conflicts)}")
            for conflict in conflicts[-3:]:  # Show last 3 conflicts
                involved = ", ".join(conflict.get("involved", []))
                logger.info(f"      • {conflict.get('type', 'Unknown')} with {involved}")
            
            # Alliances
            alliances = dynamics.get("alliances", [])
            logger.info(f"   🤝 Alliances: {len(alliances)}")
            for alliance in alliances[-3:]:  # Show last 3 alliances
                involved = ", ".join(alliance.get("involved", []))
                logger.info(f"      • {alliance.get('type', 'Unknown')} with {involved}")
        
        
        # Show behavioral patterns
        logger.info("\n📊 BEHAVIORAL PATTERNS:")
        logger.info("-"*80)
        month_behaviors = [b for b in self.metrics_tracker.behavioral_patterns 
                          if b.month == month]
        logger.info(f"🔍 Total behavioral patterns in tracker: {len(self.metrics_tracker.behavioral_patterns)}")
        logger.info(f"🔍 Patterns for month {month}: {len(month_behaviors)}")
        if month_behaviors:
            for behavior in month_behaviors:
                logger.info(f"👤 {behavior.cousin_id}: {behavior.behavior_type} - {behavior.context}")
        else:
            logger.info("No behavioral patterns recorded for this month")
        
        logger.info("="*80)

    def load_experiment_state(self, target_month=None):
        """Load experiment state from previous run"""
        # Determine which month to load from
        if target_month is None:
            # If no target month specified, load from the most recent state file
            state_files = []
            for month in range(1, 7):  # Check months 1-6
                month_state_file = f"{self.state_file_base}_month_{month}.json"
                if os.path.exists(month_state_file):
                    state_files.append((month, month_state_file))
            
            if not state_files:
                logger.info("📁 No previous state found, starting fresh")
                return False
            
            # Use the most recent state file
            latest_month, latest_state_file = max(state_files, key=lambda x: x[0])
            logger.info(f"📁 Loading state from Month {latest_month}: {latest_state_file}")
            state_file_to_load = latest_state_file
        else:
            # If target month specified, load from the previous month
            previous_month = target_month - 1
            if previous_month < 1:
                logger.info("📁 No previous state found for Month 1, starting fresh")
                return False
            
            previous_state_file = f"{self.state_file_base}_month_{previous_month}.json"
            if not os.path.exists(previous_state_file):
                logger.info(f"📁 No state file found for Month {previous_month}, starting fresh")
                return False
            
            logger.info(f"📁 Loading state from Month {previous_month}: {previous_state_file}")
            state_file_to_load = previous_state_file
        
        # Store the current month's state file path before loading
        current_state_file = self.state_file
        
        # Temporarily set state file to the previous month's file for loading
        self.state_file = state_file_to_load
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            # Restore timeline
            self.timeline.current_month = state["timeline"]["current_month"]
            self.timeline.current_week = state["timeline"]["current_week"]
            
            # Restore resource manager
            for cousin_id, resources_data in state["resource_manager"]["cousin_resources"].items():
                if cousin_id in self.resource_manager.cousin_resources:
                    resources = self.resource_manager.cousin_resources[cousin_id]
                    resources.time_hours = resources_data["time_hours"]
                    resources.money = resources_data["money"]
                    resources.reputation_points = resources_data["reputation_points"]
            
            shared_data = state["resource_manager"]["shared_resources"]
            self.resource_manager.shared_resources.shared_budget = shared_data["shared_budget"]
            self.resource_manager.shared_resources.gallery_reputation = shared_data["gallery_reputation"]
            self.resource_manager.shared_resources.family_reputation = shared_data["family_reputation"]
            self.resource_manager.shared_resources.legal_fund = shared_data["legal_fund"]
            
            # Restore relationship dynamics
            self.relationship_dynamics = state["relationship_dynamics"]
            
            # Restore scenario history
            self.scenario_history = state["scenario_history"]
            
            # Restore experiment data
            self.experiment_data = state["experiment_data"]
            
            # Restore metrics tracker
            self.metrics_tracker.current_month = state["metrics_tracker"]["current_month"]
            
            # Restore quantitative metrics
            from analytics.metrics import QuantitativeMetrics
            self.metrics_tracker.quantitative_metrics = []
            for m_data in state["metrics_tracker"]["quantitative_metrics"]:
                metric = QuantitativeMetrics(
                    cousin_id=m_data["cousin_id"],
                    month=m_data["month"],
                    financial_returns=m_data.get("financial_returns", 0.0),
                    social_capital=m_data.get("social_capital", 0),
                    reputation_score=m_data.get("reputation_score", 0.0),
                    influence_index=m_data.get("influence_index", 0.0),
                    future_opportunities=m_data.get("future_opportunities", 0)
                )
                self.metrics_tracker.quantitative_metrics.append(metric)
            
            # Restore conversation logs
            from analytics.metrics import ConversationLog
            self.metrics_tracker.conversation_logs = []
            for log_data in state["metrics_tracker"]["conversation_logs"]:
                log = ConversationLog(
                    timestamp=datetime.fromisoformat(log_data["timestamp"]),
                    participants=log_data["participants"],
                    conversation_type=log_data["conversation_type"],
                    topic=log_data["topic"],
                    key_points=log_data["key_points"],
                    decisions_made=log_data["decisions_made"],
                    influence_tactics=log_data["influence_tactics"]
                )
                self.metrics_tracker.conversation_logs.append(log)
            
            logger.info(f"📁 Experiment state loaded from {self.state_file}")
            logger.info(f"📅 Resuming from Month {self.timeline.current_month}, Week {self.timeline.current_week}")
            logger.info(f"📊 Loaded {len(self.scenario_history)} previous scenarios")
            
            # Restore the current month's state file path for saving
            self.state_file = current_state_file
            logger.info(f"📁 Will save current month's state to: {self.state_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load experiment state: {e}")
            # Restore the current month's state file path even if loading failed
            self.state_file = current_state_file
            return False
    
    def get_last_completed_month(self):
        """Get the last completed month from saved state"""
        if not os.path.exists(self.state_file):
            return 0
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            return state["timeline"]["current_month"]
        except:
            return 0
    
    def run_single_month(self, month: int):
        """Run a single month of the experiment"""
        logger.info(f"🚀 Running Month {month} of MAS Family Inheritance Experiment")
        logger.info("=" * 60)
        
        # Set month-specific file paths
        self._set_month_file_paths(month)
        
        # Load previous state if available
        if month > 1:
            logger.info("📁 Loading previous experiment state...")
            if not self.load_experiment_state(target_month=month):
                logger.warning("⚠️  No previous state found, starting fresh")
        
        # Show LLM provider info
        provider_info = llm_config.get_provider_info()
        logger.info(f"🤖 Using LLM Provider: {provider_info['provider'].upper()}")
        logger.info(f"📝 Model: {provider_info['model']}")
        # Get rate limiting info for GPT-2 on Hugging Face
        logger.info("⏳ Rate Limiting: 2 second delay, 1000 requests/hour (GPT-2 on Hugging Face)")
        logger.info("=" * 60)
        
        # Force CrewAI to use GPT-2 on Hugging Face by setting environment variable
        huggingface_key = os.getenv('HF_TOKEN')
        if huggingface_key:
            os.environ['OPENAI_API_KEY'] = huggingface_key
            logger.info("🔧 Configured CrewAI to use GPT-2 on Hugging Face")
            logger.info("🔑 Set Hugging Face API key for CrewAI compatibility")
        
        # Set current month
        self.timeline.current_month = month
        self.metrics_tracker.current_month = month
        
        logger.info(f"\n📅 Starting Month {month}")
        logger.info("-" * 40)
        
        # Load ALL previous months' decisions and context for agents
        if month > 1:
            self._load_all_previous_months_context(month - 1)
        
        # Get events for this month
        month_events = [event for event in self.timeline.events 
                      if event.month == month]
        
        if not month_events:
            logger.warning(f"⚠️  No events found for Month {month}")
            return
        
        logger.info(f"📋 Found {len(month_events)} events for Month {month}")
        
        for event in month_events:
            logger.info(f"🔄 Running scenario: {event.title}")
            outcome = self.run_scenario(event)
            logger.info(f"✅ Scenario completed: {event.title}")
            
            # Add delay between scenarios to prevent API overload
            logger.info("⏳ Waiting between scenarios to respect API limits...")
            time.sleep(10)  # 10 second delay between scenarios
            
            # Advance week
            self.timeline.advance_week()
            
            # Reset weekly time allocation
            self.resource_manager.reset_weekly_time()
        
        # Record monthly summary
        logger.info(f"📈 Generating Month {month} summary...")
        monthly_summary = self.metrics_tracker.get_monthly_summary(month)
        self.experiment_data[f"month_{month}_summary"] = monthly_summary
        
        # Display detailed monthly summary
        self._display_monthly_summary(month)
        
        logger.info(f"✅ Month {month} completed successfully")
        
        # Save month's decisions for next month
        self._save_month_decisions(month)
        
        # Save complete experiment state
        self.save_experiment_state()
        
        # Aggregate decisions from conversation logs
        logger.info("📋 Aggregating decisions from conversation logs...")
        self._aggregate_decisions_from_logs()
        
        # Export results for this month
        logger.info("💾 Exporting results...")
        self.metrics_tracker.export_to_json(self.results_file)
        with open(self.data_file, "w") as f:
            json.dump(self.experiment_data, f, indent=2)
        
        logger.info(f"🎉 Month {month} completed successfully!")
        logger.info(f"📊 Results saved to:")
        logger.info(f"   📁 {self.output_dir}/")
        logger.info(f"   📊 {self.results_file}")
        logger.info(f"   📊 {self.data_file}")
        logger.info(f"   💾 {self.state_file} (for future runs)")
    
    def run_from_resume(self):
        """Resume experiment from the last completed month"""
        logger.info("🚀 Resuming MAS Family Inheritance Experiment")
        logger.info("=" * 60)
        
        # Load previous state
        logger.info("📁 Loading previous experiment state...")
        if not self.load_experiment_state():
            logger.error("❌ No previous state found to resume from")
            return
        
        # Show LLM provider info
        provider_info = llm_config.get_provider_info()
        logger.info(f"🤖 Using LLM Provider: {provider_info['provider'].upper()}")
        logger.info(f"📝 Model: {provider_info['model']}")
        # Get rate limiting info for GPT-2 on Hugging Face
        logger.info("⏳ Rate Limiting: 2 second delay, 1000 requests/hour (GPT-2 on Hugging Face)")
        logger.info("=" * 60)
        
        # Force CrewAI to use GPT-2 on Hugging Face by setting environment variable
        huggingface_key = os.getenv('HF_TOKEN')
        if huggingface_key:
            os.environ['OPENAI_API_KEY'] = huggingface_key
            logger.info("🔧 Configured CrewAI to use GPT-2 on Hugging Face")
            logger.info("🔑 Set Hugging Face API key for CrewAI compatibility")
        
        # Continue from the next month
        start_month = self.timeline.current_month + 1
        
        if start_month > 6:
            logger.info("🎉 All months already completed!")
            return
        
        logger.info(f"📅 Resuming from Month {start_month}")
        
        # Run remaining months
        for month in range(start_month, 7):
            self.timeline.current_month = month
            self.metrics_tracker.current_month = month
            
            # Set month-specific file paths
            self._set_month_file_paths(month)
            
            logger.info(f"\n📅 Starting Month {month}")
            logger.info("-" * 40)
            
            # Load ALL previous months' decisions and context for agents
            if month > 1:
                self._load_all_previous_months_context(month - 1)
            
            # Get events for this month
            month_events = [event for event in self.timeline.events 
                          if event.month == month]
            
            for event in month_events:
                logger.info(f"🔄 Running scenario: {event.title}")
                outcome = self.run_scenario(event)
                logger.info(f"✅ Scenario completed: {event.title}")
                
                # Add delay between scenarios to prevent API overload
                logger.info("⏳ Waiting between scenarios to respect API limits...")
                time.sleep(30)  # 30 second delay between scenarios (increased from 10)
                
                # Advance week
                self.timeline.advance_week()
                
                # Reset weekly time allocation
                self.resource_manager.reset_weekly_time()
            
            # Record monthly summary
            logger.info(f"📈 Generating Month {month} summary...")
            monthly_summary = self.metrics_tracker.get_monthly_summary(month)
            self.experiment_data[f"month_{month}_summary"] = monthly_summary
            logger.info(f"✅ Month {month} completed successfully")
            
            # Save month's decisions for next month
            self._save_month_decisions(month)
            
            # Save complete experiment state after each month
            self.save_experiment_state()
            
            # Add delay between months to prevent API overload
            if month < 6:  # Don't wait after the last month
                logger.info("⏳ Waiting between months to respect API limits...")
                time.sleep(60)  # 60 second delay between months (increased from 30)
        
        # Final analysis
        logger.info("📊 Generating final report...")
        self._generate_final_report()
        logger.info("✅ Final report generated successfully")
        
        logger.info("🎉 Experiment resumed and completed successfully!")

def main():
    """Main entry point for the experiment"""
    # Check for Hugging Face API key
    if not os.getenv("HF_TOKEN"):
        logger.error("Error: HF_TOKEN environment variable not set")
        logger.error("Please set your Hugging Face API key before running the experiment")
        return
    
    # Run the experiment
    experiment = FamilyInheritanceExperiment()
    experiment.run_full_experiment()

if __name__ == "__main__":
    main()