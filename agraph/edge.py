from itertools import product
from typing import Callable, List, Set

from agraph.point import Point


class Edge:
    def __init__(self):
        pass
    @staticmethod
    def applicable(character: str):
        return False
    def connected_cells(self, matrix, edge_row_index, edge_column_index) -> List[Point]:
        pass
    def connects(self, edge_row: int, edge_col: int, target_row: int, target_col) -> bool:
        pass

class VerticalEdge(Edge):
    @staticmethod
    def applicable(character: str):
        return character == r'|'
    def connected_cells(self, matrix, edge_row_index, edge_column_index) -> List[Point]:
        return [
            Point(row=edge_row_index-1, col=edge_column_index),
            Point(row=edge_row_index+1, col=edge_column_index)]
    def connects(self, edge_row: int, edge_col: int, target_row: int, target_col) -> bool:
        return edge_col is target_col and abs(target_row - edge_row) is 1

class HorizontalEdge(Edge):
    @staticmethod
    def applicable(character: str):
        return character == r'-'
    def connected_cells(self, matrix, edge_row_index, edge_column_index) -> List[Point]:
        return [
            Point(row=edge_row_index, col=edge_column_index-1),
            Point(row=edge_row_index, col=edge_column_index+1)]
    def connects(self, edge_row: int, edge_col: int, target_row: int, target_col) -> bool:
        return edge_row is target_row and abs(target_col - edge_col) is 1

class BackslashEdge(Edge):
    @staticmethod
    def applicable(character: str):
        return character == '\\'
    def connected_cells(self, matrix, edge_row_index, edge_column_index) -> List[Point]:
        return [
            Point(row=edge_row_index-1, col=edge_column_index-1),
            Point(row=edge_row_index+1, col=edge_column_index+1)]
    def connects(self, edge_row: int, edge_col: int, target_row: int, target_col) -> bool:
        return (target_row - edge_row) * (target_col - edge_col) is 1

class ForwardslashEdge(Edge):
    @staticmethod
    def applicable(character: str):
        return character == r'/'
    def connected_cells(self, matrix, edge_row_index, edge_column_index) -> List[Point]:
        return [
            Point(row=edge_row_index-1, col=edge_column_index+1),
            Point(row=edge_row_index+1, col=edge_column_index-1)]
    def connects(self, edge_row: int, edge_col: int, target_row: int, target_col) -> bool:
        return (target_row - edge_row) * (target_col - edge_col) is -1

class AsteriskConnector(Edge):
    @staticmethod
    def applicable(character: str):
        return character == r'*'
    def connected_cells(self, matrix, edge_row_index, edge_column_index) -> List[Point]:
        return self.__neighbour_edges_cords(matrix, edge_row_index, edge_column_index)
    def __neighbour_edges_cords(self, matrix: List[List[str]], center_row_index: int, center_column_index: int) -> List[Point]:
        points: List[Point] = []
        for row, col in product(range(max(center_row_index-1, 0), center_row_index+2), range(max(center_column_index-1, 0), center_column_index+2)):
            if row is center_row_index and col is center_column_index:
                continue
            try:
                if isinstance(matrix[row][col], Edge) and matrix[row][col].connects(row, col, center_row_index, center_column_index):
                    points.append(Point(row=row, col=col))
            except IndexError:
                continue
        return points
    def connects(self, edge_row: int, edge_col: int, target_row: int, target_col) -> bool:
        return False

class EdgeFactory:
    AVAILABLE_EDGES: Set[Edge] = set([VerticalEdge, HorizontalEdge, BackslashEdge, ForwardslashEdge, AsteriskConnector])
    @staticmethod
    def make_edge(edge_character: str):
        try:
            return next(filter(lambda edge: edge.applicable(edge_character), EdgeFactory.AVAILABLE_EDGES))()
        except Exception:
            return None
