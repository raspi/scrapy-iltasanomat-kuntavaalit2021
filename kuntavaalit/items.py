from dataclasses import dataclass


@dataclass
class Item:
    url: str
    data: dict


@dataclass
class Municipality(Item):
    pass


@dataclass
class Party(Item):
    pass


@dataclass
class ItemWithMunicipality(Item):
    municipalityid: int


@dataclass
class Candidate(ItemWithMunicipality):
    id: int


@dataclass
class PartyAlliance(ItemWithMunicipality):
    pass


@dataclass
class Question(ItemWithMunicipality):
    brandname: str
