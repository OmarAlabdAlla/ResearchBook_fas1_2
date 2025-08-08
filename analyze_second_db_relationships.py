#!/usr/bin/env python3

from neo4j import GraphDatabase
import json

# Second database credentials  
NEO4J_URI = "neo4j+s://7ae716c3.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "NmDzl4lSyYJqhAAtJinGbhNgbNFeiQIsH2M6IrfFECM"
NEO4J_DATABASE = "neo4j"

def analyze_all_relationships():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            print("🔍 COMPREHENSIVE ANALYSIS OF SECOND DATABASE RELATIONSHIPS\n")
            
            # 1. Get all relationship types and their counts
            print("📊 ALL RELATIONSHIP TYPES WITH COUNTS:")
            rel_count_query = """
            MATCH ()-[r]->()
            RETURN type(r) as relationship_type, count(r) as count
            ORDER BY count DESC
            """
            
            rel_counts = session.run(rel_count_query)
            relationship_stats = {}
            total_relationships = 0
            
            for record in rel_counts:
                rel_type = record['relationship_type']
                count = record['count']
                relationship_stats[rel_type] = count
                total_relationships += count
                print(f"   {rel_type}: {count:,}")
            
            print(f"\n📈 Total Relationships: {total_relationships:,}")
            print(f"📈 Unique Relationship Types: {len(relationship_stats)}")
            
            # 2. Analyze top relationship types in detail
            print(f"\n🔬 DETAILED ANALYSIS OF TOP 20 RELATIONSHIP TYPES:\n")
            
            top_relationships = sorted(relationship_stats.items(), key=lambda x: x[1], reverse=True)[:20]
            
            for rel_type, count in top_relationships:
                print(f"🔗 {rel_type} ({count:,} relationships)")
                
                # Get sample relationships for this type
                sample_query = f"""
                MATCH (source)-[r:{rel_type}]->(target)
                RETURN labels(source)[0] as source_label,
                       source.name as source_name,
                       labels(target)[0] as target_label,
                       target.title as target_title,
                       target.name as target_name,
                       keys(r) as rel_properties,
                       r
                LIMIT 3
                """
                
                try:
                    sample_result = session.run(sample_query)
                    samples = list(sample_result)
                    
                    if samples:
                        print(f"   Pattern: {samples[0]['source_label']} --{rel_type}--> {samples[0]['target_label']}")
                        print(f"   Examples:")
                        
                        for i, record in enumerate(samples, 1):
                            source_display = record['source_name'] or 'Unnamed'
                            target_display = record['target_title'] or record['target_name'] or 'Unnamed'
                            
                            print(f"     {i}. {source_display[:50]} --> {target_display[:50]}")
                            
                            # Show relationship properties if any
                            rel_props = dict(record['r'])
                            if rel_props:
                                print(f"        Properties: {list(rel_props.keys())}")
                                # Show sample values for interesting properties
                                for key, value in list(rel_props.items())[:3]:
                                    if value and str(value).strip():
                                        print(f"          {key}: {str(value)[:100]}")
                    else:
                        print(f"   No sample data available")
                        
                except Exception as e:
                    print(f"   Error getting samples: {e}")
                
                print()
            
            # 3. Categorize relationships by academic function
            print(f"🎓 RELATIONSHIP CATEGORIZATION BY ACADEMIC FUNCTION:\n")
            
            # Define categories
            categories = {
                "Thesis Supervision & Examination": [
                    "SUPERVISOR", "EXAMINER", "CO_SUPERVISOR", "MAIN_SUPERVISOR", 
                    "EXTERNAL_SUPERVISOR", "COMPANY_SUPERVISOR", "ACADEMIC_SUPERVISOR",
                    "INDUSTRIAL_SUPERVISOR", "THESIS_SUPERVISOR", "DEPUTY_SUPERVISOR",
                    "ASSISTANT_SUPERVISOR", "PRINCIPAL_SUPERVISOR", "HEAD_SUPERVISOR",
                    "LEAD_SUPERVISOR", "SECOND_SUPERVISOR", "FORMER_SUPERVISOR",
                    "UNIVERSITY_SUPERVISOR", "COLLEGE_SUPERVISOR", "RESEARCH_SUPERVISOR",
                    "INTERNAL_SUPERVISOR", "EXTERNAL_EXAMINER", "STUDENT_EXAMINER",
                    "EXAMINATOR", "ASSISTANT_EXAMINER", "FORMER_EXAMINER", 
                    "INITIAL_EXAMINER", "ACADEMIC_EXAMINER", "GUARDIAN_EXAMINER"
                ],
                
                "Advisory & Mentorship": [
                    "ADVISOR", "MENTOR", "THESIS_ADVISOR", "TECHNICAL_ADVISOR",
                    "ACADEMIC_ADVISOR", "COMPANY_ADVISOR", "INDUSTRIAL_ADVISOR", 
                    "ADVISER", "EXPERT_ADVISOR", "RESEARCH_ADVISOR", "MEDICAL_ADVISOR",
                    "CLINICAL_ADVISOR", "ARCHITECTURAL_ADVISOR", "UX_ADVISOR",
                    "EXTERNAL_ADVISOR", "SCIENTIFIC_ADVISOR", "ACADEMIC_MENTOR",
                    "MASTER_STUDENT_MENTOR", "TECHNICAL_MENTOR", "INDUSTRY_MENTOR"
                ],
                
                "Authorship & Publications": [
                    "AUTHOR", "CO_AUTHOR", "REFERENCED_AUTHOR", "REPORT_AUTHOR",
                    "PREVIOUS_REPORT_AUTHOR", "PRIOR_THESIS_AUTHOR"
                ],
                
                "Project Management & Leadership": [
                    "PROJECT_LEADER", "PROJECT_MANAGER", "PROJECT_COORDINATOR",
                    "PROJECT_SUPERVISOR", "PROJECT_INITIATOR", "PROJECT_OWNER",
                    "PROJECT_SPONSOR", "PROJECT_DEVELOPER", "PROJECT_FACILITATOR",
                    "PROJECT_ORGANIZER", "PROJECT_COMMISSIONER", "PROJECT_PROVIDER",
                    "PROJECT_SUPPORTER", "PROJECT_ADVISOR", "PROJECT_CONTACT",
                    "PROJECT_STARTER", "PROJECT_CREATOR", "PROJECT_PROPOSER",
                    "PROJECT_PARTNER", "PROJECT_CLIENT", "PROJECT_CONTRIBUTOR",
                    "PROJECT_ADMINISTRATOR", "PROJECT_SECRETARY", "PROJECT_PROPOSER"
                ],
                
                "Technical Support & Consultation": [
                    "TECHNICAL_SUPPORT", "TECHNICAL_CONSULTANT", "CONSULTANT", 
                    "EXPERT_CONSULTANT", "TECHNICAL_EXPERT", "EXPERT", "SPECIALIST",
                    "TECHNICAL_SPECIALIST", "RESEARCH_CONSULTANT", "INDUSTRY_CONSULTANT",
                    "ACADEMIC_CONSULTANT", "MEDICAL_CONSULTANT", "CLINICAL_CONSULTANT",
                    "STATISTICAL_CONSULTANT", "TECHNICAL_ADVISOR", "TECHNICAL_COACH",
                    "TECHNICAL_MENTOR", "TECHNICAL_GUIDANCE", "GUIDANCE_PROVIDER"
                ],
                
                "Collaboration & Research": [
                    "COLLABORATOR", "RESEARCH_COLLABORATOR", "INDUSTRY_COLLABORATOR",
                    "ACADEMIC_COLLABORATOR", "EXTERNAL_COLLABORATOR", "RESEARCH_PARTNER",
                    "CONTRIBUTOR", "RESEARCH_CONTRIBUTOR", "TECHNICAL_CONTRIBUTOR",
                    "INDUSTRY_CONTRIBUTOR", "RESEARCH_PARTICIPANT", "RESEARCHER",
                    "RESEARCH_ASSISTANT", "RESEARCH_ENGINEER", "RESEARCH_MANAGER"
                ],
                
                "Administrative & Support": [
                    "SUPPORT", "ADMINISTRATIVE_SUPPORT", "ACADEMIC_SUPPORT", 
                    "RESEARCH_SUPPORT", "INDUSTRY_SUPPORT", "LABORATORY_SUPPORT",
                    "SUPPORT_STAFF", "SUPPORT_PROVIDER", "SUPPORTER", "LAB_SUPPORT",
                    "IT_SUPPORT", "FINANCIAL_SUPPORT_PROVIDER", "FINANCIAL_SUPPORT",
                    "PERSONAL_SUPPORT", "MORAL_SUPPORT", "DATA_SUPPORT"
                ],
                
                "Teaching & Education": [
                    "TEACHER", "LECTURER", "PROFESSOR", "ASSISTANT_PROFESSOR", 
                    "ASSOCIATE_PROFESSOR", "SENIOR_LECTURER", "UNIVERSITY_LECTURER",
                    "TECHNICAL_LECTURER", "GUEST_LECTURER", "INSTRUCTOR", 
                    "LAB_INSTRUCTOR", "COURSE_INSTRUCTOR", "TUTOR", "TRAINER"
                ],
                
                "Industry & External Relations": [
                    "COMPANY_SUPERVISOR", "COMPANY_CONTACT", "COMPANY_REPRESENTATIVE",
                    "COMPANY_SPONSOR", "COMPANY_ADVISOR", "COMPANY_TUTOR", "CEO",
                    "MANAGER", "DIRECTOR", "INDUSTRY_CONTACT", "INDUSTRY_EXPERT",
                    "INDUSTRIAL_PARTNER", "CONTACT_PERSON", "CLIENT", "HOST"
                ]
            }
            
            # Categorize and count
            for category, rel_types in categories.items():
                total_count = sum(relationship_stats.get(rel_type, 0) for rel_type in rel_types)
                found_types = [rel_type for rel_type in rel_types if rel_type in relationship_stats]
                
                print(f"📂 {category}: {total_count:,} relationships")
                print(f"   Types found: {len(found_types)}/{len(rel_types)}")
                
                # Show top 5 in this category
                category_sorted = [(rel_type, relationship_stats[rel_type]) 
                                 for rel_type in found_types]
                category_sorted.sort(key=lambda x: x[1], reverse=True)
                
                for rel_type, count in category_sorted[:5]:
                    print(f"     • {rel_type}: {count:,}")
                print()
            
            # 4. Find uncategorized relationships
            all_categorized = set()
            for rel_types in categories.values():
                all_categorized.update(rel_types)
            
            uncategorized = [(rel_type, count) for rel_type, count in relationship_stats.items() 
                           if rel_type not in all_categorized]
            uncategorized.sort(key=lambda x: x[1], reverse=True)
            
            if uncategorized:
                print(f"🔍 UNCATEGORIZED RELATIONSHIPS ({len(uncategorized)} types):")
                for rel_type, count in uncategorized[:20]:  # Show top 20 uncategorized
                    print(f"   • {rel_type}: {count:,}")
                print()
            
            # 5. Academic hierarchy analysis
            print(f"🏛️ ACADEMIC HIERARCHY PATTERNS:")
            
            hierarchy_query = """
            MATCH (p:Person)-[r:SUPERVISOR]->(t:Thesis)<-[r2:AUTHOR]-(student:Person)
            WHERE p <> student
            RETURN p.name as supervisor, 
                   student.name as student,
                   t.title as thesis_title
            LIMIT 10
            """
            
            try:
                hierarchy_result = session.run(hierarchy_query)
                print("   Sample Supervisor-Student relationships:")
                for record in hierarchy_result:
                    print(f"     {record['supervisor']} supervises {record['student']}")
                    print(f"       Thesis: {record['thesis_title'][:80]}...")
                    print()
            except Exception as e:
                print(f"   Error analyzing hierarchy: {e}")
                
    except Exception as e:
        print(f"❌ Analysis error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    analyze_all_relationships()