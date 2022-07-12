import random
import numpy as np
from PongAI import PongAI

class Agent:
    # Esta clase posee al agente y define sus comportamientos.

    def __init__(self):
        # Creamos la q_table y la inicializamos en 0.

        self.states_index = dict() # Diccionario con el estado del agente como key
                                   # y su indice en la q_table como value.
        index = 0
        for velocity in range(-5,6):
            for proximity in range(6):
                for ball_pos_up in range(4):
                    for ball_pos_down in range(4):
                        for total_bounces in range(3):
                            self.states_index[tuple([velocity, proximity, ball_pos_up, ball_pos_down, total_bounces])] = index
                            index += 1

        # Cargamos la q-table
        self.q_table = np.load("q_table.npy")

        # Inicializamos los juegos realizados por el agente en 0.
        self.n_games = 0

    def get_state(self, game):
        # Este método consulta al juego por el estado del agente y lo retorna como una tupla.
        state = []

        # Obtenemos la velocidad en y de la pelota
        velocity = int(round(game.ball.y_vel, 0))
        state.append(velocity)

        # Obtenemos el cuadrante de la pelota
        proximity = 5 - int(round(game.ball.x / game.MAX_X * 5))
        state.append(proximity)

        # Revisamos la posición de la pelota respecto al extremo superior del agente  
        if game.ball.y < (game.right_paddle.y):
            if game.right_paddle.y - game.ball.y > game.right_paddle.height:
                up_state = 0
            else:
                up_state = 1
        else:
            if game.ball.y - game.right_paddle.y < game.right_paddle.height:
                up_state = 2
            else:
                up_state = 3
        state.append(up_state)

        # Revisamos la posición de la pelota respecto al extremo inferior del agente 
        if game.ball.y < (game.right_paddle.y + game.right_paddle.height):
            if game.right_paddle.y + game.right_paddle.height - game.ball.y > game.right_paddle.height:
                down_state = 0
            else:
                down_state = 1
        else:
            if game.ball.y - game.right_paddle.y - game.right_paddle.height < game.right_paddle.height:
                down_state = 2
            else:
                down_state = 3
        state.append(down_state)

        # Número de botes contra la pared que ha dado la pelota
        bounces = game.ball.bounces
        state.append(bounces)

        return tuple(state)

    def get_action(self, state):
        # Este método recibe una estado del agente y retorna una
        # tupla con el indice de la acción correspondiente y una lista que la
        # representa.

        move = 0
        if not np.any(self.q_table[self.states_index[state],:]): 
            move = random.randint(0, 2)
        else: 
            move = np.argmax(self.q_table[self.states_index[state],:])
        return move

def play():
    # Esta función es la encargada de entrenar al agente.

    # Instanciamos al agente o lo cargamos desde un pickle.
    agent = Agent()
    
    # Instanciamos el juego. El bool 'vis' define si queremos visualizar el juego o no.
    # Visualizarlo lo hace mucho más lento.
    game = PongAI(vis=True)

    while True:
        # Obtenemos el estado actual.
        state = agent.get_state(game)

        # Generamos la acción correspondiente al estado actual.
        move = agent.get_action(state)
        
        # Ejecutamos la acción.
        reward, done, score = game.play_step(move)
        
        if done:
            # En caso de terminar el juego.

            # Reiniciamos el juego.
            # game.reset()
            # Actualizamos los juegos jugados por el agente.
            agent.n_games += 1

if __name__ == '__main__':
    play()