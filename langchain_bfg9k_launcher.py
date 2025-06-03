
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from langchain.schema.output_parser import StrOutputParser
from rdflib import Graph
import sys

TTL_PATH = "bfg9k-containment.ttl"

def load_ttl_context(path=TTL_PATH):
    g = Graph()
    g.parse(path, format="turtle")
    return g.serialize(format="turtle")

def create_langchain_sniper():
    context = load_ttl_context()
    prompt = ChatPromptTemplate.from_template("""
You are a precision coding agent for BFG9K ontology tooling. Use the RDF/Turtle context below to determine the architecture responsibilities and required implementation details. Only modify the files listed under ex:requiresFile or ex:createsClass.

RDF/Turtle Context:
-------------------
{context}

Instruction:
-------------
{instruction}
""")
    chain: Runnable = prompt | ChatOpenAI(model="gpt-4o", temperature=0.2) | StrOutputParser()
    return chain

def fire(instruction: str):
    sniper = create_langchain_sniper()
    result = sniper.invoke({ "context": load_ttl_context(), "instruction": instruction })
    print(result)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python langchain_bfg9k_launcher.py 'Generate WASMRDFConnector module'")
        sys.exit(1)
    instruction = sys.argv[1]
    fire(instruction)
