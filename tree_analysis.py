# in this script we make some visualizations of the knowledge graphs
# we should characterise them for the following properties:
# 1. number of nodes
# 2. depth of the tree
# 3. number of keywords per node
# 4. keyword visualization (word cloud)
# 5. keyword relevance
# 6. keyword alternative wording (average count + few examples)
import numpy as np
import pandas as pd
from typing import List
import json
import os
from objects import TreeNode, load_tree


def calculate_tree_depth(tree: List[TreeNode]) -> int:
    """
    Calculate the depth of the tree.

    Args:
        tree (List[TreeNode]): List of TreeNode objects representing the tree.

    Returns:
        int: Depth of the tree.
    """
    indexed_tree = {node.title: node for node in tree}
    def depth(node: TreeNode) -> int:
        if not node.parents:
            return 1
        return 1 + max([0] + [depth(indexed_tree[parent]) for parent in node.parents if parent in indexed_tree])

    return max([depth(node) for node in tree])

def tree_properties(tree_file) -> dict:
    """
    Summarizes numeric properties of trees into a dataframe.

    Args:
        tree_files (list): List of filenames containing tree data.

    Returns:
        pd.DataFrame: Dataframe with summed properties for each tree.
    """

    # Load tree data (assuming a function `load_tree` exists)
    tree = load_tree(tree_file)
    
    # Calculate properties
    num_nodes = len(tree)
    depth = calculate_tree_depth(tree)
    num_keywords = np.mean([len(node.keywords) for node in tree])
    keyword_relevance = np.mean([int(kw.relevance) for node in tree for kw in node.keywords])
    alternative_wordings = np.mean([len(kw.alternative_wording) for node in tree for kw in node.keywords])

    # Append to summary
    return {
        "tree": " ".join(os.path.split(tree_file)[-1].split("_")[:-1]),
        "num_nodes": num_nodes,
        "depth": depth,
        "avg_keywords": num_keywords,
        "avg_keyword_relevance": keyword_relevance,
        "avg_alternative_wordings": alternative_wordings
    }

if __name__ == "__main__":
    # Example usage
    data_directory = "data"  # Replace with the actual directory path
    covered_names = []
    data = []
    for fname in os.listdir(data_directory):
        if fname.endswith(".json"):
            print(fname)
            name = " ".join(fname.split("_")[:-1])
            if name in covered_names:
                continue
            covered_names.append(name)
            data.append(tree_properties(os.path.join(data_directory, fname)))
            df = pd.DataFrame(data)
            df.to_csv("tree_properties.csv", index=False)
    print(df)
