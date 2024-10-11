def format_node(node):
    node_type = list(node.labels)[0]  
    properties = node.items()  
    formatted_props = ", ".join([f'{k}: "{v}"' for k, v in properties])
    return f"(:{node_type} {{{formatted_props}}})"

def format_relationship(rel):
    rel_type = rel.__class__.__name__  
    return f"-[:{rel_type}]->"