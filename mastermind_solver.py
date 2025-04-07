import itertools
import random
from operadores_logicos import *
import time
import sys
from typing import List, Tuple, Set, Dict, Optional
from dataclasses import dataclass, field

COLORES = ["azul", "rojo", "blanco", "negro", "verde", "purpura"]

@dataclass
class MastermindKB:
    todas_combinaciones: List[Tuple[str, str, str, str]] = field(default_factory=lambda: list(itertools.product(COLORES, repeat=4)))
    combinaciones_posibles: Set[Tuple[str, str, str, str]] = field(init=False)
    knowledge: And = field(default_factory=lambda: And([]))
    symbols: Dict[Tuple[int, str], Symbol] = field(default_factory=dict)
    
    def __post_init__(self):
        self.combinaciones_posibles = set(self.todas_combinaciones)
        
        for pos in range(4):
            for color in COLORES:
                self.symbols[(pos, color)] = Symbol(f"{color}_{pos}")
    
    def actualizar_con_feedback(self, combinacion: Tuple[str, str, str, str], 
                              posiciones_correctas: int, 
                              colores_correctos: int) -> None:
        if posiciones_correctas + colores_correctos > 4:
            print("\nADVERTENCIA: Feedback inválido. La suma de posiciones correctas y")
            print("colores correctos no puede ser mayor que 4.")
            return
        
        nuevas_combinaciones = set()
        for candidato in self.combinaciones_posibles:
            if self._coincide_feedback(combinacion, candidato, posiciones_correctas, colores_correctos):
                nuevas_combinaciones.add(candidato)
        
        if not nuevas_combinaciones and self.combinaciones_posibles:
            print("\nADVERTENCIA: No hay combinaciones que coincidan con el feedback proporcionado.")
            print(f"Feedback recibido: {posiciones_correctas} posiciones correctas, {colores_correctos} colores correctos")
            print("Es posible que haya un error en el feedback ingresado.")
            
            return
        
        self.combinaciones_posibles = nuevas_combinaciones
        
        self._agregar_restriccion_logica(combinacion, posiciones_correctas, colores_correctos)
        
    def _coincide_feedback(self, combinacion1: Tuple[str, str, str, str], 
                          combinacion2: Tuple[str, str, str, str], 
                          posiciones_correctas: int, 
                          colores_correctos: int) -> bool:
        counter1 = {color: 0 for color in COLORES}
        counter2 = {color: 0 for color in COLORES}
        
        pos_correctas = 0
        for i in range(4):
            if combinacion1[i] == combinacion2[i]:
                pos_correctas += 1
            else:
                counter1[combinacion1[i]] += 1
                counter2[combinacion2[i]] += 1
        
        colores_comunes = sum(min(counter1[color], counter2[color]) for color in COLORES)
        
        return pos_correctas == posiciones_correctas and colores_comunes == colores_correctos
    
    def _agregar_restriccion_logica(self, combinacion: Tuple[str, str, str, str], 
                                  posiciones_correctas: int, 
                                  colores_correctos: int) -> None:
        pass
        
    def siguiente_combinacion(self) -> Tuple[str, str, str, str]:
        if not self.combinaciones_posibles:
            print("\nADVERTENCIA: No hay combinaciones posibles restantes.")
            print("Esto puede deberse a un feedback inconsistente o a un error en el cálculo.")
            print("Reiniciando con una combinación aleatoria...\n")
            
            return tuple(random.choice(COLORES) for _ in range(4))
        
        if len(self.combinaciones_posibles) == len(self.todas_combinaciones):
            return ("azul", "azul", "rojo", "verde")
        
        if len(self.combinaciones_posibles) <= 2:
            return next(iter(self.combinaciones_posibles))
            
        if len(self.combinaciones_posibles) <= 10:
            return random.choice(list(self.combinaciones_posibles))
        
        combinaciones_a_evaluar = random.sample(
            list(self.combinaciones_posibles) if len(self.combinaciones_posibles) <= 50 
            else list(self.todas_combinaciones),
            min(20, len(self.combinaciones_posibles))
        )
        
        mejor_combinacion = None
        mejor_puntuacion = float('inf')
        
        for combinacion in combinaciones_a_evaluar:
            max_conjunto_restante = 0
            
            resultados = {}
            
            for candidato in random.sample(list(self.combinaciones_posibles), 
                                          min(50, len(self.combinaciones_posibles))):
                pos_correctas = 0
                counter1 = {color: 0 for color in COLORES}
                counter2 = {color: 0 for color in COLORES}
                
                for i in range(4):
                    if combinacion[i] == candidato[i]:
                        pos_correctas += 1
                    else:
                        counter1[combinacion[i]] += 1
                        counter2[candidato[i]] += 1
                
                colores_comunes = sum(min(counter1[color], counter2[color]) for color in COLORES)
                
                feedback = (pos_correctas, colores_comunes)
                if feedback not in resultados:
                    resultados[feedback] = 0
                resultados[feedback] += 1
                
                max_conjunto_restante = max(max_conjunto_restante, resultados[feedback])
            
            if max_conjunto_restante < mejor_puntuacion:
                mejor_puntuacion = max_conjunto_restante
                mejor_combinacion = combinacion
        
        if mejor_combinacion is None:
            return random.choice(list(self.combinaciones_posibles))
        
        return mejor_combinacion
    
    def tamano_espacio_busqueda(self) -> int:
        return len(self.combinaciones_posibles)

@dataclass
class MastermindSolver:
    kb: MastermindKB = field(default_factory=MastermindKB)
    intentos: int = 0
    historia_espacio_busqueda: List[int] = field(default_factory=list)
    
    def evaluar_combinacion(self, combinacion: Tuple[str, str, str, str], 
                           combinacion_secreta: Tuple[str, str, str, str]) -> Tuple[int, int]:
        counter1 = {color: 0 for color in COLORES}
        counter2 = {color: 0 for color in COLORES}
        
        pos_correctas = 0
        for i in range(4):
            if combinacion[i] == combinacion_secreta[i]:
                pos_correctas += 1
            else:
                counter1[combinacion[i]] += 1
                counter2[combinacion_secreta[i]] += 1
        
        colores_comunes = sum(min(counter1[color], counter2[color]) for color in COLORES)
        
        return (pos_correctas, colores_comunes)
    
    def modo_automatico(self, combinacion_secreta: Tuple[str, str, str, str]) -> Tuple[int, List[int]]:
        self.kb = MastermindKB()
        self.intentos = 0
        self.historia_espacio_busqueda = [self.kb.tamano_espacio_busqueda()]
        
        while True:
            self.intentos += 1
            
            combinacion = self.kb.siguiente_combinacion()
            
            posiciones_correctas, colores_correctos = self.evaluar_combinacion(
                combinacion, combinacion_secreta
            )
            
            if posiciones_correctas == 4:
                return (self.intentos, self.historia_espacio_busqueda)
            
            self.kb.actualizar_con_feedback(combinacion, posiciones_correctas, colores_correctos)
            
            self.historia_espacio_busqueda.append(self.kb.tamano_espacio_busqueda())
    
    def modo_tiempo_real(self) -> int:
        self.kb = MastermindKB()
        self.intentos = 0
        self.historia_espacio_busqueda = [self.kb.tamano_espacio_busqueda()]
        
        print("¡Bienvenido al solucionador de Mastermind!")
        print("Piensa en una combinación secreta de 4 fichas con los siguientes colores:")
        print(", ".join(COLORES))
        print("Responderé con mis propuestas y tú me darás retroalimentación.")
        print()
        
        while True:
            self.intentos += 1
            
            combinacion = self.kb.siguiente_combinacion()
            
            print(f"\nIntento #{self.intentos}:")
            print(f"Mi propuesta es: {combinacion}")
            
            while True:
                try:
                    pos_correctas = int(input("Número de fichas en posición correcta (0-4): "))
                    if 0 <= pos_correctas <= 4:
                        break
                    print("Por favor, ingrese un valor entre 0 y 4.")
                except ValueError:
                    print("Por favor, ingrese un número válido.")
            
            while True:
                try:
                    colores_correctos = int(input("Número de fichas con color correcto pero en posición incorrecta (0-4): "))
                    if 0 <= colores_correctos <= 4 and colores_correctos + pos_correctas <= 4:
                        break
                    print("Por favor, ingrese un valor válido (la suma con posiciones correctas no debe exceder 4).")
                except ValueError:
                    print("Por favor, ingrese un número válido.")
            
            if pos_correctas == 4:
                print(f"\n¡Se ha encontrado la solución en {self.intentos} intentos!")
                return self.intentos
            
            self.kb.actualizar_con_feedback(combinacion, pos_correctas, colores_correctos)
            
            nuevo_tamano = self.kb.tamano_espacio_busqueda()
            self.historia_espacio_busqueda.append(nuevo_tamano)
            print(f"Espacio de búsqueda reducido a {nuevo_tamano} combinaciones posibles.")

def generar_combinacion_aleatoria() -> Tuple[str, str, str, str]:
    return tuple(random.choice(COLORES) for _ in range(4))

def convertir_entrada_a_combinacion(entrada: str) -> Optional[Tuple[str, str, str, str]]:
    if ',' in entrada:
        colores = [color.strip().lower() for color in entrada.split(',')]
    else:
        colores = [color.strip().lower() for color in entrada.split()]
    
    if len(colores) != 4:
        print("¡Debes especificar exactamente 4 colores!")
        return None
    
    for color in colores:
        if color not in COLORES:
            print(f"Color '{color}' no válido. Los colores válidos son: {', '.join(COLORES)}")
            return None
    
    return tuple(colores)

def main():
    print("=== SOLUCIONADOR DE MASTERMIND ===")
    print("Colores disponibles:", ", ".join(COLORES))
    print()
    print("Modos disponibles:")
    print("1. Modo Automático")
    print("2. Modo en Tiempo Real")
    print()
    
    while True:
        try:
            modo = int(input("Seleccione un modo (1-2): "))
            if 1 <= modo <= 2:
                break
            print("Por favor, ingrese 1 o 2.")
        except ValueError:
            print("Por favor, ingrese un número válido.")
    
    solver = MastermindSolver()
    
    if modo == 1:
        print("\n=== MODO AUTOMÁTICO ===")
        print("Ingrese la combinación secreta o deje en blanco para generar una aleatoria.")
        print("Formato: azul rojo verde negro  -o-  azul, rojo, verde, negro")
        
        entrada = input("Combinación secreta: ").strip()
        if entrada:
            combinacion_secreta = convertir_entrada_a_combinacion(entrada)
            if combinacion_secreta is None:
                return
        else:
            combinacion_secreta = generar_combinacion_aleatoria()
            print(f"Combinación secreta generada: {combinacion_secreta}")
        
        print("\nResolviendo...")
        inicio = time.time()
        intentos, historia = solver.modo_automatico(combinacion_secreta)
        fin = time.time()
        
        print(f"\n¡Solución encontrada en {intentos} intentos!")
        print(f"Tiempo de ejecución: {fin - inicio:.2f} segundos")
        print("\nEvolución del espacio de búsqueda:")
        for i, tamano in enumerate(historia):
            print(f"Después del intento {i}: {tamano} combinaciones posibles")
    
    else:
        print("\n=== MODO EN TIEMPO REAL ===")
        solver.modo_tiempo_real()

if __name__ == "__main__":
    main()