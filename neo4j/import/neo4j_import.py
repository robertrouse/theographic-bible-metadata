import os
from pathlib import Path
from neo4j import GraphDatabase
import re

# Set Variables
DB_PATH = "bolt://localhost:7687"
DB_USER = "neo4j"
DB_PASSWORD = "ChangeMyPassword"

# Connect to Neo4j
driver = GraphDatabase.driver(DB_PATH, auth=(DB_USER, DB_PASSWORD))

def clean_statement(stmt: str) -> str:
    stmt = stmt.strip()
    # Remove single-line comments (// or --), but be careful with /* */
    stmt = re.sub(r'//.*?$|^\s*--.*?$', '', stmt, flags=re.MULTILINE)
    return stmt

def run_cypher_file(filepath):
    """Read and execute a Cypher script file."""
    with open(filepath, 'r') as f:
        script = f.read()
    with driver.session() as session:
        session.run(script)

THIS_SCRIPT_DIR = Path(__file__).resolve().parent

# Create indexes for fast loading
with open(THIS_SCRIPT_DIR / 'index.cypher', encoding="utf-8") as f:
    index_content = f.read()
raw_statements = [s.strip() for s in index_content.split(';') if s.strip()]

with driver.session() as session:
    for raw in raw_statements:
        stmt = clean_statement(raw)
        if not stmt or stmt.startswith((':', '//')):  # skip empty / meta commands
            continue
        try:
            session.run(stmt)
            # print(f"Executed: {stmt[:60]}{'...' if len(stmt) > 60 else ''}")
        except Exception as e:
            print(f"Error in statement:\n{stmt[:200]}...\n→ {e}")

# Load nodes
nodes_dir = THIS_SCRIPT_DIR / 'nodes'
for filename in sorted(os.listdir(nodes_dir)):
    if filename.endswith('.cypher'):
        run_cypher_file(nodes_dir/filename)

# Load Relationships
rel_dir = THIS_SCRIPT_DIR / 'relationships'
for filename in sorted(os.listdir(rel_dir)):
    if filename.endswith('.cypher'):
        run_cypher_file(rel_dir/filename)

# Close the driver
driver.close()
