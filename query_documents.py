import os
from typing import List
from dataclasses import dataclass
import json
from elasticsearch import Elasticsearch
import matplotlib.pyplot as plt
import networkx as nx
from objects import Document, Keyword, TreeNode


def flatten(lst: List[List]) -> List:
    """Flatten a list of lists into a single list."""
    return [item for sublist in lst for item in sublist]

def qstring(kwd: str,field: str) -> str:
    kwd=kwd.replace("/"," ")
    return {"query_string": {"query":kwd,
                             "default_field":field,"default_operator":"AND"}}

def keyword_query(client: Elasticsearch, kwd: Keyword, country: str,startyear:int) -> List[Document]:
    query = {
        "query": {"bool":{"filter": [{"term": {"countries": country}},
                               {"range": {"publication_year": {"gte": startyear}}}],
                "should": [
                    qstring(kwd.name,"title"),
                    qstring(kwd.name,"topics.display_name"),
                    qstring(kwd.name,"concepts.display_name"),
                    qstring(kwd.name,"keywords.display_name")
                ] + flatten([
                    [qstring(alt,"title"),
                     qstring(alt,"topics.display_name"),
                     qstring(alt,"concepts.display_name"),
                     qstring(alt,"keywords.display_name")]
                    for alt in kwd.alternative_wording
                   
                ]),
                "minimum_should_match": 1
            
            }},
        "size": 100
    }
    #print(query)
    response = client.search(index="ngrams3", body=query)
    documents = []
    for hit in response['hits']['hits']:
        source = hit['_source']
        documents.append(Document(
            id=source['id'],
            title=source['title'],
            publication_year=source['publication_year'],
            countries=source['countries'],
            fwci=source.get('fwci', 0),
            citedby=source.get('citedby', 0),
            score=hit['_score']
        ))
    return documents

def parse_node(d: dict) -> TreeNode:
    keywords = [
        Keyword(
            name=kw['keyword'],
            relevance=kw['relevance'],
            alternative_wording=kw.get('alternative_wording', [])
        )
        for kw in d.get("kwds", [])
    ]
    return TreeNode(
        title=d['title'],
        is_root=d.get('is_root', False),
        description=d['description'],
        parents=d.get('parents', []),
        keywords=keywords
    )

def parse_tree(path: str) -> List[TreeNode]:
    with open(path, 'r') as file:
        data = json.load(file)
    root = parse_node(data["root"])
    root.is_root = True
    return [root] + [parse_node(node) for node in data["leafs"]]


def full_tree(client: Elasticsearch, tree_path: str, country: str, startyear:int) -> List[TreeNode]:
    tree = parse_tree(tree_path)
    for node in tree:
        print(node.title)
        for keyword in node.keywords:
            if keyword.name=="--":
                continue
            keyword.documents = keyword_query(client, keyword, country,startyear)
        # calculate the score for the node
        node.score = node_score(node)
    return tree


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
    if total_relevance==0:
        return 0
    # Normalize the score by the total relevance
    # to avoid bias towards nodes with more keywords
    # with lower relevance        
    return score / total_relevance


def visualize_tree(tree: List[TreeNode], figpath: str):
    G = nx.DiGraph()
    node_colors = []

    for node in tree:
        G.add_node(node.title, score=node.score)
        node_colors.append(node.score)
        for parent in node.parents:
            G.add_edge(parent, node.title)

    # Normalize scores for coloring
    max_score = max(node_colors) if node_colors else 1
    min_score = min(node_colors) if node_colors else 0
    normalized_colors = [(score - min_score) / (max_score - min_score) for score in node_colors]

    # Draw the graph
    pos = nx.nx_agraph.graphviz_layout(G, prog="dot", args="-Gnodesep=2.0")
    
    # Adjust labels to fit within node size, breaking into multiple rows if necessary
    adjusted_labels = {}
    for n in G.nodes:
        label = n
        max_width = 15  # Maximum characters per line
        if len(label) > max_width:
            label = "\n".join([label[i:i+max_width] for i in range(0, len(label), max_width)])
        adjusted_labels[n] = label
    plt.figure(figsize=(12, 8))
    nx.draw(
        G, pos, with_labels=True, labels=adjusted_labels,
        node_color=normalized_colors, cmap="coolwarm", node_size=5000, font_size=10,
        edgecolors="black"  # Add black outline to each node
    )
    plt.title("Tree Visualization")
    plt.savefig(figpath)
    plt.show()

if __name__ == '__main__':
    es = Elasticsearch(["http://localhost:9200"])
    countries = ["IL", "IR", "EG", "IQ", "LB", "JO", "TR", "SY", "SA"]
    for country in countries[0:1]:
        for tree_file in os.listdir("trees"):
            print(tree_file, country)
            f = os.path.join("trees", tree_file)
            name = "_".join(tree_file.split(".")[0].split("_")[4:])
            tree = full_tree(es, f, country,1000)
            #visualize_tree(tree, "images/photonic_quantum_computer_{}.png".format(country))
            # Save the tree to a JSON file
            with open(f"nodes/{name}_{country}.json", "w") as outfile:
                json.dump([node.to_json() for node in tree], outfile, indent=4)
                