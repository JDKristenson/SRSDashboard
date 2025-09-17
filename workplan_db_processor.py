"""
Database-backed Workplan Data Processor for Cloud Deployment
Handles comprehensive task management with PostgreSQL backend
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import streamlit as st

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
    subtasks: List[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.subtasks is None:
            self.subtasks = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class DatabaseManager:
    def __init__(self):
        """Initialize database connection"""
        self.connection = None
        self.connect()
    
    def get_db_url(self):
        """Get database URL from environment or Streamlit secrets"""
        # Try Streamlit secrets first (for cloud deployment)
        try:
            if hasattr(st, 'secrets') and 'database' in st.secrets:
                return st.secrets['database']['url']
        except:
            pass
        
        # Try environment variable
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            return db_url
            
        # Fallback to local PostgreSQL for development
        return "postgresql://localhost:5432/workplan_db"
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            db_url = self.get_db_url()
            self.connection = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
            self.connection.autocommit = True
            self.init_database()
        except Exception as e:
            print(f"Database connection error: {e}")
            # For development/demo, we'll use a fallback
            self.connection = None
    
    def init_database(self):
        """Initialize database tables"""
        if not self.connection:
            return
            
        cursor = self.connection.cursor()
        
        # Create categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                team_size INTEGER DEFAULT 1,
                total_estimated_hours INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id VARCHAR(50) PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                description TEXT,
                category VARCHAR(255) REFERENCES categories(name),
                priority VARCHAR(20) DEFAULT 'Medium',
                status VARCHAR(20) DEFAULT 'Not Started',
                start_date DATE,
                end_date DATE,
                estimated_hours INTEGER,
                actual_hours INTEGER,
                dependencies TEXT[], -- Array of task IDs
                assigned_to VARCHAR(255),
                completion_percentage FLOAT DEFAULT 0.0,
                notes TEXT,
                subtasks TEXT[], -- Array of subtask descriptions
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create timeline weeks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeline_weeks (
                id SERIAL PRIMARY KEY,
                week_number INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                month VARCHAR(50),
                assigned_tasks TEXT[], -- Array of task IDs
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.close()
        print("Database initialized successfully")

class WorkplanDatabaseManager:
    def __init__(self):
        """Initialize workplan database manager"""
        self.db = DatabaseManager()
        self.categories = {}
        self.tasks = {}
        self.timeline_weeks = []
        self.initialize_data()
        
    def initialize_data(self):
        """Initialize data from database or create default data"""
        if not self.db.connection:
            # Fallback to in-memory data for demo
            self._create_default_data()
            return
            
        try:
            self._load_from_database()
            if not self.categories:  # If database is empty, populate with default data
                self._populate_default_data()
        except Exception as e:
            print(f"Error loading from database: {e}")
            self._create_default_data()
    
    def _load_from_database(self):
        """Load all data from database"""
        if not self.db.connection:
            return
            
        cursor = self.db.connection.cursor()
        
        # Load categories
        cursor.execute("SELECT * FROM categories ORDER BY name")
        for row in cursor.fetchall():
            self.categories[row['name']] = {
                'description': row['description'],
                'team_size': row['team_size'],
                'total_estimated_hours': row['total_estimated_hours'],
                'tasks': []
            }
        
        # Load tasks
        cursor.execute("SELECT * FROM tasks ORDER BY id")
        for row in cursor.fetchall():
            task = Task(
                id=row['id'],
                title=row['title'],
                description=row['description'] or '',
                category=row['category'],
                priority=TaskPriority(row['priority']),
                status=TaskStatus(row['status']),
                start_date=row['start_date'],
                end_date=row['end_date'],
                estimated_hours=row['estimated_hours'],
                actual_hours=row['actual_hours'],
                dependencies=row['dependencies'] or [],
                assigned_to=row['assigned_to'],
                completion_percentage=row['completion_percentage'],
                notes=row['notes'] or '',
                subtasks=row['subtasks'] or [],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            self.tasks[task.id] = task
            
            # Add to category tasks
            if task.category in self.categories:
                task_dict = {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'priority': task.priority,
                    'estimated_hours': task.estimated_hours,
                    'subtasks': task.subtasks
                }
                self.categories[task.category]['tasks'].append(task_dict)
        
        # Load timeline weeks
        cursor.execute("SELECT * FROM timeline_weeks ORDER BY week_number")
        for row in cursor.fetchall():
            self.timeline_weeks.append({
                'week_number': row['week_number'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'month': row['month'],
                'tasks': row['assigned_tasks'] or []
            })
        
        cursor.close()
    
    def _populate_default_data(self):
        """Populate database with default workplan data"""
        if not self.db.connection:
            return
            
        cursor = self.db.connection.cursor()
        
        # Insert categories
        categories_data = [
            ("Business Operations Development (2)", "Comprehensive business operations development and scaling support", 2, 332),
            ("Financial Excellence (2)", "Financial leadership, modeling, and FP&A implementation", 2, 420),
            ("CEO and Client Leadership Support (1)", "Executive support and leadership meeting facilitation", 1, 120)
        ]
        
        for name, desc, team_size, hours in categories_data:
            cursor.execute("""
                INSERT INTO categories (name, description, team_size, total_estimated_hours)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (name) DO NOTHING
            """, (name, desc, team_size, hours))
        
        # Insert tasks with comprehensive data
        tasks_data = self._get_default_tasks_data()
        
        for task_data in tasks_data:
            cursor.execute("""
                INSERT INTO tasks (
                    id, title, description, category, priority, estimated_hours, subtasks
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                task_data['id'],
                task_data['title'],
                task_data['description'],
                task_data['category'],
                task_data['priority'].value,
                task_data['estimated_hours'],
                task_data['subtasks']
            ))
        
        # Insert timeline weeks
        self._create_timeline_weeks()
        
        cursor.close()
        
        # Reload data
        self._load_from_database()
    
    def _get_default_tasks_data(self):
        """Get default tasks data structure - all 20 tasks"""
        return [
            # Business Operations Development tasks (8 tasks)
            {
                "id": "BO001",
                "title": "Business Requirements Assessment",
                "description": "Assess and consolidate program needs and future state business requirements to operate at significantly higher scale",
                "category": "Business Operations Development (2)",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 40,
                "subtasks": ["Conduct stakeholder interviews", "Document current state processes", "Identify scaling bottlenecks", "Define future state requirements", "Create requirements consolidation report"]
            },
            {
                "id": "BO002", 
                "title": "Future State Operating Model",
                "description": "Build on prior assessments to finalize target future state business operating model and implementation plans for each business discipline",
                "category": "Business Operations Development (2)",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 60,
                "subtasks": ["Review prior assessment findings", "Design target operating model", "Create discipline-specific implementation plans", "Define organizational structure", "Document process flows"]
            },
            {
                "id": "BO003",
                "title": "Business Discipline Maturity Framework",
                "description": "Codify requisite business discipline maturity, with associated 'heatmap' to prioritize development",
                "category": "Business Operations Development (2)",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 32,
                "subtasks": ["Define maturity levels for each discipline", "Assess current maturity state", "Create maturity heatmap", "Prioritize development areas", "Document maturity framework"]
            },
            {
                "id": "BO004",
                "title": "Implementation Plan Execution",
                "description": "Support implementation plan execution, with initial emphasis on HR, technology, and contract compliance",
                "category": "Business Operations Development (2)",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 80,
                "subtasks": ["Establish HR implementation workstream", "Launch technology upgrade initiatives", "Implement contract compliance framework", "Monitor implementation progress", "Provide ongoing execution support"]
            },
            {
                "id": "BO005",
                "title": "Progress Monitoring & Reporting",
                "description": "Monitor, evaluate, and report implementation progress",
                "category": "Business Operations Development (2)",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 24,
                "subtasks": ["Establish progress tracking metrics", "Create reporting templates", "Conduct weekly progress reviews", "Generate monthly progress reports", "Present findings to leadership"]
            },
            {
                "id": "BO006",
                "title": "Business Operations Rhythm",
                "description": "Establish long-term business operations operating rhythm, to include governance, decision rights, and meeting/decision cadence",
                "category": "Business Operations Development (2)",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 36,
                "subtasks": ["Design governance structure", "Define decision rights matrix", "Establish meeting cadences", "Create decision-making processes", "Document operating rhythm"]
            },
            {
                "id": "BO007",
                "title": "Risk & Opportunity Register",
                "description": "Document and codify risk and opportunity register for regular Client leadership review",
                "category": "Business Operations Development (2)",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 28,
                "subtasks": ["Identify program risks and opportunities", "Create risk assessment framework", "Establish opportunity evaluation process", "Document register format", "Schedule regular leadership reviews"]
            },
            {
                "id": "BO008",
                "title": "Stakeholder Engagement Support",
                "description": "Support Client engagement with key program stakeholders",
                "category": "Business Operations Development (2)",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 32,
                "subtasks": ["Map key stakeholders", "Develop engagement strategy", "Prepare stakeholder communications", "Facilitate stakeholder meetings", "Maintain stakeholder relationships"]
            },
            # Financial Excellence tasks (9 tasks)
            {
                "id": "FE001",
                "title": "Interim CFO Function",
                "description": "Serve in an interim 'CFO' function for Client",
                "category": "Financial Excellence (2)",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 120,
                "subtasks": ["Establish CFO operational framework", "Implement financial controls", "Oversee cash flow management", "Provide strategic financial guidance", "Report to board/leadership"]
            },
            {
                "id": "FE002",
                "title": "Financial Data Integration",
                "description": "Collect, integrate and analyze financial inputs from each Client activity",
                "category": "Financial Excellence (2)",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 48,
                "subtasks": ["Map all financial data sources", "Establish data collection processes", "Create integration workflows", "Develop analytical frameworks", "Generate integrated reports"]
            },
            {
                "id": "FE003",
                "title": "Integrated Financial Model",
                "description": "Build upon prior models to create integrated financial model for expansion program",
                "category": "Financial Excellence (2)",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 56,
                "subtasks": ["Review existing financial models", "Design integrated model architecture", "Build expansion scenario models", "Validate model assumptions", "Document model methodology"]
            },
            {
                "id": "FE004",
                "title": "Scenario & Sensitivity Analysis",
                "description": "Conduct scenario and sensitivity analyses",
                "category": "Financial Excellence (2)",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 40,
                "subtasks": ["Define scenario parameters", "Build sensitivity analysis framework", "Run multiple scenario models", "Analyze results and implications", "Present findings to leadership"]
            },
            {
                "id": "FE005",
                "title": "Program Risk Identification",
                "description": "Use financial information to identify key program risks at scale",
                "category": "Financial Excellence (2)",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 32,
                "subtasks": ["Analyze financial risk indicators", "Identify scaling risk factors", "Quantify potential risk impact", "Develop risk mitigation strategies", "Create risk monitoring dashboard"]
            },
            {
                "id": "FE006",
                "title": "Employee Retention Incentives",
                "description": "Work with Client HR lead to incentivize long-term employee retention and platform expansion",
                "category": "Financial Excellence (2)",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 24,
                "subtasks": ["Analyze current retention metrics", "Design retention incentive programs", "Model financial impact of retention", "Collaborate with HR on implementation", "Monitor program effectiveness"]
            },
            {
                "id": "FE007",
                "title": "Financial Guidance & Decision Support",
                "description": "Provide financial guidance to other Client employees and decisions",
                "category": "Financial Excellence (2)",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 36,
                "subtasks": ["Establish financial advisory framework", "Create decision support tools", "Provide ongoing financial coaching", "Review major financial decisions", "Document guidance processes"]
            },
            {
                "id": "FE008",
                "title": "Formal FP&A Function",
                "description": "Implement formal FP&A function",
                "category": "Financial Excellence (2)",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 44,
                "subtasks": ["Design FP&A organizational structure", "Implement planning processes", "Establish budgeting and forecasting", "Create performance analytics", "Train staff on FP&A processes"]
            },
            {
                "id": "FE009",
                "title": "External Stakeholder Support",
                "description": "Support financial inquiries from external Client stakeholders",
                "category": "Financial Excellence (2)",
                "priority": TaskPriority.LOW,
                "estimated_hours": 20,
                "subtasks": ["Identify external stakeholders", "Prepare stakeholder information packages", "Respond to financial inquiries", "Maintain stakeholder relationships", "Document all interactions"]
            },
            # CEO and Client Leadership Support tasks (3 tasks)
            {
                "id": "CL001",
                "title": "Ad Hoc Issue Support",
                "description": "Provide ad hoc support to emergent issues",
                "category": "CEO and Client Leadership Support (1)",
                "priority": TaskPriority.HIGH,
                "estimated_hours": 40,
                "subtasks": ["Establish issue escalation process", "Create rapid response framework", "Maintain issue tracking system", "Provide timely issue resolution", "Document lessons learned"]
            },
            {
                "id": "CL002",
                "title": "Presentation & Meeting Materials",
                "description": "Prepare presentation and meeting materials for Client leadership",
                "category": "CEO and Client Leadership Support (1)",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 32,
                "subtasks": ["Create presentation templates", "Develop executive dashboard content", "Prepare board meeting materials", "Design stakeholder presentations", "Maintain materials library"]
            },
            {
                "id": "CL003",
                "title": "Direct Meeting Support",
                "description": "Provide direct meeting support to Client leadership",
                "category": "CEO and Client Leadership Support (1)",
                "priority": TaskPriority.MEDIUM,
                "estimated_hours": 48,
                "subtasks": ["Attend leadership meetings", "Provide real-time analytical support", "Take meeting notes and actions", "Follow up on meeting outcomes", "Coordinate meeting logistics"]
            }
        ]
    
    def _create_timeline_weeks(self):
        """Create timeline weeks in database"""
        if not self.db.connection:
            return
            
        cursor = self.db.connection.cursor()
        
        start_date = datetime(2025, 9, 1)
        end_date = datetime(2025, 12, 12)
        current_date = start_date
        week_num = 1
        
        while current_date <= end_date:
            week_end = min(current_date + timedelta(days=6), end_date)
            
            cursor.execute("""
                INSERT INTO timeline_weeks (week_number, start_date, end_date, month, assigned_tasks)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                week_num,
                current_date.date(),
                week_end.date(),
                current_date.strftime("%B %Y"),
                []
            ))
            
            current_date += timedelta(days=7)
            week_num += 1
        
        cursor.close()
    
    def _create_default_data(self):
        """Create default in-memory data for fallback"""
        # Create default data structure when database is not available
        self._build_default_categories_structure()
        self._build_default_tasks_structure()
        self._build_default_timeline_structure()
    
    def _build_default_categories_structure(self):
        """Build default categories structure"""
        self.categories = {
            "Business Operations Development (2)": {
                'description': "Comprehensive business operations development and scaling support",
                'team_size': 2,
                'total_estimated_hours': 332,
                'tasks': []
            },
            "Financial Excellence (2)": {
                'description': "Financial leadership, modeling, and FP&A implementation", 
                'team_size': 2,
                'total_estimated_hours': 420,
                'tasks': []
            },
            "CEO and Client Leadership Support (1)": {
                'description': "Executive support and leadership meeting facilitation",
                'team_size': 1, 
                'total_estimated_hours': 120,
                'tasks': []
            }
        }
    
    def _build_default_tasks_structure(self):
        """Build default tasks structure"""
        tasks_data = self._get_default_tasks_data()
        
        # Create task objects and populate categories
        for task_data in tasks_data:
            task = Task(
                id=task_data["id"],
                title=task_data["title"],
                description=task_data["description"],
                category=task_data["category"],
                priority=task_data["priority"],
                status=TaskStatus.NOT_STARTED,
                estimated_hours=task_data["estimated_hours"],
                subtasks=task_data["subtasks"]
            )
            self.tasks[task.id] = task
            
            # Add to category tasks
            if task.category in self.categories:
                task_dict = {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'priority': task.priority,
                    'estimated_hours': task.estimated_hours,
                    'subtasks': task.subtasks
                }
                self.categories[task.category]['tasks'].append(task_dict)
    
    def _build_default_timeline_structure(self):
        """Build default timeline structure"""
        start_date = datetime(2025, 9, 1)
        end_date = datetime(2025, 12, 12)
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
    
    # Database operations
    def save_task(self, task: Task):
        """Save or update task in database"""
        if not self.db.connection:
            return
            
        cursor = self.db.connection.cursor()
        
        cursor.execute("""
            INSERT INTO tasks (
                id, title, description, category, priority, status,
                start_date, end_date, estimated_hours, actual_hours,
                dependencies, assigned_to, completion_percentage, notes,
                subtasks, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                priority = EXCLUDED.priority,
                status = EXCLUDED.status,
                start_date = EXCLUDED.start_date,
                end_date = EXCLUDED.end_date,
                estimated_hours = EXCLUDED.estimated_hours,
                actual_hours = EXCLUDED.actual_hours,
                dependencies = EXCLUDED.dependencies,
                assigned_to = EXCLUDED.assigned_to,
                completion_percentage = EXCLUDED.completion_percentage,
                notes = EXCLUDED.notes,
                subtasks = EXCLUDED.subtasks,
                updated_at = EXCLUDED.updated_at
        """, (
            task.id, task.title, task.description, task.category,
            task.priority.value, task.status.value,
            task.start_date, task.end_date, task.estimated_hours, task.actual_hours,
            task.dependencies, task.assigned_to, task.completion_percentage,
            task.notes, task.subtasks, datetime.now()
        ))
        
        cursor.close()
    
    def update_task_title(self, task_id: str, new_title: str):
        """Update task title"""
        if task_id in self.tasks:
            self.tasks[task_id].title = new_title
            self.tasks[task_id].updated_at = datetime.now()
            self.save_task(self.tasks[task_id])
            return True
        return False
    
    def update_task_description(self, task_id: str, new_description: str):
        """Update task description"""
        if task_id in self.tasks:
            self.tasks[task_id].description = new_description
            self.tasks[task_id].updated_at = datetime.now()
            self.save_task(self.tasks[task_id])
            return True
        return False
    
    def update_task_status(self, task_id: str, status: TaskStatus, completion_percentage: float = None):
        """Update task status and completion"""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            if completion_percentage is not None:
                self.tasks[task_id].completion_percentage = completion_percentage
            self.tasks[task_id].updated_at = datetime.now()
            self.save_task(self.tasks[task_id])
    
    def update_task_hours(self, task_id: str, actual_hours: int):
        """Update actual hours for a task"""
        if task_id in self.tasks:
            self.tasks[task_id].actual_hours = actual_hours
            self.tasks[task_id].updated_at = datetime.now()
            self.save_task(self.tasks[task_id])
    
    def create_new_task(self, category: str, title: str, description: str, priority: str, estimated_hours: int):
        """Create a new task"""
        # Generate new task ID
        category_prefix = {
            "Business Operations Development (2)": "BO",
            "Financial Excellence (2)": "FE",
            "CEO and Client Leadership Support (1)": "CL"
        }.get(category, "XX")
        
        # Find next available ID number
        existing_ids = [task_id for task_id in self.tasks.keys() if task_id.startswith(category_prefix)]
        next_num = len(existing_ids) + 1
        new_id = f"{category_prefix}{next_num:03d}"
        
        # Ensure unique ID
        while new_id in self.tasks:
            next_num += 1
            new_id = f"{category_prefix}{next_num:03d}"
        
        # Create new task
        new_task = Task(
            id=new_id,
            title=title,
            description=description,
            category=category,
            priority=TaskPriority(priority),
            status=TaskStatus.NOT_STARTED,
            estimated_hours=estimated_hours
        )
        
        self.tasks[new_id] = new_task
        self.save_task(new_task)
        
        return new_id
    
    # Read operations
    def get_all_categories(self) -> Dict[str, Any]:
        """Get all categories with their tasks"""
        return self.categories
    
    def get_category_tasks(self, category_name: str) -> List[Dict]:
        """Get all tasks for a specific category"""
        return self.categories.get(category_name, {}).get("tasks", [])
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get specific task by ID"""
        return self.tasks.get(task_id)
    
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

# Helper function
def initialize_workplan_db_manager() -> WorkplanDatabaseManager:
    """Initialize workplan database manager"""
    return WorkplanDatabaseManager()