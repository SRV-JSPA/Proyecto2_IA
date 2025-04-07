import matplotlib.pyplot as plt
import numpy as np
import time
from mastermind_solver import MastermindSolver, generar_combinacion_aleatoria

def ejecutar_experimento_200_juegos():
    num_juegos = 200
    solver = MastermindSolver()
    
    intentos_por_juego = []
    todas_historias = []
    
    print(f"Ejecutando {num_juegos} juegos automáticos...")
    inicio_total = time.time()
    
    for i in range(num_juegos):
        if i % 20 == 0:
            print(f"Juego {i}/{num_juegos}")
            
        combinacion_secreta = generar_combinacion_aleatoria()
        
        intentos, historia = solver.modo_automatico(combinacion_secreta)
        
        intentos_por_juego.append(intentos)
        todas_historias.append(historia)
    
    fin_total = time.time()
    print(f"Experimento completado en {fin_total - inicio_total:.2f} segundos")
    
    promedio_intentos = np.mean(intentos_por_juego)
    
    max_intentos = max(len(historia) for historia in todas_historias)
    
    espacio_por_intento = np.zeros((num_juegos, max_intentos))
    
    for i, historia in enumerate(todas_historias):
        for j, tamano in enumerate(historia):
            if j < max_intentos:  
                espacio_por_intento[i, j] = tamano
        
        ultimo_valor = historia[-1] if historia else 0
        for j in range(len(historia), max_intentos):
            espacio_por_intento[i, j] = ultimo_valor
    
    promedio_espacio_por_intento = np.mean(espacio_por_intento, axis=0)
    
    return {
        'promedio_intentos': promedio_intentos,
        'promedio_espacio_por_intento': promedio_espacio_por_intento,
        'intentos_por_juego': intentos_por_juego,
        'max_intentos': max_intentos
    }

def generar_grafico_espacio_busqueda(resultados):
    promedio_intentos = resultados['promedio_intentos']
    promedio_espacio = resultados['promedio_espacio_por_intento']
    
    intentos = np.arange(len(promedio_espacio))
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    bars = ax.bar(intentos, promedio_espacio, color='#1f77b4', width=0.7)
    
    promedio_redondeado = round(promedio_intentos)
    ax.axvline(x=promedio_redondeado, color='red', linestyle='-', linewidth=2)
    
    ax.text(promedio_redondeado + 0.5, max(promedio_espacio) * 0.8, 
            f"Promedio de intentos\nhasta solución", 
            color='red', fontsize=12, ha='left', va='center')

    for i, bar in enumerate(bars):
        if promedio_espacio[i] > 0: 
            ax.text(i, bar.get_height() + (max(promedio_espacio) * 0.01), 
                   f"{int(promedio_espacio[i])}", 
                   ha='center', va='bottom', fontsize=10)
    
    ax.set_title('Espacio de búsqueda', fontsize=16)
    ax.set_ylabel('Espacio de búsqueda', fontsize=12)
    
    ax.set_xticks(intentos)
    ax.set_xticklabels([f'Intento\n{i}' for i in intentos])

    ax.grid(axis='y', linestyle='--', alpha=0.7)

    ax.legend(['Espacio de búsqueda'], loc='upper right')

    plt.tight_layout()
    plt.savefig('espacio_busqueda_200_juegos.png', dpi=300)
    print("Gráfico guardado: espacio_busqueda_200_juegos.png")

    print("\n=== RESULTADOS DE 200 JUEGOS AUTOMÁTICOS ===")
    print(f"Promedio de intentos necesarios: {promedio_intentos:.2f}")
    print(f"Tamaño inicial del espacio de búsqueda: {int(promedio_espacio[0])}")

    for i in range(1, min(10, len(promedio_espacio))):
        porcentaje = (1 - (promedio_espacio[i] / promedio_espacio[i-1])) * 100
        print(f"Reducción tras intento {i}: {int(promedio_espacio[i-1])} → {int(promedio_espacio[i])} ({porcentaje:.1f}%)")
    
    return fig

def main():

    print("=== EXPERIMENTO DE 200 JUEGOS MASTERMIND ===")
    
    resultados = ejecutar_experimento_200_juegos()
    
    generar_grafico_espacio_busqueda(resultados)
    
    import json
    with open('resultados_200_juegos.json', 'w') as f:
        datos_json = {
            'promedio_intentos': float(resultados['promedio_intentos']),
            'promedio_espacio_por_intento': [float(x) for x in resultados['promedio_espacio_por_intento']],
        }
        json.dump(datos_json, f)
    
    print("Datos guardados en 'resultados_200_juegos.json'")

if __name__ == "__main__":
    main()