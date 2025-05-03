from typing import List
from dataclasses import dataclass
import json


@dataclass
class Document:

    id: str
    title: str
    publication_year: int
    countries: list
    fwci: float
    citedby: int
    score: float

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "publication_year": self.publication_year,
            "countries": self.countries,
            "fwci": self.fwci,
            "citedby": self.citedby,
            "score": self.score
        }
    
    @staticmethod
    def from_json(data: dict) -> 'Document':
        return Document(
            id=data.get('id'),
            title=data.get('title'),
            publication_year=data.get('publication_year'),
            countries=data.get('countries', []),
            fwci=data.get('fwci', None),
            citedby=data.get('citedby', None),
            score=data.get('score', None)
        )


@dataclass
class Keyword:

    name: str
    relevance: str
    alternative_wording: List[str]
    documents: List[Document]

    def to_json(self) -> dict:
        if self.documents is None:
            self.documents = []
        return {
            "name": self.name,
            "relevance": self.relevance,
            "alternative_wording": self.alternative_wording,
            "documents": [
                doc.to_json() for doc in self.documents
            ]
        }

    @staticmethod
    def from_json(data: dict) -> 'Keyword':
        return Keyword(
            name=data.get('name'),
            relevance=data.get('relevance'),
            alternative_wording=data.get('alternative_wording', []),
            documents=[
                Document.from_json(doc) for doc in data.get('documents', [])
            ]
        )

@dataclass
class TreeNode:
    title: str
    is_root: bool
    description: str
    parents: List[str]
    keywords: List[Keyword]
    score: float

    def to_json(self) -> dict:
        return {
            "title": self.title,
            "is_root": self.is_root,
            "description": self.description,
            "parents": self.parents,
            "keywords": [
                keyword.to_json() for keyword in self.keywords
            ]
        }

    @staticmethod
    def from_json(data: dict) -> 'TreeNode':
        return TreeNode(
            title=data.get('title'),
            is_root=data.get('is_root', False),
            description=data.get('description'),
            parents=data.get('parents', []),
            keywords=[
                Keyword.from_json(kw) for kw in data.get('keywords', [])
            ],
            score=data.get('score', None)
        )


def load_tree(path: str) -> List[TreeNode]:
    with open(path, 'r') as file:
        data = json.load(file)
    if type(data) is dict:
        root = TreeNode.from_json(data["root"])
        root.is_root = True
        return [root] + [TreeNode.from_json(node) for node in data["leafs"]]
    else:
        return [TreeNode.from_json(node) for node in data]