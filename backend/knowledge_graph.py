from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from collections import deque
import uuid


class Knowledge_Node(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    title: str = None
    description: Optional[str] = None  # optional的意思是可以没有，有的话变量类型就是str
    content: Optional[Any] = None
    in_edge: List[str] = []
    out_edge: List[str] = []


class Knowledge_Edge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = None
    start_node: Knowledge_Node
    end_node: Knowledge_Node
    description: Optional[str]


class Knowledge_Graph(BaseModel):
    nodes: Dict[str, Knowledge_Node] = {}
    edges: Dict[str, Knowledge_Edge] = {}

    def add_node(self, node: Knowledge_Node):
        if node.id in self.nodes:
            raise ValueError(f"节点ID{node.id}已存在")
        self.nodes[node.id] = node

    def add_edge(self, edge: Knowledge_Edge):
        if edge.start_node.id not in self.nodes:
            raise ValueError(f"节点ID{edge.start_node.id}不存在")
        elif edge.end_node.id not in self.nodes:
            raise ValueError(f"节点ID{edge.end_node.id}不存在")
        if edge.id in self.edges:
            raise ValueError(f"节点ID{edge.id}已存在")

        self.edges[edge.id] = edge
        edge.start_node.out_edge.append(edge.id)
        edge.end_node.in_edge.append(edge.id)

    def get_node(self, node_id: str):
        return self.nodes.get(node_id)

    def get_edge(self, edge_id: str):
        return self.edges.get(edge_id)

    def get_all_node(self):
        node_list = list(self.nodes.values())
        return node_list

    def get_all_edge(self):
        edge_list = list(self.edges.values())
        return edge_list

    def get_out_edge(self, node_id: str):
        if node_id not in self.nodes:
            raise ValueError(f"节点ID{node_id}不存在")
        node = self.nodes[node_id]
        out_edge_list = [self.edges[id] for id in node.out_edge]
        return out_edge_list

    def get_in_edge(self, node_id: str):
        if node_id not in self.nodes:
            raise ValueError(f"节点ID{node_id}不存在")
        node = self.nodes[node_id]
        in_edge_list = [self.edges[id] for id in node.in_edge]
        return in_edge_list

    def get_neighbours(self, node_id: str):
        if node_id not in self.nodes:
            raise ValueError(f"节点ID{node_id}不存在")
        node = self.nodes[node_id]
        node_list = []
        for edge_id in node.in_edge:
            edge = self.edges[edge_id]
            node_list.append(edge.start_node.id)
            node_list.append(edge.end_node.id)
        for edge_id in node.out_edge:
            edge = self.edges[edge_id]
            node_list.append(edge.start_node.id)
            node_list.append(edge.end_node.id)

        node_list = list(set(node_list))
        node_list.remove(node.id)
        new_node_list = [self.nodes[node_id] for node_id in node_list]
        return new_node_list

    def get_out_neighbours(self,node_id:str):
        if node_id not in self.nodes:
            raise ValueError(f"节点ID{node_id}不存在")
        node = self.nodes[node_id]
        node_list = []
        for edge_id in node.out_edge:
            edge = self.edges[edge_id]
            node_list.append(edge.start_node.id)
            node_list.append(edge.end_node.id)

        node_list = list(set(node_list))
        return node_list
    
    def remove_node(self, node_id: str):
        if node_id not in self.nodes:
            raise ValueError(f"节点ID{node_id}不存在")
        node = self.nodes[node_id]
        for edge_id in node.in_edge:
            edge = self.edges[edge_id]
            edge.start_node.out_edge.remove(edge_id)
            del self.edges[edge_id]

        for edge_id in node.out_edge:
            edge = self.edges[edge_id]
            edge.end_node.in_edge.remove(edge_id)
            del self.edges[edge_id]

        del self.nodes[node_id]

    def remove_edge(self, edge_id: str):

        if edge_id not in self.edges:
            raise ValueError(f"节点ID{edge_id}不存在")
        edge = self.edges[edge_id]
        edge.start_node.out_edge.remove(edge_id)
        edge.end_node.in_edge.remove(edge_id)
        del self.edges[edge_id]

    def find_path(self, start_id: str, end_id: str) -> List[str]:
        """使用 BFS 查找两个节点之间的最短路径，返回节点 ID 列表"""
        if start_id not in self.nodes or end_id not in self.nodes:
            raise ValueError("起始或终止节点不存在")

        visited = set()
        queue = deque()
        queue.append([start_id])  # 存储路径

        while queue:
            path = queue.popleft()
            node_id = path[-1]

            if node_id == end_id:
                return path  # 找到路径

            if node_id not in visited:
                visited.add(node_id)
                # 获取当前节点的所有邻居
                neighbors = []
                node = self.nodes[node_id]
                for edge_id in node.out_edge:
                    edge = self.edges[edge_id]
                    neighbors.append(edge.end_node.id)
                for edge_id in node.in_edge:
                    edge = self.edges[edge_id]
                    neighbors.append(edge.start_node.id)

                for neighbor in neighbors:
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)

        return []  # 没有找到路径
    
    def find_path(self,start_node_id,goal_node_id):
        if start_node_id == goal_node_id:
            return [start_node_id]
        
        queue = deque()
        queue.append(start_node_id)
        parent = {start_node_id: None}
        while queue:
            current = queue.popleft()
            
            if current == goal_node_id:
                path = []
                while current is not None: 
                    path.append(current)
                    current = parent[current]
                return path[::-1]
            
            current_list = self.get_out_neighbours(current)
            for neighbour in current_list:
                if neighbour not in parent:
                    parent[neighbour] = current
                    queue.append(neighbour)
            
        return 1
                
    
if __name__ == '__main__':
    user_1 = Knowledge_Node(name="dht", content="a student of hit")
    user_2 = Knowledge_Node(name="ldd", content="a student of sustech")
    user_3 = Knowledge_Node(name="yy", description="he like reading books")

    edge_1 = Knowledge_Edge(
        start_node=user_1, end_node=user_2, description="dht thinks ldd likes loli"
    )
    edge_2 = Knowledge_Edge(
        start_node=user_2,
        end_node=user_3,
        description="ldd thinks yy uses phone too much time",
    )
    edge_3 = Knowledge_Edge(
        start_node=user_3,
        end_node=user_1,
        description="yy and dht both played Honkai Star Rail",
    )


    graph = Knowledge_Graph()
    graph.add_node(user_1)
    graph.add_node(user_2)
    graph.add_node(user_3)
    graph.add_edge(edge_1)
    graph.add_edge(edge_2)
    graph.add_edge(edge_3)
    graph.find_path(user_1.id,user_2.id)