from crewai import Crew, LLM
from trip_agents import TripAgents, StreamToExpander
from trip_tasks import TripTasks
import streamlit as st
import datetime
import sys
from langchain_openai import OpenAI


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
        try:
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

            result = crew.kickoff()
            self.output_placeholder.markdown(result)
            return result
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None


if __name__ == "__main__":
    icon("🏖️ VacAIgent")

    st.subheader("Let AI agents plan your next vacation!",
                 divider="rainbow", anchor=False)

    import datetime

    today = datetime.datetime.now().date()
    next_year = today.year + 1
    jan_16_next_year = datetime.date(next_year, 1, 10)

    with st.sidebar:
        st.header("👇 Enter your trip details")
        with st.form("my_form"):
            location = st.text_input(
                "Where are you currently located?", placeholder="San Mateo, CA")
            cities = st.text_input(
                "City and country are you interested in vacationing at?", placeholder="Bali, Indonesia")
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

            submitted = st.form_submit_button("Submit")

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
