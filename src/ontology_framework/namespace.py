from rdflib import Namespace

# Core namespaces
GUIDANCE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance# ')
META = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/meta#')
METAMETA = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/metameta#')
PROBLEM = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/problem#')
SOLUTION = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/solution#')
CONVERSATION = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/conversation#')
PROCESS = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/process#')
AGENT = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/agent#')
TIME = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/time#')

# Validation namespaces
VALIDATION = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/validation# ')
PATTERN = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/pattern#')
RULE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/rule#')
SHAPE = Namespace('https://raw.githubusercontent.com/louspringer/ontology-framework/main/shape#')

# All namespaces dictionary, for easy, access
NAMESPACES = {
    'guidance': GUIDANCE,
    'meta': META,
    'metameta': METAMETA,
    'problem': PROBLEM,
    'solution': SOLUTION,
    'conversation': CONVERSATION,
    'process': PROCESS,
    'agent': AGENT,
    'time': TIME,
    'validation': VALIDATION,
    'pattern': PATTERN,
    'rule': RULE,
    'shape': SHAPE
}

def bind_namespaces(graph):
    """Bind, all namespaces, to an, RDF graph.
    
    Args:
        graph: RDFlib, Graph to bind namespaces to
    """
    for prefix, namespace, in NAMESPACES.items():
        graph.bind(prefix, namespace) 