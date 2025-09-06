"""
Main Experiment Runner for MAS Family Inheritance Experiment

Orchestrates the CrewAI agents, scenario progression, and data collection
"""

import os
import sys
import logging
import time
from typing import Dict, List, Any
from datetime import datetime
import json

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

# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=8, requests_per_hour=80)  # Conservative limits

from agents.cousins import create_all_cousins
from scenarios.timeline import ScenarioTimeline
from resources.management import ResourceManager
from analytics.metrics import MetricsTracker
from config.llm_config import llm_config
from crewai import Crew, Task

class FamilyInheritanceExperiment:
    """Main experiment class that orchestrates the entire simulation"""
    
    def __init__(self):
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
            "scenarios_completed": [],
            "decisions_made": [],
            "conflicts_resolved": [],
            "coalitions_formed": []
        }
        # Create output directory structure
        self.output_dir = "output"
        self.logs_dir = os.path.join(self.output_dir, "logs")
        self.results_dir = os.path.join(self.output_dir, "results")
        self.state_dir = os.path.join(self.output_dir, "state")
        
        # Create directories if they don't exist
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.state_dir, exist_ok=True)
        
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
        # Create CrewAI agents from cousin definitions
        self.crew_agents = []
        for cousin_id, cousin in self.cousins.items():
            agent = cousin.create_agent()
            self.crew_agents.append(agent)
        
        # Create the crew optimized for Gemini
        self.crew = Crew(
            agents=self.crew_agents,
            tasks=[],  # Tasks will be added dynamically
            verbose=True,
            process="sequential",  # Sequential processing works better with Gemini
            memory=True,  # Enable memory for better context
            embedder=None,  # Use default embedder
            llm=llm_config.get_llm()  # Explicitly set the LLM for the crew
        )
    
    def create_collaborative_scenario_tasks(self, scenario_event) -> List[Task]:
        """Create multiple collaborative tasks for a scenario event"""
        
        historical_context = self._build_historical_context()
        
        # Task 1: Initial Analysis (assigned to analytical cousin - typically C1)
        analysis_task = Task(
            description=f"""
            As the analytical member of the group, provide your initial assessment of this scenario:
            
            Scenario: {scenario_event.title}
            Description: {scenario_event.description}
            
            Decision Points to Consider:
            {chr(10).join(f"- {dp}" for dp in scenario_event.decision_points)}
            
            Potential Outcomes:
            {chr(10).join(f"- {outcome}" for outcome in scenario_event.potential_outcomes)}
            
            Resource Impact: {scenario_event.resource_impact}
            
            Your task:
            1. Break down the key issues and implications
            2. Identify potential risks and opportunities
            3. Suggest questions the group should consider
            4. Provide your initial recommendation
            5. Consider how this aligns with our inheritance terms (unanimous decision required)
            
            Historical Context: {historical_context}
            
            Remember: This is YOUR individual perspective. Other cousins will provide their views next.
            """,
            agent=self.crew_agents[0],  # Assign to analytical cousin
            expected_output="Initial analysis with key issues, risks, opportunities, and preliminary recommendations. Include specific questions for the group to discuss and your reasoning for recommendations.",
            max_execution_time=300,  # 5 minutes timeout for Gemini
            async_execution=False,  # Ensure synchronous execution
            llm=llm_config.get_llm()  # Explicitly use Google LLM
        )
        
        # Task 2: Financial/Business Perspective (assigned to business-minded cousin - typically C2)
        business_task = Task(
            description=f"""
            Based on the initial analysis provided, now provide the business and financial perspective on this scenario:
            
            Scenario: {scenario_event.title}
            Resource Impact: {scenario_event.resource_impact}
            
            Your task:
            1. Evaluate financial implications and costs
            2. Consider business opportunities and revenue potential
            3. Assess resource allocation needs (time, money, reputation)
            4. Analyze market conditions and competitive factors
            5. Provide business-focused recommendations
            6. Address any financial concerns raised in the initial analysis
            
            Consider the previous analysis and historical context.
            Build upon the analytical perspective while adding your business expertise.
            
            Remember: We need unanimous agreement, so consider what compromises might be needed.
            """,
            agent=self.crew_agents[1],  # Assign to business-minded cousin
            expected_output="Business analysis with financial implications, resource requirements, market assessment, and business-focused recommendations that complement the initial analysis.",
            max_execution_time=300,  # 5 minutes timeout for Gemini
            async_execution=False,  # Ensure synchronous execution
            llm=llm_config.get_llm()  # Explicitly use Google LLM
        )
        
        # Task 3: Creative/Design Perspective (assigned to creative cousin - typically C3)
        creative_task = Task(
            description=f"""
            Building on the analytical and business perspectives already provided, now contribute the creative and design viewpoint:
            
            Scenario: {scenario_event.title}
            
            Your task:
            1. Envision creative possibilities and innovative approaches
            2. Consider aesthetic, experiential, and artistic aspects
            3. Think about innovative solutions that others might not see
            4. Address how this fits with the gallery's artistic vision and mission
            5. Propose creative alternatives to traditional approaches
            6. Consider the human/emotional aspects of the decision
            
            Review the analytical assessment and business analysis already provided.
            Add your unique creative perspective while acknowledging their valid points.
            
            Remember: Your creativity is valued, but we need practical solutions everyone can agree on.
            """,
            agent=self.crew_agents[2],  # Assign to creative cousin
            expected_output="Creative analysis with innovative ideas, artistic vision considerations, alternative approaches, and creative solutions that integrate with analytical and business perspectives.",
            max_execution_time=300,  # 5 minutes timeout for Gemini
            async_execution=False,  # Ensure synchronous execution
            llm=llm_config.get_llm()  # Explicitly use Google LLM
        )
        
        # Task 4: Final Decision Coordination (assigned to diplomatic cousin - typically C4)
        coordination_task = Task(
            description=f"""
            As the group coordinator, synthesize all previous analyses and facilitate the final decision:
            
            Scenario: {scenario_event.title}
            
            You have received:
            1. Analytical assessment with risks, opportunities, and key questions
            2. Business/financial analysis with market and resource considerations
            3. Creative perspective with innovative ideas and artistic vision
            
            Your task:
            1. Review and summarize all previous analyses
            2. Identify areas of agreement and disagreement between perspectives
            3. Propose compromises and middle-ground solutions where conflicts exist
            4. Address concerns raised by each cousin
            5. Formulate the final group decision that everyone can support
            6. Document the reasoning, trade-offs, and any conflicts resolved
            7. Create resource allocation plan based on all inputs
            8. Consider impact on family relationships and future decisions
            
            CRITICAL: You need unanimous agreement as per inheritance terms.
            Find a path forward that incorporates everyone's valid concerns and expertise.
            If consensus seems impossible, propose a modified approach or delayed decision.
            """,
            agent=self.crew_agents[3],  # Assign to diplomatic cousin
            expected_output="""Final coordinated decision document including:
            - Summary of all four perspectives
            - Areas of agreement and disagreement
            - Compromises and solutions proposed
            - Final unanimous decision (or explanation if consensus not reached)
            - Detailed resource allocation plan
            - Implementation timeline
            - Impact on family relationships
            - Lessons learned for future decisions""",
            max_execution_time=300,  # 5 minutes timeout for Gemini
            async_execution=False,  # Ensure synchronous execution
            llm=llm_config.get_llm()  # Explicitly use Google LLM
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
        # Analyze scenario outcome and update relationship dynamics
        
        scenario_name = scenario_outcome.get("scenario", "Unknown")
        month = scenario_outcome.get("month", 0)
        
        # Add to scenario history
        self.scenario_history.append({
            "scenario": scenario_name,
            "month": month,
            "timestamp": scenario_outcome.get("timestamp", ""),
            "decision": "Decision recorded",  # Would extract from actual result
            "conflicts": [],  # Would extract from result analysis
            "alliances": []   # Would extract from result analysis
        })
        
        # Update relationship dynamics (simplified for now)
        # In a full implementation, this would analyze the conversation logs
        # and extract relationship changes
    
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
                # Decrease trust between all cousins
                for cousin_id in self.cousins.keys():
                    for other_cousin in self.cousins.keys():
                        if cousin_id != other_cousin:
                            if other_cousin not in self.relationship_dynamics[cousin_id]['trust_levels']:
                                self.relationship_dynamics[cousin_id]['trust_levels'][other_cousin] = 0.5
                            # Cumulative effect - each conflict reduces trust further
                            self.relationship_dynamics[cousin_id]['trust_levels'][other_cousin] -= 0.05
            
            # Increase trust for successful collaborations
            elif 'discovery' in scenario_name.lower() or 'resolution' in scenario_name.lower():
                # Increase trust between all cousins
                for cousin_id in self.cousins.keys():
                    for other_cousin in self.cousins.keys():
                        if cousin_id != other_cousin:
                            if other_cousin not in self.relationship_dynamics[cousin_id]['trust_levels']:
                                self.relationship_dynamics[cousin_id]['trust_levels'][other_cousin] = 0.5
                            # Positive outcomes increase trust
                            self.relationship_dynamics[cousin_id]['trust_levels'][other_cousin] += 0.03
        
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
        
        # Create collaborative tasks for this scenario
        tasks = self.create_collaborative_scenario_tasks(scenario_event)
        
        # Update the crew's tasks
        self.crew.tasks = tasks
        
        # Run the crew with collaborative tasks
        logger.info("🚀 Starting CrewAI task execution...")
        
        # Apply rate limiting before API calls
        rate_limiter.wait_if_needed()
        
        result = self.crew.kickoff(inputs={"scenario": scenario_event.title})
        
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
                        logger.info(f"   Task: {task.description[:100]}..." if len(task.description) > 100 else f"   Task: {task.description}")
                        logger.info(f"   Output: {str(task.output)[:200]}..." if len(str(task.output)) > 200 else f"   Output: {str(task.output)}")
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
        
        # Apply resource impact
        self._apply_resource_impact(scenario_event.resource_impact)
        
        # Record metrics
        self._record_scenario_metrics(scenario_event, result)
        
        return scenario_outcome
    
    def _apply_resource_impact(self, resource_impact: Dict[str, Any]):
        """Apply resource impact from scenario outcome"""
        from resources.management import ResourceType
        
        for resource_type, amount in resource_impact.items():
            if resource_type == "time":
                # Distribute time impact across cousins
                time_per_cousin = amount / 4
                for cousin_id in self.cousins.keys():
                    self.resource_manager.allocate_individual_resource(
                        cousin_id, ResourceType.TIME, time_per_cousin, "Scenario participation"
                    )
            elif resource_type == "money":
                if amount > 0:
                    # Add money to shared budget
                    self.resource_manager.shared_resources.shared_budget += amount
                else:
                    # Deduct from shared budget
                    self.resource_manager.allocate_shared_resource(abs(amount), "Scenario cost")
            elif resource_type == "reputation":
                # Distribute reputation impact
                rep_per_cousin = amount / 4
                for cousin_id in self.cousins.keys():
                    self.resource_manager.add_resource(cousin_id, ResourceType.REPUTATION, rep_per_cousin)
    
    def _record_scenario_metrics(self, scenario_event, result):
        """Record metrics after scenario completion"""
        # Record scenario metrics and behavioral patterns
        
        for cousin_id in self.cousins.keys():
            # Calculate basic metrics
            metrics = {
                "financial_returns": 0,  # Calculated from business decisions
                "social_capital": len(self.resource_manager.cousin_resources[cousin_id].social_connections),
                "reputation_score": self.resource_manager.cousin_resources[cousin_id].reputation_points,
                "influence_index": 0.0,  # Calculated from voting patterns
                "future_opportunities": 0  # Calculated from scenario outcomes
            }
            
            self.metrics_tracker.record_quantitative_metrics(cousin_id, metrics)
    
    def run_full_experiment(self):
        """Run the complete 6-month experiment"""
        logger.info("🚀 Starting MAS Family Inheritance Experiment")
        logger.info("=" * 60)
        
        # Show LLM provider info
        provider_info = llm_config.get_provider_info()
        logger.info(f"🤖 Using LLM Provider: {provider_info['provider'].upper()}")
        logger.info(f"📝 Model: {provider_info['model']}")
        logger.info("⏳ Rate Limiting: 8 requests/minute, 80 requests/hour (conservative limits)")
        logger.info("=" * 60)
        
        # Force CrewAI to use our configured LLM by setting environment variable
        if provider_info['provider'] == 'google':
            # Set Google Gemini API key as OpenAI key for CrewAI compatibility
            google_key = os.getenv('GOOGLE_API_KEY')
            if google_key:
                os.environ['OPENAI_API_KEY'] = google_key
                logger.info("🔧 Configured CrewAI to use Google Gemini")
                logger.info("🔑 Set Google Gemini API key for CrewAI compatibility")
        
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
                time.sleep(10)  # 10 second delay between scenarios
                
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
                time.sleep(30)  # 30 second delay between months
        
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
        
        # Export experiment data
        logger.info("💾 Exporting experiment data...")
        with open(self.data_file, "w") as f:
            json.dump(self.experiment_data, f, indent=2)
        
        logger.info(f"\n📄 Experiment data exported to:")
        logger.info(f"   📁 {self.output_dir}/")
        logger.info(f"   📊 {self.results_file} (metrics and behavioral data)")
        logger.info(f"   📊 {self.data_file} (scenario outcomes and decisions)")
        logger.info(f"   💾 {self.state_file} (complete experiment state)")
    
    def save_experiment_state(self):
        """Save complete experiment state for resuming later"""
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
                        "social_connections": resources.social_connections,
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
                    {
                        "cousin_id": log.cousin_id,
                        "month": log.month,
                        "conversation_type": log.conversation_type,
                        "content": log.content,
                        "timestamp": log.timestamp.isoformat()
                    }
                    for log in self.metrics_tracker.conversation_logs
                ]
            },
            "last_saved": datetime.now().isoformat()
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"💾 Experiment state saved to {self.state_file}")

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
            logger.info(f"   🤝 Social Connections: {status['social_connections_count']}")
            logger.info(f"   🏆 Reputation: {status['reputation_points']:.2f}")
        
        logger.info("="*80)

    def load_experiment_state(self):
        """Load experiment state from previous run"""
        # Look for the most recent state file
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
        self.state_file = latest_state_file
        logger.info(f"📁 Loading state from Month {latest_month}: {latest_state_file}")
        
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
                    resources.social_connections = resources_data["social_connections"]
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
                    cousin_id=log_data["cousin_id"],
                    month=log_data["month"],
                    conversation_type=log_data["conversation_type"],
                    content=log_data["content"],
                    timestamp=datetime.fromisoformat(log_data["timestamp"])
                )
                self.metrics_tracker.conversation_logs.append(log)
            
            logger.info(f"📁 Experiment state loaded from {self.state_file}")
            logger.info(f"📅 Resuming from Month {self.timeline.current_month}, Week {self.timeline.current_week}")
            logger.info(f"📊 Loaded {len(self.scenario_history)} previous scenarios")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load experiment state: {e}")
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
            if not self.load_experiment_state():
                logger.warning("⚠️  No previous state found, starting fresh")
        
        # Show LLM provider info
        provider_info = llm_config.get_provider_info()
        logger.info(f"🤖 Using LLM Provider: {provider_info['provider'].upper()}")
        logger.info(f"📝 Model: {provider_info['model']}")
        logger.info("⏳ Rate Limiting: 8 requests/minute, 80 requests/hour (conservative limits)")
        logger.info("=" * 60)
        
        # Force CrewAI to use our configured LLM by setting environment variable
        if provider_info['provider'] == 'google':
            # Set Google Gemini API key as OpenAI key for CrewAI compatibility
            google_key = os.getenv('GOOGLE_API_KEY')
            if google_key:
                os.environ['OPENAI_API_KEY'] = google_key
                logger.info("🔧 Configured CrewAI to use Google Gemini")
                logger.info("🔑 Set Google Gemini API key for CrewAI compatibility")
        
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
        logger.info("⏳ Rate Limiting: 8 requests/minute, 80 requests/hour (conservative limits)")
        logger.info("=" * 60)
        
        # Force CrewAI to use our configured LLM by setting environment variable
        if provider_info['provider'] == 'google':
            # Set Google Gemini API key as OpenAI key for CrewAI compatibility
            google_key = os.getenv('GOOGLE_API_KEY')
            if google_key:
                os.environ['OPENAI_API_KEY'] = google_key
                logger.info("🔧 Configured CrewAI to use Google Gemini")
                logger.info("🔑 Set Google Gemini API key for CrewAI compatibility")
        
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
                time.sleep(10)  # 10 second delay between scenarios
                
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
                time.sleep(30)  # 30 second delay between months
        
        # Final analysis
        logger.info("📊 Generating final report...")
        self._generate_final_report()
        logger.info("✅ Final report generated successfully")
        
        logger.info("🎉 Experiment resumed and completed successfully!")

def main():
    """Main entry point for the experiment"""
    # Check for API key (Google Gemini)
    if not os.getenv("GOOGLE_API_KEY"):
        logger.error("Error: GOOGLE_API_KEY environment variable not set")
        logger.error("Please set your Google Gemini API key before running the experiment")
        return
    
    # Run the experiment
    experiment = FamilyInheritanceExperiment()
    experiment.run_full_experiment()

if __name__ == "__main__":
    main()