"""
Cloud-Ready 3-Month Client Workplan Dashboard with Database Backend
Full wiki-style editing capabilities with PostgreSQL persistence
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import json
import os
from datetime import datetime, timedelta
from workplan_db_processor import initialize_workplan_db_manager, TaskStatus, TaskPriority

# Configure Streamlit page
st.set_page_config(
    page_title="3-Month Workplan Dashboard",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme management
if 'theme' not in st.session_state:
    st.session_state.theme = 'system'

def apply_theme():
    """Apply selected theme"""
    if st.session_state.theme == 'dark':
        theme_colors = {
            'bg_color': '#1e1e1e',
            'text_color': '#ffffff', 
            'card_bg': '#2d2d2d',
            'border_color': '#404040'
        }
    elif st.session_state.theme == 'light':
        theme_colors = {
            'bg_color': '#ffffff',
            'text_color': '#000000',
            'card_bg': '#f8f9fa', 
            'border_color': '#e9ecef'
        }
    else:  # system
        theme_colors = {
            'bg_color': 'var(--background-color)',
            'text_color': 'var(--text-color)',
            'card_bg': 'var(--secondary-background-color)',
            'border_color': 'var(--border-color)'
        }
    return theme_colors

# Apply theme and custom CSS
theme_colors = apply_theme()

st.markdown(f"""
<style>
    .metric-container {{
        background-color: {theme_colors['card_bg']};
        border: 1px solid {theme_colors['border_color']};
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        color: {theme_colors['text_color']};
    }}
    .category-header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        text-align: center;
        font-weight: bold;
    }}
    .task-card {{
        background-color: {theme_colors['card_bg']};
        border: 1px solid {theme_colors['border_color']};
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: {theme_colors['text_color']};
    }}
    .editable-field {{
        border: 1px dashed {theme_colors['border_color']};
        padding: 5px;
        border-radius: 4px;
        cursor: text;
        min-height: 20px;
    }}
    .editable-field:hover {{
        background-color: {theme_colors['border_color']};
        opacity: 0.7;
    }}
    .priority-high {{ border-left: 4px solid #dc3545; }}
    .priority-medium {{ border-left: 4px solid #ffc107; }}
    .priority-low {{ border-left: 4px solid #28a745; }}
    .status-completed {{ background-color: #d4edda; }}
    .status-in-progress {{ background-color: #fff3cd; }}
    .status-not-started {{ background-color: #f8d7da; }}
    .timeline-week {{
        background-color: {theme_colors['card_bg']};
        border: 1px solid {theme_colors['border_color']};
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
        color: {theme_colors['text_color']};
    }}
    .subtask-item {{
        background-color: {theme_colors['card_bg']};
        border: 1px solid {theme_colors['border_color']};
        border-radius: 4px;
        padding: 5px 10px;
        margin: 3px 0;
        font-size: 0.9em;
        color: {theme_colors['text_color']};
        cursor: pointer;
    }}
    .subtask-item:hover {{
        background-color: {theme_colors['border_color']};
    }}
    .cloud-indicator {{
        position: fixed;
        top: 10px;
        right: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        z-index: 999;
    }}
</style>
""", unsafe_allow_html=True)

# Cloud deployment indicator
st.markdown('<div class="cloud-indicator">☁️ Cloud Ready</div>', unsafe_allow_html=True)

def render_theme_selector():
    """Render theme selector in sidebar"""
    st.sidebar.markdown("### 🎨 Theme")
    
    theme_options = {
        "🌅 Light": "light",
        "🌙 Dark": "dark", 
        "💻 System": "system"
    }
    
    current_theme = st.session_state.get('theme', 'system')
    
    # Find current theme label
    current_label = "💻 System"  # default
    for label, value in theme_options.items():
        if value == current_theme:
            current_label = label
            break
    
    new_theme_label = st.sidebar.selectbox(
        "Select Theme",
        options=list(theme_options.keys()),
        index=list(theme_options.keys()).index(current_label),
        key="theme_selector"
    )
    
    new_theme = theme_options[new_theme_label]
    if new_theme != current_theme:
        st.session_state.theme = new_theme
        st.rerun()

def inline_text_edit(label, current_value, key, manager=None, update_func=None):
    """Create an inline editable text field with database persistence"""
    # Initialize editing state
    edit_key = f"editing_{key}"
    if edit_key not in st.session_state:
        st.session_state[edit_key] = False
    
    col1, col2 = st.columns([6, 1])
    
    with col2:
        if st.session_state[edit_key]:
            if st.button("💾", key=f"save_{key}", help="Save changes"):
                new_value = st.session_state.get(f"input_{key}", current_value)
                if update_func and manager and new_value != current_value:
                    success = update_func(manager, new_value)
                    if success:
                        st.success(f"✅ Updated {label}!")
                    else:
                        st.error(f"❌ Failed to update {label}")
                st.session_state[edit_key] = False
                st.rerun()
        else:
            if st.button("✏️", key=f"edit_{key}", help=f"Edit {label}"):
                st.session_state[edit_key] = True
                st.session_state[f"input_{key}"] = current_value
                st.rerun()
    
    with col1:
        if st.session_state[edit_key]:
            new_value = st.text_input(
                f"Edit {label}",
                value=st.session_state.get(f"input_{key}", current_value),
                key=f"input_{key}",
                label_visibility="collapsed"
            )
            st.session_state[f"input_{key}"] = new_value
        else:
            st.write(f"**{current_value}**")
    
    return current_value

def inline_text_area_edit(label, current_value, key, manager=None, update_func=None):
    """Create an inline editable text area field with database persistence"""
    # Initialize editing state
    edit_key = f"editing_{key}"
    if edit_key not in st.session_state:
        st.session_state[edit_key] = False
    
    col1, col2 = st.columns([6, 1])
    
    with col2:
        if st.session_state[edit_key]:
            if st.button("💾", key=f"save_{key}", help="Save changes"):
                new_value = st.session_state.get(f"textarea_{key}", current_value)
                if update_func and manager and new_value != current_value:
                    success = update_func(manager, new_value)
                    if success:
                        st.success(f"✅ Updated {label}!")
                    else:
                        st.error(f"❌ Failed to update {label}")
                st.session_state[edit_key] = False
                st.rerun()
        else:
            if st.button("✏️", key=f"edit_{key}", help=f"Edit {label}"):
                st.session_state[edit_key] = True
                st.session_state[f"textarea_{key}"] = current_value
                st.rerun()
    
    with col1:
        if st.session_state[edit_key]:
            new_value = st.text_area(
                f"Edit {label}",
                value=st.session_state.get(f"textarea_{key}", current_value),
                key=f"textarea_{key}",
                label_visibility="collapsed",
                height=100
            )
            st.session_state[f"textarea_{key}"] = new_value
        else:
            st.write(current_value)
    
    return current_value

@st.cache_resource
def load_workplan_data():
    """Load and cache workplan database manager"""
    try:
        manager = initialize_workplan_db_manager()
        return manager
    except Exception as e:
        st.error(f"Error loading workplan data: {e}")
        return None

def create_category_overview_chart(manager):
    """Create overview chart showing category progress"""
    categories = manager.get_all_categories()
    
    category_names = []
    estimated_hours = []
    actual_hours = []
    completion_percentages = []
    
    for category_name, category_data in categories.items():
        progress = manager.calculate_category_progress(category_name)
        category_names.append(category_name.replace(" (2)", "").replace(" (1)", ""))
        estimated_hours.append(progress["estimated_hours"])
        actual_hours.append(progress["actual_hours"])
        completion_percentages.append(progress["completion_percentage"])
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Hours Breakdown', 'Completion Progress'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Hours chart
    fig.add_trace(
        go.Bar(name='Estimated Hours', x=category_names, y=estimated_hours, 
               marker_color='lightblue', offsetgroup=1),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name='Actual Hours', x=category_names, y=actual_hours,
               marker_color='darkblue', offsetgroup=2),
        row=1, col=1
    )
    
    # Completion chart
    fig.add_trace(
        go.Bar(name='Completion %', x=category_names, y=completion_percentages,
               marker_color='green', text=[f'{x:.1f}%' for x in completion_percentages],
               textposition='outside'),
        row=1, col=2
    )
    
    fig.update_layout(
        title_text="Category Overview Dashboard",
        height=500,
        showlegend=True
    )
    
    return fig

def create_task_status_pie_chart(manager):
    """Create pie chart showing task status distribution"""
    status_counts = {}
    for task in manager.tasks.values():
        status = task.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if status_counts:
        fig = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            title="Task Status Distribution",
            color_discrete_map={
                'Not Started': '#ff6b6b',
                'In Progress': '#feca57',
                'Completed': '#48cab2',
                'Blocked': '#ff9ff3',
                'On Hold': '#a55eea'
            }
        )
        return fig
    return None

def update_task_title_wrapper(manager, task_id, new_title):
    """Wrapper for updating task title"""
    return manager.update_task_title(task_id, new_title)

def update_task_description_wrapper(manager, task_id, new_description):
    """Wrapper for updating task description"""
    return manager.update_task_description(task_id, new_description)

def render_task_details(manager, task_id):
    """Render detailed task view with full database-backed inline editing"""
    task = manager.get_task_by_id(task_id)
    if not task:
        st.error("Task not found")
        return False
    
    changes_made = False
    
    st.markdown(f'<div class="task-card priority-{task.priority.value.lower()}">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Editable task title with database persistence
        st.subheader("🎯 Task Title")
        inline_text_edit(
            "Task Title",
            task.title,
            f"title_{task_id}",
            manager,
            lambda mgr, val: update_task_title_wrapper(mgr, task_id, val)
        )
        
        st.write(f"**ID:** {task.id}")
        st.write(f"**Category:** {task.category}")
        
        # Editable task description with database persistence
        st.write("**Description:**")
        inline_text_area_edit(
            "Description",
            task.description,
            f"desc_{task_id}",
            manager,
            lambda mgr, val: update_task_description_wrapper(mgr, task_id, val)
        )
        
        # Display subtasks (editable in future version)
        if task.subtasks:
            st.write("**Subtasks:**")
            for i, subtask in enumerate(task.subtasks):
                st.markdown(f'<div class="subtask-item">• {subtask}</div>', unsafe_allow_html=True)
    
    with col2:
        st.write("**Task Management:**")
        
        # Status update
        current_status = task.status.value
        new_status = st.selectbox(
            "Status",
            options=[status.value for status in TaskStatus],
            index=[status.value for status in TaskStatus].index(current_status),
            key=f"status_{task_id}"
        )
        
        if new_status != current_status:
            manager.update_task_status(task_id, TaskStatus(new_status))
            changes_made = True
            st.success("✅ Status updated!")
        
        # Completion percentage
        completion = st.slider(
            "Completion %",
            min_value=0.0,
            max_value=100.0,
            value=task.completion_percentage,
            step=5.0,
            key=f"completion_{task_id}"
        )
        
        if completion != task.completion_percentage:
            manager.update_task_status(task_id, task.status, completion)
            changes_made = True
            st.success("✅ Progress updated!")
        
        # Hours tracking
        estimated_hours = task.estimated_hours or 0
        actual_hours = st.number_input(
            f"Actual Hours (Est: {estimated_hours}h)",
            min_value=0,
            value=task.actual_hours or 0,
            key=f"hours_{task_id}"
        )
        
        if actual_hours != (task.actual_hours or 0):
            manager.update_task_hours(task_id, actual_hours)
            changes_made = True
            st.success("✅ Hours updated!")
        
        # Progress bar
        st.progress(completion / 100.0)
        
        # Dependencies
        if task.dependencies:
            st.write("**Dependencies:**")
            for dep in task.dependencies:
                dep_task = manager.get_task_by_id(dep)
                if dep_task:
                    dep_status = "✅" if dep_task.status == TaskStatus.COMPLETED else "⏳"
                    st.write(f"{dep_status} {dep}: {dep_task.title}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    return changes_made

def render_new_task_form(manager):
    """Render form to create new tasks with database persistence"""
    st.subheader("➕ Create New Task")
    
    with st.form("new_task_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            task_title = st.text_input("Task Title", placeholder="Enter task title...")
            task_description = st.text_area("Description", placeholder="Enter task description...", height=100)
        
        with col2:
            category = st.selectbox(
                "Category",
                options=list(manager.categories.keys())
            )
            priority = st.selectbox(
                "Priority",
                options=["High", "Medium", "Low"],
                index=1
            )
            estimated_hours = st.number_input(
                "Estimated Hours",
                min_value=1,
                max_value=200,
                value=20,
                step=1
            )
        
        submitted = st.form_submit_button("🚀 Create Task")
        
        if submitted:
            if task_title.strip() and task_description.strip():
                new_task_id = manager.create_new_task(
                    category, task_title.strip(), 
                    task_description.strip(), priority, estimated_hours
                )
                st.success(f"✅ New task created: {new_task_id} - {task_title}")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Please fill in both title and description")

def main():
    """Main dashboard application"""
    st.title("📅 3-Month Client Workplan Dashboard")
    st.markdown("☁️ **Cloud-Ready** | Comprehensive task management with database persistence")
    
    # Load workplan manager
    manager = load_workplan_data()
    if not manager:
        st.error("Unable to load workplan data. Please check database connection.")
        return
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    
    # Theme selector
    render_theme_selector()
    
    # Database status indicator
    if manager.db.connection:
        st.sidebar.success("🟢 Database Connected")
    else:
        st.sidebar.warning("🟡 Using Demo Mode")
    
    # Get project summary
    summary = manager.get_project_summary()
    
    # Display key metrics in sidebar
    st.sidebar.markdown("### 📊 Project Metrics")
    st.sidebar.metric("Total Tasks", summary['total_tasks'])
    st.sidebar.metric("Overall Completion", f"{summary['overall_completion']:.1f}%")
    st.sidebar.metric("Estimated Hours", f"{summary['total_estimated_hours']:,}")
    
    if summary['total_actual_hours'] > 0:
        st.sidebar.metric("Actual Hours", f"{summary['total_actual_hours']:,}", 
                         f"{summary['hours_variance']:+,}")
    
    # Navigation options
    view_options = [
        "🏠 Project Overview",
        "📅 Timeline View", 
        "🎯 Task Management",
        "📊 Category Details"
    ]
    selected_view = st.sidebar.selectbox("Select View", view_options)
    
    if selected_view == "🏠 Project Overview":
        # Project overview
        st.header("📊 Project Overview")
        
        # Top-level metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Tasks",
                summary['total_tasks'],
                f"{summary['completed_tasks']} completed"
            )
        
        with col2:
            st.metric(
                "Overall Progress",
                f"{summary['overall_progress']:.1f}%"
            )
        
        with col3:
            st.metric(
                "Estimated Hours", 
                f"{summary['total_estimated_hours']:,}"
            )
        
        with col4:
            st.metric(
                "Timeline Weeks",
                summary['timeline_weeks'],
                "Sept - Dec 2025"
            )
        
        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            # Category overview chart
            overview_chart = create_category_overview_chart(manager)
            if overview_chart:
                st.plotly_chart(overview_chart, use_container_width=True)
        
        with col2:
            # Task status pie chart
            status_chart = create_task_status_pie_chart(manager)
            if status_chart:
                st.plotly_chart(status_chart, use_container_width=True)
        
        # Category summaries
        st.subheader("📋 Category Summary")
        summary_data = []
        for category_name, progress in summary['categories'].items():
            summary_data.append({
                'Category': category_name,
                'Completion (%)': f"{progress['completion_percentage']:.1f}%",
                'Progress (%)': f"{progress['average_progress']:.1f}%",
                'Est. Hours': progress['estimated_hours'],
                'Actual Hours': progress['actual_hours'],
                'Variance': f"{progress['hours_variance']:+.0f}"
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
    elif selected_view == "🎯 Task Management":
        st.header("🎯 Task Management")
        
        # Add expandable new task form
        with st.expander("➕ Create New Task", expanded=False):
            render_new_task_form(manager)
        
        st.markdown("---")
        
        # Task filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category_filter = st.selectbox(
                "Filter by Category",
                options=["All"] + list(manager.get_all_categories().keys())
            )
        
        with col2:
            status_filter = st.selectbox(
                "Filter by Status",
                options=["All"] + [status.value for status in TaskStatus]
            )
        
        with col3:
            priority_filter = st.selectbox(
                "Filter by Priority",
                options=["All"] + [priority.value for priority in TaskPriority]
            )
        
        # Filter tasks
        filtered_tasks = []
        for task in manager.tasks.values():
            if category_filter != "All" and task.category != category_filter:
                continue
            if status_filter != "All" and task.status.value != status_filter:
                continue
            if priority_filter != "All" and task.priority.value != priority_filter:
                continue
            filtered_tasks.append(task)
        
        st.write(f"Showing {len(filtered_tasks)} tasks")
        
        # Display filtered tasks
        for task in filtered_tasks:
            with st.expander(f"🎯 {task.id}: {task.title}", expanded=False):
                render_task_details(manager, task.id)
                
    elif selected_view == "📊 Category Details":
        st.header("📊 Category Details")
        
        categories = manager.get_all_categories()
        selected_category = st.selectbox(
            "Select Category",
            options=list(categories.keys())
        )
        
        if selected_category:
            category_data = categories[selected_category]
            progress = manager.calculate_category_progress(selected_category)
            
            st.markdown(f'<div class="category-header">{selected_category}</div>', 
                       unsafe_allow_html=True)
            
            # Category metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Team Size", category_data['team_size'])
            
            with col2:
                st.metric("Completion", f"{progress['completion_percentage']:.1f}%")
            
            with col3:
                st.metric("Est. Hours", category_data['total_estimated_hours'])
            
            with col4:
                st.metric("Actual Hours", progress['actual_hours'])
            
            st.write(f"**Description:** {category_data['description']}")
            
            # Category tasks
            st.subheader(f"Tasks in {selected_category}")
            
            category_tasks = [task for task in manager.tasks.values() 
                            if task.category == selected_category]
            
            for task in category_tasks:
                with st.expander(f"🎯 {task.title}", expanded=False):
                    render_task_details(manager, task.id)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌐 Cloud Deployment")
    st.sidebar.info("This dashboard is ready for Streamlit Community Cloud deployment with database persistence!")

if __name__ == "__main__":
    main()