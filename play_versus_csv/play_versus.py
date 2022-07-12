import random
import numpy as np
from PongAI_versus import PongAI

VISUALIZATION = True

# RECIBE UN ARCHIVO CSV DE 3168 FILAS CON CONFIGURACIÓN DE COLUMNAS
# VELOCIDAD | PROXIMIDAD | BALL_POS_LEFT | BALL_POS_RIGHT | TOTAL_BOUNCES | QValue Up | QValue Stay | QValue Down
# Y el nombre del jugador (ej. jugador.csv)
# Ingresar el nombre del jugador a cada lado

class AgentL:
    # Esta clase posee al agente y define sus comportamientos.

    def __init__(self, q_table_user = None):
        # Creamos la q_table y la inicializamos en 0.
        self.proximity_edit = False
        self.states_index = dict() # Diccionario con el estado del agente como key
                                   # y su indice en la q_table como value.
        index = 0
        for velocity in range(-5,6):
            for proximity in range(6):
                for ball_pos_left in range(4):
                    for ball_pos_right in range(4):
                        for total_bounces in range(3):
                            self.states_index[tuple([velocity, proximity, ball_pos_left, ball_pos_right, total_bounces])] = index
                            index += 1 
        # Inicializamos la q_table en 0.
        self.q_table = np.zeros((index, 3))
        self.q_table[:, 1] = 1

        if q_table_user:
            self.proximity_edit = self.load_q_tables(q_table_user)
        
        # print(self.q_table)
        # Inicializamos los juegos realizados por el agente en 0.
        self.n_games = 0

    def get_state(self, game):
        # Este método consulta al juego por el estado del agente
        # y lo retorna como una tupla.
        state = []

        # Obtenemos la velocidad en y de la pelota
        velocity = int(round(game.ball.y_vel, 0))
        state.append(velocity)

        # Obtenemos el cuadrante de la pelota
        proximity = 5 - int(round((game.MAX_X - game.ball.x) / game.MAX_X) * 5)
        if self.proximity_edit:
            proximity = 5 - int(round(((game.MAX_X - game.ball.x) / game.MAX_X) * 5))
        state.append(proximity)

        # Revisamos si la pelota está a la izquierda del agente  
        if game.ball.y < (game.left_paddle.y):
            if game.left_paddle.y - game.ball.y > game.left_paddle.height:
                ref_from_top = 0
            else:
                ref_from_top = 1
        else:
            if game.ball.y - game.left_paddle.y < game.left_paddle.height:
                ref_from_top = 2
            else:
                ref_from_top = 3
        state.append(ref_from_top)

        # Revisamos si la pelota está a la izquierda del agente  
        if game.ball.y < (game.left_paddle.y + game.left_paddle.height):
            if game.left_paddle.y + game.left_paddle.height - game.ball.y > game.left_paddle.height:
                ref_from_bot = 0
            else:
                ref_from_bot = 1
        else:
            if game.ball.y - game.left_paddle.y - game.left_paddle.height < game.left_paddle.height:
                ref_from_bot = 2
            else:
                ref_from_bot = 3
        state.append(ref_from_bot)

        bounces = game.ball.bounces
        state.append(bounces)

        # print(state)

        return tuple(state)

    def get_action(self, state):
        # Si los valores para este estado siguen en 0, tomamos una acción random para no sesgar al agente.
        if not np.any(self.q_table[self.states_index[state],:]): 
            move = random.randint(0, 2)
        else: 
            move = np.argmax(self.q_table[self.states_index[state],:])
        return move
    
    def load_q_tables(self, q_table_user):
        # Este método carga la q_table desde un csv.
        proximity_edit = False
        q_table_path = f"data/qtables/q_table - {q_table_user}.csv"
        q_table = np.loadtxt(q_table_path, delimiter=',')
        proximities = q_table[(q_table[:, 1] > 0) & (q_table[:, 1] < 5),:]
        if np.count_nonzero(proximities[:,5:]) > 0:
            proximity_edit = True
        for i in range(len(q_table)):
            state = tuple(q_table[i][:5].astype(int))
            q_values = q_table[i][5:9]
            # print(q_table[i])
            # print("state:", state)
            # print("q_values:", q_values)
            self.q_table[self.states_index[state],:] = q_values
        return proximity_edit

class AgentR:
    # Esta clase posee al agente y define sus comportamientos.

    def __init__(self, q_table_user = None):
        # Creamos la q_table y la inicializamos en 0.
        self.proximity_edit = False
        self.states_index = dict() # Diccionario con el estado del agente como key
                                   # y su indice en la q_table como value.
        index = 0
        for velocity in range(-5,6):
            for proximity in range(6):
                for ball_pos_left in range(4):
                    for ball_pos_right in range(4):
                        for total_bounces in range(3):
                            self.states_index[tuple([velocity, proximity, ball_pos_left, ball_pos_right, total_bounces])] = index
                            index += 1

        # Inicializamos la q_table en 0.
        self.q_table = np.zeros((index, 3))
        self.q_table[:, 1] = 1

        if q_table_user:
            self.proximity_edit = self.load_q_tables(q_table_user)

        # Inicializamos los juegos realizados por el agente en 0.
        self.n_games = 0

    def get_state(self, game):
        # Este método consulta al juego por el estado del agente
        # y lo retorna como una tupla.
        state = []

        # Obtenemos la velocidad en y de la pelota
        velocity = int(round(game.ball.y_vel, 0))
        state.append(velocity)

        # Obtenemos el cuadrante de la pelota
        proximity = 5 - int(round(game.ball.x / game.MAX_X) * 5)
        if self.proximity_edit:
            proximity = 5 - int(round((game.ball.x / game.MAX_X) * 5))
            # print(proximity)
        state.append(proximity)

        # Revisamos si la pelota está a la izquierda del agente  
        if game.ball.y < (game.right_paddle.y):
            if game.right_paddle.y - game.ball.y > game.right_paddle.height:
                ref_from_top = 0
            else:
                ref_from_top = 1
        else:
            if game.ball.y - game.right_paddle.y < game.right_paddle.height:
                ref_from_top = 2
            else:
                ref_from_top = 3
        state.append(ref_from_top)

        # Revisamos si la pelota está a la izquierda del agente  
        if game.ball.y < (game.right_paddle.y + game.right_paddle.height):
            if game.right_paddle.y + game.right_paddle.height - game.ball.y > game.right_paddle.height:
                ref_from_bot = 0
            else:
                ref_from_bot = 1
        else:
            if game.ball.y - game.right_paddle.y - game.right_paddle.height < game.right_paddle.height:
                ref_from_bot = 2
            else:
                ref_from_bot = 3
        state.append(ref_from_bot)

        bounces = game.ball.bounces
        state.append(bounces)

        # print(is_left, is_right)

        return tuple(state)

    def get_action(self, state):
        # Si los valores para este estado siguen en 0, tomamos una acción random para no sesgar al agente.
        if not np.any(self.q_table[self.states_index[state],:]): 
            move = random.randint(0, 2)
        else: 
            move = np.argmax(self.q_table[self.states_index[state],:])
        return move
    
    def load_q_tables(self, q_table_user):
        # Este método carga la q_table desde un csv.
        proximity_edit = False
        q_table_path = f"data/qtables/q_table - {q_table_user}.csv"
        q_table = np.loadtxt(q_table_path, delimiter=',')
        proximities = q_table[(q_table[:, 1] > 0) & (q_table[:, 1] < 5),:]
        if np.count_nonzero(proximities[:,5:]) > 0:
            proximity_edit = True
        for i in range(len(q_table)):
            state = tuple(q_table[i][:5].astype(int))
            q_values = q_table[i][5:9]
            # print(q_table[i])
            # print("state:", state)
            # print("q_values:", q_values)
            self.q_table[self.states_index[state],:] = q_values
        return proximity_edit

def play():
    # Esta función es la encargada de entrenar al agente.

    # Las siguientes variables nos permitirán llevar registro del
    # desempeño del agente.

    score_l = 0
    score_r = 0

    total_games = 0

    left_wins = 0
    right_wins = 0

    left_username = input("Inserta el nombre del primer jugador: ")
    right_username = input("Inserta el nombre del segundo jugador: ")

    # Instanciamos al agente o lo cargamos desde un pickle.
    agent_l = AgentL(q_table_user = left_username)
    agent_r = AgentR(q_table_user = right_username)
    # agent = pickle.load(open("model/agent_6.p", "rb"))
    # Instanciamos el juego. El bool 'vis' define si queremos visualizar el juego o no.
    # Visualizarlo lo hace mucho más lento.
    game = PongAI(vis= VISUALIZATION)
    game.set_usernames(left_username, right_username)
    # Inicializamos los pasos del agente en 0.
    steps = 0

    while True:
        if not game.won:
            # Obtenemos el estado actual.
            state_l = agent_l.get_state(game)
            state_r = agent_r.get_state(game)

            # Generamos la acción correspondiente al estado actual.
            move_l = agent_l.get_action(state_l)
            move_r = agent_r.get_action(state_r)
            # Ejecutamos la acción.
            reward, done, score = game.play_step(move_l, move_r)
        
        elif not VISUALIZATION:

            total_games += 1

            if game.lwin:
                # print("left win")
                left_wins += 1
                score_l += game.left_score
            
            elif game.rwin:
                # print("right win")
                right_wins += 1
                score_r += game.right_score

            if not total_games % 100:
                print(total_games, "Partidas:", 'Victorias Izquierdas =', left_wins, 'Victorias Derechas =', right_wins, f"({score_l} - {score_r})")

            game.reset()

if __name__ == '__main__':
    play()