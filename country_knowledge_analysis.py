import os
import networkx as nx
from matplotlib import pyplot as plt
from typing import List
from objects import TreeNode, load_tree

def node_score(node: TreeNode):
    score = 0
    total_relevance = 0
    for kwd in node.keywords:
        if kwd.relevance == "---":
            continue
        relevance = 6 - int(kwd.relevance if kwd.relevance else 5)  
        total_relevance += relevance
        for doc in kwd.documents:
            fwci = float(doc.fwci) if doc.fwci else 0
            score += doc.score / 100 * fwci * relevance
    if total_relevance == 0:
        return 0
    # Normalize the score by the total relevance
    # to avoid bias towards nodes with more keywords
    # with lower relevance        
    return score / total_relevance

def tree_to_networkx(tree: List[TreeNode]) -> nx.DiGraph:
    G = nx.DiGraph()
    for node in tree:
        G.add_node(node.title, score=node.score)
    # adding edges. note it should be after nodes to avoid adding edges to non-existing nodes
    for node in tree:
        for parent in node.parents:
            if parent in G:
                G.add_edge(parent, node.title)
    return G

def visualize_tree(tree: List[TreeNode], node_size: float=5000, max_score: float=None, min_score: float=None):
    # load graph data
    G = tree_to_networkx(tree)
    scores = [node.score for node in tree]
    if max_score is None:
        max_score = max(scores)
    if min_score is None:
        min_score = min(scores)

    # Calculate node positions (tree layout)
    pos = nx.nx_agraph.graphviz_layout(G, prog="dot", args="-Gnodesep=2.0")
    # set color map
    sm = plt.cm.ScalarMappable(cmap="coolwarm", norm=plt.Normalize(vmin=min_score, vmax=max_score))
    
    # draw the network edges
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_shape="o", node_color=scores, cmap=sm.cmap, vmin=min_score, vmax=max_score)
    nx.draw_networkx_edges(G, pos, node_size=node_size, node_shape="o", arrows=True)

    labels = {}
    for node in G:
        # add label to node
        l = f"{node} ({G.nodes[node]['score']:.2f})"
        # Split the label into words and add line breaks if the label is too long
        words = l.split()
        max_line_length = int(node_size / 1000 * 15)
        ajr = ""
        for word in words:
            if len(ajr) + len(word) + 1 > max_line_length:
                ajr += word + " "
            else:
                ajr += "\n" + word + " "
        labels[node] = ajr
    # Draw node labels 
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_color="black", font_family="sans-serif", verticalalignment="center")    

    # Add color bar
    cbar = plt.colorbar(sm, ax=plt.gca())

    xlim = plt.xlim()
    plt.xlim(xlim[0] - 0.1, xlim[1] + 0.1)
    ylim = plt.ylim()
    plt.ylim(ylim[0] - 0.1, ylim[1] + 0.1)

    # remove splines
    plt.axis("off")

if __name__ == "__main__": 
    tree_files = [os.path.join("data", fname) for fname in os.listdir("data") if "auv" not in fname]
    trees = []
    scores = []
    for tree_file in tree_files:
        tree = load_tree(tree_file)
        for node in tree:
            node.score = node_score(node)
        trees.append(tree)
        scores += [node.score for node in tree]
    max_score = max(scores)
    min_score = min(scores)
    for i, tree in enumerate(trees):
        print(tree_files[i])    
        plt.figure(figsize=(16, 8))
        visualize_tree(tree, node_size=5000, max_score=max_score, min_score=min_score)
        plt.savefig(f"results/trees/{tree_files[i][5:-5]}.png", format="png", dpi=300)