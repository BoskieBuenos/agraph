import unittest
from functools import reduce

from agraph.compiler import AGraphCompiler
from agraph.model import AGraphModel


# TODO Allow custom relation builders (TDD ofc)
# TODO Definiowanie "mnożonych" relacji (może między typami a nie instancjami)


class TestBasicRepresentations(unittest.TestCase):
    def setUp(self):
        self.agraph_model = AGraphModel()
        self.agraph_model.register_node('N0', 'node0')
        self.agraph_model.register_node('N1', 'node1')
        self.agraph_compiler = AGraphCompiler(self.agraph_model)

    def tearDown(self):
        self.agraph_compiler.set_representation(self.agraph_representation)
        self.graph = self.agraph_compiler.compile()

        self.assertEqual(len(self.graph), 1)
        self.assertTrue('node0' in self.graph[0])
        self.assertTrue('node1' in self.graph[0])
        self.graph = None

    def test_vertical(self):
        self.agraph_representation = r'''
            N0
            |
            N1
        '''

    def test_horizontal(self):
        self.agraph_representation = r'N0-N1'

    def test_backslash(self):
        self.agraph_representation = r'''
            N0
              \
               N1
        '''

    def test_forwardslash(self):
        self.agraph_representation = r'''
               N0
              /
            N1
        '''

    def test_multisegment_vertical(self):
        self.agraph_representation = r'''
            N0
            |
            |
            N1
        '''

    def test_multisegment_horizontal(self):
        self.agraph_representation = r'N0--N1'

    def test_multisegment_backslash(self):
        self.agraph_representation = r'''
            N0
              \
               \
                N1
        '''

    def test_multisegment_forwardslash(self):
        self.agraph_representation = r'''
                N0
               /
              /
            N1
        '''

class TestAsteriskConnector(TestBasicRepresentations):
    def test_asterisk_vertical(self):
        self.agraph_representation = r'''
            N0
            |
            *
            |
            N1
        '''

    def test_asterisk_horizontal(self):
        self.agraph_representation = r'N0-*-N1'

    def test_asterisk_backslash(self):
        self.agraph_representation = r'''
            N0
              \
               *
                \
                 N1
        '''

    def test_asterisk_forwardslash(self):
        self.agraph_representation = r'''
                 N0
                /
               *
              /
            N1
        '''

    def test_asterisk_combination_1(self):
        self.agraph_representation = r'''
        N0-*
           |
           N1
        '''

    def test_asterisk_combination_2(self):
        self.agraph_representation = r'''
           *
          /|
        N0 N1
        '''

    def test_asterisk_combination_3(self):
        self.agraph_representation = r'''
           *
          / \
        N0   N1
        '''

    def test_asterisk_combination_4(self):
        self.agraph_representation = r'''
        N0
          \ 
           *-N1
        '''

    def test_multiple_asterisk_1(self):
        self.agraph_representation = r'''
        N0     N1
          \   /
           *-*
        '''

    def test_multiple_asterisk_2(self):
        self.agraph_representation = r'''
        N0-*N1---*
            \    |
             *---*
        '''

class TestComplexRepresentations(unittest.TestCase):
    def setUp(self):
        self.tested_nodes = 1
        self.tested_edges = 1
        self.assert_pairs = []

    def tearDown(self):
        self.agraph_model = AGraphModel()
        self.agraph_compiler = AGraphCompiler(self.agraph_model)
        self.agraph_compiler.set_representation(self.agraph_representation)
        self.__register_nodes_from_representation()
        self.graph = self.agraph_compiler.compile()
        self.assertEqual(len(self.graph), self.tested_edges)
        self.__assert_nodes_on_graph()
        self.__assert_explicit_edges()

    def __assert_nodes_on_graph(self) -> None:
        connected_nodes = [node for edge in self.graph for node in edge]
        for index in range(0, self.tested_nodes):
            self.assertTrue(f'node{index}' in connected_nodes, msg=f'node{index} should be in any pair of {self.graph}')

    def __assert_explicit_edges(self) -> None:
        for nodes_pair in list(map(lambda ids_pair: (ids_pair[0].replace('N', 'node'), ids_pair[1].replace('N', 'node')), self.assert_pairs)):
            self.assertTrue(
                reduce(lambda result, edge: result or (nodes_pair[0] in edge and nodes_pair[1] in edge), self.graph, False),
                msg=f'pair {nodes_pair} should be in {self.graph}'
            )

    def __register_nodes_from_representation(self) -> None:
        for index in range(0, self.tested_nodes):
            self.agraph_model.register_node(f'N{index}', f'node{index}')

    def register_nodes_in_representation(self, count: int) -> None:
        self.tested_nodes = count

    def register_edges_in_representation(self, count: int, *pairs: tuple) -> None:
        self.tested_edges = count
        self.assert_pairs = pairs

    def test_circular_should_connect_itself(self):
        self.agraph_representation = r'''
              N0
             /  \
            *----* 
        '''

    def test_multiple_occurances_of_node(self):
        self.agraph_representation = r'''
            N0-N1-N2-N0
        '''
        self.register_nodes_in_representation(3)
        self.register_edges_in_representation(3)

    def test_tight_edges(self):
        self.agraph_representation = r'''
             N0
            /N1\
           N2| N3
          N4-*
        '''
        self.register_nodes_in_representation(5)
        self.register_edges_in_representation(3)

    def test_asterisk_should_detect_only_edges_connected_to_it_1(self):
        self.agraph_representation = r'''
         N2-*N1
            ||
           N0*-N3 
        '''
        self.register_nodes_in_representation(4)
        self.register_edges_in_representation(2, ('N0', 'N2'), ('N1', 'N3'))

    def test_asterisk_should_detect_only_edges_connected_to_it_2(self):
        self.agraph_representation = r'''
          N3
            \
         N2-*N1
             \
             N0
        '''
        self.register_nodes_in_representation(4)
        self.register_edges_in_representation(2, ('N0', 'N2'), ('N1', 'N3'))

    def test_multiple_graphs(self):
        self.agraph_representation = r'''
          N0
            \ N1--N2    N9
             N3--N4 \  /
            /  \ N5--N6--N10
          N7    N8  /  \
                   N11 N12
        '''
        self.register_nodes_in_representation(13)
        self.register_edges_in_representation(11,
            ('N0', 'N3'), ('N4', 'N3'), ('N7', 'N3'), ('N8', 'N3'),
            ('N1', 'N2'), ('N2', 'N6'), ('N5', 'N6'), ('N9', 'N6'), ('N10', 'N6'), ('N11', 'N6'), ('N12', 'N6')
        )

    def test_hexagram(self):
        self.agraph_representation = r'''
          N0----N1
         /|    /||\
        N7**--* |*N2
        |//     | \\
        N6      |  N3
         \      | /
          N5----N4
        '''
        self.register_nodes_in_representation(8)
        self.register_edges_in_representation(12, ('N0', 'N6'), ('N1', 'N3'), ('N1', 'N4'), ('N1', 'N6'))

class TestBrokenGraphs():
    def setUp(self):
        self.agraph_model = AGraphModel()
        self.agraph_model.register_node('N0', 'node0')
        self.agraph_model.register_node('N1', 'node1')
        self.agraph_compiler = AGraphCompiler(self.agraph_model)

    # TODO ZBĘDNE DO MVP

    def tearDown(self):
        self.agraph_compiler.set_representation(self.agraph_representation)
        self.graph = self.agraph_compiler.compile()


    def test_unattached_edge(self):
        self.agraph_representation = r'''
        N0-N1-
        '''
        # should raise exception or ignore bad edge
        pass

    def test_crossing_edge(self):
        self.agraph_representation = r'''
           N2
           |
        N0---N1
           |
           N3
        '''
        # should raise exception or ignore bad edge
        pass
