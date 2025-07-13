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
        """Simple file logging with better data handling."""
        try:
            self._ensure_log_directory()
            timestamp = datetime.datetime.now().strftime('%H:%M:%S')
            
            # Better handling of data for debugging
            clean_data = {}
            for key, value in data.items():
                if value is None:
                    clean_data[key] = "NULL"
                elif value == "":
                    clean_data[key] = "EMPTY"
                elif isinstance(value, str) and len(value) > 300:
                    clean_data[key] = value[:300] + "..."
                else:
                    clean_data[key] = value
            
            # Write to log file
            with open(self.log_file, 'a') as f:
                f.write(f"{timestamp} - {event_type}: {json.dumps(clean_data, indent=2)}\n")
                
            # Also print to console for debugging
            print(f"📝 LOG [{event_type}]: {clean_data}")
                
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
        """Log agent execution with detailed output tracking."""
        duration = (end_time - start_time).total_seconds() if start_time and end_time else 0
        
        # Debug the actual output
        print(f"🔍 DEBUG - Agent {agent_name} output: {type(output)} - {len(str(output)) if output else 0} chars")
        if output:
            print(f"🔍 DEBUG - Output preview: {str(output)[:100]}...")
        
        self._safe_log({
            "agent": agent_name,
            "task": task_description[:50] if task_description else "NO_TASK",
            "duration_sec": round(duration, 2),
            "success": success,
            "output_length": len(str(output)) if output else 0,
            "output_preview": str(output)[:150] if output else "NULL_OUTPUT",
            "has_output": output is not None,
            "error": str(error)[:100] if error else None
        }, "agent_execution")

    def log_crew_execution(self, crew_type: str, agents_count: int, tasks_count: int,
                          start_time: datetime.datetime, end_time: datetime.datetime,
                          success: bool, destinations: List[str] = None, result: str = None) -> None:
        """Log crew execution with detailed result tracking."""
        duration = (end_time - start_time).total_seconds() if start_time and end_time else 0
        
        # Debug the crew result
        print(f"🔍 DEBUG - Crew {crew_type} result: {type(result)} - {len(str(result)) if result else 0} chars")
        if result:
            print(f"🔍 DEBUG - Result preview: {str(result)[:100]}...")
        else:
            print(f"⚠️ WARNING - Crew {crew_type} returned NULL result!")
        
        # More detailed result analysis
        result_info = {
            "has_result": result is not None,
            "result_type": str(type(result)),
            "result_length": len(str(result)) if result else 0,
            "result_empty": result == "" if result is not None else True,
            "result_preview": str(result)[:150] if result else "NULL_RESULT"
        }
        
        self._safe_log({
            "crew_type": crew_type,
            "agents_count": agents_count,
            "tasks_count": tasks_count,
            "duration_sec": round(duration, 2),
            "success": success,
            "destinations": destinations if destinations else [],
            **result_info  # Unpack the detailed result info
        }, "crew_execution")

    def log_weather_analysis(self, destinations: List[str], analysis_result: str,
                           execution_time: float, success: bool) -> None:
        """Log weather analysis with detailed result tracking."""
        
        # Debug the weather analysis result
        print(f"🔍 DEBUG - Weather analysis result: {type(analysis_result)} - {len(str(analysis_result)) if analysis_result else 0} chars")
        if analysis_result:
            print(f"🔍 DEBUG - Weather result preview: {str(analysis_result)[:100]}...")
        else:
            print(f"⚠️ WARNING - Weather analysis returned NULL result!")
        
        self._safe_log({
            "destinations": destinations,
            "success": success,
            "execution_time": round(execution_time, 2),
            "result_length": len(str(analysis_result)) if analysis_result else 0,
            "result_preview": str(analysis_result)[:150] if analysis_result else "NULL_RESULT",
            "has_result": analysis_result is not None
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
