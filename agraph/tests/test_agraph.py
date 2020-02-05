import unittest

from agraph.agraph import AGraph


class NodeType:
    def __init__(self, value = None):
        self.value = value
    def set_related(self, related):
        self.related = related

class TestAGraph(unittest.TestCase):
    def test_should_be_able_to_register_node(self):
        agraph = AGraph()
        agraph.register_node('node_id', 'test')
        agraph.set_representation(r'node_id-node_id')
        model = agraph.build()

        self.assertTrue('test' in model[0])

    def test_should_be_able_to_register_node_builder(self):
        agraph = AGraph()
        agraph.register_node_builder(NodeType, lambda: NodeType('test'))
        agraph.set_representation(r'NodeType-NodeType')
        model = agraph.build()

        self.assertTrue(model[0][0].value == 'test')

    def test_should_be_able_to_register_relation_builder(self):
        agraph = AGraph()
        agraph.register_relation_builder(NodeType, NodeType, lambda nt1, nt2: (nt1.set_related(nt2), nt2.set_related(nt1)))
        agraph.set_representation(r'NodeType-NodeType')
        model = agraph.build()

        self.assertTrue(model[0][0].related is model[0][1])
