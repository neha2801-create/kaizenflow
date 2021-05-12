import IPython
import networkx as networ
import pygraphviz

import core.dataflow as dtf
import helpers.dbg as dbg
import helpers.io_ as hio


def draw(dag: dtf.DAG) -> IPython.core.display.Image:
    """
    Render NetworkX graph in a notebook.
    """
    agraph = _extract_agraph_from_dag(dag)
    image = IPython.display.Image(agraph.draw(format="png", prog="dot"))
    return image


def to_file(dag: dtf.DAG, file_name: str = "graph.png") -> str:
    """
    Save NetworkX graph to a file.
    """
    agraph = _extract_agraph_from_dag(dag)
    # Save to file.
    hio.create_enclosing_dir(file_name)
    agraph.draw(file_name, prog="dot")
    return file_name


def _extract_agraph_from_dag(dag: dtf.DAG) -> pygraphviz.agraph.AGraph:
    """
    Extract a pygraphviz `agraph` from a DAG.
    """
    dbg.dassert_isinstance(dag, dtf.DAG)
    graph = dag.dag
    dbg.dassert_isinstance(graph, networ.Graph)
    # Convert the graph into pygraphviz object.
    agraph = networ.nx_agraph.to_agraph(graph)
    return agraph