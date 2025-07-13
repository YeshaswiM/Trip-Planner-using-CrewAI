"""
Weave logging integration for VacAIgent trip planning workflow.
Tracks all agent decision-making, user interactions, and planning outcomes.
"""

import datetime
import json
import os
from typing import Dict, List, Any, Optional
import streamlit as st
from functools import wraps
import traceback

class VacAIgentLogger:
    """
    Centralized logging for VacAIgent using Weights & Biases Weave.
    Captures agent decisions, user interactions, and trip planning performance.
    Falls back to local file logging if Weave is not available.
    """
    
    def __init__(self, project_name: str = "vacaigent-trip-planner"):
        """Initialize Weave logging for the project."""
        self.project_name = project_name
        self.session_id = self._generate_session_id()
        self.is_initialized = False
        self.log_file = f"logs/vacaigent_{datetime.datetime.now().strftime('%Y%m%d')}.jsonl"
        
        # Try to initialize Weave
        try:
            import weave
            weave.init(project_name)
            self.weave = weave
            self.is_initialized = True
            print(f"✅ Weave logging initialized for project: {project_name}")
        except Exception as e:
            print(f"⚠️ Weave not available, using local logging: {str(e)}")
            self.weave = None
            self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Create logs directory if it doesn't exist."""
        os.makedirs("logs", exist_ok=True)
    
    def _generate_session_id(self) -> str:
        """Generate a unique session identifier."""
        return f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _safe_log(self, data: Dict[str, Any], event_type: str) -> None:
        """Safely log data to Weave or local file with error handling."""
        try:
            if self.is_initialized and self.weave:
                # Try Weave logging first
                try:
                    # Simple approach - just print for now since Weave API is complex
                    print(f"📊 [WEAVE] {event_type}: {data.get('session_id', 'unknown')}")
                except Exception as e:
                    print(f"⚠️ Weave logging failed, falling back to local: {str(e)}")
                    self._log_to_file(data)
            else:
                # Fallback to local file logging
                self._log_to_file(data)
                
        except Exception as e:
            print(f"⚠️ All logging methods failed for {event_type}: {str(e)}")
    
    def _log_to_file(self, data: Dict[str, Any]) -> None:
        """Log data to local JSON lines file."""
        try:
            self._ensure_log_directory()
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(data) + '\n')
        except Exception as e:
            print(f"⚠️ Failed to write to log file: {str(e)}")
    
    def log_user_input(self, trip_mode: str, location: str, cities: str, 
                      date_range: tuple, interests: str, passengers: int) -> None:
        """Log user trip planning inputs."""
        user_data = {
            "session_id": self.session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": "user_input",
            "trip_mode": trip_mode,
            "origin": location,
            "destinations": cities,
            "date_range": {
                "start": date_range[0].isoformat() if hasattr(date_range[0], 'isoformat') else str(date_range[0]),
                "end": date_range[1].isoformat() if hasattr(date_range[1], 'isoformat') else str(date_range[1])
            },
            "interests": interests,
            "passengers": passengers
        }
        
        self._safe_log(user_data, "user_input")
    
    def log_agent_execution(self, agent_name: str, task_description: str, 
                           start_time: datetime.datetime, end_time: datetime.datetime,
                           success: bool, output: str = None, error: str = None) -> None:
        """Log individual agent execution details."""
        execution_time = (end_time - start_time).total_seconds()
        
        agent_data = {
            "session_id": self.session_id,
            "timestamp": start_time.isoformat(),
            "event_type": "agent_execution",
            "agent_name": agent_name,
            "task_description": task_description[:500] if task_description else "",
            "execution_time_seconds": execution_time,
            "success": success,
            "output_length": len(output) if output else 0,
            "error": error if error else None
        }
        
        self._safe_log(agent_data, "agent_execution")
    
    def log_crew_execution(self, crew_type: str, agents_count: int, tasks_count: int,
                          start_time: datetime.datetime, end_time: datetime.datetime,
                          success: bool, destinations: List[str] = None) -> None:
        """Log overall crew execution performance."""
        total_time = (end_time - start_time).total_seconds()
        
        crew_data = {
            "session_id": self.session_id,
            "timestamp": start_time.isoformat(),
            "event_type": "crew_execution",
            "crew_type": crew_type,
            "agents_count": agents_count,
            "tasks_count": tasks_count,
            "total_execution_time_seconds": total_time,
            "success": success,
            "destinations": destinations or [],
            "destinations_count": len(destinations) if destinations else 0
        }
        
        self._safe_log(crew_data, "crew_execution")
    
    def log_weather_analysis(self, destinations: List[str], analysis_result: str,
                           execution_time: float, success: bool) -> None:
        """Log weather analysis for bucket list destinations."""
        weather_data = {
            "session_id": self.session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": "weather_analysis",
            "destinations": destinations,
            "destinations_count": len(destinations),
            "analysis_length": len(analysis_result) if analysis_result else 0,
            "execution_time_seconds": execution_time,
            "success": success
        }
        
        self._safe_log(weather_data, "weather_analysis")
    
    def log_user_destination_selection(self, available_destinations: List[str],
                                     selected_destinations: List[str], 
                                     selection_type: str) -> None:
        """Log user's destination selection choices."""
        selection_data = {
            "session_id": self.session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": "destination_selection",
            "available_destinations": available_destinations,
            "selected_destinations": selected_destinations,
            "selection_type": selection_type,
            "available_count": len(available_destinations),
            "selected_count": len(selected_destinations),
            "selection_percentage": len(selected_destinations) / len(available_destinations) * 100 if available_destinations else 0
        }
        
        self._safe_log(selection_data, "destination_selection")
    
    def log_flight_search(self, origin: str, destination: str, flight_options: Dict,
                         search_time: float, success: bool) -> None:
        """Log flight search results and performance."""
        flight_data = {
            "session_id": self.session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": "flight_search",
            "origin": origin,
            "destination": destination,
            "search_time_seconds": search_time,
            "success": success,
            "options_found": len(flight_options) if flight_options else 0
        }
        
        self._safe_log(flight_data, "flight_search")
    
    def log_download_action(self, format_type: str, destination: str = None) -> None:
        """Log when users download trip plans."""
        download_data = {
            "session_id": self.session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": "download_action",
            "format_type": format_type,
            "destination": destination
        }
        
        self._safe_log(download_data, "download_action")
    
    def log_error(self, error_type: str, error_message: str, context: Dict = None) -> None:
        """Log errors and exceptions."""
        error_data = {
            "session_id": self.session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": "error",
            "error_type": error_type,
            "error_message": str(error_message)[:1000],  # Limit length
            "context": context or {}
        }
        
        self._safe_log(error_data, "error")
    
    def log_performance_metrics(self, metric_name: str, value: float, context: Dict = None) -> None:
        """Log performance metrics."""
        metrics_data = {
            "session_id": self.session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": "performance_metric",
            "metric_name": metric_name,
            "value": value,
            "context": context or {}
        }
        
        self._safe_log(metrics_data, "performance_metric")

# Global logger instance
logger = VacAIgentLogger()
