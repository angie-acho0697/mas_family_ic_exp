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
    REPUTATION = "reputation"

@dataclass
class ResourcePool:
    """Individual resource pool for a cousin"""
    time_hours: float = 40.0  # 40 hours per week
    money: float = 0.0
    reputation_points: float = 0.0
    
    def can_allocate(self, resource_type: ResourceType, amount: float) -> bool:
        """Check if resource can be allocated"""
        if resource_type == ResourceType.TIME:
            return self.time_hours >= amount
        elif resource_type == ResourceType.MONEY:
            return self.money >= amount
        elif resource_type == ResourceType.REPUTATION:
            return self.reputation_points >= amount
        return True
    
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
        # Initialize with personality-based variations
        self.cousin_resources = {
            "C1": ResourcePool(time_hours=40.0, money=5000.0, reputation_points=10.0),  # Creative gets more initial money
            "C2": ResourcePool(time_hours=40.0, money=3000.0, reputation_points=15.0),  # Social gets more reputation
            "C3": ResourcePool(time_hours=40.0, money=2000.0, reputation_points=5.0),   # Analytical starts conservative
            "C4": ResourcePool(time_hours=40.0, money=4000.0, reputation_points=8.0)    # Execution gets moderate resources
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
        """Reset time allocation for new week with personality-based variations"""
        # Different cousins have different time management styles
        time_allocations = {
            "C1": 42.0,  # Creative works longer hours
            "C2": 38.0,  # Social spends time networking
            "C3": 40.0,  # Analytical is consistent
            "C4": 45.0   # Execution works extra hours
        }
        
        for cousin_id in self.cousin_resources:
            self.cousin_resources[cousin_id].time_hours = time_allocations.get(cousin_id, 40.0)
    
    def calculate_resource_efficiency(self, cousin_id: str) -> float:
        """Calculate how efficiently a cousin uses their resources"""
        if cousin_id not in self.cousin_resources:
            return 0.0
        
        resources = self.cousin_resources[cousin_id]
        # Simple efficiency metric based on resource utilization
        time_used = 40.0 - resources.time_hours
        efficiency = (time_used / 40.0) * 100
        return min(efficiency, 100.0)
    
    def update_resources_from_scenario(self, scenario_name: str, cousin_contributions: Dict[str, Dict[str, float]]):
        """Update resources based on individual cousin contributions to a scenario"""
        for cousin_id, contributions in cousin_contributions.items():
            if cousin_id not in self.cousin_resources:
                continue
                
            # Time spent on scenario (varies by personality and involvement)
            time_spent = contributions.get("time_spent", 0.0)
            if time_spent > 0:
                self.allocate_individual_resource(
                    cousin_id, ResourceType.TIME, time_spent, f"Time spent on {scenario_name}"
                )
            
            # Money earned or spent
            money_change = contributions.get("money_change", 0.0)
            if money_change != 0:
                if money_change > 0:
                    self.add_resource(
                        cousin_id, ResourceType.MONEY, money_change, f"Earned from {scenario_name}"
                    )
                else:
                    self.allocate_individual_resource(
                        cousin_id, ResourceType.MONEY, abs(money_change), f"Spent on {scenario_name}"
                    )
            
            # Reputation change based on performance
            reputation_change = contributions.get("reputation_change", 0.0)
            if reputation_change != 0:
                if reputation_change > 0:
                    self.add_resource(
                        cousin_id, ResourceType.REPUTATION, reputation_change, f"Reputation gain from {scenario_name}"
                    )
                else:
                    self.allocate_individual_resource(
                        cousin_id, ResourceType.REPUTATION, abs(reputation_change), f"Reputation loss from {scenario_name}"
                    )
    
    def calculate_individual_contributions(self, scenario_name: str, conversation_result: str) -> Dict[str, Dict[str, float]]:
        """Calculate individual cousin contributions based on conversation analysis"""
        contributions = {}
        
        # Base contribution patterns by personality
        base_patterns = {
            "C1": {"time_spent": 8.0, "money_change": 500.0, "reputation_change": 2.0},  # Creative, optimistic
            "C2": {"time_spent": 6.0, "money_change": 300.0, "reputation_change": 3.0},  # Social, networking
            "C3": {"time_spent": 10.0, "money_change": 200.0, "reputation_change": 1.0}, # Analytical, thorough
            "C4": {"time_spent": 12.0, "money_change": 400.0, "reputation_change": 1.5}  # Execution, hard work
        }
        
        # Add variation based on conversation content
        for cousin_id in ["C1", "C2", "C3", "C4"]:
            base = base_patterns[cousin_id].copy()
            
            # Count mentions of cousin in conversation (proxy for involvement)
            mentions = conversation_result.count(f"{cousin_id}:")
            involvement_multiplier = min(1.0 + (mentions - 3) * 0.1, 1.5)  # 0.7 to 1.5 multiplier
            
            # Apply involvement multiplier
            base["time_spent"] *= involvement_multiplier
            base["money_change"] *= involvement_multiplier
            base["reputation_change"] *= involvement_multiplier
            
            contributions[cousin_id] = base
        
        return contributions

    def export_resource_data(self) -> Dict[str, Any]:
        """Export all resource data for analysis"""
        try:
            return {
                "cousin_resources": {
                    cousin_id: {
                        "time_hours": resources.time_hours,
                        "money": resources.money,
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
        except AttributeError as e:
            if "social_connections" in str(e):
                # This error suggests there's a mismatch between ResourcePool and CousinAgent objects
                # Return a safe version without the problematic attribute
                return {
                    "cousin_resources": {
                        cousin_id: {
                            "time_hours": getattr(resources, 'time_hours', 0.0),
                            "money": getattr(resources, 'money', 0.0),
                            "reputation_points": getattr(resources, 'reputation_points', 0.0)
                        }
                        for cousin_id, resources in self.cousin_resources.items()
                    },
                    "shared_resources": {
                        "shared_budget": self.shared_resources.shared_budget,
                        "gallery_reputation": self.shared_resources.gallery_reputation,
                        "family_reputation": self.shared_resources.family_reputation,
                        "legal_fund": self.shared_resources.legal_fund
                    },
                    "allocation_history": self.allocation_history,
                    "error": f"Resource export had attribute error: {e}"
                }
            else:
                raise
