# 📊 WhatsApp Support Analytics Dashboard

A beautiful, interactive Streamlit dashboard for analyzing WhatsApp support chat data with comprehensive KPIs, visualizations, and insights.

## ✨ Features

### 🎯 Key Performance Indicators
- **Total Issues**: Complete count of identified issues
- **Resolution Rate**: Percentage of issues successfully resolved
- **Response Rate**: Percentage of issues that received support responses
- **Average Response Time**: Mean time from issue report to first support reply

### 📊 Interactive Visualizations
- **Issue Status Distribution**: Pie chart showing resolved, pending, and no-response issues
- **Category Analysis**: Bar chart of issues by category (zabbix_monitoring, port_down, etc.)
- **Response Time Distribution**: Histogram showing response time patterns
- **Resolution Time Analysis**: Box plot of resolution times
- **Peak Hours Analysis**: Bar chart showing when most issues occur
- **Daily Trends**: Line chart showing issue volume over time
- **Support Performance**: Staff performance metrics and comparisons

### 🔍 Interactive Filters
- **Date Range Filter**: Analyze specific time periods
- **Status Filter**: Focus on resolved, pending, or no-response issues
- **Category Filter**: Drill down into specific issue types

### 📋 Detailed Data Tables
- **Issues Table**: Complete issue details with timestamps and metrics
- **Messages Table**: Full message log with classifications
- **Support Performance**: Staff metrics and response counts

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_dashboard.txt
```

### 2. Generate Analysis Data
First, run the analysis script to create the Excel data:
```bash
python extract.py
```

### 3. Launch Dashboard
```bash
python run_dashboard.py
```

Or directly with Streamlit:
```bash
streamlit run dashboard.py
```

### 4. Access Dashboard
Open your browser to: `http://localhost:8501`

## 📁 File Structure

```
whatsapp_data/
├── dashboard.py              # Main dashboard application
├── run_dashboard.py         # Dashboard launcher script
├── requirements_dashboard.txt # Python dependencies
├── extract.py               # Data analysis script
├── support_analysis.xlsx    # Generated analysis data
└── README.md               # This file
```

## 🎨 Dashboard Sections

### 📈 KPI Cards
Beautiful gradient cards displaying key metrics:
- Total Issues count
- Resolution Rate percentage
- Response Rate percentage  
- Average Response Time in minutes

### 📊 Analytics Overview
Six interactive charts providing comprehensive insights:
1. **Status Distribution**: Visual breakdown of issue outcomes
2. **Category Analysis**: Most common issue types
3. **Response Time Distribution**: Performance timing patterns
4. **Resolution Time Analysis**: Time-to-resolution statistics
5. **Peak Hours**: When issues most commonly occur
6. **Daily Trends**: Issue volume over time

### 👥 Support Performance
Staff performance metrics showing:
- Issues handled per support member
- Response counts
- Resolution contributions

### 📋 Data Tables
Detailed tabular views of:
- All issues with complete metadata
- Message logs with classifications
- Support staff performance data

## 🔧 Customization

### Adding New Charts
```python
def create_custom_chart(data_df):
    fig = px.bar(data_df, x='column1', y='column2', title='Custom Chart')
    return fig
```

### Modifying KPIs
Edit the `create_kpi_metrics()` function to add or modify KPI cards.

### Styling Changes
Modify the CSS in the `st.markdown()` section at the top of `dashboard.py`.

## 📊 Data Requirements

The dashboard expects an Excel file (`support_analysis.xlsx`) with these sheets:
- **Issues**: Issue details with timestamps and metrics
- **Messages**: Complete message log
- **KPI Summary**: Key performance indicators
- **Categories**: Issue category breakdown
- **Support Performance**: Staff metrics
- **Timing Analysis**: Response time distributions

## 🎯 Use Cases

### Support Managers
- Monitor team performance and response times
- Identify peak issue hours for staffing
- Track resolution rates and trends

### Operations Teams
- Analyze issue patterns by category
- Identify recurring problems
- Measure customer satisfaction through response metrics

### Business Analysts
- Generate reports on support efficiency
- Identify areas for process improvement
- Track performance over time

## 🛠️ Technical Details

### Built With
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation and analysis
- **OpenPyXL**: Excel file handling

### Performance
- Data is cached for fast loading
- Charts are interactive and responsive
- Filters update visualizations in real-time

### Browser Compatibility
- Chrome (recommended)
- Firefox
- Safari
- Edge

## 🔍 Troubleshooting

### Dashboard Won't Start
1. Check if all dependencies are installed: `pip install -r requirements_dashboard.txt`
2. Ensure `support_analysis.xlsx` exists in the same directory
3. Run `python extract.py` first to generate the data

### Charts Not Displaying
1. Check if the Excel file has all required sheets
2. Verify data format matches expected structure
3. Check browser console for JavaScript errors

### Performance Issues
1. Reduce date range in filters
2. Use specific status/category filters
3. Check if Excel file is too large (>100MB)

## 📈 Future Enhancements

- [ ] Real-time data updates
- [ ] Export functionality for charts
- [ ] Advanced filtering options
- [ ] Custom date range presets
- [ ] Mobile-responsive design improvements
- [ ] Dark mode theme
- [ ] Data refresh automation

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the dashboard!

## 📄 License

This project is open source and available under the MIT License.
