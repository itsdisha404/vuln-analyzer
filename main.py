import os
import json
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from llama_cpp import Llama
from dotenv import load_dotenv

load_dotenv()

print("Loading models...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

model_path = "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
if not os.path.exists(model_path):
    print(f"Warning: Model file not found at {model_path}")
    print("Please download the model and place it in the models/ directory.")
    exit(1)

try:
    llama_model = Llama(
        model_path=model_path,
        n_ctx=2048,
        n_threads=4
    )
except Exception as e:
    print(f"Error loading Llama model: {e}")
    exit(1)

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index("vuln-db")

def analyze_vulnerability(user_input):
    """Analyze code for security vulnerabilities using embeddings and LLM"""
    
    print("Searching for similar vulnerabilities...")
    query_embedding = embedding_model.encode(user_input).tolist()
    
    results = index.query(
        vector=query_embedding,
        top_k=3,
        include_metadata=True
    )
    
    context = "\n\n".join([match['metadata']['text'] for match in results['matches']])
    
    prompt = f"""<|system|>
You are a cybersecurity expert. Analyze the given code/scan and provide a structured vulnerability report.
</s>
<|user|>
Context from vulnerability database:
{context}

Code/Scan to analyze:
{user_input}

Provide your analysis in valid JSON format with these exact keys:
- vulnerability: name of the vulnerability
- severity: Critical/High/Medium/Low
- description: brief description
- impact: potential impact
- remediation: list of steps to fix

Response (valid JSON only):
</s>
<|assistant|>"""

    print("Generating analysis with LLaMA...")
    response = llama_model(
        prompt,
        max_tokens=500,
        temperature=0.3,
        stop=["</s>", "<|user|>"]
    )
    
    result_text = response['choices'][0]['text'].strip()
    
    try:
        start_idx = result_text.find('{')
        end_idx = result_text.rfind('}') + 1
        json_str = result_text[start_idx:end_idx]
        result = json.loads(json_str)
    except Exception:
        result = {
            "vulnerability": "Parse Error",
            "severity": "Unknown",
            "description": result_text,
            "impact": "Could not parse LLaMA output",
            "remediation": ["Review the raw output"]
        }
    
    return result

def main():
    print("=" * 60)
    print("AI Vulnerability Analyzer")
    print("=" * 60)
    
    sample_input = """
user = input()
query = "SELECT * FROM users WHERE name = '" + user + "'"
cursor.execute(query)
    """.strip()
    
    print("\nAnalyzing code:\n")
    print(sample_input)
    print("\n" + "-" * 60 + "\n")
    
    result = analyze_vulnerability(sample_input)
    
    print("VULNERABILITY REPORT:")
    print(json.dumps(result, indent=2))
    
    with open('vulnerability_report.json', 'w') as f:
        json.dump(result, indent=2, fp=f)
    
    print("\nReport saved to vulnerability_report.json")

if __name__ == "__main__":
    main()
