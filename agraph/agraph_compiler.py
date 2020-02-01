import sys, inspect

from itertools import product
from functools import reduce
from typing import List, Callable, Set

from agraph.agraph_model import AGraphModel
from agraph.edge import Edge, EdgeFactory
from agraph.point import Point


class AGraphCompiler:
    relation_builders = {}

    def __init__(self, model: AGraphModel = None): # TODO None should not be optional? - Jeśli da się bez modelu to nie powinien być obowiązkowy
        self.model = model or AGraphModel()
        self.__build_class_registry()

    def set_representation(self, representation: str) -> None:
        self.representation = representation

    def register_relation_builder(self, type1, type2, build_relation: Callable) -> None:
        # Czy da się odczytać z funkcji typy jej argumentów i typ zwracany
        # Maybe hash*hash
        # Co jak builder już zdefiniowany?
        if type1 not in self.relation_builders:
            self.relation_builders[type1] = {}
        self.relation_builders[type1][type2] = build_relation
        # if type2 not in self.relation_builders:
        #     self.relation_builders[type2] = {}
        # self.relation_builders[type2][type1] = build_relation

    def compile(self) -> List:
        lines = self.__split_representation_lines(self.representation)
        # Make matrix of nodes
        matrix = []
        matrix_max_x = max(list(map(lambda line: len(line), lines)))
        matrix_max_y = len(lines)
        for line in lines:
            node_ids = self.__separate_identifiers(line)
            matrix_row = [None] * matrix_max_x # [None, None, None, None, None, None]
            # 'N1 N12' => ['N1', 'N1', None, 'N12', 'N12', 'N12']
            # Mark nodes on matrix
            after_end_index = 0
            for node_id in node_ids:
                start_index = line.index(node_id, after_end_index)
                after_end_index = start_index + len(node_id)
                for occupied_position in range(start_index, after_end_index):
                    matrix_row[occupied_position] = node_id

            # Mark edges on matrix
            for col in range(0, len(line)):
                edge = EdgeFactory.make_edge(line[col])
                if edge is not None:
                    matrix_row[col] = edge

            matrix.append(matrix_row)

        # Matrix is constructed
        edges = []

        # Iterate over the matrix - resolve edge if found and erase it from matrix
        for column_index, row_index in product(range(matrix_max_x), range(matrix_max_y)):
            try:
                if isinstance(matrix[row_index][column_index], Edge):
                    edges.append(self.resolve_edge(matrix, row_index, column_index))
            except IndexError:
                continue

        return edges

    def resolve_edge(self, matrix: List[List[str]], edge_row_index: int, edge_column_index: int) -> List[str]:
        nodes: List[str] = [None, None]
        # get connected matrix cells coordinates (each eadge character should have its own resolver)
        # cords - coordinates
        edge = matrix[edge_row_index][edge_column_index]
        connected_cells_cords: List[Point] = edge.connected_cells(matrix, edge_row_index, edge_column_index)
        c: List[Point] = connected_cells_cords
        # remove edge from matrix
        matrix[edge_row_index][edge_column_index] = None

        for i in range(2):
            connected_cell = c[i]
            while isinstance(matrix[connected_cell.row][connected_cell.col], Edge):
                edge = matrix[connected_cell.row][connected_cell.col]
                edge_connected_cells: List[Point] = edge.connected_cells(matrix, connected_cell.row, connected_cell.col)
                e: List[Point] = edge_connected_cells
                if matrix[e[0].row][e[0].col] is not None:
                    connected_cell_cords = e[0]
                else:
                    connected_cell_cords = e[1]
                # remove edge from matrix
                matrix[connected_cell.row][connected_cell.col] = None
                connected_cell = connected_cell_cords
            nodes[i] = self.__get_node(id=matrix[connected_cell.row][connected_cell.col])

        self.__build_relation(nodes[0], nodes[1])
        return nodes # list of connected nodes

    def __build_class_registry(self) -> None:
        # zamodelować class_registry zgodnie z potrzebą
        # self.__class_registry = []
        self.__class_registry = {}
        for module_id in list(sys.modules):
            try:
                module = sys.modules[module_id]
                if inspect.ismodule(module):
                    members = inspect.getmembers(module, inspect.isclass) # [(member_name, member_value), (member_name, member_value), ...]
                    for member in members:
                        self.__class_registry[member[0]] = member[1]
            except ModuleNotFoundError:
                continue

    def __get_node(self, id: str) -> object:
        # Try from registered
        if id in self.model.nodes:
            return self.model.nodes[id]
        # Try to new object with id -> Próbuje dopasować początek do typu (odcinając po kolei ostatanie znaki?)
        # Może oczekiwać separatora '_' między typem a id ? - zwiększy długość
        type_candidates = sorted(filter(lambda type: id.startswith(type), list(self.__class_registry)), key=len)
        if type_candidates is not None and len(type_candidates) > 0:
            top_priority_candidate = type_candidates.pop()
            ambigious_candidates = list(filter(lambda candidate: len(candidate) == len(top_priority_candidate), type_candidates))
            if not bool(ambigious_candidates):
                if len(top_priority_candidate) < len(id):
                    id_candidate = id[len(top_priority_candidate):]
                    return self.__class_registry[top_priority_candidate](id=id_candidate) # what about id type str/int?
                else:
                    return self.__class_registry[top_priority_candidate]()
        # Try to new object
        # if id in self.__class_registry:
        #     return self.__class_registry[id]() # Co jak wymagane są argumenty?
        # TODO rzuć wyjątek, że nie udało się dopasować typu i obiektu LUB zwrócić None (wtedy nie wiadomo, że coś się nie udało)

    def __build_relation(self, node1, node2) -> None:
        node1_type = type(node1)
        node2_type = type(node2)
        if node1_type in self.relation_builders and node2_type in self.relation_builders[node1_type]:
            self.relation_builders[node1_type][node2_type](node1, node2)
        elif node2_type in self.relation_builders and node1_type in self.relation_builders[node2_type]:
            self.relation_builders[node2_type][node1_type](node2, node1)

    def __split_representation_lines(self, representation: str) -> List[List]:
        lines = representation.splitlines()
        if len(lines[0]) is 0 or lines[0].isspace():
            del lines[0]
        if len(lines[-1]) is 0 or lines[-1].isspace():
            del lines[-1]
        return lines

    def __separate_identifiers(self, line: str) -> List[str]:
        line_copy = []
        for character in line:
            if EdgeFactory.make_edge(character) is not None:
                character = ' '
            line_copy.append(character)
        return ''.join(line_copy).split() # ['N1', 'N12'] - with repeats, keeping order
