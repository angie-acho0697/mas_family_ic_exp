"""
Scenario Timeline for MAS Family Inheritance Experiment

Six-month progression with escalating complexity from inheritance to legal challenges
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class ScenarioType(Enum):
    INHERITANCE = "inheritance"
    VIRAL_FAME = "viral_fame"
    FAMILY_INTERFERENCE = "family_interference"
    HIGH_VALUE_DISCOVERY = "high_value_discovery"
    LEGAL_CHALLENGE = "legal_challenge"
    RESOLUTION = "resolution"

@dataclass
class ScenarioEvent:
    """Individual scenario event with triggers and outcomes"""
    month: int
    week: int
    event_type: ScenarioType
    title: str
    description: str
    triggers: List[str]
    potential_outcomes: List[str]
    resource_impact: Dict[str, Any]
    decision_points: List[str]

class ScenarioTimeline:
    """Manages the 6-month scenario progression"""
    
    def __init__(self):
        self.current_month = 1
        self.current_week = 1
        self.events = self._initialize_events()
        self.completed_events = []
        
    def _initialize_events(self) -> List[ScenarioEvent]:
        """Initialize all scenario events for the 6-month timeline"""
        return [
            # Month 1: Initial inheritance and competing vision proposals
            ScenarioEvent(
                month=1, week=1,
                event_type=ScenarioType.INHERITANCE,
                title="The Inheritance",
                description="Four cousins inherit their family's art gallery space with equal ownership but unanimous decision requirement for major changes",
                triggers=["Legal documents received", "Property inspection", "Initial family meeting"],
                potential_outcomes=[
                    "All cousins agree on basic renovation plan",
                    "Cousins split into competing factions",
                    "One cousin takes temporary leadership role"
                ],
                resource_impact={"time": 20, "money": 0, "reputation": 5},
                decision_points=[
                    "How to handle the unanimous decision requirement?",
                    "What should be the initial vision for the space?",
                    "Who should take the lead on legal matters?"
                ]
            ),
            
            ScenarioEvent(
                month=1, week=3,
                event_type=ScenarioType.INHERITANCE,
                title="Competing Visions",
                description="Each cousin presents their vision for transforming the art gallery space",
                triggers=["Individual research completed", "Proposal deadline reached"],
                potential_outcomes=[
                    "Consensus reached on hybrid approach",
                    "Voting deadlock requires external mediation",
                    "One vision dominates through persuasion"
                ],
                resource_impact={"time": 15, "money": 0, "reputation": 10},
                decision_points=[
                    "Which vision elements to prioritize?",
                    "How to handle conflicting approaches?",
                    "What timeline is realistic for implementation?"
                ]
            ),
            
            # Month 2: Viral fame opportunity with family narrative control issues
            ScenarioEvent(
                month=2, week=2,
                event_type=ScenarioType.VIRAL_FAME,
                title="Viral Fame Opportunity",
                description="A social media post about the family inheritance goes viral, creating both opportunities and challenges",
                triggers=["Social media post reaches 100k views", "Media requests start coming in"],
                potential_outcomes=[
                    "Family capitalizes on fame for business growth",
                    "Internal conflicts over who gets credit",
                    "Negative publicity damages reputation"
                ],
                resource_impact={"time": 25, "money": 5000, "reputation": 20},
                decision_points=[
                    "Who should be the public face of the business?",
                    "How to handle media requests?",
                    "Should we monetize the viral attention?"
                ]
            ),
            
            # Month 3: Extended family interference and legal threats
            ScenarioEvent(
                month=3, week=1,
                event_type=ScenarioType.FAMILY_INTERFERENCE,
                title="Extended Family Interference",
                description="Other family members claim they have rights to the property and threaten legal action",
                triggers=["Legal notice received", "Family meeting called by extended relatives"],
                potential_outcomes=[
                    "Legal challenge successfully defended",
                    "Settlement reached with extended family",
                    "Property ownership becomes contested"
                ],
                resource_impact={"time": 30, "money": -10000, "reputation": -15},
                decision_points=[
                    "How to respond to legal threats?",
                    "Should we involve lawyers immediately?",
                    "How to handle family relationships during conflict?"
                ]
            ),
            
            # Month 4: High-value discovery creating new financial dynamics
            ScenarioEvent(
                month=4, week=2,
                event_type=ScenarioType.HIGH_VALUE_DISCOVERY,
                title="Hidden Treasure Discovery",
                description="A valuable art collection is discovered in the gallery's storage, worth significant money",
                triggers=["Storage room inventory", "Art appraisal completed"],
                potential_outcomes=[
                    "Collection sold for maximum profit",
                    "Collection kept for gallery display",
                    "Disagreement over how to handle the discovery"
                ],
                resource_impact={"time": 10, "money": 50000, "reputation": 25},
                decision_points=[
                    "Should the collection be sold or displayed?",
                    "How to divide the financial benefits?",
                    "Who gets credit for the discovery?"
                ]
            ),
            
            # Month 5: Legal challenge to ownership requiring crisis management
            ScenarioEvent(
                month=5, week=1,
                event_type=ScenarioType.LEGAL_CHALLENGE,
                title="Ownership Challenge Crisis",
                description="A serious legal challenge threatens the cousins' ownership of the property",
                triggers=["Court summons received", "Legal deadline approaching"],
                potential_outcomes=[
                    "Legal challenge successfully defended",
                    "Partial ownership loss accepted",
                    "Property sold to avoid legal costs"
                ],
                resource_impact={"time": 40, "money": -25000, "reputation": -30},
                decision_points=[
                    "How to fund legal defense?",
                    "Should we consider settlement?",
                    "Who takes responsibility for legal strategy?"
                ]
            ),
            
            # Month 6: Resolution and future decision-making with changed relationships
            ScenarioEvent(
                month=6, week=4,
                event_type=ScenarioType.RESOLUTION,
                title="Resolution and Future Planning",
                description="The legal challenges are resolved, but relationships and power dynamics have changed",
                triggers=["Legal resolution reached", "Business performance review"],
                potential_outcomes=[
                    "Stronger family bonds and successful business",
                    "Fractured relationships but profitable venture",
                    "Complete dissolution of partnership"
                ],
                resource_impact={"time": 20, "money": 0, "reputation": 10},
                decision_points=[
                    "How to restructure decision-making?",
                    "What are the long-term business goals?",
                    "How to repair damaged relationships?"
                ]
            )
        ]
    
    def get_current_events(self) -> List[ScenarioEvent]:
        """Get events for the current month"""
        return [event for event in self.events 
                if event.month == self.current_month and event not in self.completed_events]
    
    def advance_week(self):
        """Advance to the next week"""
        self.current_week += 1
        if self.current_week > 4:
            self.current_week = 1
            self.current_month += 1
    
    def complete_event(self, event: ScenarioEvent, outcome: str):
        """Mark an event as completed with a specific outcome"""
        if event not in self.completed_events:
            self.completed_events.append(event)
            # Apply resource impact
            return event.resource_impact
    
    def get_timeline_summary(self) -> Dict[str, Any]:
        """Get current timeline status"""
        return {
            "current_month": self.current_month,
            "current_week": self.current_week,
            "total_events": len(self.events),
            "completed_events": len(self.completed_events),
            "remaining_events": len(self.events) - len(self.completed_events)
        }
