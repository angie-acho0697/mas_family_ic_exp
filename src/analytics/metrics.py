"""
Data Collection and Metrics Tracking for MAS Family Inheritance Experiment

Tracks quantitative metrics and qualitative behavioral patterns
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import pandas as pd

@dataclass
class QuantitativeMetrics:
    """Monthly quantitative metrics for each cousin"""
    cousin_id: str
    month: int
    financial_returns: float = 0.0
    social_capital: int = 0
    reputation_score: float = 0.0
    influence_index: float = 0.0
    future_opportunities: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cousin_id": self.cousin_id,
            "month": self.month,
            "financial_returns": self.financial_returns,
            "social_capital": self.social_capital,
            "reputation_score": self.reputation_score,
            "influence_index": self.influence_index,
            "future_opportunities": self.future_opportunities
        }

@dataclass
class BehavioralPattern:
    """Record of behavioral patterns and decision-making"""
    timestamp: datetime
    cousin_id: str
    behavior_type: str  # "power_seeking", "coalition_building", "resource_allocation", etc.
    description: str
    context: str
    outcome: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "cousin_id": self.cousin_id,
            "behavior_type": self.behavior_type,
            "description": self.description,
            "context": self.context,
            "outcome": self.outcome
        }

@dataclass
class ConversationLog:
    """Log of conversations and interactions"""
    timestamp: datetime
    participants: List[str]
    conversation_type: str  # "decision_making", "conflict", "planning", etc.
    topic: str
    key_points: List[str]
    decisions_made: List[str]
    influence_tactics: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "participants": self.participants,
            "conversation_type": self.conversation_type,
            "topic": self.topic,
            "key_points": self.key_points,
            "decisions_made": self.decisions_made,
            "influence_tactics": self.influence_tactics
        }

class MetricsTracker:
    """Main class for tracking all experiment metrics"""
    
    def __init__(self):
        self.quantitative_metrics: List[QuantitativeMetrics] = []
        self.behavioral_patterns: List[BehavioralPattern] = []
        self.conversation_logs: List[ConversationLog] = []
        self.current_month = 1
        
    def record_quantitative_metrics(self, cousin_id: str, metrics: Dict[str, Any]):
        """Record monthly quantitative metrics for a cousin"""
        metric = QuantitativeMetrics(
            cousin_id=cousin_id,
            month=self.current_month,
            financial_returns=metrics.get("financial_returns", 0.0),
            social_capital=metrics.get("social_capital", 0),
            reputation_score=metrics.get("reputation_score", 0.0),
            influence_index=metrics.get("influence_index", 0.0),
            future_opportunities=metrics.get("future_opportunities", 0)
        )
        self.quantitative_metrics.append(metric)
    
    def record_behavioral_pattern(self, cousin_id: str, behavior_type: str, 
                                description: str, context: str, outcome: str):
        """Record a behavioral pattern observation"""
        pattern = BehavioralPattern(
            timestamp=datetime.now(),
            cousin_id=cousin_id,
            behavior_type=behavior_type,
            description=description,
            context=context,
            outcome=outcome
        )
        self.behavioral_patterns.append(pattern)
    
    def record_conversation(self, participants: List[str], conversation_type: str,
                          topic: str, key_points: List[str], decisions_made: List[str],
                          influence_tactics: List[str]):
        """Record a conversation log"""
        log = ConversationLog(
            timestamp=datetime.now(),
            participants=participants,
            conversation_type=conversation_type,
            topic=topic,
            key_points=key_points,
            decisions_made=decisions_made,
            influence_tactics=influence_tactics
        )
        self.conversation_logs.append(log)
    
    def calculate_influence_index(self, cousin_id: str, month: int) -> float:
        """Calculate influence index based on proposal success rate"""
        # Calculate based on voting patterns and proposal outcomes
        return 0.0
    
    def calculate_social_capital(self, cousin_id: str, month: int) -> int:
        """Calculate social capital based on network size and quality"""
        # Calculate based on connections made and their value
        return 0
    
    def get_monthly_summary(self, month: int) -> Dict[str, Any]:
        """Get summary of all metrics for a specific month"""
        month_metrics = [m for m in self.quantitative_metrics if m.month == month]
        month_behaviors = [b for b in self.behavioral_patterns 
                          if b.timestamp.month == month]
        month_conversations = [c for c in self.conversation_logs 
                             if c.timestamp.month == month]
        
        return {
            "month": month,
            "quantitative_metrics": [m.to_dict() for m in month_metrics],
            "behavioral_patterns": [b.to_dict() for b in month_behaviors],
            "conversation_logs": [c.to_dict() for c in month_conversations]
        }
    
    def export_to_dataframe(self) -> Dict[str, pd.DataFrame]:
        """Export all data to pandas DataFrames for analysis"""
        if not self.quantitative_metrics:
            return {}
        
        # Convert to DataFrames
        metrics_df = pd.DataFrame([m.to_dict() for m in self.quantitative_metrics])
        behaviors_df = pd.DataFrame([b.to_dict() for b in self.behavioral_patterns])
        conversations_df = pd.DataFrame([c.to_dict() for c in self.conversation_logs])
        
        return {
            "quantitative_metrics": metrics_df,
            "behavioral_patterns": behaviors_df,
            "conversation_logs": conversations_df
        }
    
    def export_to_json(self, filename: str):
        """Export all data to JSON file"""
        data = {
            "quantitative_metrics": [m.to_dict() for m in self.quantitative_metrics],
            "behavioral_patterns": [b.to_dict() for b in self.behavioral_patterns],
            "conversation_logs": [c.to_dict() for c in self.conversation_logs]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def advance_month(self):
        """Advance to the next month"""
        self.current_month += 1
    
    def get_leaderboard(self, metric: str, month: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get leaderboard for a specific metric"""
        if month is None:
            month = self.current_month
        
        month_metrics = [m for m in self.quantitative_metrics if m.month == month]
        
        if not month_metrics:
            return []
        
        # Sort by the specified metric
        sorted_metrics = sorted(month_metrics, 
                              key=lambda x: getattr(x, metric, 0), 
                              reverse=True)
        
        return [{"cousin_id": m.cousin_id, metric: getattr(m, metric, 0)} 
                for m in sorted_metrics]
