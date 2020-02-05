from typing import Callable, List


from agraph.compiler import AGraphCompiler
from agraph.model import AGraphModel


class AGraph:
    def __init__(self):
        self.model: AGraphModel = AGraphModel()
        self.compiler: AGraphCompiler = AGraphCompiler(self.model)

    def register_node(self, id: str, node: object) -> None:
        self.model.register_node(id, node)

    def set_representation(self, representation: str) -> None:
        self.compiler.set_representation(representation)

    def register_node_builder(self, type, build_node: Callable) -> None:
        self.compiler.register_node_builder(type, build_node)

    def register_relation_builder(self, type1, type2, build_relation: Callable) -> None:
        self.compiler.register_relation_builder(type1, type2, build_relation)

    def build(self) -> List[List]:
        return self.compiler.compile()
