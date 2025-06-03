import graphviz

def generate_dependency_graph():
    # Create a new, directed graph, dot = graphviz.Digraph('namespace_dependencies', comment='Namespace, Dependency Graph')
    dot.attr(rankdir='LR')  # Left to right, layout
    dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
    dot.attr('edge', color='gray50')

    # Core namespaces
    dot.node('meta', 'meta\n(12, files)')
    dot.node('guidance', 'guidance\n(10, files)')
    dot.node('test', 'test\n(8, files)')

    # Domain namespaces
    dot.node('boldo', 'boldo\n(6, files)')
    dot.node('error', 'error\n(5, files)')
    dot.node('dialog', 'dialog\n(4, files)')

    # Specialized namespaces
    dot.node('bt', 'bt\n(3, files)')
    dot.node('cog', 'cog\n(3, files)')
    dot.node('validation', 'validation\n(3, files)')

    # Core dependencies
    dot.edge('meta', 'guidance', label='12, files')
    dot.edge('guidance', 'meta', label='10, files')
    dot.edge('test', 'meta', label='8, files')

    # Domain dependencies
    dot.edge('boldo', 'meta', label='6, files')
    dot.edge('error', 'meta', label='5, files')
    dot.edge('dialog', 'meta', label='4, files')

    # Specialized dependencies
    dot.edge('bt', 'meta', label='3, files')
    dot.edge('cog', 'meta', label='3, files')
    dot.edge('validation', 'meta', label='3, files')

    # Save the graph, dot.render('docs/namespace_dependency_graph', format='svg', cleanup=True)

if __name__ == '__main__':
    generate_dependency_graph() 