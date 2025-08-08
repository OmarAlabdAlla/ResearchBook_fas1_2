#!/usr/bin/env python3

from neo4j import GraphDatabase
import os

# Database credentials
NEO4J_URI = "neo4j+s://84711dd6.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "kvWkwedbwzpifLYyA_lhgUTIVdR-l37Gz1XJHKB7bWI"
NEO4J_DATABASE = "neo4j"

def test_connection():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    try:
        # Test basic connectivity
        with driver.session(database=NEO4J_DATABASE) as session:
            # Test connection with a simple query
            result = session.run("RETURN 'Connection successful!' as message")
            print("✅ Database connection successful!")
            
            # Get basic database stats
            stats_query = """
            CALL apoc.meta.stats() YIELD labels, relTypesCount, nodeCount, relCount
            RETURN labels, relTypesCount, nodeCount, relCount
            """
            
            try:
                stats_result = session.run(stats_query)
                for record in stats_result:
                    print(f"📊 Database Stats:")
                    print(f"   Node count: {record['nodeCount']}")
                    print(f"   Relationship count: {record['relCount']}")
                    print(f"   Labels: {record['labels']}")
                    print(f"   Relationship types: {record['relTypesCount']}")
            except Exception as e:
                # Fallback if APOC is not available
                print("APOC not available, getting basic stats...")
                
                # Get node counts by label
                node_stats = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY count DESC
                """)
                
                print("📊 Node counts by type:")
                for record in node_stats:
                    if record['label']:
                        print(f"   {record['label']}: {record['count']}")
            
            # Test Chalmers structure
            chalmers_query = """
            MATCH (c:Organization {name: 'Chalmers University of Technology'})
            RETURN c.name as name LIMIT 1
            """
            
            chalmers_result = session.run(chalmers_query)
            chalmers_record = chalmers_result.single()
            
            if chalmers_record:
                print(f"🏛️ Found Chalmers: {chalmers_record['name']}")
            else:
                # Try alternative search
                alt_query = """
                MATCH (c:Organization)
                WHERE c.name CONTAINS 'Chalmers' OR c.name CONTAINS 'chalmers'
                RETURN c.name as name LIMIT 5
                """
                alt_result = session.run(alt_query)
                print("🔍 Chalmers-related organizations:")
                for record in alt_result:
                    print(f"   {record['name']}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    test_connection()