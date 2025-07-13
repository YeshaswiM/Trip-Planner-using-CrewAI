# 🏖️ VacAIgent - AI Trip Planner Setup Guide

## Quick Start

VacAIgent is now running successfully! Here's how to use and maintain your AI-powered trip planning system.

## Current Status ✅

- ✅ **Main App Running**: http://localhost:8502
- ✅ **All Dependencies Installed**: CrewAI, Streamlit, Gemini, Exa, Weave, etc.
- ✅ **Logging System**: Weave integration with local fallback
- ✅ **Flight Integration**: Exa-powered flight search
- ✅ **Weather Analysis**: Multi-destination comparison
- ✅ **Sharing Features**: Download as Markdown/PDF, copy to clipboard
- ✅ **Two Planning Modes**: Single destination & bucket list

## Running the Applications

### 1. Main VacAIgent App
```bash
cd "/Users/yeshaswi.menghmalani/Documents/YeshPersonalGithub/RandomPlayground/Trip-Planner-using-CrewAI"
/Users/yeshaswi.menghmalani/Library/Caches/pypoetry/virtualenvs/trip-planner-248Jes3D-py3.12/bin/python3 -m streamlit run streamlit_app.py --server.port 8502
```
**URL**: http://localhost:8502

### 2. Analytics Dashboard (NEW!)
```bash
cd "/Users/yeshaswi.menghmalani/Documents/YeshPersonalGithub/RandomPlayground/Trip-Planner-using-CrewAI"
/Users/yeshaswi.menghmalani/Library/Caches/pypoetry/virtualenvs/trip-planner-248Jes3D-py3.12/bin/python3 -m streamlit run analytics_dashboard.py --server.port 8503
```
**URL**: http://localhost:8503

## Features Overview

### 🎯 Single Destination Mode
- Comprehensive trip planning for one destination
- Flight search with 3 options (cheapest, recommended, premium)
- Local expert insights and itinerary planning
- Instant download/sharing capabilities

### 🗺️ Bucket List Mode
- Weather analysis for multiple destinations
- Destination ranking and recommendations
- Individual detailed plans for selected destinations
- Bulk planning with progress tracking

### 📊 Analytics Dashboard
- Agent performance monitoring
- User interaction tracking
- Popular destination insights
- Execution time metrics
- Success rate analysis

### 📤 Sharing Options
- **Markdown Download**: Easy editing and sharing
- **PDF Export**: Professional presentation format
- **Copy to Clipboard**: Quick sharing via messaging apps

## API Keys Required

Make sure your `.streamlit/secrets.toml` contains:
```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
SERPER_API_KEY = "your_serper_api_key_here"
BROWSERLESS_API_KEY = "your_browserless_api_key_here"
EXA_API_KEY = "your_exa_api_key_here"
```

## Logging & Analytics

### Weave Integration
- **Project Name**: `vacaigent-trip-planner`
- **Tracks**: User inputs, agent executions, performance metrics
- **Fallback**: Local JSON logs in `logs/` directory

### Local Logs
If Weave is unavailable, logs are saved to:
```
logs/vacaigent_YYYYMMDD.jsonl
```

## Architecture Overview

```
VacAIgent System
├── streamlit_app.py          # Main application
├── analytics_dashboard.py    # Performance monitoring
├── trip_agents.py           # AI agent definitions
├── trip_tasks.py            # Task definitions
├── weave_logger.py          # Logging utility
├── tools/
│   ├── flight_tools.py      # Exa flight search
│   ├── browser_tools.py     # Web browsing
│   ├── calculator_tools.py  # Calculations
│   └── search_tools.py      # Web search
└── .streamlit/
    ├── secrets.toml         # API keys
    └── config.toml          # App configuration
```

## Usage Tips

### For Best Results:
1. **Be Specific**: Include specific interests and travel preferences
2. **Date Flexibility**: Consider seasonal recommendations
3. **Passenger Count**: Accurate count helps with flight pricing
4. **Bucket List**: Start with 3-5 destinations for optimal analysis

### Performance Optimization:
- Bucket list mode: Use "Selected" option for faster results
- Popular destinations are cached for better performance
- Morning hours typically have better API response times

## Troubleshooting

### Common Issues:
1. **Weave Login Required**: Enter your W&B API key when prompted
2. **API Rate Limits**: Some searches may be slower during peak times
3. **PDF Generation**: Requires reportlab package (already installed)

### Error Recovery:
- All operations have fallback mechanisms
- Logging continues even if Weave is unavailable
- Mock data provided if API keys are missing

## Future Enhancements

### Planned Features:
- [ ] Real-time collaboration on trip plans
- [ ] Integration with booking platforms
- [ ] Advanced weather forecasting
- [ ] Budget tracking and optimization
- [ ] Group travel coordination
- [ ] Custom agent training

### Analytics Improvements:
- [ ] Real-time Weave dashboard integration
- [ ] A/B testing for agent configurations
- [ ] User journey analysis
- [ ] Performance benchmarking

## Support

For issues or questions:
1. Check the analytics dashboard for system health
2. Review logs in the `logs/` directory
3. Verify API keys in secrets.toml
4. Restart the application if needed

---

**🎉 Your VacAIgent system is ready! Start planning amazing trips with AI assistance!**
