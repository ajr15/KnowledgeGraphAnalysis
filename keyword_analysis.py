# in this script we will analyze the content of the keywords in the graph
# we visualize them as a word cloud

from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import os
from objects import TreeNode, load_tree

def visualize_keywords_as_wordcloud(node: TreeNode):
    """
    Visualizes the keywords of a TreeNode object as a word cloud.
    The relevance of each keyword (1-5 scale, 1 most important) is used to adjust its size.

    Args:
        tree_node (TreeNode): The node containing keywords and their relevance.
    """
    # Assuming tree_node.keywords is a dictionary with keywords as keys and relevance as values
    # Adjust weights based on relevance (1 most important -> higher weight)
    weights = {kw.name: 6 - float(kw.relevance) for kw in node.keywords if kw.relevance != "---"}
    if len(weights) == 0:
        print(f"No keywords found for node: {node.title}")
        return
    # Generate the word cloud with custom colormap and font
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white', 
        colormap='viridis',  # Use a visually appealing colormap
        stopwords=STOPWORDS,  # Add default stopwords
        font_path=None  # You can specify a custom font path if desired
    ).generate_from_frequencies(weights)

    # Display the word cloud
    plt.figure(figsize=(12, 6))  # Adjust figure size for better visibility
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')

if __name__ == "__main__":
    fnames = ["data/auvs_IL.json", "data/photonic_quantum_computing_IL.json", "data/superconducting_circuits_IL.json", "data/trapped_ions_IL.json"]
    for fname in fnames:
        treename = fname.split("/")[-1].split(".")[0]
        if not os.path.exists("results/wordcloud/" + treename):
            os.mkdir("results/wordcloud/" + treename)
        tree = load_tree(fname)
        for node in tree:
            plt.figure()
            visualize_keywords_as_wordcloud(node)
            plt.savefig("results/wordcloud/" + treename + "/" + node.title + ".png")
            plt.close()