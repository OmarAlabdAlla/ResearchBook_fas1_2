#!/usr/bin/env python3

from neo4j import GraphDatabase
import os

# Second database credentials
NEO4J_URI = "neo4j+s://7ae716c3.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "NmDzl4lSyYJqhAAtJinGbhNgbNFeiQIsH2M6IrfFECM"
NEO4J_DATABASE = "neo4j"

def test_second_database():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            # Test connection
            result = session.run("RETURN 'Second database connected!' as message")
            print("✅ Second database connection successful!")
            
            # Get basic database stats
            try:
                stats_query = """
                CALL apoc.meta.stats() YIELD labels, relTypesCount, nodeCount, relCount
                RETURN labels, relTypesCount, nodeCount, relCount
                """
                stats_result = session.run(stats_query)
                for record in stats_result:
                    print(f"📊 Second Database Stats:")
                    print(f"   Node count: {record['nodeCount']}")
                    print(f"   Relationship count: {record['relCount']}")
                    print(f"   Labels: {record['labels']}")
                    print(f"   Relationship types: {record['relTypesCount']}")
            except Exception as e:
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
                        
                # Get relationship counts
                rel_stats = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as rel_type, count(r) as count
                ORDER BY count DESC
                """)
                
                print("🔗 Relationship counts:")
                for record in rel_stats:
                    print(f"   {record['rel_type']}: {record['count']}")
            
            # Explore the structure - get sample nodes from each label
            print("\n🔍 Exploring database structure:")
            
            # Get all labels first
            labels_query = "CALL db.labels()"
            labels_result = session.run(labels_query)
            labels = [record['label'] for record in labels_result]
            
            for label in labels[:5]:  # Limit to first 5 labels
                sample_query = f"""
                MATCH (n:{label})
                RETURN n LIMIT 3
                """
                sample_result = session.run(sample_query)
                print(f"\n📝 Sample {label} nodes:")
                
                for i, record in enumerate(sample_result):
                    node = record['n']
                    print(f"   {i+1}. {dict(node)}")
            
            # Get relationship types
            rel_types_query = "CALL db.relationshipTypes()"
            rel_types_result = session.run(rel_types_query)
            rel_types = [record['relationshipType'] for record in rel_types_result]
            
            print(f"\n🔗 Available relationship types: {rel_types}")
            
            # Show some sample relationships
            if rel_types:
                sample_rel_query = f"""
                MATCH (a)-[r:{rel_types[0]}]->(b)
                RETURN labels(a)[0] as from_label, type(r) as rel_type, labels(b)[0] as to_label
                LIMIT 5
                """
                sample_rel_result = session.run(sample_rel_query)
                print(f"\n🔗 Sample {rel_types[0]} relationships:")
                for record in sample_rel_result:
                    print(f"   {record['from_label']} --{record['rel_type']}--> {record['to_label']}")
            
    except Exception as e:
        print(f"❌ Second database connection failed: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    test_second_database()