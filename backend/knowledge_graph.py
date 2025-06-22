from pydantic import BaseModel
from typing import Optional, Dict, Any,List


class Knowledge_Node(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    content: Optional[Any] = None
    in_edge:List[str] = []
    out_edge:List[str] = []


class Knowledge_Edge(BaseModel):
    id: str
    start_node: Knowledge_Node
    end_node: Knowledge_Node
    description: Optional[str]


class Knowledge_Graph(BaseModel):
    nodes: Dict[str, Knowledge_Node] = {}
    edges: Dict[str, Knowledge_Edge] = {}

    def __init__(self, **data):
        super().__init__(**data)
        self.nodes = data.get('nodes', {})
        self.edges = data.get('edges', {})
        self.node_connection = data.get('node_connection', {}) #ai写的，这三句不是很理解

    def add_node(self, node: Knowledge_Node):
        if self.verify_node(self,node) == -1:
            print("ValueError")
            exit(0)
        else:
            self.nodes[node.id] = node
    
    def verify_node(self,node:Knowledge_Node):
        return self.nodes.get(node.id,-1)
    
    def verify_edge_id(self,edge:Knowledge_Edge):
        return self.edges.get(edge.id,-1)
    
    def add_edge(self,edge:Knowledge_Edge):
        if self.verify_node(edge.start_node) == -1 or self.verify_node(edge.end_node) == -1:
            print('ValueError')
            exit(0)
        elif self.verify_edge_id(edge) != -1:
            print('ValueError')
            exit(0)
        else:
            self.edges[edge.id] = edge
            edge.start_node.out_edge.append(edge.id)
            edge.end_node.in_edge.append(edge.id)
            
        
            