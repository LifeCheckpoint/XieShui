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
        if self.verify_node(node) == -1:
            print('Valueerror')
            exit(0)
        else:
            out_edge_list = [self.nodes[id] for id in node.out_edge]
            return out_edge_list
    
    def get_in_node(self,node_id:str):
        node = self.nodes[node_id]
        if self.verify_node(self,node) == -1:
            print("ValueError")
            exit(0)
        else:
            in_edge_list = [self.nodes[id] for id in node.in_edge]
            return in_edge_list
    
    def get_neighbours(self,node_id:str):
        node = self.nodes[node_id]
        if self.verify_node(self,node) == -1:
            print("ValueError")
            exit(0)
        else:
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
        if self.verify_node(self,node) == -1:
            print("ValueError")
            exit(0)
        else:
            for edge_id in node.in_edge:
                edge = self.edges[edge_id]
                edge.start_node.out_edge.remove(edge_id)
                del self.edges[edge_id]
            
            for egde_id in node.out_edge:
                edge = self.edges[edge_id]
                edge.end_node.in_edge.remove(edge_id)
                del self.edges[edge_id]
            
            del self.nodes[node_id]
                
                
        
        
    
            
        
            