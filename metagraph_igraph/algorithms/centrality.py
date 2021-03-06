from metagraph import concrete_algorithm
from metagraph.plugins.numpy.types import NumpyNodeMap, NumpyNodeSet
from metagraph.plugins.core import exceptions
from ..types import IGraph
import numpy as np
import metagraph as mg
import igraph


@concrete_algorithm("centrality.pagerank")
def igraph_pagerank(
    graph: IGraph, damping: float, maxiter: int, tolerance: float
) -> NumpyNodeMap:
    weights = "weight" if graph.value.is_weighted() else None
    opts = igraph.ARPACKOptions()
    opts.maxiter = maxiter
    opts.tol = tolerance
    try:
        pr = graph.value.pagerank(
            weights=weights,
            damping=damping,
            implementation="arpack",
            arpack_options=opts,
        )
    except igraph.InternalError as e:
        if "Maximum number of iterations reached" in str(e):
            raise exceptions.ConvergenceError(
                f"failed to converge within {maxiter} iterations"
            )
        raise
    node_ids = None if graph.is_sequential() else graph.value.vs["NodeId"]
    return NumpyNodeMap(np.array(pr), node_ids)


@concrete_algorithm("centrality.betweenness")
def igraph_betweenness_centrality(
    graph: IGraph, nodes: mg.Optional[NumpyNodeSet], normalize: bool
) -> NumpyNodeMap:
    if nodes is not None:
        nodes = nodes.value
        node_ids = nodes
    else:
        node_ids = None if graph.is_sequential() else graph.value.vs["NodeId"]
    if graph.value.is_weighted():
        bc = graph.value.betweenness(vertices=nodes, weights="weight")
    else:
        bc = graph.value.betweenness(vertices=nodes)
    return NumpyNodeMap(np.array(bc), node_ids)


@concrete_algorithm("centrality.closeness")
def closeness_centrality(
    graph: IGraph,
    nodes: mg.Optional[NumpyNodeSet],
) -> NumpyNodeMap:
    if nodes is not None:
        nodes = nodes.value
        node_ids = nodes
    else:
        node_ids = None if graph.is_sequential() else graph.value.vs["NodeId"]
    cc = graph.value.closeness(
        vertices=nodes, mode="in", weights=graph.edge_weight_label
    )
    return NumpyNodeMap(np.array(cc), node_ids)


@concrete_algorithm("centrality.eigenvector")
def eigenvector_centrality(
    graph: IGraph, maxiter: int, tolerance: float
) -> NumpyNodeMap:
    weights = "weight" if graph.value.is_weighted() else None
    opts = igraph.ARPACKOptions()
    opts.maxiter = maxiter
    opts.tol = tolerance
    eigv = graph.value.eigenvector_centrality(
        scale=False, weights=weights, arpack_options=opts
    )
    node_ids = None if graph.is_sequential() else graph.value.vs["NodeId"]
    return NumpyNodeMap(np.array(eigv), node_ids)
