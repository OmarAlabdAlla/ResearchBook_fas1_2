#!/usr/bin/env python3
"""
ResearchBook - Streamlit Web Interface
Academic Intelligence Platform
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from researchbook_final import ResearchBookFinal
import json
import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="ResearchBook - Academic Intelligence Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize ResearchBook
@st.cache_resource
def init_researchbook():
    """Initialize ResearchBook connection (cached for performance)"""
    return ResearchBookFinal()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin: 1rem 0;
    }
    .result-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<h1 class="main-header">🔬 ResearchBook</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Academic Intelligence Platform powered by Neo4j + AI</p>', unsafe_allow_html=True)
    
    # Initialize ResearchBook
    try:
        rb = init_researchbook()
        st.success("✅ Connected to databases and AI system")
    except Exception as e:
        st.error(f"❌ Connection error: {e}")
        st.stop()
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    feature = st.sidebar.selectbox(
        "Choose ResearchBook Feature:",
        [
            "🏠 Home",
            "👤 Person Lookup", 
            "🎯 Expert Finder",
            "📊 Field Intelligence Brief",
            "💝 Researcher Matching",
            "📈 Database Overview",
            "📚 User Guide"
        ]
    )
    
    # Main content based on selection
    if feature == "🏠 Home":
        show_home_page()
    elif feature == "👤 Person Lookup":
        show_person_lookup(rb)
    elif feature == "🎯 Expert Finder":
        show_expert_finder(rb)
    elif feature == "📊 Field Intelligence Brief":
        show_field_brief(rb)
    elif feature == "💝 Researcher Matching":
        show_researcher_matching(rb)
    elif feature == "📈 Database Overview":
        show_database_overview(rb)
    elif feature == "📚 User Guide":
        show_user_guide()

def show_home_page():
    """Home page with feature overview"""
    st.markdown("## Welcome to ResearchBook! 🚀")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>👤 Person Lookup</h3>
            <p>Search our comprehensive researcher network. Get detailed profiles with ORCID data, career history, thesis involvement, and AI-generated expertise analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Field Intelligence Brief</h3>
            <p>Generate comprehensive research field reports. Analyze researcher networks, trends, and opportunities with AI-powered insights.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🎯 Expert Finder</h3>
            <p>Find experts on any topic with AI ranking. Get specific recommendations for media interviews, collaborations, or student supervision.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>💝 Researcher Matching</h3>
            <p>"Tinder for Researchers" - Find compatible researchers for collaboration based on expertise, roles, and AI compatibility analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Database stats
    st.markdown("## 📊 Database Coverage")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Academic Network", "154K", "Researchers")
    with col2:
        st.metric("Thesis Ecosystem", "58K", "Academic Relationships")
    with col3:
        st.metric("ORCID Coverage", "78K", "50% Coverage")
    with col4:
        st.metric("Relationship Roles", "731", "Unique Types")

def show_person_lookup(rb):
    """Person lookup interface"""
    st.markdown("## 👤 Person Lookup")
    st.markdown("Search our comprehensive academic network and get AI-powered researcher insights.")
    
    # Quick help
    with st.expander("💡 Quick Tips", expanded=False):
        st.markdown("""
        **✅ Best Practices:**
        - Use **full names**: "Maria Andersson" not just "Maria"
        - Try variations: "John Smith" vs "J. Smith"  
        - Check ORCID data for verification
        - **Read the AI analysis** - it's the most valuable part!
        
        **Perfect for:** Finding specific researchers, understanding their networks, checking expertise
        """)
    
    # Input
    researcher_name = st.text_input("Enter researcher name:", placeholder="e.g., Anders, Maria, John Smith")
    
    if st.button("🔍 Search Researcher", type="primary"):
        if researcher_name:
            with st.spinner("Searching databases and generating AI analysis..."):
                try:
                    result = rb.lookup_person(researcher_name)
                    
                    # Display results
                    st.markdown(f"### Results for: **{researcher_name}**")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Research Profiles", len(result.get('researcher_data', [])))
                    with col2:
                        st.metric("Academic Activities", len(result.get('thesis_data', [])))
                    with col3:
                        found_status = "Found" if (result['found_in_db1'] or result['found_in_db2']) else "Not Found"
                        st.metric("Status", found_status)
                    
                    if result['found_in_db1'] or result['found_in_db2']:
                        # AI Analysis
                        st.markdown("### 🤖 AI Profile Analysis")
                        st.markdown(f"""
                        <div class="result-box">
                        {result.get('ai_analysis', 'No analysis available')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Detailed data tabs
                        tab1, tab2 = st.tabs(["📊 Research Profile", "🎓 Thesis Activities"])
                        
                        with tab1:
                            if result.get('researcher_data'):
                                st.markdown("#### Database 1: Research Profile")
                                for i, profile in enumerate(result['researcher_data']):
                                    with st.expander(f"Profile {i+1}: {profile['name']}"):
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.write(f"**ORCID ID:** {profile.get('orcid_id', 'N/A')}")
                                            st.write(f"**Publications:** {profile.get('total_publications', 0)}")
                                        with col2:
                                            st.write(f"**Given Names:** {profile.get('given_names', 'N/A')}")
                                            st.write(f"**Family Name:** {profile.get('family_name', 'N/A')}")
                                        
                                        if profile.get('affiliations'):
                                            st.write("**Affiliations:**")
                                            for aff in profile['affiliations']:
                                                st.write(f"- {aff.get('organization', 'Unknown')} ({aff.get('role', 'N/A')})")
                        
                        with tab2:
                            if result.get('thesis_data'):
                                st.markdown("#### Database 2: Thesis Activities")
                                df = pd.DataFrame(result['thesis_data'])
                                st.dataframe(df, use_container_width=True)
                    else:
                        st.warning("No researcher found with that name in either database.")
                        
                except Exception as e:
                    st.error(f"Search error: {e}")
        else:
            st.warning("Please enter a researcher name to search.")

def show_expert_finder(rb):
    """Expert finder interface"""
    st.markdown("## 🎯 Expert Finder")
    st.markdown("Find experts on any topic with AI ranking and recommendations.")
    
    # Quick help
    with st.expander("💡 Quick Tips", expanded=False):
        st.markdown("""
        **✅ Best Practices:**
        - Be **specific**: "machine learning" not "AI"
        - Try synonyms: "sustainability" + "environmental science"
        - Use AI rankings - they consider expertise depth
        - Check "Best for:" recommendations (media, collaboration, supervision)
        
        **Perfect for:** Finding collaborators, media experts, understanding research landscape
        """)
    
    # Input
    topic = st.text_input("Enter research topic:", placeholder="e.g., machine learning, sustainability, robotics")
    limit = st.slider("Number of experts to find:", 5, 20, 10)
    
    if st.button("🔍 Find Experts", type="primary"):
        if topic:
            with st.spinner("Searching for experts and generating AI rankings..."):
                try:
                    result = rb.find_expert(topic, limit=limit)
                    
                    # Display results
                    st.markdown(f"### Expert Results for: **{topic}**")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Experts", result['experts_found'])
                    with col2:
                        st.metric("Research Network", result['db1_matches'])
                    with col3:
                        st.metric("Academic Network", result['db2_matches'])
                    
                    if result['experts_found'] > 0:
                        # AI Ranking
                        st.markdown("### 🤖 AI Expert Ranking & Analysis")
                        st.markdown(f"""
                        <div class="result-box">
                        {result['ai_ranking']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Expert details
                        st.markdown("### 📋 Expert Details")
                        for i, expert in enumerate(result.get('expert_list', [])):
                            with st.expander(f"Expert {i+1}: {expert['name']}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Source:** {expert.get('source', 'Unknown')}")
                                    if 'relevant_publications' in expert:
                                        st.write(f"**Relevant Publications:** {expert['relevant_publications']}")
                                    if 'relevant_theses' in expert:
                                        st.write(f"**Relevant Theses:** {expert['relevant_theses']}")
                                
                                with col2:
                                    if 'organizations' in expert:
                                        st.write(f"**Organizations:** {', '.join(expert['organizations'])}")
                                    if 'roles' in expert:
                                        st.write(f"**Roles:** {', '.join(expert['roles'])}")
                    else:
                        st.warning(f"No experts found for topic: {topic}")
                        
                except Exception as e:
                    st.error(f"Search error: {e}")
        else:
            st.warning("Please enter a research topic to search for experts.")

def show_field_brief(rb):
    """Field intelligence brief interface"""
    st.markdown("## 📊 Field Intelligence Brief")
    st.markdown("Generate comprehensive research field analysis with AI insights.")
    
    # Quick help
    with st.expander("💡 Quick Tips", expanded=False):
        st.markdown("""
        **✅ Best Practices:**
        - Use **field names**: "artificial intelligence", "biotechnology"
        - Try broader terms for better coverage
        - Review activity trends for field momentum
        - Use AI insights for strategic planning
        
        **Perfect for:** Grant writing, strategic planning, identifying research gaps
        """)
    
    # Input
    research_field = st.text_input("Enter research field:", placeholder="e.g., artificial intelligence, sustainability, biotechnology")
    
    if st.button("📊 Generate Field Brief", type="primary"):
        if research_field:
            with st.spinner("Analyzing field data and generating intelligence brief..."):
                try:
                    result = rb.generate_field_brief(research_field)
                    
                    # Display results
                    st.markdown(f"### Field Brief: **{research_field}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Active Researchers", result['researchers_found'])
                    with col2:
                        st.metric("Recent Activity", result['trends']['total_recent'])
                    
                    # AI Intelligence Brief
                    st.markdown("### 🤖 AI Intelligence Brief")
                    st.markdown(f"""
                    <div class="result-box">
                    {result['ai_intelligence_brief']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Trends visualization
                    if result['trends']['yearly_activity']:
                        st.markdown("### 📈 Activity Trends")
                        df = pd.DataFrame(result['trends']['yearly_activity'])
                        fig = px.bar(df, x='year', y='count', 
                                   title=f"Annual Research Activity in {research_field}",
                                   labels={'year': 'Year', 'count': 'Number of Theses'})
                        st.plotly_chart(fig, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Analysis error: {e}")
        else:
            st.warning("Please enter a research field to analyze.")

def show_researcher_matching(rb):
    """Researcher matching interface"""
    st.markdown("## 💝 Researcher Matching")
    st.markdown('"Tinder for Researchers" - Find compatible researchers for collaboration.')
    
    # Quick help
    with st.expander("💡 Quick Tips", expanded=False):
        st.markdown("""
        **✅ Best Practices:**
        - Use **full researcher names** for best matches
        - Target researchers with thesis/publication activity
        - Look for complementary (not identical) expertise
        - Use AI compatibility analysis to understand WHY matches work
        
        **Perfect for:** Finding collaborators, understanding academic networks, career progression
        """)
    
    # Input
    researcher_name = st.text_input("Enter researcher name to find matches:", placeholder="e.g., Anders, Maria")
    
    if st.button("💝 Find Matches", type="primary"):
        if researcher_name:
            with st.spinner("Finding compatible researchers and generating match analysis..."):
                try:
                    result = rb.match_researchers(researcher_name)
                    
                    if 'error' not in result:
                        # Display results
                        st.markdown(f"### Matches for: **{researcher_name}**")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Potential Matches", result['matches_found'])
                        with col2:
                            st.metric("Keywords Used", len(result.get('target_keywords', [])))
                        
                        # Target keywords
                        if result.get('target_keywords'):
                            st.markdown("### 🏷️ Target Researcher Keywords")
                            keywords_display = ", ".join(result['target_keywords'][:10])  # Show first 10
                            st.info(f"Matching based on: {keywords_display}")
                        
                        # AI Analysis
                        st.markdown("### 🤖 AI Match Analysis")
                        st.markdown(f"""
                        <div class="result-box">
                        {result['ai_analysis']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Match details
                        if result.get('potential_matches'):
                            st.markdown("### 👥 Potential Matches")
                            for i, match in enumerate(result['potential_matches']):
                                with st.expander(f"Match {i+1}: {match['name']} (Relevance: {match['relevance']})"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write(f"**Name:** {match['name']}")
                                        st.write(f"**Relevance Score:** {match['relevance']}")
                                    with col2:
                                        st.write(f"**Roles:** {', '.join(match.get('roles', []))}")
                                    
                                    if match.get('sample_work'):
                                        st.write("**Sample Work:**")
                                        for work in match['sample_work']:
                                            st.write(f"- {work}")
                    else:
                        st.error(result['error'])
                        
                except Exception as e:
                    st.error(f"Matching error: {e}")
        else:
            st.warning("Please enter a researcher name to find matches.")

def show_database_overview(rb):
    """Database overview and statistics"""
    st.markdown("## 📈 Database Overview")
    st.markdown("Overview of ResearchBook data sources and statistics.")
    
    # Database info
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="success-box">
        <h3>🌍 Research Intelligence System</h3>
        <ul>
        <li><strong>154,272</strong> researchers</li>
        <li><strong>78,287</strong> with ORCID IDs (50.7%)</li>
        <li><strong>685,709</strong> relationships</li>
        <li><strong>ORCID integration</strong> with career tracking</li>
        <li><strong>Temporal data</strong> for career progression</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="success-box">
        <h3>🎓 Academic Collaboration Network</h3>
        <ul>
        <li><strong>57,633</strong> nodes (40K people, 18K theses)</li>
        <li><strong>52,772</strong> relationships</li>
        <li><strong>731</strong> unique relationship types</li>
        <li><strong>Complete thesis ecosystems</strong></li>
        <li><strong>Granular role mapping</strong></li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature status
    st.markdown("### ✅ Feature Status")
    features = [
        ("Person Lookup", "✅ Working", "Search across database with AI analysis"),
        ("Expert Finder", "✅ Working", "Topic-based expert discovery with ranking"),
        ("Field Intelligence", "✅ Working", "Comprehensive research field reports"),
        ("Researcher Matching", "✅ Working", "AI-powered collaboration matching"),
        ("Cross-database Integration", "✅ Working", "Seamless data correlation"),
        ("AI Analysis", "✅ Working", "Via LightLLM")
    ]
    
    for feature, status, description in features:
        col1, col2, col3 = st.columns([2, 1, 4])
        with col1:
            st.write(f"**{feature}**")
        with col2:
            st.write(status)
        with col3:
            st.write(description)

def show_user_guide():
    """Comprehensive User Guide"""
    st.markdown("## 📚 ResearchBook User Guide")
    st.markdown("Complete guide to getting maximum value from ResearchBook")
    
    # Quick Start section
    with st.expander("🚀 Quick Start (2 minutes)", expanded=True):
        st.markdown("""
        ### Get Started in 3 Steps:
        1. **Choose your task:** Find expert? Research field analysis? Collaboration partners?
        2. **Enter specific search terms** (avoid single words - be descriptive!)
        3. **Read the AI analysis** - this is where the real insights are!
        
        **💡 Pro Tip:** ResearchBook isn't just search - it's research intelligence. The AI analysis provides insights you won't find anywhere else.
        """)
    
    # Use Cases
    with st.expander("🎯 Real Use Cases", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### 👨‍🔬 For Researchers:
            - **"I need AI/ML collaborators for my project"**
              → Expert Finder: "machine learning"
            
            - **"Who should I contact about sustainability?"**
              → Person Lookup: specific names from Field Brief
              
            - **"What's the landscape in my research area?"**  
              → Field Intelligence Brief: your field
            
            - **"Who could I collaborate with?"**
              → Researcher Matching: your name
            """)
        
        with col2:
            st.markdown("""
            #### 👩‍💼 For Administrators/Media:
            - **"Find media experts on current topics"**
              → Expert Finder + "Best for media interviews"
            
            - **"Analyze our research strengths"**
              → Field Intelligence across multiple areas
              
            - **"Identify collaboration opportunities"**
              → Field Brief + Researcher Matching
            
            - **"Background on research areas"**
              → Field Intelligence + Person Lookup
            """)
    
    # Feature Guides
    st.markdown("## 🔧 Feature-by-Feature Guides")
    
    # Person Lookup Guide
    with st.expander("👤 Person Lookup - Master Guide", expanded=False):
        st.markdown("""
        ### ✅ Best Practices:
        - **Use full names:** "Maria Andersson" not "Maria"
        - **Try variations:** "John Smith", "J. Smith", "J.A. Smith"
        - **Look for ORCID verification:** Green checkmark = verified researcher
        - **Don't skip AI analysis:** Contains career insights and collaboration potential
        
        ### 📊 Understanding Results:
        - **Research Profiles:** ORCID data, publications, career history
        - **Academic Activities:** Thesis supervision, examination, collaboration roles
        - **AI Analysis:** Expertise areas, career progression, network connections
        
        ### 🎯 When to Use:
        - Researching potential collaborators
        - Preparing for meetings/conferences  
        - Understanding someone's academic background
        - Verifying expertise areas
        """)
    
    # Expert Finder Guide  
    with st.expander("🎯 Expert Finder - Master Guide", expanded=False):
        st.markdown("""
        ### ✅ Search Strategy:
        - **Be specific:** "machine learning" not "computers"
        - **Try synonyms:** "sustainability" AND "environmental science"
        - **Use compound terms:** "biomedical engineering", "quantum computing"
        
        ### 📈 Interpreting Rankings:
        - **AI considers:** Publication relevance, supervision experience, career depth
        - **"Best for" recommendations:** Media (communication skills), Collaboration (complementary expertise), Supervision (teaching experience)
        - **Higher thesis counts:** More teaching/mentoring experience
        
        ### 🔍 Pro Tips:
        - Research Network = publication-based expertise
        - Academic Network = thesis/supervision expertise  
        - Both networks = well-rounded expert
        - Check sample work for relevance verification
        """)
    
    # Field Intelligence Guide
    with st.expander("📊 Field Intelligence Brief - Master Guide", expanded=False):
        st.markdown("""
        ### 🎯 Strategic Applications:
        - **Grant Writing:** Understanding field landscape and key players
        - **Research Planning:** Identifying gaps and opportunities
        - **Partnership Development:** Finding collaboration potential
        - **Competitive Analysis:** Mapping research strengths
        
        ### 📈 Reading Trends:
        - **Rising thesis counts:** Growing, active field
        - **Multiple institutions:** Collaborative opportunities exist
        - **Recent activity spikes:** Emerging hot topics
        - **Stable patterns:** Mature, established field
        
        ### 💡 AI Insights Decode:
        - **"Key Players":** Most influential researchers
        - **"Research Networks":** Collaboration clusters
        - **"Opportunities":** Gaps where you could contribute
        - **"Strategic Insights":** Actionable recommendations
        """)
    
    # Researcher Matching Guide
    with st.expander("💝 Researcher Matching - Master Guide", expanded=False):
        st.markdown("""
        ### 🤝 Collaboration Success Tips:
        - **Target active researchers:** Those with recent thesis/publication activity
        - **Look for complementary expertise:** Not identical skills
        - **Use AI compatibility scores:** Understand WHY matches work
        - **Check academic progression:** Career stage compatibility
        
        ### 📊 Match Quality Indicators:
        - **High relevance scores:** Strong keyword/topic overlap
        - **Diverse roles:** Supervision + examination = well-connected
        - **Recent activity:** Currently active in research
        - **AI explanations:** Specific collaboration opportunities
        
        ### 💡 Networking Strategy:
        - Use matches to map research communities
        - Follow supervision chains for academic lineages
        - Look for bridge people connecting different areas
        """)
    
    # AI Analysis Guide
    with st.expander("🤖 Understanding AI Analysis", expanded=False):
        st.markdown("""
        ### What AI Analysis Tells You:
        
        **📊 "Expertise Areas"** = What they actually work on (not just job titles)
        
        **📈 "Career Progression"** = How they've developed professionally over time
        
        **🤝 "Academic Networks"** = Who they're connected to and how
        
        **🔗 "Collaboration Potential"** = Why you should work together (specific opportunities)
        
        **🎯 "Strategic Insights"** = Bigger picture opportunities for the field
        
        ### 🎯 Trust the AI When:
        - It explains WHY someone is an expert (methodology-based reasoning)
        - It suggests specific use cases (media, collaboration, supervision)
        - It identifies patterns across multiple data points
        - It connects dots you might miss manually
        
        ### ⚠️ Verify When:
        - Names seem unusual (potential matching errors)
        - Claims seem too broad (cross-check with source data)
        - Very recent information (AI works on historical patterns)
        """)
    
    # Search Tips
    with st.expander("🔍 Advanced Search Tips", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 Better Search Terms:
            
            **Instead of:** "computers"  
            **Use:** "computer science", "computational methods"
            
            **Instead of:** "environment"  
            **Use:** "sustainability", "climate science"
            
            **Instead of:** "medicine"  
            **Use:** "biomedical engineering", "clinical research"
            
            **Instead of:** "AI"  
            **Use:** "artificial intelligence", "machine learning"
            """)
        
        with col2:
            st.markdown("""
            ### 🔄 Finding Hidden Connections:
            
            1. **Use Field Intelligence** to discover field-specific terminology
            2. **Check thesis keywords** for research area vocabulary  
            3. **Try related concepts:** "robotics" → "automation", "control systems"
            4. **Follow supervision chains** to map academic families
            5. **Cross-reference different searches** to find intersection points
            """)
    
    # Getting Maximum Value
    with st.expander("💰 Getting Maximum Value", expanded=False):
        st.markdown("""
        ### 🔬 Research Planning Workflow:
        1. **Field Intelligence** → Understand the landscape
        2. **Expert Finder** → Identify key players  
        3. **Person Lookup** → Deep-dive on specific people
        4. **Researcher Matching** → Find your collaboration partners
        
        ### 📊 Strategic Analysis Workflow:
        1. **Multiple field searches** to compare research areas
        2. **Track same searches over time** to spot trends
        3. **Use AI insights for decision-making** (not just data)
        4. **Cross-reference ORCID data** for verification
        
        ### 🚀 Pro User Strategies:
        - **Bookmark interesting researchers** (copy/paste AI analysis)
        - **Build collaboration target lists** from multiple searches
        - **Use for competitive intelligence** (who's working on what)
        - **Research preparation** for conferences, meetings, partnerships
        """)
    
    # FAQ
    with st.expander("❓ Frequently Asked Questions", expanded=False):
        st.markdown("""
        ### Common Questions:
        
        **Q: "Why no results for my search?"**  
        A: Try broader terms, check spelling, use synonyms, or search related concepts
        
        **Q: "How accurate is the AI analysis?"**  
        A: AI interprets data patterns - always cross-check with source data when making important decisions
        
        **Q: "What if someone appears in both networks?"**  
        A: Great! More complete profile = better insights and more reliable analysis
        
        **Q: "Can I export or save results?"**  
        A: Currently view-only, but you can copy/paste AI analysis for your records
        
        **Q: "How often is data updated?"**  
        A: Research network updated regularly, thesis network reflects historical academic relationships
        
        **Q: "Why do some searches find more experts than others?"**  
        A: Popular research areas have more activity; niche fields may have fewer but higher-quality matches
        """)
    
    # Quick Reference
    with st.expander("⚡ Quick Reference Card", expanded=False):
        st.markdown("""
        ### 🚀 ResearchBook Cheat Sheet:
        
        | Feature | Best For | Pro Tip |
        |---------|----------|---------|
        | **👤 Person Lookup** | Specific researchers | Full names work best |
        | **🎯 Expert Finder** | Topic experts | Be specific, check AI rankings |
        | **📊 Field Intelligence** | Strategic planning | Perfect for grant writing |
        | **💝 Researcher Matching** | Collaboration | Use AI compatibility analysis |
        
        ### 💡 Remember:
        **ResearchBook isn't just search - it's research intelligence!**
        
        The AI analysis is the most valuable part - it connects dots, identifies patterns, and provides insights you won't find anywhere else.
        """)


if __name__ == "__main__":
    main()