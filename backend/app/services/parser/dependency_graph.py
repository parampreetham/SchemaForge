"""Dependency analysis and topological sorting."""

import re
import networkx as nx

from app.services.parser.classifier import ObjectClassifier
from app.services.parser.ast_generator import ASTGenerator

# Regex fallback for foreign keys and simple procedure calls
REFERENCES_PATTERN = re.compile(r"REFERENCES\s+([A-Z0-9_]+\.)?([A-Z0-9_]+)", re.IGNORECASE)

class DependencyGraph:
    """Builds a dependency graph and determines conversion order."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self._chunks = {}  # chunk_id -> dict
        self._name_to_chunk_id = {}  # object_name -> chunk_id

    def add_chunk(self, chunk_id: str, sql_chunk: str):
        """Add a SQL chunk to the graph structure."""
        metadata = ObjectClassifier.classify(sql_chunk)
        obj_name = metadata["object_name"]
        
        self._chunks[chunk_id] = {
            "chunk_id": chunk_id,
            "sql": sql_chunk,
            "metadata": metadata,
            "dependencies": self._extract_dependencies(sql_chunk)
        }
        
        # We only map CREATE statements for dependency targets, 
        # or just map the first thing that defines this object.
        if obj_name and metadata["object_type"] and not metadata["object_type"].startswith("ALTER"):
            self._name_to_chunk_id[obj_name] = chunk_id

    def _extract_dependencies(self, sql_chunk: str) -> set[str]:
        """Extract referenced objects from a SQL chunk."""
        deps = set()
        
        # Fast fallback: simple regex for FKs
        for match in REFERENCES_PATTERN.finditer(sql_chunk):
            deps.add(match.group(2))
            
        ast = ASTGenerator.generate(sql_chunk)
        if ast:
            from sqlglot.expressions import Table
            for table in ast.find_all(Table):
                if table.name:
                    deps.add(table.name)
                    
        return deps

    def get_ordered_chunks(self) -> list[dict]:
        """Build graph, sort it topologically and return ordered chunks."""
        # Pass 2: Build graph
        for chunk_id, data in self._chunks.items():
            self.graph.add_node(chunk_id, **data)
            
            for dep_name in data["dependencies"]:
                # If we know the chunk that creates this dependency, add an edge
                dep_chunk_id = self._name_to_chunk_id.get(dep_name)
                # But don't make a chunk depend on itself
                if dep_chunk_id and dep_chunk_id != chunk_id:
                    self.graph.add_edge(dep_chunk_id, chunk_id)
        
        # Sort
        try:
            ordered_nodes = list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            ordered_nodes = list(self.graph.nodes())

        result = []
        for order_idx, node_id in enumerate(ordered_nodes):
            node_data = self.graph.nodes[node_id]
            preds = list(self.graph.predecessors(node_id))
            
            result.append({
                "chunk_id": node_id,
                "object_name": node_data["metadata"]["object_name"],
                "metadata": node_data["metadata"],
                "dependencies": preds,
                "dependency_order": order_idx
            })
            
        return result
