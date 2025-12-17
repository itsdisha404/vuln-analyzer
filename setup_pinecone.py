import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
model = SentenceTransformer('all-MiniLM-L6-v2')

index_name = "vuln-db"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )

index = pc.Index(index_name)

vuln_docs = [
    {
        "id": "sql-injection-1",
        "text": "SQL Injection: Occurs when user input is directly concatenated into SQL queries without sanitization. Severity: Critical. Use parameterized queries or prepared statements. Example: query = 'SELECT * FROM users WHERE name = ' + user_input is vulnerable.",
        "type": "SQL Injection"
    },
    {
        "id": "xss-1",
        "text": "Cross-Site Scripting (XSS): Malicious scripts injected into web pages viewed by users. Severity: High. Sanitize all user inputs and use Content Security Policy. Escape HTML characters before rendering.",
        "type": "XSS"
    },
    {
        "id": "command-injection-1",
        "text": "Command Injection: Executing arbitrary system commands through unvalidated input. Severity: Critical. Never pass user input directly to system calls. Use allowlists and input validation. Example: os.system('ping ' + user_input) is dangerous.",
        "type": "Command Injection"
    },
    {
        "id": "insecure-deps-1",
        "text": "Insecure Dependencies: Using outdated libraries with known vulnerabilities. Severity: Medium to Critical. Regularly update dependencies, use tools like npm audit or pip-audit. Check CVE databases.",
        "type": "Dependency Vulnerability"
    },
    {
        "id": "open-ports-1",
        "text": "Open Ports and Misconfigurations: Unnecessary services exposed to internet. Severity: Medium. Close unused ports, use firewalls, implement principle of least privilege. Common risky ports: 22 (SSH), 3389 (RDP), 27017 (MongoDB).",
        "type": "Network Misconfiguration"
    }
]

vectors = []
for doc in vuln_docs:
    embedding = model.encode(doc["text"]).tolist()
    vectors.append({
        "id": doc["id"],
        "values": embedding,
        "metadata": {"text": doc["text"], "type": doc["type"]}
    })

index.upsert(vectors=vectors)
print(f"Uploaded {len(vectors)} vulnerability documents to Pinecone!")
