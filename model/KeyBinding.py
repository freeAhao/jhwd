from dataclasses import dataclass, field

from model.MacroFunction import MacroFunction

@dataclass
class KeyBinding:
    mouseBtn: int 
    func: MacroFunction 
    modifiers:list[str] = field(default_factory=list)

    def is_valid(self) -> bool:
        return self.mouseBtn != None and self.func !=None and isinstance(self.modifiers,list)
    
    def get_key(self) -> str:
        return ",".join(self.modifiers)+"+"+str(self.mouseBtn)