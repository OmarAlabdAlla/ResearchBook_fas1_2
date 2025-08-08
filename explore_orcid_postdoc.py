#!/usr/bin/env python3

from neo4j import GraphDatabase

# First database credentials
NEO4J_URI = "neo4j+s://84711dd6.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "kvWkwedbwzpifLYyA_lhgUTIVdR-l37Gz1XJHKB7bWI"
NEO4J_DATABASE = "neo4j"

def explore_orcid_and_postdoc():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            print("🔍 Exploring ORCID and Postdoc data in first database...\n")
            
            # 1. Look for ORCID data
            print("📋 ORCID Integration:")
            orcid_query = """
            MATCH (p:Person)
            WHERE p.orcid_id IS NOT NULL OR 
                  p.orcid_given_names IS NOT NULL OR
                  p.orcid_family_name IS NOT NULL OR
                  any(key IN keys(p) WHERE key CONTAINS 'orcid')
            RETURN p
            LIMIT 5
            """
            
            orcid_result = session.run(orcid_query)
            orcid_count = 0
            for record in orcid_result:
                person = record['p']
                print(f"   Person: {person.get('name', 'N/A')}")
                # Show all orcid-related properties
                orcid_props = {k: v for k, v in person.items() if 'orcid' in k.lower()}
                if orcid_props:
                    for key, value in orcid_props.items():
                        print(f"     {key}: {value}")
                orcid_count += 1
            
            if orcid_count == 0:
                # Try alternative search
                print("   Searching for ORCID in different property patterns...")
                alt_orcid_query = """
                CALL db.propertyKeys() YIELD propertyKey
                WHERE toLower(propertyKey) CONTAINS 'orcid'
                RETURN propertyKey
                LIMIT 10
                """
                alt_result = session.run(alt_orcid_query)
                orcid_props = [record['propertyKey'] for record in alt_result]
                print(f"   Found ORCID-related properties: {orcid_props}")
                
                if orcid_props:
                    # Sample data with these properties
                    sample_query = f"""
                    MATCH (p:Person)
                    WHERE p.{orcid_props[0]} IS NOT NULL
                    RETURN p.{orcid_props[0]} as orcid_value, p.name as name
                    LIMIT 5
                    """
                    sample_result = session.run(sample_query)
                    for record in sample_result:
                        print(f"   {record['name']}: {record['orcid_value']}")
            
            # 2. Look for postdoc history in WORKED_AT relationships
            print(f"\n🎓 Postdoc History Analysis:")
            postdoc_query = """
            MATCH (p:Person)-[r:WORKED_AT]->(o:Organization)
            WHERE toLower(r.position) CONTAINS 'postdoc' OR
                  toLower(r.position) CONTAINS 'post-doc' OR
                  toLower(r.position) CONTAINS 'post doc' OR
                  toLower(r.role) CONTAINS 'postdoc' OR
                  toLower(r.role) CONTAINS 'post-doc' OR
                  toLower(r.role) CONTAINS 'post doc'
            RETURN p.name as person_name, 
                   o.name as organization, 
                   r.position as position,
                   r.role as role,
                   r.start_year as start_year,
                   r.end_year as end_year
            LIMIT 10
            """
            
            postdoc_result = session.run(postdoc_query)
            postdoc_count = 0
            for record in postdoc_result:
                print(f"   {record['person_name']} -> {record['organization']}")
                print(f"     Position: {record['position']}")
                print(f"     Role: {record['role']}")
                if record['start_year'] or record['end_year']:
                    print(f"     Period: {record['start_year']} - {record['end_year']}")
                print()
                postdoc_count += 1
            
            if postdoc_count == 0:
                # Look for any WORKED_AT relationships with time data
                print("   Looking for WORKED_AT relationships with temporal data...")
                work_query = """
                MATCH (p:Person)-[r:WORKED_AT]->(o:Organization)
                WHERE r.start_year IS NOT NULL OR r.end_year IS NOT NULL OR
                      r.position IS NOT NULL OR r.role IS NOT NULL
                RETURN p.name as person_name, 
                       o.name as organization, 
                       r.position as position,
                       r.role as role,
                       r.start_year as start_year,
                       r.end_year as end_year
                LIMIT 10
                """
                
                work_result = session.run(work_query)
                for record in work_result:
                    print(f"   {record['person_name']} -> {record['organization']}")
                    if record['position']:
                        print(f"     Position: {record['position']}")
                    if record['role']:
                        print(f"     Role: {record['role']}")
                    if record['start_year'] or record['end_year']:
                        print(f"     Period: {record['start_year']} - {record['end_year']}")
                    print()
            
            # 3. Explore what relationship properties exist
            print("🔗 WORKED_AT Relationship Properties:")
            prop_query = """
            MATCH ()-[r:WORKED_AT]->()
            WITH keys(r) as props
            UNWIND props as prop
            RETURN DISTINCT prop
            ORDER BY prop
            """
            
            prop_result = session.run(prop_query)
            props = [record['prop'] for record in prop_result]
            print(f"   Available properties: {props}")
            
            # 4. Sample some WORKED_AT relationships to see structure
            print(f"\n📊 Sample WORKED_AT relationships:")
            sample_work_query = """
            MATCH (p:Person)-[r:WORKED_AT]->(o:Organization)
            RETURN p.name as person, o.name as org, r
            LIMIT 5
            """
            
            sample_result = session.run(sample_work_query)
            for record in sample_result:
                print(f"   {record['person']} -> {record['org']}")
                rel_props = dict(record['r'])
                if rel_props:
                    for key, value in rel_props.items():
                        print(f"     {key}: {value}")
                print()
            
    except Exception as e:
        print(f"❌ Error exploring data: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    explore_orcid_and_postdoc()