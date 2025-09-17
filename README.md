# 📅 3-Month Client Workplan Dashboard

A comprehensive, cloud-ready project management dashboard built with **Streamlit** and **PostgreSQL/Supabase** for tracking client engagement progress.

## ✨ Features

### 🎯 **Wiki-Style Editing**
- ✏️ **Click to edit** task titles and descriptions directly in the dashboard
- 💾 **Real-time database saves** - all changes persist immediately
- 👥 **Multi-user collaboration** - team members can edit simultaneously
- 📝 **No command line needed** - everything editable through the web interface

### 🎨 **Theme Support**
- 🌅 **Light Mode** - Clean, professional interface
- 🌙 **Dark Mode** - Easy on eyes for extended use
- 💻 **System Mode** - Automatically matches OS preference

## 🚀 **Live Dashboard**

**Deployed at:** [Deploy to get your live URL]

## 🛠️ **Local Development**

```bash
# Install dependencies
pip install -r requirements.txt

# Run cloud-ready version locally
streamlit run workplan_cloud_dashboard.py
```

## 📋 Features

### Dashboard Overview
- **Project-wide completion percentage** - See overall progress across all functional areas
- **Interactive completion charts** - Visual representation of progress by area
- **Summary statistics** - Key metrics and top performing areas
- **Functional areas summary table** - Quick status overview

### Individual Functional Area Tracking
- **Detailed completion tracking** for each area:
  - Financial subactivities
  - Governance
  - HR
  - IT (WIP)
  - Strategic Sourcing
  - Supply Chain (Operations)
  - Legal and Regulatory Compliance
  - Marketing
  - Risk

### Interactive Features
- ✅ **Clickable checkboxes** for each aspect (Process, Policy, People, Technology, Reports, Review Cadence, Best Practices)
- 📈 **Real-time percentage calculations** - Updates automatically as you check items
- 🎯 **Individual item progress bars** - See completion status for each category
- 📊 **Aspect breakdown charts** - Visual breakdown by different business aspects

### Data Management
- 💾 **Automatic progress saving** - Your progress is saved to `completion_data.json`
- 🔄 **Data persistence** - Resume where you left off between sessions
- 📤 **Export functionality** - Export summary statistics
- 🔄 **Refresh data** - Reload from Excel file when needed

## 🗂️ File Structure

```
├── dashboard.py           # Main Streamlit dashboard application
├── data_processor.py      # Excel data processing and tracking logic
├── run_dashboard.py       # Simple launcher script
├── completion_data.json   # Your progress data (auto-generated)
└── README.md             # This file
```

## 📊 How It Works

1. **Data Loading**: The dashboard reads your Excel file (`Heat Map Workbook .xlsx`) from the Desktop
2. **Structure Recognition**: Identifies functional areas and completion checkboxes
3. **Interactive Tracking**: Provides web interface for checking completion status
4. **Progress Calculation**: Automatically calculates percentages at multiple levels:
   - Individual item level (by aspect)
   - Functional area level (overall area completion)
   - Project level (entire project completion)
5. **Data Persistence**: Saves your progress so you can continue later

## 💡 Usage Tips

### Navigation
- Use the sidebar to navigate between **Dashboard Overview** and individual **Functional Areas**
- The overview gives you the big picture, individual areas let you make updates

### Tracking Progress
- Click checkboxes next to each aspect (Process, Policy, People, etc.) to mark as complete
- Progress bars and percentages update automatically
- Use the "Save Progress" button to ensure your changes are saved

### Managing Data
- Your progress is automatically saved to `completion_data.json`
- Use "Save All Progress" to manually save everything
- Use "Refresh Data" to reload from the original Excel file
- Use "Export Summary" to see detailed statistics

## 🛠️ Requirements

- Python 3.7+
- Required packages (install with `pip install`):
  - `streamlit`
  - `pandas`
  - `openpyxl`
  - `plotly`

## 🔧 Customization

The dashboard is designed to work with your specific Excel structure but can be customized:

- **Excel file path**: Modify the path in `data_processor.py` line 222
- **Aspect names**: Update the `aspect_names` list in `data_processor.py` line 66
- **Dashboard styling**: Modify the CSS in `dashboard.py` lines 25-48

## 📈 Example Workflow

1. **Start the dashboard**: `python3 run_dashboard.py`
2. **Review overview**: Check overall project status and identify areas needing attention
3. **Select a functional area**: Choose an area from the sidebar (e.g., "HR", "Governance")
4. **Update completion status**: Check off completed aspects for each category
5. **Monitor progress**: Watch percentages update in real-time
6. **Save progress**: Use the save button or it saves automatically
7. **Return later**: Your progress will be restored when you restart the dashboard

## 🎯 Project Structure in Dashboard

```
Project (Overall %)
├── Financial subactivities (Area %)
│   ├── FP&A (Item %)
│   │   ├── ✅ Process
│   │   ├── ☐ Policy  
│   │   └── ✅ People
│   └── [Other categories...]
├── Governance (Area %)
├── HR (Area %)
└── [Other functional areas...]
```

## 🚫 Troubleshooting

**Dashboard won't start:**
- Make sure all Python packages are installed: `pip install streamlit pandas openpyxl plotly`
- Check that the Excel file exists on your Desktop

**Data not loading:**
- Verify the Excel file path in `data_processor.py`
- Make sure the file name matches exactly (including spaces)

**Progress not saving:**
- Check file permissions in the current directory
- Make sure you click "Save Progress" after making changes

## 🤝 Support

The dashboard is designed to be intuitive, but if you need help:
1. Check the sidebar for key metrics and navigation
2. Use the expandable sections to organize your work
3. Export summary data if you need to share progress externally

---

🎉 **Happy tracking!** Your business function assessment progress is now just a click away.