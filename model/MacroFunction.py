from dataclasses import dataclass


@dataclass
class MacroFunction:
    name: str
    openContent: str
    closeContent: str
    description: str 
    custome: bool