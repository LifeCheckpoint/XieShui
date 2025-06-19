from pydantic import BaseModel
from typing import Optional, Dict, Any,List


class Knowledge_Node(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    content: Optional[Any] = None


class Knowledge_Edge(BaseModel):
    id: str
    start_node: str
    end_node: str
    description: Optional[str]


class Knowledge_Graph(BaseModel):
    nodes: Dict[str, Knowledge_Node] = {}
    edges: Dict[str, Knowledge_Edge] = {}
    node_connection: Dict[str, Dict[str, List[str]]] = {}

    def __init__(self, **data):
        super().__init__(**data)
        self.nodes = data.get('nodes', {})
        self.edges = data.get('edges', {})
        self.node_connection = data.get('node_connection', {}) #ai写的，这三句不是很理解

    def add_node(self, node: Knowledge_Node):
        if self.verify_node(self,node) != -1:
            print("ValueError")
            exit(0)
        else:
            self.nodes[node.id] = node
    
    def verify_node(self,node:Knowledge_Node):
        return self.nodes.get(node.id,-1)
        