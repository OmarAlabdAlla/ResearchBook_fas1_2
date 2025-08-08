#!/usr/bin/env python3
"""
ResearchBook Extended - Adding Field Intelligence Brief & Researcher Matching
"""

from researchbook import ResearchBook
import json

class ResearchBookExtended(ResearchBook):
    
    def generate_field_brief(self, research_field: str) -> dict:
        """
        RESEARCHBOOK CORE FEATURE 3: Field Intelligence Brief
        Generate comprehensive research field analysis
        """
        print(f"📊 Generating field brief for: {research_field}")
        
        # Get researchers from both databases
        db1_researchers = self._get_field_researchers_db1(research_field)
        db2_researchers = self._get_field_researchers_db2(research_field)
        
        # Analyze collaboration networks
        collaboration_data = self._analyze_field_collaborations(research_field)
        
        # Get recent trends and activities
        trends_data = self._get_field_trends(research_field)
        
        # Generate AI intelligence brief
        brief_prompt = self._create_field_brief_prompt(
            research_field, db1_researchers, db2_researchers, 
            collaboration_data, trends_data
        )
        
        ai_brief = self.ai_query(brief_prompt, max_tokens=2000)
        
        return {
            "field": research_field,
            "db1_researchers": len(db1_researchers),
            "db2_researchers": len(db2_researchers),
            "total_unique_researchers": len(set([r["name"] for r in db1_researchers + db2_researchers])),
            "collaboration_networks": collaboration_data,
            "trends": trends_data,
            "ai_intelligence_brief": ai_brief
        }
    
    def _get_field_researchers_db1(self, field: str) -> list:
        """Get researchers working in field from DB1"""
        with self.db1_driver.session(database="neo4j") as session:
            query = """
            MATCH (p:Person)-[w:WORKED_AT]->(org:Organization)
            WHERE toLower(w.department) CONTAINS toLower($field) OR
                  toLower(w.role) CONTAINS toLower($field)
            WITH p, org, w
            MATCH (p)-[auth:AUTHORED]->(pub:Publication)
            RETURN p.name as name,
                   p.orcid_id as orcid_id,
                   org.name as organization,
                   w.department as department,
                   w.role as role,
                   count(pub) as publications
            ORDER BY publications DESC
            LIMIT 20
            """
            
            result = session.run(query, field=field)
            return [dict(record) for record in result]
    
    def _get_field_researchers_db2(self, field: str) -> list:
        """Get researchers in field from DB2 thesis data"""
        with self.db2_driver.session(database="neo4j") as session:
            query = """
            MATCH (p:Person)-[r]->(t:Thesis)
            WHERE toLower(t.title) CONTAINS toLower($field) OR
                  any(keyword IN t.keywords WHERE toLower(keyword) CONTAINS toLower($field))
            WITH p, type(r) as role, count(t) as thesis_count
            RETURN p.name as name,
                   collect(DISTINCT role) as thesis_roles,
                   thesis_count
            ORDER BY thesis_count DESC
            LIMIT 20
            """
            
            result = session.run(query, field=field)
            return [dict(record) for record in result]
    
    def _analyze_field_collaborations(self, field: str) -> dict:
        """Analyze collaboration patterns in the field"""
        with self.db1_driver.session(database="neo4j") as session:
            # Find co-authorship networks in the field
            query = """
            MATCH (p1:Person)-[:AUTHORED]->(pub:Publication)<-[:AUTHORED]-(p2:Person)
            WHERE p1 <> p2
            WITH p1, p2, count(pub) as shared_pubs
            WHERE shared_pubs >= 2
            RETURN p1.name as person1, p2.name as person2, shared_pubs
            ORDER BY shared_pubs DESC
            LIMIT 10
            """
            
            result = session.run(query)
            collaborations = [dict(record) for record in result]
            
            return {
                "top_collaborations": collaborations,
                "total_collaboration_pairs": len(collaborations)
            }
    
    def _get_field_trends(self, field: str) -> dict:
        """Get recent trends and activity in the field"""
        with self.db2_driver.session(database="neo4j") as session:
            # Get recent thesis activity
            query = """
            MATCH (t:Thesis)
            WHERE toLower(t.title) CONTAINS toLower($field) OR
                  any(keyword IN t.keywords WHERE toLower(keyword) CONTAINS toLower($field))
            WITH t, t.created_date.year as year
            WHERE year >= 2020
            RETURN year, count(t) as thesis_count
            ORDER BY year DESC
            """
            
            result = session.run(query, field=field)
            yearly_activity = [dict(record) for record in result]
            
            return {
                "yearly_thesis_activity": yearly_activity,
                "recent_activity": sum(record["thesis_count"] for record in yearly_activity)
            }
    
    def _create_field_brief_prompt(self, field: str, db1_researchers: list, 
                                 db2_researchers: list, collaborations: dict, trends: dict) -> str:
        """Create AI prompt for field intelligence brief"""
        prompt = f"""
        Generate a comprehensive intelligence brief for the research field: "{field}"
        
        DATABASE 1 RESEARCHERS (Publications & Career Data):
        {json.dumps(db1_researchers, indent=2)}
        
        DATABASE 2 RESEARCHERS (Thesis Activities):
        {json.dumps(db2_researchers, indent=2)}
        
        COLLABORATION NETWORKS:
        {json.dumps(collaborations, indent=2)}
        
        TRENDS & ACTIVITY:
        {json.dumps(trends, indent=2)}
        
        Please provide a comprehensive intelligence brief including:
        
        1. **Field Overview**: Current state and scope of "{field}" research
        2. **Key Players**: Top researchers, their roles, and expertise areas
        3. **Research Networks**: Collaboration patterns and research clusters
        4. **Activity Trends**: Recent developments, thesis production, growth patterns
        5. **Institutional Landscape**: Major organizations and departments involved
        6. **Research Opportunities**: Gaps, emerging areas, collaboration potential
        7. **Strategic Insights**: Recommendations for stakeholders (researchers, students, funders)
        
        Format as a professional intelligence report (max 1500 words).
        """
        
        return prompt
    
    def match_researchers(self, researcher_name: str, match_type: str = "collaboration") -> dict:
        """
        RESEARCHBOOK CORE FEATURE 4: Researcher Matching
        Find compatible researchers for collaboration, supervision, etc.
        """
        print(f"💝 Matching researchers for: {researcher_name} (type: {match_type})")
        
        # Get target researcher profile
        target_profile = self.lookup_person(researcher_name)
        
        if not (target_profile["found_in_db1"] or target_profile["found_in_db2"]):
            return {"error": f"Researcher {researcher_name} not found"}
        
        # Find potential matches based on type
        if match_type == "collaboration":
            matches = self._find_collaboration_matches(target_profile)
        elif match_type == "supervision":
            matches = self._find_supervision_matches(target_profile)
        elif match_type == "expertise":
            matches = self._find_expertise_matches(target_profile)
        else:
            matches = self._find_general_matches(target_profile)
        
        # Generate AI matching analysis
        matching_prompt = self._create_matching_prompt(target_profile, matches, match_type)
        ai_analysis = self.ai_query(matching_prompt, max_tokens=1500)
        
        return {
            "target_researcher": researcher_name,
            "match_type": match_type,
            "potential_matches": len(matches),
            "matches": matches,
            "ai_matching_analysis": ai_analysis
        }
    
    def _find_collaboration_matches(self, target_profile: dict) -> list:
        """Find researchers for collaboration based on complementary expertise"""
        # Extract expertise areas from target
        target_keywords = []
        
        # Get keywords from thesis data
        for thesis in target_profile.get("thesis_data", []):
            target_keywords.extend(thesis.get("keywords", []))
        
        if not target_keywords:
            return []
        
        # Find researchers with related but different expertise
        with self.db2_driver.session(database="neo4j") as session:
            query = """
            MATCH (p:Person)-[r]->(t:Thesis)
            WHERE any(keyword IN t.keywords WHERE keyword IN $target_keywords)
              AND p.name <> $target_name
            WITH p, collect(DISTINCT type(r)) as roles, 
                 collect(DISTINCT t.title)[..2] as sample_work,
                 count(t) as relevance_score
            RETURN p.name as name, roles, sample_work, relevance_score
            ORDER BY relevance_score DESC
            LIMIT 10
            """
            
            result = session.run(query, 
                               target_keywords=target_keywords[:10], 
                               target_name=target_profile["name"])
            
            return [dict(record) for record in result]
    
    def _find_supervision_matches(self, target_profile: dict) -> list:
        """Find supervision matches (supervisors for students or students for supervisors)"""
        with self.db2_driver.session(database="neo4j") as session:
            query = """
            MATCH (p:Person)-[r:SUPERVISOR]->(t:Thesis)
            WHERE p.name <> $target_name
            WITH p, count(t) as supervised_count,
                 collect(DISTINCT t.title)[..2] as sample_theses
            RETURN p.name as name, supervised_count, sample_theses
            ORDER BY supervised_count DESC
            LIMIT 10
            """
            
            result = session.run(query, target_name=target_profile["name"])
            return [dict(record) for record in result]
    
    def _find_expertise_matches(self, target_profile: dict) -> list:
        """Find researchers with similar expertise"""
        return self._find_collaboration_matches(target_profile)
    
    def _find_general_matches(self, target_profile: dict) -> list:
        """Find general matches across multiple criteria"""
        return self._find_collaboration_matches(target_profile)
    
    def _create_matching_prompt(self, target_profile: dict, matches: list, match_type: str) -> str:
        """Create AI prompt for researcher matching analysis"""
        prompt = f"""
        Analyze researcher matching for "{target_profile['name']}" seeking {match_type}.
        
        TARGET RESEARCHER PROFILE:
        {json.dumps({k: v for k, v in target_profile.items() if k != 'ai_analysis'}, indent=2)}
        
        POTENTIAL MATCHES:
        {json.dumps(matches, indent=2)}
        
        Please provide:
        
        1. **Top 5 Recommended Matches** ranked by compatibility for {match_type}
        2. **Match Explanations**: Why each match would work well
        3. **Complementary Strengths**: How they complement the target researcher
        4. **Collaboration Potential**: Specific areas where they could work together
        5. **Match Quality Assessment**: Score and rationale for top matches
        
        Focus on {match_type} specifically and provide actionable recommendations.
        """
        
        return prompt

# Demo the extended features
if __name__ == "__main__":
    rb_extended = ResearchBookExtended()
    
    print("=== TESTING FIELD INTELLIGENCE BRIEF ===")
    field_brief = rb_extended.generate_field_brief("artificial intelligence")
    print(f"Field: {field_brief['field']}")
    print(f"Researchers found: DB1={field_brief['db1_researchers']}, DB2={field_brief['db2_researchers']}")
    print(f"Total unique: {field_brief['total_unique_researchers']}")
    print(f"Recent activity: {field_brief['trends']['recent_activity']} theses")
    print("\nAI Intelligence Brief:")
    print(field_brief['ai_intelligence_brief'])
    
    print("\n" + "="*70 + "\n")
    
    print("=== TESTING RESEARCHER MATCHING ===")
    matches = rb_extended.match_researchers("Anders", "collaboration")
    if "error" not in matches:
        print(f"Target: {matches['target_researcher']}")
        print(f"Match type: {matches['match_type']}")
        print(f"Potential matches found: {matches['potential_matches']}")
        print("\nAI Matching Analysis:")
        print(matches['ai_matching_analysis'])
    else:
        print(matches["error"])
    
    rb_extended.close_connections()