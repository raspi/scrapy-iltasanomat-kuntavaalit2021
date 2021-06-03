from dataclasses import dataclass


@dataclass
class Item:
    url: str
    data: dict


@dataclass
class Candidate(Item):
    id: int
    municipalityid: int


@dataclass
class Party(Item):
    pass


@dataclass
class Question(Item):
    municipalityid: int
