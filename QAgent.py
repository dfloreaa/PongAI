import random
import numpy as np
from PongAI_follow_ball import PongAI
import pickle

# Hiperparámetros
LR = 0.07
NUM_EPISODES = 10_000_000
DISCOUNT_RATE = 0
MAX_EXPLORATION_RATE = 1
MIN_EXPLORATION_RATE = 0.0002
EXPLORATION_DECAY_RATE = 0.0005

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

        # Inicializamos la q_table en 0.
        self.q_table = np.zeros((index, 3))
        self.q_table[:, 1] = 1

        # Inicializamos los juegos realizados por el agente en 0.
        self.n_games = 0
        
        # Inicializamos el exploration rate.
        self.EXPLORATION_RATE = MIN_EXPLORATION_RATE + (MAX_EXPLORATION_RATE - MIN_EXPLORATION_RATE) * np.exp(-EXPLORATION_DECAY_RATE*self.n_games)

    def get_state(self, game):
        # Este método consulta al juego por el estado del agente
        # y lo retorna como una tupla.
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

        bounces = game.ball.bounces
        state.append(bounces)

        return tuple(state)

    def get_action(self, state):
        # Este método recibe una estado del agente y retorna una
        # tupla con el indice de la acción correspondiente y una lista que la
        # representa.

        move = 0
        if random.uniform(0, 1) < self.EXPLORATION_RATE: # Exploramos
            move = random.randint(0, 2)
        else: # Explotamos
            # Si los valores para este estado siguen en 0, tomamos una acción random para no sesgar al agente.
            if not np.any(self.q_table[self.states_index[state],:]): 
                move = random.randint(0, 2)
            else: 
                move = np.argmax(self.q_table[self.states_index[state],:])
        return move

def train():
    # Esta función es la encargada de entrenar al agente.

    # Las siguientes variables nos permitirán llevar registro del
    # desempeño del agente.
    plot_scores = []
    plot_mean_scores = []
    mean_score = 0
    total_score = 0
    record = 0
    period_steps = 0
    period_score = 0

    # Instanciamos al agente o lo cargamos desde un pickle.
    agent = Agent()
    # agent = pickle.load(open("model/agent_6.p", "rb"))
    # Instanciamos el juego. El bool 'vis' define si queremos visualizar el juego o no.
    # Visualizarlo lo hace mucho más lento.
    game = PongAI(vis=False)
    # Inicializamos los pasos del agente en 0.
    steps = 0

    while True:
        # Obtenemos el estado actual.
        state = agent.get_state(game)
        # Generamos la acción correspondiente al estado actual.
        move = agent.get_action(state)
        # Ejecutamos la acción.
        reward, done, score = game.play_step(move)
        # Obtenemos el nuevo estado.
        state_new = agent.get_state(game)
        # Actualizamos la q-table.
        agent.q_table[agent.states_index[state], move] = agent.q_table[agent.states_index[state], move] * (1 - LR) + \
            LR * (reward + DISCOUNT_RATE * np.max(agent.q_table[agent.states_index[state_new],:]))

        
        if done:
            # En caso de terminar el juego.

            # Actualizamos el exploration rate.
            agent.EXPLORATION_RATE = MIN_EXPLORATION_RATE + \
                (MAX_EXPLORATION_RATE - MIN_EXPLORATION_RATE) * np.exp(-EXPLORATION_DECAY_RATE*agent.n_games)
            # Reiniciamos el juego.
            game.reset()
            # Actualizamos los juegos jugados por el agente.
            agent.n_games += 1
            # Imprimimos el desempeño del agente cada 100 juegos.
            if agent.n_games % 100 == 0:
                # pickle.dump(agent.q_table, open("QTable.p", "wb"))
                np.save("q_table.npy", agent.q_table)
                print('Game', agent.n_games, 'Mean Score', period_score/100, 'Record:', record, "EXP_RATE:", agent.EXPLORATION_RATE, "STEPS:", period_steps/100)
                # pickle.dump([plot_scores, plot_mean_scores], open("scores.p", "wb"))
                record = 0
                period_score = 0
                period_steps = 0
            # Actualizamos el record del agente.
            if score > record:
                record = score
            
            # Actualizamos nuestros indicadores.
            period_steps += steps
            period_score += score
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            steps = 0
            # Descomentar la linea de abajo en caso de querer ver gráficos en vivo.
            # plot(plot_scores, plot_mean_scores)
            
            # En caso de alcanzar el máximo de juegos cerramos el loop. 
            if agent.n_games == NUM_EPISODES:
                break
        else:
            steps += 1
                


if __name__ == '__main__':
    train()