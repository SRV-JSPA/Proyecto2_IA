from dataclasses import dataclass
from typing import List, Set, Dict, Any
SentenceType = Any

@dataclass
class Symbol:
    name: str
    
    def __repr__(self):
        return self.name
    
    def evaluate(self, model: Dict[str, bool]) -> bool:
        try:
            return bool(model[self.name])
        except KeyError:
            raise Exception(f"variable {self.name} not in model")
    
    def symbols(self) -> Set[str]:
        return {self.name}

@dataclass
class Not:
    operand: SentenceType
    
    def __repr__(self):
        return f"Not({self.operand})"
    
    def evaluate(self, model: Dict[str, bool]) -> bool:
        return not self.operand.evaluate(model)
    
    def symbols(self) -> Set[str]:
        return self.operand.symbols()

@dataclass
class And:
    conjuncts: List[SentenceType]
    
    def __repr__(self):
        conjunctions = ", ".join([str(conjunct) for conjunct in self.conjuncts])
        return f"And({conjunctions})"
    
    def add(self, conjunct: SentenceType) -> None:
        self.conjuncts.append(conjunct)
    
    def evaluate(self, model: Dict[str, bool]) -> bool:
        return all(conjunct.evaluate(model) for conjunct in self.conjuncts)
    
    def symbols(self) -> Set[str]:
        if not self.conjuncts:
            return set()
        return set().union(*[conjunct.symbols() for conjunct in self.conjuncts])

@dataclass
class Or:
    disjuncts: List[SentenceType]
    
    def __repr__(self):
        disjuncts = ", ".join([str(disjunct) for disjunct in self.disjuncts])
        return f"Or({disjuncts})"
    
    def evaluate(self, model: Dict[str, bool]) -> bool:
        return any(disjunct.evaluate(model) for disjunct in self.disjuncts)
    
    def symbols(self) -> Set[str]:
        if not self.disjuncts:
            return set()
        return set().union(*[disjunct.symbols() for disjunct in self.disjuncts])

@dataclass
class Implication:
    antecedent: SentenceType
    consequent: SentenceType
    
    def __repr__(self):
        return f"Implication({self.antecedent}, {self.consequent})"
    
    def evaluate(self, model: Dict[str, bool]) -> bool:
        return not self.antecedent.evaluate(model) or self.consequent.evaluate(model)
    
    def symbols(self) -> Set[str]:
        return self.antecedent.symbols().union(self.consequent.symbols())

@dataclass
class Biconditional:
    left: SentenceType
    right: SentenceType
    
    def __repr__(self):
        return f"Biconditional({self.left}, {self.right})"
    
    def evaluate(self, model: Dict[str, bool]) -> bool:
        return self.left.evaluate(model) == self.right.evaluate(model)
    
    def symbols(self) -> Set[str]:
        return self.left.symbols().union(self.right.symbols())

def model_check(knowledge: SentenceType, query: SentenceType) -> bool:

    def check_all(knowledge: SentenceType, query: SentenceType, symbols: Set[str], model: Dict[str, bool]) -> bool:

        if not symbols:
            if knowledge.evaluate(model):
                return query.evaluate(model)
            return True
        else:
            remaining = symbols.copy()
            p = remaining.pop()

            model_true = model.copy()
            model_true[p] = True

            model_false = model.copy()
            model_false[p] = False

            return (check_all(knowledge, query, remaining, model_true) and
                    check_all(knowledge, query, remaining, model_false))

    symbols = knowledge.symbols().union(query.symbols())

    return check_all(knowledge, query, symbols, dict())

def create_symbol(name: str) -> Symbol:
    return Symbol(name)

def create_not(operand: SentenceType) -> Not:
    return Not(operand)

def create_and(*conjuncts: SentenceType) -> And:
    return And(list(conjuncts))

def create_or(*disjuncts: SentenceType) -> Or:
    return Or(list(disjuncts))

def create_implication(antecedent: SentenceType, consequent: SentenceType) -> Implication:
    return Implication(antecedent, consequent)

def create_biconditional(left: SentenceType, right: SentenceType) -> Biconditional:
    return Biconditional(left, right)