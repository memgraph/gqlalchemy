from transporter import Transporter

class GraphTransporter(Transporter):

    def __init__(self, graph_type: str) -> None:
        """Initializes GraphTransporter. It is used for converting Memgraph graph to the specific graph type offered by some Python package (PyG, DGL, NX...)
        """
        super().__init__()
        self.graph_type = graph_type


    def export(query_results):
        # TODO
        return super().export()

