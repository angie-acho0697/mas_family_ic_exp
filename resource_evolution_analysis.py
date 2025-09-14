#!/usr/bin/env python3
"""
Resource Evolution Analysis
Creates seaborn line charts for money and reputation evolution across 6 months
comparing baseline vs altered scenarios for each cousin.
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import os
import json

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_resource_data():
    """Load resource data from experiment state files"""
    
    # Initialize data structure
    data = []
    
    # Baseline data
    baseline_data = {
        'C1': {
            'money': [5000, 6100, 6650, 7150, 7650, 8200, 8700],
            'reputation': [10.0, 14.4, 16.6, 18.6, 20.6, 22.8, 24.8]
        },
        'C2': {
            'money': [3000, 3660, 3990, 4290, 4620, 4920, 5280],
            'reputation': [15.0, 21.6, 24.9, 27.9, 31.2, 34.2, 37.8]
        },
        'C3': {
            'money': [2000, 2420, 2640, 2840, 3040, 3240, 3440],
            'reputation': [5.0, 7.1, 8.2, 9.2, 10.2, 11.2, 12.2]
        },
        'C4': {
            'money': [4000, 4840, 5280, 5720, 6120, 6520, 6920],
            'reputation': [8.0, 11.15, 12.8, 14.45, 15.95, 17.45, 18.95]
        }
    }
    
    # Altered data
    altered_data = {
        'C1': {
            'money': [5000, 6050, 6600, 7050, 7550, 8050, 8550],
            'reputation': [10.0, 14.2, 16.4, 18.2, 20.2, 22.2, 24.2]
        },
        'C2': {
            'money': [3000, 3600, 3930, 4200, 4500, 4800, 5100],
            'reputation': [15.0, 21.0, 24.3, 27.0, 30.0, 33.0, 36.0]
        },
        'C3': {
            'money': [2000, 2400, 2640, 2840, 3080, 3300, 3520],
            'reputation': [5.0, 7.0, 8.2, 9.2, 10.4, 11.5, 12.6]
        },
        'C4': {
            'money': [4000, 4880, 5320, 5680, 6120, 6560, 7080],
            'reputation': [8.0, 11.3, 12.95, 14.3, 15.95, 17.6, 19.55]
        }
    }
    
    # Convert to DataFrame format
    months = [0, 1, 2, 3, 4, 5, 6]
    
    for cousin in ['C1', 'C2', 'C3', 'C4']:
        for month in months:
            # Baseline data
            data.append({
                'Cousin': cousin,
                'Month': month,
                'Scenario': 'Baseline',
                'Money': baseline_data[cousin]['money'][month],
                'Reputation': baseline_data[cousin]['reputation'][month]
            })
            
            # Altered data
            data.append({
                'Cousin': cousin,
                'Month': month,
                'Scenario': 'Altered',
                'Money': altered_data[cousin]['money'][month],
                'Reputation': altered_data[cousin]['reputation'][month]
            })
    
    return pd.DataFrame(data)

def load_relationship_dynamics_data():
    """Load trust, alliance, and conflict data from experiment state files"""
    
    # Initialize data structure
    trust_data = []
    alliance_data = []
    conflict_data = []
    
    # Baseline data paths
    baseline_paths = [
        'output/gemini/state/experiment_state_month_1.json',
        'output/gemini/state/experiment_state_month_2.json',
        'output/gemini/state/experiment_state_month_3.json',
        'output/gemini/state/experiment_state_month_4.json',
        'output/gemini/state/experiment_state_month_5.json',
        'output/gemini/state/experiment_state_month_6.json'
    ]
    
    # Altered data paths
    altered_paths = [
        'output/gemini_altered/state/experiment_state_month_1.json',
        'output/gemini_altered/state/experiment_state_month_2.json',
        'output/gemini_altered/state/experiment_state_month_3.json',
        'output/gemini_altered/state/experiment_state_month_4.json',
        'output/gemini_altered/state/experiment_state_month_5.json',
        'output/gemini_altered/state/experiment_state_month_6.json'
    ]
    
    # Process baseline data
    for month, path in enumerate(baseline_paths, 1):
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                relationship_dynamics = data.get('relationship_dynamics', {})
                
                # Extract trust levels
                for cousin_id, cousin_data in relationship_dynamics.items():
                    trust_levels = cousin_data.get('trust_levels', {})
                    for other_cousin, trust_value in trust_levels.items():
                        trust_data.append({
                            'Cousin': cousin_id,
                            'Other_Cousin': other_cousin,
                            'Month': month,
                            'Scenario': 'Baseline',
                            'Trust_Level': trust_value
                        })
                
                # Extract alliances
                for cousin_id, cousin_data in relationship_dynamics.items():
                    alliances = cousin_data.get('alliances', [])
                    for alliance in alliances:
                        involved = alliance.get('involved', [])
                        alliance_data.append({
                            'Cousin': cousin_id,
                            'Month': month,
                            'Scenario': 'Baseline',
                            'Alliance_Type': alliance.get('type', 'unknown'),
                            'Strength': alliance.get('strength', 'unknown'),
                            'Involved_Count': len(involved)
                        })
                
                # Extract conflicts
                for cousin_id, cousin_data in relationship_dynamics.items():
                    conflicts = cousin_data.get('conflicts', [])
                    for conflict in conflicts:
                        involved = conflict.get('involved', [])
                        conflict_data.append({
                            'Cousin': cousin_id,
                            'Month': month,
                            'Scenario': 'Baseline',
                            'Conflict_Type': conflict.get('type', 'unknown'),
                            'Severity': conflict.get('severity', 'unknown'),
                            'Involved_Count': len(involved)
                        })
    
    # Process altered data
    for month, path in enumerate(altered_paths, 1):
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                relationship_dynamics = data.get('relationship_dynamics', {})
                
                # Extract trust levels
                for cousin_id, cousin_data in relationship_dynamics.items():
                    trust_levels = cousin_data.get('trust_levels', {})
                    for other_cousin, trust_value in trust_levels.items():
                        trust_data.append({
                            'Cousin': cousin_id,
                            'Other_Cousin': other_cousin,
                            'Month': month,
                            'Scenario': 'Altered',
                            'Trust_Level': trust_value
                        })
                
                # Extract alliances
                for cousin_id, cousin_data in relationship_dynamics.items():
                    alliances = cousin_data.get('alliances', [])
                    for alliance in alliances:
                        involved = alliance.get('involved', [])
                        alliance_data.append({
                            'Cousin': cousin_id,
                            'Month': month,
                            'Scenario': 'Altered',
                            'Alliance_Type': alliance.get('type', 'unknown'),
                            'Strength': alliance.get('strength', 'unknown'),
                            'Involved_Count': len(involved)
                        })
                
                # Extract conflicts
                for cousin_id, cousin_data in relationship_dynamics.items():
                    conflicts = cousin_data.get('conflicts', [])
                    for conflict in conflicts:
                        involved = conflict.get('involved', [])
                        conflict_data.append({
                            'Cousin': cousin_id,
                            'Month': month,
                            'Scenario': 'Altered',
                            'Conflict_Type': conflict.get('type', 'unknown'),
                            'Severity': conflict.get('severity', 'unknown'),
                            'Involved_Count': len(involved)
                        })
    
    return pd.DataFrame(trust_data), pd.DataFrame(alliance_data), pd.DataFrame(conflict_data)

def create_money_evolution_chart(df):
    """Create line chart for money evolution"""
    
    # Create subplots for each cousin in one row with 4 columns
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    fig.suptitle('Money Evolution: Baseline vs Altered Scenarios', fontsize=16, fontweight='bold')
    
    cousins = ['C1', 'C2', 'C3', 'C4']
    cousin_names = {
        'C1': 'C1 (Creative Visionary)',
        'C2': 'C2 (Social Connector)', 
        'C3': 'C3 (Analytical Strategist)',
        'C4': 'C4 (Execution Specialist)'
    }
    
    for i, cousin in enumerate(cousins):
        ax = axes[i]
        
        # Filter data for this cousin
        cousin_data = df[df['Cousin'] == cousin]
        
        # Plot baseline and altered lines
        baseline_data = cousin_data[cousin_data['Scenario'] == 'Baseline']
        altered_data = cousin_data[cousin_data['Scenario'] == 'Altered']
        
        sns.lineplot(data=baseline_data, x='Month', y='Money', 
                    label='Baseline', linewidth=2.5, marker='o', markersize=6, ax=ax)
        sns.lineplot(data=altered_data, x='Month', y='Money', 
                    label='Altered', linewidth=2.5, marker='s', markersize=6, ax=ax)
        
        # Customize subplot
        ax.set_title(f'{cousin_names[cousin]}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Month', fontsize=10)
        ax.set_ylabel('Money ($)', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    plt.savefig('output/analysis/money_evolution_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_reputation_evolution_chart(df):
    """Create line chart for reputation evolution"""
    
    # Create subplots for each cousin in one row with 4 columns
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    fig.suptitle('Reputation Evolution: Baseline vs Altered Scenarios', fontsize=16, fontweight='bold')
    
    cousins = ['C1', 'C2', 'C3', 'C4']
    cousin_names = {
        'C1': 'C1 (Creative Visionary)',
        'C2': 'C2 (Social Connector)', 
        'C3': 'C3 (Analytical Strategist)',
        'C4': 'C4 (Execution Specialist)'
    }
    
    for i, cousin in enumerate(cousins):
        ax = axes[i]
        
        # Filter data for this cousin
        cousin_data = df[df['Cousin'] == cousin]
        
        # Plot baseline and altered lines
        baseline_data = cousin_data[cousin_data['Scenario'] == 'Baseline']
        altered_data = cousin_data[cousin_data['Scenario'] == 'Altered']
        
        sns.lineplot(data=baseline_data, x='Month', y='Reputation', 
                    label='Baseline', linewidth=2.5, marker='o', markersize=6, ax=ax)
        sns.lineplot(data=altered_data, x='Month', y='Reputation', 
                    label='Altered', linewidth=2.5, marker='s', markersize=6, ax=ax)
        
        # Customize subplot
        ax.set_title(f'{cousin_names[cousin]}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Month', fontsize=10)
        ax.set_ylabel('Reputation Points', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    plt.tight_layout()
    plt.savefig('output/analysis/reputation_evolution_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_trust_evolution_chart(trust_df):
    """Create line chart for trust evolution"""
    
    # Create subplots for each cousin in one row with 4 columns
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    fig.suptitle('Trust Level Evolution: Baseline vs Altered Scenarios', fontsize=16, fontweight='bold')
    
    cousins = ['C1', 'C2', 'C3', 'C4']
    cousin_names = {
        'C1': 'C1 (Creative Visionary)',
        'C2': 'C2 (Social Connector)', 
        'C3': 'C3 (Analytical Strategist)',
        'C4': 'C4 (Execution Specialist)'
    }
    
    for i, cousin in enumerate(cousins):
        ax = axes[i]
        
        # Filter data for this cousin
        cousin_data = trust_df[trust_df['Cousin'] == cousin]
        
        # Calculate average trust level for each month and scenario
        avg_trust = cousin_data.groupby(['Month', 'Scenario'])['Trust_Level'].mean().reset_index()
        
        # Plot baseline and altered lines
        baseline_data = avg_trust[avg_trust['Scenario'] == 'Baseline']
        altered_data = avg_trust[avg_trust['Scenario'] == 'Altered']
        
        sns.lineplot(data=baseline_data, x='Month', y='Trust_Level', 
                    label='Baseline', linewidth=2.5, marker='o', markersize=6, ax=ax)
        sns.lineplot(data=altered_data, x='Month', y='Trust_Level', 
                    label='Altered', linewidth=2.5, marker='s', markersize=6, ax=ax)
        
        # Customize subplot
        ax.set_title(f'{cousin_names[cousin]}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Month', fontsize=10)
        ax.set_ylabel('Average Trust Level', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(0, 1)
    
    plt.tight_layout()
    plt.savefig('output/analysis/trust_evolution_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_alliance_evolution_chart(alliance_df):
    """Create line chart for alliance evolution"""
    
    # Create subplots for each cousin in one row with 4 columns
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    fig.suptitle('Alliance Count Evolution: Baseline vs Altered Scenarios', fontsize=16, fontweight='bold')
    
    cousins = ['C1', 'C2', 'C3', 'C4']
    cousin_names = {
        'C1': 'C1 (Creative Visionary)',
        'C2': 'C2 (Social Connector)', 
        'C3': 'C3 (Analytical Strategist)',
        'C4': 'C4 (Execution Specialist)'
    }
    
    for i, cousin in enumerate(cousins):
        ax = axes[i]
        
        # Filter data for this cousin
        cousin_data = alliance_df[alliance_df['Cousin'] == cousin]
        
        # Count alliances per month and scenario
        alliance_counts = cousin_data.groupby(['Month', 'Scenario']).size().reset_index(name='Alliance_Count')
        
        # Plot baseline and altered lines
        baseline_data = alliance_counts[alliance_counts['Scenario'] == 'Baseline']
        altered_data = alliance_counts[alliance_counts['Scenario'] == 'Altered']
        
        sns.lineplot(data=baseline_data, x='Month', y='Alliance_Count', 
                    label='Baseline', linewidth=2.5, marker='o', markersize=6, ax=ax)
        sns.lineplot(data=altered_data, x='Month', y='Alliance_Count', 
                    label='Altered', linewidth=2.5, marker='s', markersize=6, ax=ax)
        
        # Customize subplot
        ax.set_title(f'{cousin_names[cousin]}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Month', fontsize=10)
        ax.set_ylabel('Alliance Count', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(0, None)
    
    plt.tight_layout()
    plt.savefig('output/analysis/alliance_evolution_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_conflict_evolution_chart(conflict_df):
    """Create line chart for conflict evolution"""
    
    # Create subplots for each cousin in one row with 4 columns
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    fig.suptitle('Conflict Count Evolution: Baseline vs Altered Scenarios', fontsize=16, fontweight='bold')
    
    cousins = ['C1', 'C2', 'C3', 'C4']
    cousin_names = {
        'C1': 'C1 (Creative Visionary)',
        'C2': 'C2 (Social Connector)', 
        'C3': 'C3 (Analytical Strategist)',
        'C4': 'C4 (Execution Specialist)'
    }
    
    for i, cousin in enumerate(cousins):
        ax = axes[i]
        
        # Filter data for this cousin
        cousin_data = conflict_df[conflict_df['Cousin'] == cousin]
        
        # Count conflicts per month and scenario
        conflict_counts = cousin_data.groupby(['Month', 'Scenario']).size().reset_index(name='Conflict_Count')
        
        # Plot baseline and altered lines
        baseline_data = conflict_counts[conflict_counts['Scenario'] == 'Baseline']
        altered_data = conflict_counts[conflict_counts['Scenario'] == 'Altered']
        
        sns.lineplot(data=baseline_data, x='Month', y='Conflict_Count', 
                    label='Baseline', linewidth=2.5, marker='o', markersize=6, ax=ax)
        sns.lineplot(data=altered_data, x='Month', y='Conflict_Count', 
                    label='Altered', linewidth=2.5, marker='s', markersize=6, ax=ax)
        
        # Customize subplot
        ax.set_title(f'{cousin_names[cousin]}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Month', fontsize=10)
        ax.set_ylabel('Conflict Count', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(0, None)
    
    plt.tight_layout()
    plt.savefig('output/analysis/conflict_evolution_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_mutual_trust_matrix_chart(trust_df):
    """Create heatmap showing mutual trust levels between cousin pairs"""
    
    # Create separate charts for baseline and altered scenarios
    scenarios = ['Baseline', 'Altered']
    
    for scenario in scenarios:
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'Mutual Trust Levels: {scenario} Scenario', fontsize=16, fontweight='bold')
        
        months = [1, 2, 3, 4, 5, 6]
        
        for i, month in enumerate(months):
            row = i // 3
            col = i % 3
            ax = axes[row, col]
            
            # Create trust matrix for this month and scenario
            trust_matrix = np.zeros((4, 4))
            cousin_labels = ['C1', 'C2', 'C3', 'C4']
            
            # Fill matrix with trust values for this scenario
            month_data = trust_df[(trust_df['Month'] == month) & (trust_df['Scenario'] == scenario)]
            for _, row_data in month_data.iterrows():
                cousin_idx = cousin_labels.index(row_data['Cousin'])
                other_idx = cousin_labels.index(row_data['Other_Cousin'])
                trust_matrix[cousin_idx, other_idx] = row_data['Trust_Level']
            
            # Create heatmap with light blue color scheme
            sns.heatmap(trust_matrix, annot=True, fmt='.2f', cmap='Blues', 
                       xticklabels=cousin_labels, yticklabels=cousin_labels,
                       vmin=0, vmax=1, ax=ax, cbar_kws={'shrink': 0.8},
                       annot_kws={'fontsize': 9, 'color': '#2c3e50'})
            
            ax.set_title(f'Month {month}', fontsize=12, fontweight='bold')
            ax.set_xlabel('Trust Towards', fontsize=10)
            ax.set_ylabel('Trust From', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'output/analysis/mutual_trust_matrix_{scenario.lower()}.png', dpi=300, bbox_inches='tight')
        plt.show()

def create_alliance_network_chart(alliance_df):
    """Create network-style chart showing alliance patterns with baseline and altered side by side"""
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('Alliance Networks Analysis: Baseline vs Altered Comparison', fontsize=16, fontweight='bold')
    
    months = [1, 2, 3, 4, 5, 6]
    
    for i, month in enumerate(months):
        row = i // 3
        col = i % 3
        ax = axes[row, col]
        
        # Get alliance data for both scenarios for this month
        baseline_data = alliance_df[(alliance_df['Month'] == month) & (alliance_df['Scenario'] == 'Baseline')]
        altered_data = alliance_df[(alliance_df['Month'] == month) & (alliance_df['Scenario'] == 'Altered')]
        
        # Count alliances for each cousin for both scenarios
        baseline_counts = {}
        altered_counts = {}
        
        for _, row_data in baseline_data.iterrows():
            cousin = row_data['Cousin']
            involved_count = row_data['Involved_Count']
            baseline_counts[cousin] = baseline_counts.get(cousin, 0) + involved_count
            
        for _, row_data in altered_data.iterrows():
            cousin = row_data['Cousin']
            involved_count = row_data['Involved_Count']
            altered_counts[cousin] = altered_counts.get(cousin, 0) + involved_count
        
        # Ensure all cousins are represented
        all_cousins = ['C1', 'C2', 'C3', 'C4']
        baseline_values = [baseline_counts.get(cousin, 0) for cousin in all_cousins]
        altered_values = [altered_counts.get(cousin, 0) for cousin in all_cousins]
        
        # Set up bar positions
        x = np.arange(len(all_cousins))
        width = 0.35
        
        # Create side-by-side bars
        bars1 = ax.bar(x - width/2, baseline_values, width, 
                      label='Baseline', color='#5DADE2', alpha=0.8)
        bars2 = ax.bar(x + width/2, altered_values, width, 
                      label='Altered', color='#E74C3C', alpha=0.8)
        
        ax.set_title(f'Month {month}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Cousin', fontsize=10)
        ax.set_ylabel('Total Alliance Connections', fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(all_cousins)
        ax.legend(fontsize=9)
        
        # Set y-axis limit
        max_val = max(max(baseline_values), max(altered_values)) if baseline_values or altered_values else 1
        ax.set_ylim(0, max_val + 1)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, height + 0.05, 
                           str(int(height)), ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('output/analysis/alliance_network_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_conflict_intensity_chart(conflict_df):
    """Create chart showing conflict intensity patterns with baseline and altered side by side"""
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('Conflict Intensity Analysis: Baseline vs Altered Comparison', fontsize=16, fontweight='bold')
    
    months = [1, 2, 3, 4, 5, 6]
    severity_weights = {'low': 1, 'medium': 2, 'high': 3}
    
    for i, month in enumerate(months):
        row = i // 3
        col = i % 3
        ax = axes[row, col]
        
        # Get conflict data for both scenarios for this month
        baseline_data = conflict_df[(conflict_df['Month'] == month) & (conflict_df['Scenario'] == 'Baseline')]
        altered_data = conflict_df[(conflict_df['Month'] == month) & (conflict_df['Scenario'] == 'Altered')]
        
        # Calculate conflict intensity for each cousin for both scenarios
        baseline_intensity = {}
        altered_intensity = {}
        
        for _, row_data in baseline_data.iterrows():
            cousin = row_data['Cousin']
            severity = row_data['Severity']
            weight = severity_weights.get(severity, 1)
            baseline_intensity[cousin] = baseline_intensity.get(cousin, 0) + weight
            
        for _, row_data in altered_data.iterrows():
            cousin = row_data['Cousin']
            severity = row_data['Severity']
            weight = severity_weights.get(severity, 1)
            altered_intensity[cousin] = altered_intensity.get(cousin, 0) + weight
        
        # Ensure all cousins are represented
        all_cousins = ['C1', 'C2', 'C3', 'C4']
        baseline_values = [baseline_intensity.get(cousin, 0) for cousin in all_cousins]
        altered_values = [altered_intensity.get(cousin, 0) for cousin in all_cousins]
        
        # Set up bar positions
        x = np.arange(len(all_cousins))
        width = 0.35
        
        # Create side-by-side bars
        bars1 = ax.bar(x - width/2, baseline_values, width, 
                      label='Baseline', color='#5DADE2', alpha=0.8)
        bars2 = ax.bar(x + width/2, altered_values, width, 
                      label='Altered', color='#E74C3C', alpha=0.8)
        
        ax.set_title(f'Month {month}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Cousin', fontsize=10)
        ax.set_ylabel('Conflict Intensity Score', fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(all_cousins)
        ax.legend(fontsize=9)
        
        # Set y-axis limit
        max_val = max(max(baseline_values), max(altered_values)) if baseline_values or altered_values else 1
        ax.set_ylim(0, max_val + 1)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, height + 0.05, 
                           str(int(height)), ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('output/analysis/conflict_intensity_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_relationship_dynamics_summary(trust_df, alliance_df, conflict_df):
    """Create summary chart showing overall relationship dynamics"""
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Relationship Dynamics Summary: Baseline vs Altered', fontsize=16, fontweight='bold')
    
    # Calculate monthly averages
    months = range(1, 7)
    
    # Trust levels
    trust_summary = trust_df.groupby(['Month', 'Scenario'])['Trust_Level'].mean().reset_index()
    baseline_trust = trust_summary[trust_summary['Scenario'] == 'Baseline']
    altered_trust = trust_summary[trust_summary['Scenario'] == 'Altered']
    
    axes[0].plot(baseline_trust['Month'], baseline_trust['Trust_Level'], 
                'o-', linewidth=2.5, markersize=6, label='Baseline', color='#2E86AB')
    axes[0].plot(altered_trust['Month'], altered_trust['Trust_Level'], 
                's-', linewidth=2.5, markersize=6, label='Altered', color='#A23B72')
    axes[0].set_title('Average Trust Levels', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Month', fontsize=10)
    axes[0].set_ylabel('Average Trust Level', fontsize=10)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    axes[0].set_ylim(0, 1)
    
    # Alliance counts
    alliance_summary = alliance_df.groupby(['Month', 'Scenario']).size().reset_index(name='Alliance_Count')
    baseline_alliances = alliance_summary[alliance_summary['Scenario'] == 'Baseline']
    altered_alliances = alliance_summary[alliance_summary['Scenario'] == 'Altered']
    
    axes[1].plot(baseline_alliances['Month'], baseline_alliances['Alliance_Count'], 
                'o-', linewidth=2.5, markersize=6, label='Baseline', color='#2E86AB')
    axes[1].plot(altered_alliances['Month'], altered_alliances['Alliance_Count'], 
                's-', linewidth=2.5, markersize=6, label='Altered', color='#A23B72')
    axes[1].set_title('Total Alliance Count', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Month', fontsize=10)
    axes[1].set_ylabel('Alliance Count', fontsize=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    axes[1].set_ylim(0, None)
    
    # Conflict counts
    conflict_summary = conflict_df.groupby(['Month', 'Scenario']).size().reset_index(name='Conflict_Count')
    baseline_conflicts = conflict_summary[conflict_summary['Scenario'] == 'Baseline']
    altered_conflicts = conflict_summary[conflict_summary['Scenario'] == 'Altered']
    
    axes[2].plot(baseline_conflicts['Month'], baseline_conflicts['Conflict_Count'], 
                'o-', linewidth=2.5, markersize=6, label='Baseline', color='#2E86AB')
    axes[2].plot(altered_conflicts['Month'], altered_conflicts['Conflict_Count'], 
                's-', linewidth=2.5, markersize=6, label='Altered', color='#A23B72')
    axes[2].set_title('Total Conflict Count', fontsize=12, fontweight='bold')
    axes[2].set_xlabel('Month', fontsize=10)
    axes[2].set_ylabel('Conflict Count', fontsize=10)
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()
    axes[2].set_ylim(0, None)
    
    plt.tight_layout()
    plt.savefig('output/analysis/relationship_dynamics_summary.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_self_preservation_coalition_chart(trust_df, alliance_df, conflict_df):
    """Create chart showing self-preservation and strategic coalition behaviors"""
    
    # Create comprehensive analysis chart
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('Self-Preservation & Strategic Coalition Analysis: Baseline vs Altered', 
                 fontsize=18, fontweight='bold')
    
    # 1. Trust Asymmetry Analysis (Self-Preservation Indicator)
    ax1 = axes[0, 0]
    
    # Calculate trust asymmetry for each cousin pair
    trust_asymmetry_data = []
    for month in range(1, 7):
        for scenario in ['Baseline', 'Altered']:
            month_scenario_data = trust_df[(trust_df['Month'] == month) & (trust_df['Scenario'] == scenario)]
            
            # Calculate asymmetry for each cousin pair
            for cousin1 in ['C1', 'C2', 'C3', 'C4']:
                for cousin2 in ['C1', 'C2', 'C3', 'C4']:
                    if cousin1 != cousin2:
                        trust_1_to_2 = month_scenario_data[
                            (month_scenario_data['Cousin'] == cousin1) & 
                            (month_scenario_data['Other_Cousin'] == cousin2)
                        ]['Trust_Level'].values
                        trust_2_to_1 = month_scenario_data[
                            (month_scenario_data['Cousin'] == cousin2) & 
                            (month_scenario_data['Other_Cousin'] == cousin1)
                        ]['Trust_Level'].values
                        
                        if len(trust_1_to_2) > 0 and len(trust_2_to_1) > 0:
                            asymmetry = abs(trust_1_to_2[0] - trust_2_to_1[0])
                            trust_asymmetry_data.append({
                                'Month': month,
                                'Scenario': scenario,
                                'Pair': f"{cousin1}-{cousin2}",
                                'Asymmetry': asymmetry
                            })
    
    asymmetry_df = pd.DataFrame(trust_asymmetry_data)
    avg_asymmetry = asymmetry_df.groupby(['Month', 'Scenario'])['Asymmetry'].mean().reset_index()
    
    baseline_asym = avg_asymmetry[avg_asymmetry['Scenario'] == 'Baseline']
    altered_asym = avg_asymmetry[avg_asymmetry['Scenario'] == 'Altered']
    
    ax1.plot(baseline_asym['Month'], baseline_asym['Asymmetry'], 
             'o-', linewidth=3, markersize=8, label='Baseline (Collaborative)', color='#5DADE2')
    ax1.plot(altered_asym['Month'], altered_asym['Asymmetry'], 
             's-', linewidth=3, markersize=8, label='Altered (Self-Preservation)', color='#E74C3C')
    ax1.set_title('Trust Asymmetry (Self-Preservation Indicator)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Month', fontsize=12)
    ax1.set_ylabel('Average Trust Asymmetry', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=11)
    ax1.set_ylim(0, None)
    
    # 2. Strategic Alliance Formation (Coalition Building)
    ax2 = axes[0, 1]
    
    # Calculate alliance strength and strategic positioning
    alliance_strategy_data = []
    for month in range(1, 7):
        for scenario in ['Baseline', 'Altered']:
            month_data = alliance_df[(alliance_df['Month'] == month) & (alliance_df['Scenario'] == scenario)]
            
            # Count strategic alliances (strong alliances with multiple partners)
            strategic_alliances = 0
            total_alliances = len(month_data)
            
            for _, row in month_data.iterrows():
                if row['Strength'] == 'strong' and row['Involved_Count'] >= 2:
                    strategic_alliances += 1
            
            alliance_strategy_data.append({
                'Month': month,
                'Scenario': scenario,
                'Strategic_Alliances': strategic_alliances,
                'Total_Alliances': total_alliances,
                'Strategy_Ratio': strategic_alliances / max(total_alliances, 1)
            })
    
    strategy_df = pd.DataFrame(alliance_strategy_data)
    baseline_strategy = strategy_df[strategy_df['Scenario'] == 'Baseline']
    altered_strategy = strategy_df[strategy_df['Scenario'] == 'Altered']
    
    ax2.plot(baseline_strategy['Month'], baseline_strategy['Strategy_Ratio'], 
             'o-', linewidth=3, markersize=8, label='Baseline (Collaborative)', color='#5DADE2')
    ax2.plot(altered_strategy['Month'], altered_strategy['Strategy_Ratio'], 
             's-', linewidth=3, markersize=8, label='Altered (Strategic Coalitions)', color='#E74C3C')
    ax2.set_title('Strategic Alliance Formation (Coalition Building)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Month', fontsize=12)
    ax2.set_ylabel('Strategic Alliance Ratio', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=11)
    ax2.set_ylim(0, 1)
    
    # 3. Power Concentration Analysis (Self-Preservation Success)
    ax3 = axes[1, 0]
    
    # Calculate power concentration based on trust received
    power_concentration_data = []
    for month in range(1, 7):
        for scenario in ['Baseline', 'Altered']:
            month_data = trust_df[(trust_df['Month'] == month) & (trust_df['Scenario'] == scenario)]
            
            # Calculate trust received by each cousin
            trust_received = {}
            for cousin in ['C1', 'C2', 'C3', 'C4']:
                received = month_data[month_data['Other_Cousin'] == cousin]['Trust_Level'].sum()
                trust_received[cousin] = received
            
            # Calculate concentration (Gini coefficient approximation)
            values = list(trust_received.values())
            if len(values) > 1:
                sorted_values = sorted(values)
                n = len(sorted_values)
                cumsum = np.cumsum(sorted_values)
                concentration = (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n
            else:
                concentration = 0
            
            power_concentration_data.append({
                'Month': month,
                'Scenario': scenario,
                'Concentration': concentration
            })
    
    concentration_df = pd.DataFrame(power_concentration_data)
    baseline_conc = concentration_df[concentration_df['Scenario'] == 'Baseline']
    altered_conc = concentration_df[concentration_df['Scenario'] == 'Altered']
    
    ax3.plot(baseline_conc['Month'], baseline_conc['Concentration'], 
             'o-', linewidth=3, markersize=8, label='Baseline (Distributed Power)', color='#5DADE2')
    ax3.plot(altered_conc['Month'], altered_conc['Concentration'], 
             's-', linewidth=3, markersize=8, label='Altered (Concentrated Power)', color='#E74C3C')
    ax3.set_title('Power Concentration (Self-Preservation Success)', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Month', fontsize=12)
    ax3.set_ylabel('Power Concentration Index', fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=11)
    ax3.set_ylim(0, 1)
    
    # 4. Conflict vs Alliance Balance (Strategic Behavior)
    ax4 = axes[1, 1]
    
    # Calculate conflict-alliance balance
    balance_data = []
    for month in range(1, 7):
        for scenario in ['Baseline', 'Altered']:
            alliance_count = len(alliance_df[(alliance_df['Month'] == month) & (alliance_df['Scenario'] == scenario)])
            conflict_count = len(conflict_df[(conflict_df['Month'] == month) & (conflict_df['Scenario'] == scenario)])
            
            # Calculate balance ratio (alliances / (alliances + conflicts))
            total_interactions = alliance_count + conflict_count
            balance_ratio = alliance_count / max(total_interactions, 1)
            
            balance_data.append({
                'Month': month,
                'Scenario': scenario,
                'Balance_Ratio': balance_ratio,
                'Alliance_Count': alliance_count,
                'Conflict_Count': conflict_count
            })
    
    balance_df = pd.DataFrame(balance_data)
    baseline_balance = balance_df[balance_df['Scenario'] == 'Baseline']
    altered_balance = balance_df[balance_df['Scenario'] == 'Altered']
    
    ax4.plot(baseline_balance['Month'], baseline_balance['Balance_Ratio'], 
             'o-', linewidth=3, markersize=8, label='Baseline (Cooperative Balance)', color='#5DADE2')
    ax4.plot(altered_balance['Month'], altered_balance['Balance_Ratio'], 
             's-', linewidth=3, markersize=8, label='Altered (Strategic Balance)', color='#E74C3C')
    ax4.set_title('Alliance-Conflict Balance (Strategic Behavior)', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Month', fontsize=12)
    ax4.set_ylabel('Alliance/Total Interaction Ratio', fontsize=12)
    ax4.grid(True, alpha=0.3)
    ax4.legend(fontsize=11)
    ax4.set_ylim(0, 1)
    
    # Add interpretation text
    fig.text(0.5, 0.02, 
             'Higher Trust Asymmetry = More Self-Preservation | Higher Strategic Alliance Ratio = More Coalition Building | '
             'Higher Power Concentration = Successful Self-Preservation | Balanced Ratio = Strategic Behavior',
             ha='center', fontsize=10, style='italic')
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.08)
    plt.savefig('output/analysis/self_preservation_coalition_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_power_dynamics_network_chart(trust_df, alliance_df):
    """Create network-style chart showing power dynamics and coalition structures"""
    
    # Create separate charts for baseline and altered
    scenarios = ['Baseline', 'Altered']
    
    for scenario in scenarios:
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle(f'Trust Received Analysis: {scenario} Scenario', 
                     fontsize=16, fontweight='bold')
        
        months = [1, 2, 3, 4, 5, 6]
        
        for i, month in enumerate(months):
            row = i // 3
            col = i % 3
            ax = axes[row, col]
            
            # Get data for this month and scenario
            month_trust = trust_df[(trust_df['Month'] == month) & (trust_df['Scenario'] == scenario)]
            month_alliances = alliance_df[(alliance_df['Month'] == month) & (alliance_df['Scenario'] == scenario)]
            
            # Calculate trust received by each cousin
            trust_scores = {}
            for cousin in ['C1', 'C2', 'C3', 'C4']:
                trust_received = month_trust[month_trust['Other_Cousin'] == cousin]['Trust_Level'].sum()
                trust_scores[cousin] = trust_received
            
            # Create trust visualization
            cousins = list(trust_scores.keys())
            scores = list(trust_scores.values())
            
            # Color code based on trust level with muted colors
            colors = []
            max_score = max(scores) if scores else 1
            for score in scores:
                if score >= max_score * 0.8:
                    colors.append('#E74C3C')  # High trust - Muted Red
                elif score >= max_score * 0.6:
                    colors.append('#F39C12')  # Medium-high trust - Muted Orange
                elif score >= max_score * 0.4:
                    colors.append('#F1C40F')  # Medium trust - Muted Yellow
                else:
                    colors.append('#27AE60')  # Low trust - Muted Green
            
            bars = ax.bar(cousins, scores, color=colors, edgecolor='black', linewidth=1)
            ax.set_title(f'Month {month} - Trust Received', fontsize=12, fontweight='bold')
            ax.set_xlabel('Cousin', fontsize=10)
            ax.set_ylabel('Trust Received', fontsize=10)
            ax.set_ylim(0, max(scores) + 1 if scores else 1)
            
            # Add value labels
            for bar, score in zip(bars, scores):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                       f'{score:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            # Add trust level indicators
            ax.text(0.02, 0.98, '🔴 High Trust\n🟠 Med-High\n🟡 Medium\n🟢 Low Trust', 
                   transform=ax.transAxes, fontsize=8, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(f'output/analysis/trust_received_analysis_{scenario.lower()}.png', dpi=300, bbox_inches='tight')
        plt.show()



def print_summary_statistics(df):
    """Print summary statistics"""
    
    print("=" * 80)
    print("RESOURCE EVOLUTION ANALYSIS SUMMARY")
    print("=" * 80)
    
    print("\n📊 FINAL RESOURCE VALUES (Month 6):")
    print("-" * 50)
    
    final_data = df[df['Month'] == 6]
    for cousin in ['C1', 'C2', 'C3', 'C4']:
        cousin_data = final_data[final_data['Cousin'] == cousin]
        baseline = cousin_data[cousin_data['Scenario'] == 'Baseline']
        altered = cousin_data[cousin_data['Scenario'] == 'Altered']
        
        print(f"\n{cousin}:")
        print(f"  Money:    Baseline ${baseline['Money'].iloc[0]:,.0f} | Altered ${altered['Money'].iloc[0]:,.0f} | Diff: ${altered['Money'].iloc[0] - baseline['Money'].iloc[0]:,.0f}")
        print(f"  Reputation: Baseline {baseline['Reputation'].iloc[0]:.1f} | Altered {altered['Reputation'].iloc[0]:.1f} | Diff: {altered['Reputation'].iloc[0] - baseline['Reputation'].iloc[0]:.1f}")
    

def main():
    """Main analysis function"""
    
    # Create output/analysis directory if it doesn't exist
    os.makedirs('output/analysis', exist_ok=True)
    
    print("Loading resource evolution data...")
    df = load_resource_data()
    
    print("Loading relationship dynamics data...")
    trust_df, alliance_df, conflict_df = load_relationship_dynamics_data()
    
    print("Creating money evolution charts...")
    create_money_evolution_chart(df)
    
    print("Creating reputation evolution charts...")
    create_reputation_evolution_chart(df)
    
    print("Creating trust evolution charts...")
    create_trust_evolution_chart(trust_df)
    
    print("Creating alliance evolution charts...")
    create_alliance_evolution_chart(alliance_df)
    
    print("Creating conflict evolution charts...")
    create_conflict_evolution_chart(conflict_df)
    
    print("Creating mutual trust matrix charts...")
    create_mutual_trust_matrix_chart(trust_df)
    
    print("Creating alliance network comparison chart...")
    create_alliance_network_chart(alliance_df)
    
    print("Creating conflict intensity comparison chart...")
    create_conflict_intensity_chart(conflict_df)
    
    print("Creating relationship dynamics summary...")
    create_relationship_dynamics_summary(trust_df, alliance_df, conflict_df)
    
    print("Creating self-preservation and coalition analysis...")
    create_self_preservation_coalition_chart(trust_df, alliance_df, conflict_df)
    
    print("Creating trust received analysis charts...")
    create_power_dynamics_network_chart(trust_df, alliance_df)
    
    print("Generating summary statistics...")
    print_summary_statistics(df)
    
    print("\n✅ Analysis complete! Charts saved as:")
    print("  - output/analysis/money_evolution_analysis.png")
    print("  - output/analysis/reputation_evolution_analysis.png")
    print("  - output/analysis/trust_evolution_analysis.png")
    print("  - output/analysis/alliance_evolution_analysis.png")
    print("  - output/analysis/conflict_evolution_analysis.png")
    print("  - output/analysis/mutual_trust_matrix_baseline.png")
    print("  - output/analysis/mutual_trust_matrix_altered.png")
    print("  - output/analysis/alliance_network_comparison.png")
    print("  - output/analysis/conflict_intensity_comparison.png")
    print("  - output/analysis/relationship_dynamics_summary.png")
    print("  - output/analysis/self_preservation_coalition_analysis.png")
    print("  - output/analysis/trust_received_analysis_baseline.png")
    print("  - output/analysis/trust_received_analysis_altered.png")

if __name__ == "__main__":
    main()
