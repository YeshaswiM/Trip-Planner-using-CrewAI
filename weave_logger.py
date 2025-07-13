"""
Weave logging integration for VacAIgent trip planning workflow.
Tracks all agent decision-making, user interactions, and planning outcomes.
"""

import weave
import datetime
import json
from typing import Dict, List, Any, Optional
import streamlit as st
from functools import wraps
import traceback

class VacAIgentLogger:
    """
    Centralized logging for VacAIgent using Weights & Biases Weave.
    Captures agent decisions, user interactions, and trip planning performance.
    """
    
    def __init__(self, project_name: str = "vacaigent-trip-planner"):
        """Initialize Weave logging for the project."""
        try:
            weave.init(project_name)
            self.project_name = project_name
            self.session_id = self._generate_session_id()
            self.is_initialized = True
            print(f"✅ Weave logging initialized for project: {project_name}")
        except Exception as e:
            print(f"⚠️ Failed to initialize Weave logging: {str(e)}")
            self.is_initialized = False
    
    def _generate_session_id(self) -> str:
        """Generate a unique session identifier."""
        return f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def log_user_input(self, trip_mode: str, location: str, cities: str, 
                      date_range: tuple, interests: str, passengers: int) -> None:
        """Log user trip planning inputs."""
        if not self.is_initialized:
            return
            
        try:
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
            
            weave.log(user_data)
            print(f"📊 Logged user input: {trip_mode} mode for {location} → {cities}")
            
        except Exception as e:
            print(f"⚠️ Failed to log user input: {str(e)}")
    
    def log_agent_execution(self, agent_name: str, task_description: str, 
                           start_time: datetime.datetime, end_time: datetime.datetime,
                           success: bool, output: str = None, error: str = None) -> None:
        """Log individual agent execution details."""
        if not self.is_initialized:
            return
            
        try:
            execution_time = (end_time - start_time).total_seconds()
            
            agent_data = {
                "session_id": self.session_id,
                "timestamp": start_time.isoformat(),
                "event_type": "agent_execution",
                "agent_name": agent_name,
                "task_description": task_description[:500],  # Limit length
                "execution_time_seconds": execution_time,
                "success": success,
                "output_length": len(output) if output else 0,
                "error": error if error else None
            }
            
            weave.log(agent_data)
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"📊 Logged {agent_name}: {status} ({execution_time:.2f}s)")
            
        except Exception as e:
            print(f"⚠️ Failed to log agent execution: {str(e)}")
    
    def log_crew_execution(self, crew_type: str, agents_count: int, tasks_count: int,
                          start_time: datetime.datetime, end_time: datetime.datetime,
                          success: bool, destinations: List[str] = None) -> None:
        """Log overall crew execution performance."""
        if not self.is_initialized:
            return
            
        try:
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
            
            weave.log(crew_data)
            print(f"📊 Logged crew execution: {crew_type} ({total_time:.2f}s)")
            
        except Exception as e:
            print(f"⚠️ Failed to log crew execution: {str(e)}")
    
    def log_weather_analysis(self, destinations: List[str], analysis_result: str,
                           execution_time: float, success: bool) -> None:
        """Log weather analysis for bucket list destinations."""
        if not self.is_initialized:
            return
            
        try:
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
            
            weave.log(weather_data)
            print(f"📊 Logged weather analysis for {len(destinations)} destinations")
            
        except Exception as e:
            print(f"⚠️ Failed to log weather analysis: {str(e)}")
    
    def log_user_destination_selection(self, available_destinations: List[str],
                                     selected_destinations: List[str], 
                                     selection_type: str) -> None:
        """Log user's destination selection choices."""
        if not self.is_initialized:
            return
            
        try:
            selection_data = {
                "session_id": self.session_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "event_type": "destination_selection",
                "available_destinations": available_destinations,
                "selected_destinations": selected_destinations,
                "selection_type": selection_type,  # "selected" or "all"
                "available_count": len(available_destinations),
                "selected_count": len(selected_destinations),
                "selection_percentage": len(selected_destinations) / len(available_destinations) * 100
            }
            
            weave.log(selection_data)
            print(f"📊 Logged destination selection: {len(selected_destinations)}/{len(available_destinations)}")
            
        except Exception as e:
            print(f"⚠️ Failed to log destination selection: {str(e)}")
    
    def log_flight_search(self, origin: str, destination: str, flight_options: Dict,
                         search_time: float, success: bool) -> None:
        """Log flight search results and performance."""
        if not self.is_initialized:
            return
            
        try:
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
            
            weave.log(flight_data)
            print(f"📊 Logged flight search: {origin} → {destination}")
            
        except Exception as e:
            print(f"⚠️ Failed to log flight search: {str(e)}")
    
    def log_download_action(self, format_type: str, destination: str = None) -> None:
        """Log when users download trip plans."""
        if not self.is_initialized:
            return
            
        try:
            download_data = {
                "session_id": self.session_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "event_type": "download_action",
                "format_type": format_type,  # "markdown", "pdf", "clipboard"
                "destination": destination
            }
            
            weave.log(download_data)
            print(f"📊 Logged download: {format_type} for {destination or 'single trip'}")
            
        except Exception as e:
            print(f"⚠️ Failed to log download action: {str(e)}")
    
    def log_error(self, error_type: str, error_message: str, context: Dict = None) -> None:
        """Log errors and exceptions."""
        if not self.is_initialized:
            return
            
        try:
            error_data = {
                "session_id": self.session_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "event_type": "error",
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {},
                "traceback": traceback.format_exc()
            }
            
            weave.log(error_data)
            print(f"📊 Logged error: {error_type}")
            
        except Exception as e:
            print(f"⚠️ Failed to log error: {str(e)}")
    
    def log_performance_metrics(self, metric_name: str, value: float, 
                               context: Dict = None) -> None:
        """Log performance metrics."""
        if not self.is_initialized:
            return
            
        try:
            metrics_data = {
                "session_id": self.session_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "event_type": "performance_metrics",
                "metric_name": metric_name,
                "value": value,
                "context": context or {}
            }
            
            weave.log(metrics_data)
            print(f"📊 Logged metric: {metric_name} = {value}")
            
        except Exception as e:
            print(f"⚠️ Failed to log performance metric: {str(e)}")


def log_agent_execution(logger: VacAIgentLogger):
    """Decorator to automatically log agent execution."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            agent_name = getattr(args[0], 'role', 'Unknown Agent') if args else 'Unknown Agent'
            start_time = datetime.datetime.now()
            
            try:
                result = func(*args, **kwargs)
                end_time = datetime.datetime.now()
                
                logger.log_agent_execution(
                    agent_name=agent_name,
                    task_description=f"Executed {func.__name__}",
                    start_time=start_time,
                    end_time=end_time,
                    success=True,
                    output=str(result)[:1000] if result else None
                )
                
                return result
                
            except Exception as e:
                end_time = datetime.datetime.now()
                
                logger.log_agent_execution(
                    agent_name=agent_name,
                    task_description=f"Executed {func.__name__}",
                    start_time=start_time,
                    end_time=end_time,
                    success=False,
                    error=str(e)
                )
                
                raise e
                
        return wrapper
    return decorator


# Global logger instance
logger = VacAIgentLogger()
