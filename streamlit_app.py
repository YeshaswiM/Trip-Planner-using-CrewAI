from crewai import Crew, LLM
from trip_agents import TripAgents, StreamToExpander
from trip_tasks import TripTasks
import streamlit as st
import datetime
import sys
from langchain_openai import OpenAI
from weave_logger_new import logger


st.set_page_config(page_icon="✈️", layout="wide")


def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


class TripCrew:

    def __init__(self, origin, cities, date_range, interests, passengers=1):
        self.cities = cities
        self.origin = origin
        self.interests = interests
        self.passengers = passengers
        # Convert date_range to string format for better handling
        self.date_range = f"{date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}"
        self.output_placeholder = st.empty()
        self.llm = LLM(model="gemini/gemini-2.0-flash")
        # self.llm = OpenAI(
        #     temperature=0.7,
        #     model_name="gpt-4",
        # )

    def run(self):
        crew_start_time = datetime.datetime.now()
        
        try:
            # Log crew execution start
            logger.log_performance_metrics(
                "crew_execution_start", 
                0,
                {"crew_type": "single_destination", "origin": self.origin, "destination": self.cities}
            )
            
            agents = TripAgents(llm=self.llm)
            tasks = TripTasks()

            # Parse dates from the date range
            start_date = self.date_range.split(' to ')[0]
            end_date = self.date_range.split(' to ')[1] if ' to ' in self.date_range else None

            # Create agents
            flight_search_agent = agents.flight_search_agent()
            city_selector_agent = agents.city_selection_agent()
            local_expert_agent = agents.local_expert()
            travel_concierge_agent = agents.travel_concierge()

            # Create tasks - flight search comes first
            flight_search_task = tasks.flight_search_task(
                flight_search_agent,
                self.origin,
                self.cities,
                start_date,
                end_date,
                passengers=self.passengers
            )

            identify_task = tasks.identify_task(
                city_selector_agent,
                self.origin,
                self.cities,
                self.interests,
                self.date_range
            )

            gather_task = tasks.gather_task(
                local_expert_agent,
                self.origin,
                self.interests,
                self.date_range
            )

            plan_task = tasks.plan_task(
                travel_concierge_agent,
                self.origin,
                self.interests,
                self.date_range
            )

            crew = Crew(
                agents=[
                    flight_search_agent, city_selector_agent, local_expert_agent, travel_concierge_agent
                ],
                tasks=[flight_search_task, identify_task, gather_task, plan_task],
                verbose=True
            )

            # Execute crew and log performance
            task_start_time = datetime.datetime.now()
            result = crew.kickoff()
            task_end_time = datetime.datetime.now()
            
            # Debug the result
            print(f"🔍 CREW RESULT TYPE: {type(result)}")
            print(f"🔍 CREW RESULT LENGTH: {len(str(result)) if result else 0}")
            print(f"🔍 CREW RESULT PREVIEW: {str(result)[:200] if result else 'NO RESULT'}")
            
            # Log successful crew execution WITH the result
            logger.log_crew_execution(
                crew_type="single_destination",
                agents_count=4,
                tasks_count=4,
                start_time=crew_start_time,
                end_time=task_end_time,
                success=True,
                destinations=[self.cities],
                result=str(result)  # Pass the actual result
            )
            
            # Log execution time metrics
            execution_time = (task_end_time - task_start_time).total_seconds()
            logger.log_performance_metrics(
                "single_destination_execution_time",
                execution_time,
                {"origin": self.origin, "destination": self.cities, "passengers": self.passengers}
            )
            
            self.output_placeholder.markdown(result)
            return result
            
        except Exception as e:
            crew_end_time = datetime.datetime.now()
            
            # Log failed crew execution
            logger.log_crew_execution(
                crew_type="single_destination",
                agents_count=4,
                tasks_count=4,
                start_time=crew_start_time,
                end_time=crew_end_time,
                success=False,
                destinations=[self.cities]
            )
            
            # Log the error
            logger.log_error(
                error_type="crew_execution_error",
                error_message=str(e),
                context={"origin": self.origin, "destination": self.cities, "passengers": self.passengers}
            )
            
            st.error(f"An error occurred: {str(e)}")
            return None


class BucketListCrew:
    
    def __init__(self, origin, bucket_list, date_range, interests, passengers=1):
        self.bucket_list = [dest.strip() for dest in bucket_list.split('\n') if dest.strip()]
        self.origin = origin
        self.interests = interests
        self.passengers = passengers
        self.date_range = f"{date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}"
        self.output_placeholder = st.empty()
        self.llm = LLM(model="gemini/gemini-2.0-flash")
        
    def run(self):
        """Initial weather analysis only - returns the analysis result."""
        analysis_start_time = datetime.datetime.now()
        
        try:
            # Log weather analysis start
            logger.log_performance_metrics(
                "weather_analysis_start",
                0,
                {"destinations_count": len(self.bucket_list), "destinations": self.bucket_list}
            )
            
            result = self._analyze_destinations_weather()
            analysis_end_time = datetime.datetime.now()
            
            # Log successful weather analysis
            execution_time = (analysis_end_time - analysis_start_time).total_seconds()
            logger.log_weather_analysis(
                destinations=self.bucket_list,
                analysis_result=result if result else "",
                execution_time=execution_time,
                success=True
            )
            
            return result
            
        except Exception as e:
            analysis_end_time = datetime.datetime.now()
            execution_time = (analysis_end_time - analysis_start_time).total_seconds()
            
            # Log failed weather analysis
            logger.log_weather_analysis(
                destinations=self.bucket_list,
                analysis_result="",
                execution_time=execution_time,
                success=False
            )
            
            logger.log_error(
                error_type="weather_analysis_error",
                error_message=str(e),
                context={"destinations": self.bucket_list, "origin": self.origin}
            )
            
            st.error(f"An error occurred during weather analysis: {str(e)}")
            return None
    
    def _analyze_destinations_weather(self):
        """Analyze weather conditions for all bucket list destinations."""
        agents = TripAgents(llm=self.llm)
        tasks = TripTasks()
        
        # Create a weather analysis agent
        weather_agent = agents.city_selection_agent()
        
        # Create analysis task
        weather_task = tasks.identify_task(
            weather_agent,
            self.origin,
            ", ".join(self.bucket_list),
            f"Weather analysis and seasonal recommendations for bucket list destinations during {self.date_range}",
            self.date_range
        )
        
        # Run weather analysis
        crew = Crew(
            agents=[weather_agent],
            tasks=[weather_task],
            verbose=True
        )
        
        crew_start_time = datetime.datetime.now()
        with st.spinner("🌤️ Analyzing weather conditions for your bucket list destinations..."):
            result = crew.kickoff()
        crew_end_time = datetime.datetime.now()
        
        # Debug the weather analysis result
        print(f"🔍 WEATHER ANALYSIS RESULT TYPE: {type(result)}")
        print(f"🔍 WEATHER ANALYSIS RESULT LENGTH: {len(str(result)) if result else 0}")
        print(f"🔍 WEATHER ANALYSIS RESULT PREVIEW: {str(result)[:200] if result else 'NO RESULT'}")
        
        # Log the weather analysis crew execution
        logger.log_crew_execution(
            crew_type="weather_analysis",
            agents_count=1,
            tasks_count=1,
            start_time=crew_start_time,
            end_time=crew_end_time,
            success=result is not None,
            destinations=self.bucket_list,
            result=str(result) if result else None
        )
        
        return result
    
    def _generate_multiple_plans(self, selected_destinations):
        """Generate detailed plans for selected destinations."""
        all_results = {}
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, destination in enumerate(selected_destinations):
            status_text.text(f"Planning trip {i+1}/{len(selected_destinations)}: {destination}")
            progress_bar.progress((i) / len(selected_destinations))
            
            # Create individual trip plan for this destination
            with st.expander(f"🎯 Detailed Plan for {destination}", expanded=True):
                trip_crew = TripCrew(
                    self.origin, 
                    destination, 
                    [datetime.datetime.strptime(self.date_range.split(' to ')[0], '%Y-%m-%d').date(),
                     datetime.datetime.strptime(self.date_range.split(' to ')[1], '%Y-%m-%d').date()],
                    self.interests, 
                    self.passengers
                )
                
                result = trip_crew.run()
                all_results[destination] = result
        
        progress_bar.progress(1.0)
        status_text.text("✅ All trip plans completed!")
        
        return all_results


if __name__ == "__main__":
    icon("🏖️ VacAIgent")

    st.subheader("Let AI agents plan your next vacation!",
                 divider="rainbow", anchor=False)

    import datetime

    today = datetime.datetime.now().date()
    next_year = today.year + 1
    jan_16_next_year = datetime.date(next_year, 1, 10)

    with st.sidebar:
        st.header("✈️ Choose Your Planning Mode")
        
        # Trip mode selection
        trip_mode = st.radio(
            "How would you like to plan your trip?",
            options=["🎯 Single Destination", "� Bucket List (Multiple Destinations)"],
            help="Choose single destination for focused planning or bucket list for multiple destinations"
        )
        
        st.divider()
        st.header("�👇 Enter your trip details")
        
        with st.form("my_form"):
            location = st.text_input(
                "Where are you currently located?", placeholder="San Mateo, CA")
            
            if trip_mode == "🎯 Single Destination":
                cities = st.text_input(
                    "City and country are you interested in vacationing at?", 
                    placeholder="Bali, Indonesia")
            else:
                cities = st.text_area(
                    "Enter your bucket list destinations (one per line):",
                    placeholder="Bali, Indonesia\nTokyo, Japan\nParis, France\nSantorini, Greece",
                    height=100,
                    help="Enter each destination on a new line. We'll analyze all destinations and recommend the best options."
                )
            
            date_range = st.date_input(
                "Date range you are interested in traveling?",
                min_value=today,
                value=(today, jan_16_next_year + datetime.timedelta(days=6)),
                format="MM/DD/YYYY",
            )
            passengers = st.number_input(
                "Number of passengers?",
                min_value=1,
                max_value=9,
                value=1,
                step=1
            )
            interests = st.text_area("High level interests and hobbies or extra details about your trip?",
                                     placeholder="2 adults who love swimming, dancing, hiking, and eating")

            submitted = st.form_submit_button("🚀 Plan My Trip!")

        st.divider()

        # Credits to joaomdmoura/CrewAI for the code: https://github.com/joaomdmoura/crewAI
        st.sidebar.markdown(
        """
        Credits to [**@joaomdmoura**](https://twitter.com/joaomdmoura)
        for creating **crewAI** 🚀
        """,
            unsafe_allow_html=True
        )

        st.sidebar.info("Click the logo to visit GitHub repo", icon="👇")
        st.sidebar.markdown(
            """
        <a href="https://github.com/joaomdmoura/crewAI" target="_blank">
            <img src="https://raw.githubusercontent.com/joaomdmoura/crewAI/main/docs/crewai_logo.png" alt="CrewAI Logo" style="width:100px;"/>
        </a>
        """,
            unsafe_allow_html=True
        )


if submitted:
    # Log user input
    logger.log_user_input(
        trip_mode=trip_mode,
        location=location,
        cities=cities,
        date_range=date_range,
        interests=interests,
        passengers=passengers
    )
    
    if trip_mode == "🎯 Single Destination":
        # Single destination mode
        with st.status("🤖 **Agents at work...**", state="running", expanded=True) as status:
            with st.container(height=500, border=False):
                sys.stdout = StreamToExpander(st)
                trip_crew = TripCrew(location, cities, date_range, interests, passengers)
                result = trip_crew.run()
            status.update(label="✅ Trip Plan Ready!",
                          state="complete", expanded=False)

        # Add download buttons ABOVE the trip plan
        if result:
            # Create a formatted version of the trip plan for download
            trip_plan_content = f"""
# 🏖️ VacAIgent Trip Plan

**Generated on:** {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}

**Trip Details:**
- **Origin:** {location}
- **Destination:** {cities}
- **Travel Dates:** {date_range[0].strftime('%B %d, %Y')} to {date_range[1].strftime('%B %d, %Y')}
- **Passengers:** {passengers}
- **Interests:** {interests}

---

{result}

---

*This trip plan was generated by VacAIgent - AI-powered travel planning*
*Visit us at: Your VacAIgent App*
            """
        
        # Create PDF content
        def create_pdf(content):
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from io import BytesIO
            import re
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor='blue'
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor='darkblue'
            )
            
            story = []
            
            # Convert markdown to simple text for PDF
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 6))
                elif line.startswith('# '):
                    story.append(Paragraph(line[2:], title_style))
                elif line.startswith('## '):
                    story.append(Paragraph(line[3:], heading_style))
                elif line.startswith('**') and line.endswith('**'):
                    story.append(Paragraph(f"<b>{line[2:-2]}</b>", styles['Normal']))
                elif line.startswith('- '):
                    story.append(Paragraph(f"• {line[2:]}", styles['Normal']))
                elif line.startswith('*') and line.endswith('*'):
                    story.append(Paragraph(f"<i>{line[1:-1]}</i>", styles['Normal']))
                else:
                    # Clean up markdown formatting
                    clean_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                    clean_line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', clean_line)
                    if clean_line:
                        story.append(Paragraph(clean_line, styles['Normal']))
            
            doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            return pdf_data
        
        # Download buttons section
        st.markdown("### 📤 Share Your Trip Plan")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Markdown download
            st.download_button(
                label="📄 Download as Markdown",
                data=trip_plan_content,
                file_name=f"VacAIgent_Trip_Plan_{cities.replace(' ', '_').replace(',', '')}_{date_range[0].strftime('%Y%m%d')}.md",
                mime="text/markdown",
                help="Download as markdown file for easy editing"
            )
        
        with col2:
            # PDF download
            try:
                pdf_data = create_pdf(trip_plan_content)
                st.download_button(
                    label="📤 Download as PDF",
                    data=pdf_data,
                    file_name=f"VacAIgent_Trip_Plan_{cities.replace(' ', '_').replace(',', '')}_{date_range[0].strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    help="Download as PDF to share with friends and family!"
                )
            except Exception as e:
                st.error(f"PDF generation temporarily unavailable: {str(e)}")
                
        with col3:
            # Copy to clipboard
            if st.button("📋 Copy to Clipboard", help="Copy trip plan to clipboard"):
                st.code(trip_plan_content, language="markdown")
                st.success("Trip plan copied! You can now paste it anywhere.")
        
        # Sharing tip
        st.info("💡 **Tip:** Download and share your trip plan via WhatsApp, email, or social media!")
        
        st.divider()

        st.subheader("Here is your Trip Plan", anchor=False, divider="rainbow")
        st.markdown(result)
    
    else:
        # Bucket list mode
        st.header("🌍 Bucket List Trip Planning", anchor=False)
        
        # Parse bucket list
        bucket_destinations = [dest.strip() for dest in cities.split('\n') if dest.strip()]
        st.markdown(f"**Planning for {len(bucket_destinations)} destinations from your bucket list:**")
        
        # Display the destinations as a nice list
        for i, dest in enumerate(bucket_destinations, 1):
            st.markdown(f"{i}. {dest}")
        
        st.divider()
        
        # Initialize bucket list crew
        bucket_list_crew = BucketListCrew(location, cities, date_range, interests, passengers)
        
        # Weather analysis phase
        with st.status("🌤️ **Analyzing weather conditions...**", state="running", expanded=True) as status:
            with st.container(height=400, border=False):
                sys.stdout = StreamToExpander(st)
                weather_analysis = bucket_list_crew.run()
            status.update(label="✅ Weather Analysis Complete!",
                          state="complete", expanded=False)
        
        # Display weather analysis results
        if weather_analysis:
            st.subheader("🌤️ Weather-Based Destination Ranking", anchor=False, divider="blue")
            st.markdown(weather_analysis)
            
            st.divider()
            
            # Let user choose destinations for detailed planning
            st.subheader("🎯 Choose Destinations for Detailed Planning", anchor=False)
            selected_destinations = st.multiselect(
                "Select destinations you'd like detailed trip plans for:",
                options=bucket_destinations,
                default=bucket_destinations[:min(3, len(bucket_destinations))],
                help="We recommend selecting 2-3 destinations for detailed planning to get comprehensive trip plans."
            )
            
            # Add planning options with buttons
            st.markdown("### 🗺️ Planning Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if selected_destinations:
                    generate_selected = st.button(
                        f"🎯 Generate Plans for Selected ({len(selected_destinations)})",
                        type="primary",
                        help=f"Generate detailed plans for: {', '.join(selected_destinations)}"
                    )
                else:
                    st.button(
                        "🎯 Generate Plans for Selected (0)",
                        disabled=True,
                        help="Please select at least one destination first"
                    )
                    generate_selected = False
            
            with col2:
                generate_all = st.button(
                    f"🌍 Generate Plans for ALL ({len(bucket_destinations)})",
                    type="secondary",
                    help=f"Generate detailed plans for all destinations: {', '.join(bucket_destinations)}"
                )
            
            # Execute based on user choice
            if generate_selected and selected_destinations:
                destinations_to_plan = selected_destinations
                plan_title = f"🎯 Selected Destinations ({len(selected_destinations)})"
            elif generate_all:
                destinations_to_plan = bucket_destinations
                plan_title = f"🌍 All Bucket List Destinations ({len(bucket_destinations)})"
            else:
                destinations_to_plan = None
                plan_title = None
            
            if destinations_to_plan:
                # Generate detailed plans
                st.subheader("🗺️ Detailed Trip Plans", anchor=False, divider="green")
                st.markdown(f"**{plan_title}**")
                
                if len(destinations_to_plan) > 3:
                    st.warning(f"⏱️ Generating plans for {len(destinations_to_plan)} destinations may take several minutes. Please be patient!")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, destination in enumerate(destinations_to_plan):
                        status_text.text(f"Generating plan {i+1}/{len(destinations_to_plan)}: {destination}")
                        progress_bar.progress(i / len(destinations_to_plan))
                        
                        # Create individual trip plan for this destination
                        with st.expander(f"✈️ Complete Trip Plan: {destination}", expanded=True):
                            with st.status(f"🤖 **Planning {destination}...**", state="running", expanded=True) as plan_status:
                                with st.container(height=300, border=False):
                                    sys.stdout = StreamToExpander(st)
                                    trip_crew = TripCrew(
                                        location, 
                                        destination, 
                                        date_range,
                                        interests, 
                                        passengers
                                    )
                                    result = trip_crew.run()
                                plan_status.update(label=f"✅ {destination} Plan Ready!",
                                                  state="complete", expanded=False)
                            
                            # Display the plan
                            if result:
                                st.markdown(result)
                                
                                # Add download option for this destination
                                destination_plan_content = f"""
# 🏖️ VacAIgent Trip Plan - {destination}

**Generated on:** {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}

**Trip Details:**
- **Origin:** {location}
- **Destination:** {destination}
- **Travel Dates:** {date_range[0].strftime('%B %d, %Y')} to {date_range[1].strftime('%B %d, %Y')}
- **Passengers:** {passengers}
- **Interests:** {interests}

---

{result}

---

*This trip plan was generated by VacAIgent - AI-powered travel planning*
                                """
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button(
                                        label=f"📄 Download {destination} Plan",
                                        data=destination_plan_content,
                                        file_name=f"VacAIgent_{destination.replace(' ', '_').replace(',', '')}_{date_range[0].strftime('%Y%m%d')}.md",
                                        mime="text/markdown",
                                        key=f"download_{destination}"
                                    )
                                with col2:
                                    if st.button(f"📋 Copy {destination} Plan", key=f"copy_{destination}"):
                                        st.code(destination_plan_content, language="markdown")
                                        st.success(f"{destination} plan copied!")
                
                progress_bar.progress(1.0)
                status_text.text("✅ All detailed trip plans completed!")
                
                st.success(f"🎉 Your {len(destinations_to_plan)} trip plans are ready! Scroll up to view each destination's detailed plan.")
            else:
                st.info("💡 **Tip:** You can either select specific destinations or generate plans for all destinations at once!")
        else:
            st.error("Weather analysis failed. Please try again.")
