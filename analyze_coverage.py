#!/usr/bin/env python3

from neo4j import GraphDatabase

# First database credentials
NEO4J_URI = "neo4j+s://84711dd6.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "kvWkwedbwzpifLYyA_lhgUTIVdR-l37Gz1XJHKB7bWI"
NEO4J_DATABASE = "neo4j"

def analyze_orcid_coverage():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            print("📊 ANALYZING ORCID COVERAGE AND TEMPORAL DATA\n")
            
            # 1. Total person count
            total_query = "MATCH (p:Person) RETURN count(p) as total_persons"
            total_result = session.run(total_query)
            total_persons = total_result.single()['total_persons']
            print(f"👥 Total Persons in Database: {total_persons:,}")
            
            # 2. ORCID coverage analysis
            orcid_queries = {
                "Has ORCID ID": "MATCH (p:Person) WHERE p.orcid_id IS NOT NULL AND p.orcid_id <> 'NOT_FOUND' RETURN count(p) as count",
                "ORCID ID = NOT_FOUND": "MATCH (p:Person) WHERE p.orcid_id = 'NOT_FOUND' RETURN count(p) as count",
                "Has ORCID given_names": "MATCH (p:Person) WHERE p.orcid_given_names IS NOT NULL RETURN count(p) as count",
                "Has ORCID publication_count": "MATCH (p:Person) WHERE p.orcid_publication_count IS NOT NULL RETURN count(p) as count",
                "Has ORCID search_date": "MATCH (p:Person) WHERE p.orcid_search_date IS NOT NULL RETURN count(p) as count",
                "No ORCID data at all": "MATCH (p:Person) WHERE p.orcid_id IS NULL AND p.orcid_given_names IS NULL AND p.orcid_search_date IS NULL RETURN count(p) as count"
            }
            
            print("🆔 ORCID Coverage Analysis:")
            orcid_stats = {}
            for description, query in orcid_queries.items():
                result = session.run(query)
                count = result.single()['count']
                percentage = (count / total_persons) * 100
                print(f"   {description}: {count:,} ({percentage:.1f}%)")
                orcid_stats[description] = count
            
            # 3. Temporal data in relationships
            print(f"\n🕐 TEMPORAL RELATIONSHIP DATA:")
            
            temporal_queries = {
                "WORKED_AT with start_year": """
                    MATCH ()-[r:WORKED_AT]->() 
                    WHERE r.start_year IS NOT NULL 
                    RETURN count(r) as count
                """,
                "WORKED_AT with end_year": """
                    MATCH ()-[r:WORKED_AT]->() 
                    WHERE r.end_year IS NOT NULL 
                    RETURN count(r) as count
                """,
                "AUTHORED with temporal data": """
                    MATCH ()-[r:AUTHORED]->() 
                    WHERE r.year IS NOT NULL OR r.date IS NOT NULL OR r.publication_year IS NOT NULL
                    RETURN count(r) as count
                """,
                "STUDIED_AT with temporal data": """
                    MATCH ()-[r:STUDIED_AT]->() 
                    WHERE r.start_year IS NOT NULL OR r.end_year IS NOT NULL OR r.graduation_year IS NOT NULL
                    RETURN count(r) as count
                """
            }
            
            for description, query in temporal_queries.items():
                try:
                    result = session.run(query)
                    count = result.single()['count']
                    print(f"   {description}: {count:,}")
                except Exception as e:
                    print(f"   {description}: Error - {e}")
            
            # 4. Sample temporal AUTHORED relationships
            print(f"\n📚 AUTHORED Relationships Temporal Analysis:")
            authored_sample_query = """
            MATCH (p:Person)-[r:AUTHORED]->(pub)
            WHERE r.year IS NOT NULL OR r.date IS NOT NULL OR r.publication_year IS NOT NULL
            RETURN p.name as person, 
                   pub.title as publication,
                   r.year as rel_year,
                   r.date as rel_date,
                   r.publication_year as pub_year,
                   keys(r) as all_props
            LIMIT 5
            """
            
            try:
                authored_result = session.run(authored_sample_query)
                for record in authored_result:
                    print(f"   {record['person']} -> {record['publication'][:50]}...")
                    print(f"     Props: {record['all_props']}")
                    if record['rel_year']:
                        print(f"     Year: {record['rel_year']}")
                    if record['pub_year']:
                        print(f"     Pub Year: {record['pub_year']}")
                    print()
            except Exception as e:
                print(f"   Error getting AUTHORED samples: {e}")
            
            # 5. Collaboration analysis
            print(f"🤝 COLLABORATION ANALYSIS:")
            
            # Co-authorship networks
            coauthor_query = """
            MATCH (p1:Person)-[:AUTHORED]->(pub:Publication)<-[:AUTHORED]-(p2:Person)
            WHERE p1 <> p2
            RETURN count(DISTINCT pub) as shared_publications,
                   count(DISTINCT [p1, p2]) as unique_pairs
            """
            
            coauthor_result = session.run(coauthor_query)
            coauthor_record = coauthor_result.single()
            print(f"   Publications with multiple authors: {coauthor_record['shared_publications']:,}")
            print(f"   Unique co-author pairs: {coauthor_record['unique_pairs']:,}")
            
            # 6. Cross-institutional collaborations
            cross_institutional_query = """
            MATCH (p1:Person)-[:WORKED_AT]->(org1:Organization),
                  (p2:Person)-[:WORKED_AT]->(org2:Organization),
                  (p1)-[:AUTHORED]->(pub:Publication)<-[:AUTHORED]-(p2)
            WHERE org1 <> org2 AND p1 <> p2
            RETURN count(DISTINCT pub) as cross_institutional_publications,
                   count(DISTINCT [org1.name, org2.name]) as institution_pairs
            LIMIT 1
            """
            
            try:
                cross_result = session.run(cross_institutional_query)
                cross_record = cross_result.single()
                if cross_record:
                    print(f"   Cross-institutional collaborations: {cross_record['cross_institutional_publications']:,} publications")
                    print(f"   Institution pairs collaborating: {cross_record['institution_pairs']:,}")
            except Exception as e:
                print(f"   Cross-institutional analysis error: {e}")
            
            # 7. Career progression patterns
            print(f"\n📈 CAREER PROGRESSION PATTERNS:")
            
            career_progression_query = """
            MATCH (p:Person)-[r1:WORKED_AT]->(org1:Organization)
            WHERE r1.start_year IS NOT NULL AND r1.end_year IS NOT NULL
            WITH p, r1, org1
            MATCH (p)-[r2:WORKED_AT]->(org2:Organization)
            WHERE r2.start_year IS NOT NULL AND r2.start_year > r1.end_year
            RETURN p.name as person,
                   org1.name as previous_org,
                   r1.role as previous_role,
                   r1.start_year + "-" + r1.end_year as previous_period,
                   org2.name as current_org,
                   r2.role as current_role,
                   r2.start_year as current_start
            LIMIT 10
            """
            
            try:
                career_result = session.run(career_progression_query)
                career_count = 0
                for record in career_result:
                    if career_count == 0:
                        print("   Sample career progressions:")
                    print(f"   • {record['person']}")
                    print(f"     {record['previous_org']} ({record['previous_role']}) {record['previous_period']}")
                    print(f"     → {record['current_org']} ({record['current_role']}) from {record['current_start']}")
                    print()
                    career_count += 1
                
                if career_count == 0:
                    print("   No clear career progression patterns found with current data")
                else:
                    print(f"   Found {career_count}+ career progression examples")
                    
            except Exception as e:
                print(f"   Career progression analysis error: {e}")
            
    except Exception as e:
        print(f"❌ Database analysis error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    analyze_orcid_coverage()

#     LinkedIn data → No professional connections outside academia
# External publication databases → Limited to Chalmers Research publications
# Conference attendance → No conference participation data
#  Editorial boards → No journal editorial information
#   - Prizes/awards → No award/recognition data
#   - Sabbaticals → No sabbatical tracking
#   - External research projects → Limited external funding/project data
