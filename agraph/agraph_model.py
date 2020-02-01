from typing import Dict

class AGraphModel:
    nodes: Dict[str, object] = {}

    def register_node(self, id: str, node: object) -> None:
        self.nodes[id] = node
