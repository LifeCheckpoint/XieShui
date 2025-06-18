from pydantic import BaseModel
from typing import Optional, Dict, Any


class Knowledge_Node(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    content: Optional[Any] = None


class Knowledge_Edge(BaseModel):
    id: int
    start_node: str
    end_node: str
    description: Optional[str]


class Knowledge_Graph(BaseModel):
    nodes: Dict[int, Knowledge_Node]
    edges: Dict[int, Knowledge_Edge]
    node_connection: Dict[int, Dict[int, list[int]]]

    def __init__(self):
        nodes: Dict[int, Knowledge_Node] = {}
        edges: Dict[int, Knowledge_Edge] = {}
        node_connection: Dict[int, Dict[int, list[int]]]  # 不是很理解

    def add_node(self, node: Knowledge_Node):
        if 2 == 2:
            pass
        else:
            self.nodes.update(node.id, node)
