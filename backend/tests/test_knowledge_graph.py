import pytest
from knowledge_graph import Knowledge_Node, Knowledge_Edge, Knowledge_Graph

# Test Knowledge_Node creation
def test_knowledge_node_creation():
    node = Knowledge_Node(name="test_node", title="Test Node", description="A node for testing")
    assert node.name == "test_node"
    assert node.title == "Test Node"
    assert node.description == "A node for testing"
    assert isinstance(node.id, str)
    assert len(node.id) == 8
    assert node.in_edge == []
    assert node.out_edge == []

def test_knowledge_node_with_content():
    node = Knowledge_Node(name="content_node", content={"key": "value"})
    assert node.name == "content_node"
    assert node.content == {"key": "value"}

# Test Knowledge_Edge creation
def test_knowledge_edge_creation():
    node1 = Knowledge_Node(name="node1")
    node2 = Knowledge_Node(name="node2")
    edge = Knowledge_Edge(start_node=node1, end_node=node2, title="relates_to", description="Node1 relates to Node2")
    assert edge.start_node == node1
    assert edge.end_node == node2
    assert edge.title == "relates_to"
    assert edge.description == "Node1 relates to Node2"
    assert isinstance(edge.id, str)
    assert len(edge.id) == 8

# Test Knowledge_Graph
@pytest.fixture
def setup_graph():
    graph = Knowledge_Graph()
    node_a = Knowledge_Node(name="A", id="nodeA")
    node_b = Knowledge_Node(name="B", id="nodeB")
    node_c = Knowledge_Node(name="C", id="nodeC")
    node_d = Knowledge_Node(name="D", id="nodeD")

    graph.add_node(node_a)
    graph.add_node(node_b)
    graph.add_node(node_c)
    graph.add_node(node_d)

    edge_ab = Knowledge_Edge(start_node=node_a, end_node=node_b, id="edgeAB", description=None)
    edge_bc = Knowledge_Edge(start_node=node_b, end_node=node_c, id="edgeBC", description=None)
    edge_ac = Knowledge_Edge(start_node=node_a, end_node=node_c, id="edgeAC", description=None)
    edge_cd = Knowledge_Edge(start_node=node_c, end_node=node_d, id="edgeCD", description=None)

    graph.add_edge(edge_ab)
    graph.add_edge(edge_bc)
    graph.add_edge(edge_ac)
    graph.add_edge(edge_cd)

    return graph, node_a, node_b, node_c, node_d, edge_ab, edge_bc, edge_ac, edge_cd

def test_add_node(setup_graph):
    graph, _, _, _, _, _, _, _, _ = setup_graph
    new_node = Knowledge_Node(name="E", id="nodeE")
    graph.add_node(new_node)
    assert graph.get_node("nodeE") == new_node
    assert len(graph.nodes) == 5

def test_add_existing_node_raises_error(setup_graph):
    graph, node_a, _, _, _, _, _, _, _ = setup_graph
    with pytest.raises(ValueError, match="节点 ID nodeA 已存在"):
        graph.add_node(node_a)

def test_add_edge(setup_graph):
    graph, node_a, node_b, _, _, _, _, _, _ = setup_graph
    node_e = Knowledge_Node(name="E", id="nodeE_new")
    node_f = Knowledge_Node(name="F", id="nodeF_new")
    graph.add_node(node_e)
    graph.add_node(node_f)
    new_edge = Knowledge_Edge(start_node=node_e, end_node=node_f, id="edgeEF", description=None)
    graph.add_edge(new_edge)
    assert graph.get_edge("edgeEF") == new_edge
    assert "edgeEF" in node_e.out_edge
    assert "edgeEF" in node_f.in_edge
    assert len(graph.edges) == 5

def test_add_edge_with_nonexistent_start_node_raises_error(setup_graph):
    graph, _, node_b, _, _, _, _, _, _ = setup_graph
    non_existent_node = Knowledge_Node(name="NonExistent", id="nonExistent")
    edge = Knowledge_Edge(start_node=non_existent_node, end_node=node_b, id="edgeNEB", description=None)
    with pytest.raises(ValueError, match=f"节点 ID {non_existent_node.id} 不存在"):
        graph.add_edge(edge)

def test_add_edge_with_nonexistent_end_node_raises_error(setup_graph):
    graph, node_a, _, _, _, _, _, _, _ = setup_graph
    non_existent_node = Knowledge_Node(name="NonExistent", id="nonExistent")
    edge = Knowledge_Edge(start_node=node_a, end_node=non_existent_node, id="edgeANE", description=None)
    with pytest.raises(ValueError, match=f"节点 ID {non_existent_node.id} 不存在"):
        graph.add_edge(edge)

def test_add_existing_edge_raises_error(setup_graph):
    graph, _, _, _, _, _, _, edge_ac, _ = setup_graph
    with pytest.raises(ValueError, match="节点 ID edgeAC 已存在"):
        graph.add_edge(edge_ac)

def test_get_node(setup_graph):
    graph, node_a, _, _, _, _, _, _, _ = setup_graph
    assert graph.get_node("nodeA") == node_a
    assert graph.get_node("nonExistent") is None

def test_get_edge(setup_graph):
    graph, _, _, _, _, _, _, edge_ac, _ = setup_graph
    assert graph.get_edge("edgeAC") == edge_ac
    assert graph.get_edge("nonExistent") is None

def test_get_all_node(setup_graph):
    graph, node_a, node_b, node_c, node_d, _, _, _, _ = setup_graph
    all_nodes = graph.get_all_node()
    expected_nodes = [node_a, node_b, node_c, node_d]
    assert len(all_nodes) == len(expected_nodes)
    assert all(node in all_nodes for node in expected_nodes)

def test_get_all_edge(setup_graph):
    graph, _, _, _, _, edge_ab, edge_bc, edge_ac, edge_cd = setup_graph
    all_edges = graph.get_all_edge()
    expected_edges = [edge_ab, edge_bc, edge_ac, edge_cd]
    assert len(all_edges) == len(expected_edges)
    assert all(edge in all_edges for edge in expected_edges)

def test_get_out_edge(setup_graph):
    graph, node_a, _, _, _, edge_ab, _, edge_ac, _ = setup_graph
    out_edges_a = graph.get_out_edge("nodeA")
    assert len(out_edges_a) == 2
    assert edge_ab in out_edges_a
    assert edge_ac in out_edges_a

def test_get_out_edge_nonexistent_node_raises_error(setup_graph):
    graph, _, _, _, _, _, _, _, _ = setup_graph
    with pytest.raises(ValueError, match="节点 ID nonExistent 不存在"):
        graph.get_out_edge("nonExistent")

def test_get_in_edge(setup_graph):
    graph, _, _, node_c, _, _, edge_bc, edge_ac, _ = setup_graph
    in_edges_c = graph.get_in_edge("nodeC")
    assert len(in_edges_c) == 2
    assert edge_bc in in_edges_c
    assert edge_ac in in_edges_c

def test_get_in_edge_nonexistent_node_raises_error(setup_graph):
    graph, _, _, _, _, _, _, _, _ = setup_graph
    with pytest.raises(ValueError, match="节点 ID nonExistent 不存在"):
        graph.get_in_edge("nonExistent")

def test_get_neighbours(setup_graph):
    graph, node_a, node_b, node_c, _, _, _, _, _ = setup_graph
    neighbours_a = graph.get_neighbours("nodeA")
    assert len(neighbours_a) == 2
    assert node_b in neighbours_a
    assert node_c in neighbours_a

    neighbours_b = graph.get_neighbours("nodeB")
    assert len(neighbours_b) == 2
    assert node_a in neighbours_b
    assert node_c in neighbours_b

def test_get_neighbours_nonexistent_node_raises_error(setup_graph):
    graph, _, _, _, _, _, _, _, _ = setup_graph
    with pytest.raises(ValueError, match="节点 ID nonExistent 不存在"):
        graph.get_neighbours("nonExistent")

def test_remove_node(setup_graph):
    graph, node_a, node_b, node_c, _, edge_ab, edge_bc, edge_ac, _ = setup_graph
    graph.remove_node("nodeB")
    assert graph.get_node("nodeB") is None
    assert "edgeAB" not in graph.edges # edge_ab should be removed
    assert "edgeBC" not in graph.edges # edge_bc should be removed
    assert "edgeAB" not in node_a.out_edge
    assert "edgeBC" not in node_c.in_edge
    assert len(graph.nodes) == 3
    assert len(graph.edges) == 2 # edge_ac and edge_cd remain

def test_remove_node_nonexistent_node_raises_error(setup_graph):
    graph, _, _, _, _, _, _, _, _ = setup_graph
    with pytest.raises(ValueError, match="节点 ID nonExistent 不存在"):
        graph.remove_node("nonExistent")

def test_remove_edge(setup_graph):
    graph, node_a, node_b, _, _, edge_ab, _, _, _ = setup_graph
    graph.remove_edge("edgeAB")
    assert graph.get_edge("edgeAB") is None
    assert "edgeAB" not in node_a.out_edge
    assert "edgeAB" not in node_b.in_edge
    assert len(graph.edges) == 3

def test_remove_edge_nonexistent_edge_raises_error(setup_graph):
    graph, _, _, _, _, _, _, _, _ = setup_graph
    with pytest.raises(ValueError, match="节点 ID nonExistentEdge 不存在"):
        graph.remove_edge("nonExistentEdge")


def test_find_path_direct_connection():
    """测试直接相连的两个节点"""
    # 创建节点和边
    node1 = Knowledge_Node(name="node1")
    node2 = Knowledge_Node(name="node2")
    edge = Knowledge_Edge(start_node=node1, end_node=node2)
    
    # 构建图
    graph = Knowledge_Graph()
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_edge(edge)
    
    # 测试路径查找
    path = graph.find_path(node1.id, node2.id)
    assert path == [node1.id, node2.id]

def test_find_path_indirect_connection():
    """测试间接相连的两个节点"""
    # 创建节点和边
    node1 = Knowledge_Node(name="node1")
    node2 = Knowledge_Node(name="node2")
    node3 = Knowledge_Node(name="node3")
    edge1 = Knowledge_Edge(start_node=node1, end_node=node2)
    edge2 = Knowledge_Edge(start_node=node2, end_node=node3)
    
    # 构建图
    graph = Knowledge_Graph()
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_edge(edge1)
    graph.add_edge(edge2)
    
    # 测试路径查找
    path = graph.find_path(node1.id, node3.id)
    assert path == [node1.id, node2.id, node3.id]

def test_find_path_no_connection():
    """测试没有路径相连的两个节点"""
    # 创建节点
    node1 = Knowledge_Node(name="node1")
    node2 = Knowledge_Node(name="node2")
    node3 = Knowledge_Node(name="node3")
    node4 = Knowledge_Node(name="node4")
    edge1 = Knowledge_Edge(start_node=node1, end_node=node2)
    edge2 = Knowledge_Edge(start_node=node3, end_node=node4)
    
    # 构建图
    graph = Knowledge_Graph()
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_node(node4)
    graph.add_edge(edge1)
    graph.add_edge(edge2)
    
    # 测试路径查找
    path = graph.find_path(node1.id, node4.id)
    assert path == []

def test_find_path_same_node():
    """测试起点和终点是同一个节点"""
    node1 = Knowledge_Node(name="node1")
    
    graph = Knowledge_Graph()
    graph.add_node(node1)
    
    path = graph.find_path(node1.id, node1.id)
    assert path == [node1.id]

def test_find_path_with_cycle():
    """测试图中存在环的情况"""
    # 创建节点和边
    node1 = Knowledge_Node(name="node1")
    node2 = Knowledge_Node(name="node2")
    node3 = Knowledge_Node(name="node3")
    edge1 = Knowledge_Edge(start_node=node1, end_node=node2)
    edge2 = Knowledge_Edge(start_node=node2, end_node=node3)
    edge3 = Knowledge_Edge(start_node=node3, end_node=node1)
    
    # 构建图
    graph = Knowledge_Graph()
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_edge(edge1)
    graph.add_edge(edge2)
    graph.add_edge(edge3)
    
    # 测试路径查找
    path = graph.find_path(node1.id, node3.id)
    assert path == [node1.id, node2.id, node3.id]

def test_find_path_multiple_paths():
    """测试存在多条路径时返回最短路径"""
    # 创建节点和边
    node1 = Knowledge_Node(name="node1")
    node2 = Knowledge_Node(name="node2")
    node3 = Knowledge_Node(name="node3")
    node4 = Knowledge_Node(name="node4")
    edge1 = Knowledge_Edge(start_node=node1, end_node=node2)
    edge2 = Knowledge_Edge(start_node=node2, end_node=node4)
    edge3 = Knowledge_Edge(start_node=node1, end_node=node3)
    edge4 = Knowledge_Edge(start_node=node3, end_node=node4)
    
    # 构建图
    graph = Knowledge_Graph()
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_node(node4)
    graph.add_edge(edge1)
    graph.add_edge(edge2)
    graph.add_edge(edge3)
    graph.add_edge(edge4)
    
    # 测试路径查找 - 应该返回较短的路径
    path = graph.find_path(node1.id, node4.id)
    assert len(path) == 3  # 两条路径长度相同，返回哪条都可以

def test_find_path_nonexistent_nodes():
    """测试节点不存在的情况"""
    graph = Knowledge_Graph()
    with pytest.raises(ValueError):
        graph.find_path("nonexistent1", "nonexistent2")
    
    node1 = Knowledge_Node(name="node1")
    graph.add_node(node1)
    with pytest.raises(ValueError):
        graph.find_path(node1.id, "nonexistent")
    with pytest.raises(ValueError):
        graph.find_path("nonexistent", node1.id)