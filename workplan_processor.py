"""
Workplan Data Processor for 3-Month Client Engagement
Handles comprehensive task management, timeline tracking, and progress monitoring
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

class TaskPriority(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class TaskStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress" 
    COMPLETED = "Completed"
    BLOCKED = "Blocked"
    ON_HOLD = "On Hold"

@dataclass
class Task:
    id: str
    title: str
    description: str
    category: str
    priority: TaskPriority
    status: TaskStatus
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    dependencies: List[str] = None
    assigned_to: Optional[str] = None
    completion_percentage: float = 0.0
    notes: str = ""
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class WorkplanManager:
    def __init__(self, excel_path: str = None):
        """Initialize workplan manager"""
        self.excel_path = excel_path or '/Users/JDKristenson/Desktop/Client_3_month_initial_workplan.xlsx'
        self.categories = {}
        self.tasks = {}
        self.timeline_weeks = []
        self.load_workplan_data()
        
    def load_workplan_data(self):
        """Load workplan data from Excel and build comprehensive structure"""
        try:
            df = pd.read_excel(self.excel_path, sheet_name='3 Month Workplan')
            self._build_comprehensive_categories()
            self._create_timeline()
            
        except Exception as e:
            print(f"Error loading workplan data: {e}")
            self._create_default_structure()
    
    def _build_comprehensive_categories(self):
        """Build out comprehensive category structure with detailed tasks"""
        
        # Category 1: Business Operations Development (2 people)
        business_ops_tasks = [
            {
                "id": "BO001",
                "title": "Business Requirements Assessment",
                "description": "Assess and consolidate program needs and future state business requirements to operate at significantly higher scale",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 40,
                "subtasks": [
                    "Conduct stakeholder interviews",
                    "Document current state processes",
                    "Identify scaling bottlenecks",
                    "Define future state requirements",
                    "Create requirements consolidation report"
                ]
            },
            {
                "id": "BO002", 
                "title": "Future State Operating Model",
                "description": "Build on prior assessments to finalize target future state business operating model and implementation plans for each business discipline",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 60,
                "dependencies": ["BO001"],
                "subtasks": [
                    "Review prior assessment findings",
                    "Design target operating model",
                    "Create discipline-specific implementation plans",
                    "Define organizational structure",
                    "Document process flows"
                ]
            },
            {
                "id": "BO003",
                "title": "Business Discipline Maturity Framework",
                "description": "Codify requisite business discipline maturity, with associated 'heatmap' to prioritize development",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 32,
                "dependencies": ["BO002"],
                "subtasks": [
                    "Define maturity levels for each discipline",
                    "Assess current maturity state",
                    "Create maturity heatmap",
                    "Prioritize development areas",
                    "Document maturity framework"
                ]
            },
            {
                "id": "BO004",
                "title": "Implementation Plan Execution",
                "description": "Support implementation plan execution, with initial emphasis on HR, technology, and contract compliance",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 80,
                "dependencies": ["BO003"],
                "subtasks": [
                    "Establish HR implementation workstream",
                    "Launch technology upgrade initiatives",
                    "Implement contract compliance framework",
                    "Monitor implementation progress",
                    "Provide ongoing execution support"
                ]
            },
            {
                "id": "BO005",
                "title": "Progress Monitoring & Reporting",
                "description": "Monitor, evaluate, and report implementation progress",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 24,
                "dependencies": ["BO004"],
                "subtasks": [
                    "Establish progress tracking metrics",
                    "Create reporting templates",
                    "Conduct weekly progress reviews",
                    "Generate monthly progress reports",
                    "Present findings to leadership"
                ]
            },
            {
                "id": "BO006",
                "title": "Business Operations Rhythm",
                "description": "Establish long-term business operations operating rhythm, to include governance, decision rights, and meeting/decision cadence",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 36,
                "dependencies": ["BO002"],
                "subtasks": [
                    "Design governance structure",
                    "Define decision rights matrix",
                    "Establish meeting cadences",
                    "Create decision-making processes",
                    "Document operating rhythm"
                ]
            },
            {
                "id": "BO007",
                "title": "Risk & Opportunity Register",
                "description": "Document and codify risk and opportunity register for regular Client leadership review",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 28,
                "subtasks": [
                    "Identify program risks and opportunities",
                    "Create risk assessment framework",
                    "Establish opportunity evaluation process",
                    "Document register format",
                    "Schedule regular leadership reviews"
                ]
            },
            {
                "id": "BO008",
                "title": "Stakeholder Engagement Support",
                "description": "Support Client engagement with key program stakeholders",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 32,
                "subtasks": [
                    "Map key stakeholders",
                    "Develop engagement strategy",
                    "Prepare stakeholder communications",
                    "Facilitate stakeholder meetings",
                    "Maintain stakeholder relationships"
                ]
            }
        ]
        
        # Category 2: Financial Excellence (2 people)
        financial_tasks = [
            {
                "id": "FE001",
                "title": "Interim CFO Function",
                "description": "Serve in an interim 'CFO' function for Client",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 120,
                "subtasks": [
                    "Establish CFO operational framework",
                    "Implement financial controls",
                    "Oversee cash flow management",
                    "Provide strategic financial guidance",
                    "Report to board/leadership"
                ]
            },
            {
                "id": "FE002",
                "title": "Financial Data Integration",
                "description": "Collect, integrate and analyze financial inputs from each Client activity",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 48,
                "dependencies": ["FE001"],
                "subtasks": [
                    "Map all financial data sources",
                    "Establish data collection processes",
                    "Create integration workflows",
                    "Develop analytical frameworks",
                    "Generate integrated reports"
                ]
            },
            {
                "id": "FE003",
                "title": "Integrated Financial Model",
                "description": "Build upon prior models to create integrated financial model for expansion program",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 56,
                "dependencies": ["FE002"],
                "subtasks": [
                    "Review existing financial models",
                    "Design integrated model architecture",
                    "Build expansion scenario models",
                    "Validate model assumptions",
                    "Document model methodology"
                ]
            },
            {
                "id": "FE004",
                "title": "Scenario & Sensitivity Analysis",
                "description": "Conduct scenario and sensitivity analyses",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 40,
                "dependencies": ["FE003"],
                "subtasks": [
                    "Define scenario parameters",
                    "Build sensitivity analysis framework",
                    "Run multiple scenario models",
                    "Analyze results and implications",
                    "Present findings to leadership"
                ]
            },
            {
                "id": "FE005",
                "title": "Program Risk Identification",
                "description": "Use financial information to identify key program risks at scale",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 32,
                "dependencies": ["FE004"],
                "subtasks": [
                    "Analyze financial risk indicators",
                    "Identify scaling risk factors",
                    "Quantify potential risk impact",
                    "Develop risk mitigation strategies",
                    "Create risk monitoring dashboard"
                ]
            },
            {
                "id": "FE006",
                "title": "Employee Retention Incentives",
                "description": "Work with Client HR lead to incentivize long-term employee retention and platform expansion",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 24,
                "subtasks": [
                    "Analyze current retention metrics",
                    "Design retention incentive programs",
                    "Model financial impact of retention",
                    "Collaborate with HR on implementation",
                    "Monitor program effectiveness"
                ]
            },
            {
                "id": "FE007",
                "title": "Financial Guidance & Decision Support",
                "description": "Provide financial guidance to other Client employees and decisions",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 36,
                "subtasks": [
                    "Establish financial advisory framework",
                    "Create decision support tools",
                    "Provide ongoing financial coaching",
                    "Review major financial decisions",
                    "Document guidance processes"
                ]
            },
            {
                "id": "FE008",
                "title": "Formal FP&A Function",
                "description": "Implement formal FP&A function",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 44,
                "dependencies": ["FE003"],
                "subtasks": [
                    "Design FP&A organizational structure",
                    "Implement planning processes",
                    "Establish budgeting and forecasting",
                    "Create performance analytics",
                    "Train staff on FP&A processes"
                ]
            },
            {
                "id": "FE009",
                "title": "External Stakeholder Support",
                "description": "Support financial inquiries from external Client stakeholders",
                "priority": TaskPriority.LOW,
                "estimated_hours": 20,
                "subtasks": [
                    "Identify external stakeholders",
                    "Prepare stakeholder information packages",
                    "Respond to financial inquiries",
                    "Maintain stakeholder relationships",
                    "Document all interactions"
                ]
            }
        ]
        
        # Category 3: CEO and Client Leadership Support (1 person)
        leadership_tasks = [
            {
                "id": "CL001",
                "title": "Ad Hoc Issue Support",
                "description": "Provide ad hoc support to emergent issues",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 40,
                "subtasks": [
                    "Establish issue escalation process",
                    "Create rapid response framework",
                    "Maintain issue tracking system",
                    "Provide timely issue resolution",
                    "Document lessons learned"
                ]
            },
            {
                "id": "CL002",
                "title": "Presentation & Meeting Materials",
                "description": "Prepare presentation and meeting materials for Client leadership",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 32,
                "subtasks": [
                    "Create presentation templates",
                    "Develop executive dashboard content",
                    "Prepare board meeting materials",
                    "Design stakeholder presentations",
                    "Maintain materials library"
                ]
            },
            {
                "id": "CL003",
                "title": "Direct Meeting Support",
                "description": "Provide direct meeting support to Client leadership",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 48,
                "subtasks": [
                    "Attend leadership meetings",
                    "Provide real-time analytical support",
                    "Take meeting notes and actions",
                    "Follow up on meeting outcomes",
                    "Coordinate meeting logistics"
                ]
            }
        ]
        
        # Organize into categories
        self.categories = {
            "Business Operations Development (2)": {
                "description": "Comprehensive business operations development and scaling support",
                "team_size": 2,
                "total_estimated_hours": sum(task["estimated_hours"] for task in business_ops_tasks),
                "tasks": business_ops_tasks
            },
            "Financial Excellence (2)": {
                "description": "Financial leadership, modeling, and FP&A implementation", 
                "team_size": 2,
                "total_estimated_hours": sum(task["estimated_hours"] for task in financial_tasks),
                "tasks": financial_tasks
            },
            "CEO and Client Leadership Support (1)": {
                "description": "Executive support and leadership meeting facilitation",
                "team_size": 1, 
                "total_estimated_hours": sum(task["estimated_hours"] for task in leadership_tasks),
                "tasks": leadership_tasks
            }
        }
        
        # Create task objects
        for category_name, category_data in self.categories.items():
            for task_data in category_data["tasks"]:
                task = Task(
                    id=task_data["id"],
                    title=task_data["title"],
                    description=task_data["description"],
                    category=category_name,
                    priority=task_data["priority"],
                    status=TaskStatus.NOT_STARTED,
                    estimated_hours=task_data["estimated_hours"],
                    dependencies=task_data.get("dependencies", [])
                )
                self.tasks[task.id] = task
    
    def _create_timeline(self):
        """Create 3-month timeline structure"""
        start_date = datetime(2025, 9, 1)  # Sept 1, 2025
        end_date = datetime(2025, 12, 12)  # Dec 12, 2025
        
        current_date = start_date
        week_num = 1
        
        while current_date <= end_date:
            week_end = min(current_date + timedelta(days=6), end_date)
            self.timeline_weeks.append({
                "week_number": week_num,
                "start_date": current_date,
                "end_date": week_end,
                "month": current_date.strftime("%B %Y"),
                "tasks": []
            })
            current_date += timedelta(days=7)
            week_num += 1
    
    def _create_default_structure(self):
        """Create default structure if Excel loading fails"""
        self._build_comprehensive_categories()
        self._create_timeline()
    
    def get_all_categories(self) -> Dict[str, Any]:
        """Get all categories with their tasks"""
        return self.categories
    
    def get_category_tasks(self, category_name: str) -> List[Dict]:
        """Get all tasks for a specific category"""
        return self.categories.get(category_name, {}).get("tasks", [])
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get specific task by ID"""
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus, completion_percentage: float = None):
        """Update task status and completion"""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            if completion_percentage is not None:
                self.tasks[task_id].completion_percentage = completion_percentage
    
    def update_task_hours(self, task_id: str, actual_hours: int):
        """Update actual hours for a task"""
        if task_id in self.tasks:
            self.tasks[task_id].actual_hours = actual_hours
    
    def assign_task_to_week(self, task_id: str, week_number: int):
        """Assign a task to a specific week"""
        if week_number <= len(self.timeline_weeks):
            week = self.timeline_weeks[week_number - 1]
            if task_id not in week["tasks"]:
                week["tasks"].append(task_id)
    
    def get_timeline_data(self) -> List[Dict]:
        """Get complete timeline data"""
        return self.timeline_weeks
    
    def calculate_category_progress(self, category_name: str) -> Dict[str, float]:
        """Calculate progress metrics for a category"""
        category_tasks = [task for task in self.tasks.values() if task.category == category_name]
        
        if not category_tasks:
            return {"completion": 0.0, "progress": 0.0}
        
        total_tasks = len(category_tasks)
        completed_tasks = sum(1 for task in category_tasks if task.status == TaskStatus.COMPLETED)
        total_progress = sum(task.completion_percentage for task in category_tasks)
        
        estimated_hours = sum(task.estimated_hours or 0 for task in category_tasks)
        actual_hours = sum(task.actual_hours or 0 for task in category_tasks)
        
        return {
            "completion_percentage": (completed_tasks / total_tasks) * 100,
            "average_progress": total_progress / total_tasks,
            "estimated_hours": estimated_hours,
            "actual_hours": actual_hours,
            "hours_variance": actual_hours - estimated_hours if actual_hours > 0 else 0
        }
    
    def get_project_summary(self) -> Dict[str, Any]:
        """Get overall project summary statistics"""
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.COMPLETED)
        in_progress_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.IN_PROGRESS)
        
        total_estimated_hours = sum(task.estimated_hours or 0 for task in self.tasks.values())
        total_actual_hours = sum(task.actual_hours or 0 for task in self.tasks.values())
        
        overall_progress = sum(task.completion_percentage for task in self.tasks.values()) / total_tasks if total_tasks > 0 else 0
        
        # Category breakdowns
        category_summaries = {}
        for category_name in self.categories.keys():
            category_summaries[category_name] = self.calculate_category_progress(category_name)
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "not_started_tasks": total_tasks - completed_tasks - in_progress_tasks,
            "overall_completion": (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0,
            "overall_progress": overall_progress,
            "total_estimated_hours": total_estimated_hours,
            "total_actual_hours": total_actual_hours,
            "hours_variance": total_actual_hours - total_estimated_hours,
            "categories": category_summaries,
            "timeline_weeks": len(self.timeline_weeks)
        }
    
    def save_workplan_data(self, save_path: str = "workplan_data.json"):
        """Save workplan data to JSON"""
        data_to_save = {
            "categories": self.categories,
            "tasks": {task_id: asdict(task) for task_id, task in self.tasks.items()},
            "timeline_weeks": self.timeline_weeks,
            "last_updated": datetime.now().isoformat(),
            "excel_path": self.excel_path
        }
        
        # Convert enums to strings for JSON serialization
        for task_data in data_to_save["tasks"].values():
            task_data["priority"] = task_data["priority"].value if hasattr(task_data["priority"], 'value') else str(task_data["priority"])
            task_data["status"] = task_data["status"].value if hasattr(task_data["status"], 'value') else str(task_data["status"])
        
        with open(save_path, 'w') as f:
            json.dump(data_to_save, f, indent=2, default=str)
    
    def load_workplan_data_from_json(self, load_path: str = "workplan_data.json"):
        """Load saved workplan data"""
        if os.path.exists(load_path):
            try:
                with open(load_path, 'r') as f:
                    data = json.load(f)
                    
                self.categories = data.get("categories", {})
                self.timeline_weeks = data.get("timeline_weeks", [])
                
                # Reconstruct task objects
                tasks_data = data.get("tasks", {})
                for task_id, task_data in tasks_data.items():
                    # Convert string enums back to enum objects
                    priority_str = task_data.get("priority", "Medium")
                    status_str = task_data.get("status", "Not Started")
                    
                    task = Task(
                        id=task_data["id"],
                        title=task_data["title"],
                        description=task_data["description"],
                        category=task_data["category"],
                        priority=TaskPriority(priority_str) if isinstance(priority_str, str) else priority_str,
                        status=TaskStatus(status_str) if isinstance(status_str, str) else status_str,
                        start_date=datetime.fromisoformat(task_data["start_date"]) if task_data.get("start_date") else None,
                        end_date=datetime.fromisoformat(task_data["end_date"]) if task_data.get("end_date") else None,
                        estimated_hours=task_data.get("estimated_hours"),
                        actual_hours=task_data.get("actual_hours"),
                        dependencies=task_data.get("dependencies", []),
                        assigned_to=task_data.get("assigned_to"),
                        completion_percentage=task_data.get("completion_percentage", 0.0),
                        notes=task_data.get("notes", "")
                    )
                    self.tasks[task_id] = task
                    
                return True
            except Exception as e:
                print(f"Error loading workplan data: {e}")
                return False
        return False

# Helper function
def initialize_workplan_manager(excel_path: str = None) -> WorkplanManager:
    """Initialize workplan manager"""
    return WorkplanManager(excel_path)