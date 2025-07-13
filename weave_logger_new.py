"""
Simple logging for VacAIgent - no complex integrations that can hang.
"""

import datetime
import json
import os
from typing import Dict, List, Any, Optional

class VacAIgentLogger:
    """
    Simple file-based logging - no external dependencies that can hang.
    """
    
    def __init__(self, project_name: str = "vacaigent-trip-planner"):
        """Initialize simple logging."""
        self.project_name = project_name
        self.session_id = self._generate_session_id()
        self.log_file = f"logs/vacaigent_{datetime.datetime.now().strftime('%Y%m%d')}.log"
        self._ensure_log_directory()
        print(f"📝 Simple logging initialized - Session: {self.session_id}")
    
    def _ensure_log_directory(self):
        """Create logs directory if it doesn't exist."""
        os.makedirs("logs", exist_ok=True)
    
    def _generate_session_id(self) -> str:
        """Generate a unique session identifier."""
        return f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _safe_log(self, data: Dict[str, Any], event_type: str) -> None:
        """Simple file logging only."""
        try:
            self._ensure_log_directory()
            timestamp = datetime.datetime.now().strftime('%H:%M:%S')
            with open(self.log_file, 'a') as f:
                f.write(f"{timestamp} - {event_type}: {str(data)[:200]}\n")
        except Exception as e:
            print(f"⚠️ Logging failed: {str(e)}")

    def log_user_input(self, trip_mode: str, location: str, cities: str, 
                      date_range: tuple, interests: str, passengers: int) -> None:
        """Log user trip planning inputs."""
        self._safe_log({
            "trip_mode": trip_mode,
            "origin": location,
            "destinations": cities
        }, "user_input")

    def log_agent_execution(self, agent_name: str, task_description: str, 
                           start_time: datetime.datetime, end_time: datetime.datetime,
                           success: bool, output: str = None, error: str = None) -> None:
        """Log agent execution."""
        self._safe_log({
            "agent": agent_name,
            "success": success
        }, "agent_execution")

    def log_crew_execution(self, crew_type: str, agents_count: int, tasks_count: int,
                          start_time: datetime.datetime, end_time: datetime.datetime,
                          success: bool, destinations: List[str] = None) -> None:
        """Log crew execution."""
        self._safe_log({
            "crew_type": crew_type,
            "success": success
        }, "crew_execution")

    def log_weather_analysis(self, destinations: List[str], analysis_result: str,
                           execution_time: float, success: bool) -> None:
        """Log weather analysis."""
        self._safe_log({
            "destinations": destinations,
            "success": success
        }, "weather_analysis")

    def log_user_destination_selection(self, available_destinations: List[str],
                                     selected_destinations: List[str], 
                                     selection_type: str) -> None:
        """Log destination selection."""
        self._safe_log({
            "selected": selected_destinations,
            "type": selection_type
        }, "destination_selection")

    def log_flight_search(self, origin: str, destination: str, flight_options: Dict,
                         search_time: float, success: bool) -> None:
        """Log flight search."""
        self._safe_log({
            "origin": origin,
            "destination": destination,
            "success": success
        }, "flight_search")

    def log_download_action(self, format_type: str, destination: str = None) -> None:
        """Log downloads."""
        self._safe_log({
            "format": format_type,
            "destination": destination
        }, "download")

    def log_error(self, error_type: str, error_message: str, context: Dict = None) -> None:
        """Log errors."""
        self._safe_log({
            "error_type": error_type,
            "error": str(error_message)[:100]
        }, "error")

    def log_performance_metrics(self, metric_name: str, value: float, context: Dict = None) -> None:
        """Log metrics."""
        self._safe_log({
            "metric": metric_name,
            "value": value
        }, "performance")

# Global logger instance
logger = VacAIgentLogger()
