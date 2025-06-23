from pydantic import BaseModel
from typing import Optional, Dict, Any,List


class Knowledge_Node(BaseModel):
    id: str
    name: str
    description: Optional[str] = None #optional的意思是可以没有，有的话变量类型就是str
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
        if node.id in self.nodes:
            raise ValueError(f'节点ID{node.id}已存在')
        self.nodes[node.id] = node
    
    def add_edge(self,edge:Knowledge_Edge):
        if edge.start_node.id not in self.nodes:
            raise ValueError(f'节点ID{edge.start_node.id}不存在')
        elif edge.end_node.id not in self.nodes:
            raise ValueError(f'节点ID{edge.end_node.id}不存在')
        if edge.id in self.edges:
            raise ValueError(f'节点ID{edge.id}已存在')
        
        self.edges[edge.id] = edge
        edge.start_node.out_edge.append(edge.id)
        edge.end_node.in_edge.append(edge.id)
    
    def get_node(self,node_id:str):
        return self.nodes.get(node_id)
    
    def get_edge(self,edge_id:str):
        return self.edges.get(edge_id)
    
    def get_all_node(self):
        node_list = list(self.nodes.values())
        return node_list
    
    def get_all_edge(self):
        edge_list = list(self.edges.values())
        return edge_list
    
    def get_out_node(self,node_id:str):
        node = self.nodes[node_id]
        if node.id not in self.nodes:
            raise ValueError(f'节点ID{node.id}不存在')
        out_edge_list = [self.nodes[id] for id in node.out_edge]
        return out_edge_list
    
    def get_in_node(self,node_id:str):
        node = self.nodes[node_id]
        if node.id not in self.nodes:
            raise ValueError(f'节点ID{node.id}不存在')
        in_edge_list = [self.nodes[id] for id in node.in_edge]
        return in_edge_list
    
    def get_neighbours(self,node_id:str):
        node = self.nodes[node_id]
        if node.id not in self.nodes:
            raise ValueError(f'节点ID{node.id}不存在')
        node_list = []
        for edge_id in node.in_edge:
            edge = self.edges[edge_id]
            node_list.append(edge.start_node)
            node_list.append(edge.end_node)
        for edge_id in node.out_edge:
            edge = self.edges[edge.id]
            node_list.append(edge.start_node)
            node_list.append(edge.end_node)
        
        node_list = list(set(node_list))
        node_list.remove(node)
        return node_list
        
    def remove_node(self,node_id:str):
        node = self.nodes[node_id]
        if node.id not in self.nodes:
            raise ValueError(f'节点ID{node.id}不存在')
        for edge_id in node.in_edge:
            edge = self.edges[edge_id]
            edge.start_node.out_edge.remove(edge_id)
            del self.edges[edge_id]
        
        for egde_id in node.out_edge:
            edge = self.edges[edge_id]
            edge.end_node.in_edge.remove(edge_id)
            del self.edges[edge_id]
        
        del self.nodes[node_id]
            
    def remove_edge(self,edge_id:str):
        edge = self.edges[edge_id]
        if edge.id not in self.edges:
            raise ValueError(f'节点ID{edge.id}不存在')
        edge.start_node.out_edge.remove(edge_id)
        edge.end_node.in_edge.remove(edge_id)
        del self.edges[edge_id]
        
        
    
            
        
            