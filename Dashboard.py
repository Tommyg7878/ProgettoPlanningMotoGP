import pygame
import subprocess
import time
import os

"""
MotoGP Planner Dashboard 


"""



# Nomi file 
ENHSP_JAR = "enhsp.jar"

DOMAIN_FILE = "motogp_domain.pddl"

PROBLEM_FILES = {
    1: "problem_1.pddl",
    2: "problem_2.pddl",
    3: "problem_3.pddl"
}

TEMP_PROBLEM_FILE = "temp_problem.pddl"

# Azioni disponibili per le moto
AZIONI = ["benzina", "elettronica", "assetto"]

# DEFINIZIONE COLORI INTERFACCIA
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 120, 215)
GREEN = (0, 200, 0)
RED = (255, 0, 0)

# INIZIALIZZAZIONE PYGAME E INTERFACCIA
pygame.init()
screen = pygame.display.set_mode((1000, 800))
pygame.display.set_caption("MotoGP Planner Dashboard")
font = pygame.font.SysFont(None, 28)





num_moto = 1
azioni_selezionate = {1: set()}     # dizionario con azioni selezionate per ogni moto
piano_generato = []                 # lista delle azioni del piano generato
simulazione_in_corso = False        # flag per la barra di progresso



def render_text(text, x, y, color=BLACK):
    #Renderizza testo sullo schermo
 
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

def carica_problem(n):
    #Carica il file del problema PDDL per n moto
    
    with open(PROBLEM_FILES[n], 'r') as f:
        return f.read()

def scrivi_problem_file(n, azioni_dict):
    #Genera il file problema PDDL temporaneo
    
    template = carica_problem(n)
    goal_lines = []
    init_lines = []

    for i in range(1, n+1):
        nome_moto = f"moto{i}"
        azioni = azioni_dict[i]

        if {"benzina", "assetto", "elettronica"} <= azioni:
            goal_lines.append(f"    (tested {nome_moto})")
        else:
            if "benzina" in azioni:
                goal_lines.append(f"    (benzina-ok {nome_moto})")
            if "assetto" in azioni:
                goal_lines.append(f"    (assetto-ok {nome_moto})")
            if "elettronica" in azioni:
                goal_lines.append(f"    (elettronica-ok {nome_moto})")

    final = template.replace(";; Le azioni richieste verranno aggiunte dinamicamente",
                              "\n".join(goal_lines))
    final = final.replace(";; inizializzazioni dinamiche", "")
    with open(TEMP_PROBLEM_FILE, 'w') as f:
        f.write(final)



def chiama_enhsp():
    #Esegue il planner ENHSP e processa il risultato

    
    
    global piano_generato
    try:
        result = subprocess.run([
            "java", "-jar", ENHSP_JAR,
            "-o", DOMAIN_FILE,
            "-f", TEMP_PROBLEM_FILE
        ], capture_output=True, text=True, timeout=15)
        print("=== Output da ENHSP ===")
        print(result.stdout)
        print("=== Errori da ENHSP ===")
        print(result.stderr)
        print("=======================")
        #estraggo dall’output del planner ENHSP (contenuto in result.stdout)
        piano_generato = [line.strip() for line in result.stdout.splitlines() if "(" in line and ")" in line]
        if not piano_generato:
            # Nessuna linea di piano trovata
            if result.stderr.strip():
                # Se c'è un messaggio di errore, mostra l'ultimo
                err_line = result.stderr.strip().splitlines()[-1]
                piano_generato = [f"Errore: {err_line}"]
            else:
                piano_generato = ["Errore: Nessun piano trovato."]    #Messaggio di errore se il planner fallisce
    except Exception as e:
        piano_generato = [f"Errore: {e}"]

def barra_progresso():

    for i, azione in enumerate(piano_generato):
        screen.fill(WHITE)
        render_text("Esecuzione del piano:", 20, 20)
        render_text(azione, 20, 60)
        pygame.draw.rect(screen, BLACK, (20, 100, 760, 30), 2)
        pygame.draw.rect(screen, GREEN, (22, 102, int((i+1)/len(piano_generato)*756), 26))
        pygame.display.flip()
        time.sleep(1.5)

def draw():
    """Disegna l'interfaccia grafica
    Mostra:
    - Selezione numero moto
    - Checkbox azioni per ogni moto
    - Pulsante generazione piano
    - Risultato del piano generato
    - Moto da testare (se tutte e 3 le azioni selezionate)
    """
    screen.fill(WHITE)
    render_text("Seleziona numero di moto:", 20, 20)
    for i in range(1, 4):
        color = BLUE if i == num_moto else BLACK
        render_text(f"[{i}]", 260 + i*40, 20, color)
    y_base = 80
    for i in range(1, num_moto+1):
        render_text(f"Moto {i}:", 20, y_base)
        for j, azione in enumerate(AZIONI):
            check = "[X]" if azione in azioni_selezionate.get(i, set()) else "[ ]"
            color = GREEN if azione in azioni_selezionate.get(i, set()) else BLACK
            render_text(f"{check} {azione}", 120 + j*200, y_base, color)
        y_base += 40
    render_text("[G] Genera Piano", 20, y_base + 20, BLUE)
    if piano_generato:
        if piano_generato[0].startswith("Errore"):
            for idx, line in enumerate(piano_generato):
                render_text(line, 20, y_base + 60 + idx*25, RED)
        else:
            render_text("Piano generato:", 20, y_base + 60)
            for idx, az in enumerate(piano_generato):
                render_text(az, 40, y_base + 90 + idx*25)
    if piano_generato and not piano_generato[0].startswith("Errore"):
        moto_test = []
        moto_pronte = []
        for i in range(1, num_moto+1):
            azioni = azioni_selezionate[i]
            if {"benzina", "assetto", "elettronica"} <= azioni:
                moto_test.append(f"moto{i}")
            elif azioni:  # Se ha almeno un'azione ma non tutte e 3
                moto_pronte.append(f"moto{i}")

        # scrivo risultati in una colonna a destra
        base_x = 600  # Posizione orizzontale a destra
        base_y = 200   # Inizio alto

        if moto_test:
            render_text("Moto testate:", base_x, base_y, BLUE)
            base_y += 30
            for m in moto_test:
                render_text(m, base_x + 20, base_y, BLACK)
                base_y += 25

        if moto_pronte:
            base_y += 20  # Spazio tra le due sezioni
            render_text("Moto pronte:", base_x, base_y, GREEN)
            base_y += 30
            for m in moto_pronte:
                render_text(m, base_x + 20, base_y, BLACK)
                base_y += 25



    pygame.display.flip()

"""
LOOP PRINCIPALE
Gestisce:
- Eventi tastiera (selezione moto, generazione piano)
- Eventi mouse (selezione azioni)
- Visualizzazione barra progresso
"""
running = True
while running:
    draw()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                num_moto = int(event.unicode)
                for i in range(1, num_moto+1):
                    azioni_selezionate.setdefault(i, set())
            elif event.key == pygame.K_g:
                # Controlla se è stata selezionata almeno un'azione
                if not any(azioni_selezionate[i] for i in range(1, num_moto+1)):
                    piano_generato = ["Nessuna azione selezionata."]
                else:
                    scrivi_problem_file(num_moto, azioni_selezionate)
                    chiama_enhsp()
                    simulazione_in_corso = True
            elif event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            y_base = 80
            for i in range(1, num_moto+1):
                for j, azione in enumerate(AZIONI):
                    x, y = 120 + j*200, y_base
                    if x < mx < x+200 and y < my < y+30:
                        if azione in azioni_selezionate[i]:
                            azioni_selezionate[i].remove(azione)
                        else:
                            azioni_selezionate[i].add(azione)
                y_base += 40
            # Rileva click sul pulsante [G] Genera Piano
            gen_y = y_base + 20
            if 20 < mx < 20+170 and gen_y < my < gen_y + 30:
                if not any(azioni_selezionate[i] for i in range(1, num_moto+1)):
                    piano_generato = ["Nessuna azione selezionata."]
                else:
                    scrivi_problem_file(num_moto, azioni_selezionate)
                    chiama_enhsp()
                    simulazione_in_corso = True
    if simulazione_in_corso:
        barra_progresso()
        simulazione_in_corso = False

pygame.quit()
