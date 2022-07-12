import random
import numpy as np
from PongAI_versus import PongAI

VISUALIZATION = True

# Lee dos archivos .npy para hacer jugar a dos jugadores distintos

l_qtable_path = None
r_qtable_path = None

class Agent:
    # Esta clase posee al agente y define sus comportamientos.

    def __init__(self, path_to_qtable = None):
        # Creamos la q_table y la inicializamos en 0.

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

        # Inicializamos la q_table.
        if path_to_qtable is None:
            self.q_table = np.load("q_table.npy")
        else:
            self.q_table = np.load(path_to_qtable)
        
        # Inicializamos los juegos realizados por el agente en 0.
        self.n_games = 0

    def get_state(self):
        # Este método consulta al juego por el estado del agente y lo retorna como una tupla.
        pass

    def get_action(self, state):
        # Este método recibe una estado del agente y retorna una
        # tupla con el indice de la acción correspondiente y una lista que la
        # representa.

        move = 0
        if not np.any(self.q_table[self.states_index[state],:]): 
            move = random.randint(0, 2)
        else: 
            # print(self.q_table[self.states_index[state],:])
            move = np.argmax(self.q_table[self.states_index[state],:])
        
        return move

class AgentL(Agent):
    def __init__(self, path_to_qtable = None):
        super().__init__(path_to_qtable)
    
    def get_state(self, game):
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

        return tuple(state)

class AgentR(Agent):
    def __init__(self, path_to_qtable = None):
        super().__init__(path_to_qtable)

    def get_state(self, game):
        state = []

        # Obtenemos la velocidad en y de la pelota
        velocity = int(round(game.ball.y_vel, 0))
        state.append(velocity)

        # Obtenemos el cuadrante de la pelota
        proximity = int((game.ball.x / game.MAX_X) * 5)
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

        return tuple(state)

def play():
    # Esta función es la encargada de entrenar al agente.

    # Las siguientes variables nos permitirán llevar registro del
    # desempeño del agente.
    score_l = 0
    score_r = 0

    total_games = 0

    left_wins = 0
    right_wins = 0

    # Instanciamos al agente o lo cargamos desde un pickle.
    agent_l = AgentL(l_qtable_path)
    agent_r = AgentR(r_qtable_path)

    # Instanciamos el juego. El bool 'vis' define si queremos visualizar el juego o no.
    # Visualizarlo lo hace mucho más lento.
    game = PongAI(vis= VISUALIZATION)

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
