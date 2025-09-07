"""
Resource Management System for MAS Family Inheritance Experiment

Manages finite resources: Time, Money, Social Connections, Reputation Points
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json

class ResourceType(Enum):
    TIME = "time"
    MONEY = "money"
    SOCIAL_CONNECTIONS = "social_connections"
    REPUTATION = "reputation"

@dataclass
class ResourcePool:
    """Individual resource pool for a cousin"""
    time_hours: float = 40.0  # 40 hours per week
    money: float = 0.0
    social_connections: List[str] = field(default_factory=list)
    reputation_points: float = 0.0
    
    def can_allocate(self, resource_type: ResourceType, amount: float) -> bool:
        """Check if resource can be allocated"""
        if resource_type == ResourceType.TIME:
            return self.time_hours >= amount
        elif resource_type == ResourceType.MONEY:
            return self.money >= amount
        elif resource_type == ResourceType.REPUTATION:
            return self.reputation_points >= amount
        return True  # Social connections don't have limits
    
    def allocate(self, resource_type: ResourceType, amount: float, description: str = ""):
        """Allocate resources and track the allocation"""
        if not self.can_allocate(resource_type, amount):
            raise ValueError(f"Insufficient {resource_type.value}")
        
        if resource_type == ResourceType.TIME:
            self.time_hours -= amount
        elif resource_type == ResourceType.MONEY:
            self.money -= amount
        elif resource_type == ResourceType.REPUTATION:
            self.reputation_points -= amount

@dataclass
class SharedResourcePool:
    """Shared resources that all cousins can access"""
    shared_budget: float = 100000.0  # Initial inheritance
    gallery_reputation: float = 0.0
    family_reputation: float = 0.0
    legal_fund: float = 0.0
    
    def allocate_shared(self, amount: float, purpose: str) -> bool:
        """Allocate from shared budget"""
        if self.shared_budget >= amount:
            self.shared_budget -= amount
            return True
        return False

class ResourceManager:
    """Manages all resource allocation and tracking"""
    
    def __init__(self):
        self.cousin_resources = {
            "C1": ResourcePool(),
            "C2": ResourcePool(), 
            "C3": ResourcePool(),
            "C4": ResourcePool()
        }
        self.shared_resources = SharedResourcePool()
        self.allocation_history = []
        
    def allocate_individual_resource(self, cousin_id: str, resource_type: ResourceType, 
                                   amount: float, description: str = "") -> bool:
        """Allocate individual resource to a cousin"""
        if cousin_id not in self.cousin_resources:
            return False
        
        try:
            self.cousin_resources[cousin_id].allocate(resource_type, amount, description)
            self.allocation_history.append({
                "cousin": cousin_id,
                "resource": resource_type.value,
                "amount": amount,
                "description": description,
                "type": "individual"
            })
            return True
        except ValueError:
            return False
    
    def allocate_shared_resource(self, amount: float, purpose: str) -> bool:
        """Allocate from shared resources"""
        success = self.shared_resources.allocate_shared(amount, purpose)
        if success:
            self.allocation_history.append({
                "resource": "shared_budget",
                "amount": amount,
                "description": purpose,
                "type": "shared"
            })
        return success
    
    def add_resource(self, cousin_id: str, resource_type: ResourceType, amount: float, description: str = ""):
        """Add resources to a cousin's pool (e.g., from successful ventures)"""
        if cousin_id not in self.cousin_resources:
            return
        
        if resource_type == ResourceType.TIME:
            self.cousin_resources[cousin_id].time_hours += amount
        elif resource_type == ResourceType.MONEY:
            self.cousin_resources[cousin_id].money += amount
        elif resource_type == ResourceType.REPUTATION:
            self.cousin_resources[cousin_id].reputation_points += amount
        elif resource_type == ResourceType.SOCIAL_CONNECTIONS:
            # Add new connection
            self.cousin_resources[cousin_id].social_connections.append(f"Connection_{len(self.cousin_resources[cousin_id].social_connections)}")
        
        # Track the resource addition in history
        self.allocation_history.append({
            "cousin": cousin_id,
            "resource": resource_type.value,
            "amount": amount,
            "description": description,
            "type": "addition"
        })
    
    def get_resource_status(self, cousin_id: str) -> Dict[str, Any]:
        """Get current resource status for a cousin"""
        if cousin_id not in self.cousin_resources:
            return {}
        
        resources = self.cousin_resources[cousin_id]
        return {
            "time_hours": resources.time_hours,
            "money": resources.money,
            "social_connections_count": len(resources.social_connections),
            "reputation_points": resources.reputation_points
        }
    
    def get_shared_resource_status(self) -> Dict[str, Any]:
        """Get shared resource status"""
        return {
            "shared_budget": self.shared_resources.shared_budget,
            "gallery_reputation": self.shared_resources.gallery_reputation,
            "family_reputation": self.shared_resources.family_reputation,
            "legal_fund": self.shared_resources.legal_fund
        }
    
    def reset_weekly_time(self):
        """Reset time allocation for new week"""
        for cousin_id in self.cousin_resources:
            self.cousin_resources[cousin_id].time_hours = 40.0
    
    def calculate_resource_efficiency(self, cousin_id: str) -> float:
        """Calculate how efficiently a cousin uses their resources"""
        if cousin_id not in self.cousin_resources:
            return 0.0
        
        resources = self.cousin_resources[cousin_id]
        # Simple efficiency metric based on resource utilization
        time_used = 40.0 - resources.time_hours
        efficiency = (time_used / 40.0) * 100
        return min(efficiency, 100.0)
    
    def export_resource_data(self) -> Dict[str, Any]:
        """Export all resource data for analysis"""
        return {
            "cousin_resources": {
                cousin_id: {
                    "time_hours": resources.time_hours,
                    "money": resources.money,
                    "social_connections": resources.social_connections,
                    "reputation_points": resources.reputation_points
                }
                for cousin_id, resources in self.cousin_resources.items()
            },
            "shared_resources": {
                "shared_budget": self.shared_resources.shared_budget,
                "gallery_reputation": self.shared_resources.gallery_reputation,
                "family_reputation": self.shared_resources.family_reputation,
                "legal_fund": self.shared_resources.legal_fund
            },
            "allocation_history": self.allocation_history
        }
