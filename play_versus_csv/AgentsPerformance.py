import random
import numpy as np
from PongAI import PongAI
import os
import csv
from operator import itemgetter

# Hiperparámetros
LR = 0.07
NUM_EPISODES = 10_000_000
DISCOUNT_RATE = 0
MAX_EXPLORATION_RATE = 1
MIN_EXPLORATION_RATE = 0.0002
EXPLORATION_DECAY_RATE = 0.0005

# Si deseas o no tener elementos gráficos del juego (más lento si se muestran)
VISUALIZATION = False

class Agent:
    # Esta clase posee al agente y define sus comportamientos.

    def __init__(self, q_table_path=None):
        # Creamos la q_table y la inicializamos en 0.
        self.proximity_edit = False
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

        if q_table_path:
            self.proximity_edit = self.load_q_tables(q_table_path)
            print("Proximity edit:", self.proximity_edit)

        # Inicializamos los juegos realizados por el agente en 0.
        self.n_games = 0
        
        # Inicializamos el exploration rate.
        self.EXPLORATION_RATE = MAX_EXPLORATION_RATE

    def get_state(self, game):
        # Este método consulta al juego por el estado del agente y lo retorna como una tupla.
        state = []

        # Obtenemos la velocidad en y de la pelota
        velocity = int(round(game.ball.y_vel, 0))
        state.append(velocity)

        # Obtenemos el cuadrante de la pelota
        proximity = 5 - int(round(game.ball.x / game.MAX_X) * 5)
        if self.proximity_edit:
            proximity = 5 - int(round((game.ball.x / game.MAX_X) * 5))
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

    def load_q_tables(self, q_table_path):
        # Este método carga la q_table desde un csv.
        proximity_edit = False
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

    def get_action(self, state):
        # Si los valores para este estado siguen en 0, tomamos una acción random para no sesgar al agente.
        if not np.any(self.q_table[self.states_index[state],:]): 
            move = random.randint(0, 2)
        else: 
            move = np.argmax(self.q_table[self.states_index[state],:])
        return move

def test(agent_path=None):
    # Esta función es la encargada de entrenar al agente.

    # Las siguientes variables nos permitirán llevar registro del desempeño del agente.
    plot_scores = []
    plot_mean_scores = []
    mean_score = 0
    total_score = 0
    record = 0
    period_steps = 0
    period_score = 0

    # Instanciamos al agente o lo cargamos desde un pickle.
    agent = Agent(agent_path)
    # Instanciamos el juego. El bool 'vis' define si queremos visualizar el juego o no.
    # Visualizarlo lo hace mucho más lento.
    game = PongAI(vis = VISUALIZATION)

    # Inicializamos los pasos del agente en 0.
    steps = 0
    force_break = False

    while True:
        # Obtenemos el estado actual.
        state = agent.get_state(game)
        # Generamos la acción correspondiente al estado actual.
        move = agent.get_action(state)
        # Ejecutamos la acción.
        reward, done, score = game.play_step(move)
        
        # En caso de terminar el juego.
        if done or force_break:
            force_break = False
            # Reiniciamos el juego.
            game.reset()
            # Actualizamos los juegos jugados por el agente.
            agent.n_games += 1

            # Imprimimos el desempeño del agente cada 100 juegos.
            if agent.n_games % 20 == 0:
                # La siguiente línea guarda la QTable en un archivo (para poder ser accedida posteriormente)
                # np.save("q_table.npy", agent.q_table)

                # Información relevante sobre los últimos 100 juegos
                print('Game', agent.n_games, 'Mean Score', period_score/20, 'Record:', record, "EXP_RATE:", agent.EXPLORATION_RATE, "STEPS:", period_steps/20)
                record = 0
                # period_score = 0
                period_steps = 0

                return period_score/20
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
            
            # En caso de alcanzar el máximo de juegos cerramos el loop. 
            if agent.n_games == NUM_EPISODES:
                break

        else:
            steps += 1
            if steps > 100_000:
              force_break = True


def evaluate_agents(agents_path=None, output_path=None):
    # loop through all the csv files in the agents_path directory
    # if agents_path is None, use the default path
    agents_preformance = []

    if agents_path is None:
        print("No agents_path specified")
        return
    # if output_path is None, use the default path
    if output_path is None:
        output_path = "agents_preformance.csv"
    # get a list of all the files in the directory
    files = os.listdir(agents_path)
    # loop through each file
    for file in files:
        # if the file is a csv, evaluate the agent
        if file.endswith(".csv"):
            # get the name of the agent
            agent_name = file.split(".")[0]
            # remove "q_table - " from the file name
            agent_name = agent_name.split("- ")[1]
            if agent_name == "BrunoFarfan":
                continue
            # get the path to the agent's q_table
            agent_path = os.path.join(agents_path, file)
            print(agent_name)
            performance = test(agent_path)
            agents_preformance.append([agent_name, performance])
    # write the agents preformance to a csv file

    agents_preformance = sorted(agents_preformance, key=itemgetter(1))
    with open(output_path, "w") as f:
        writer = csv.writer(f)
        writer.writerows(agents_preformance)


if __name__ == '__main__':
    # test(agent_path="data/qtables/q_table - CarloGauss33.csv")
    evaluate_agents(agents_path="data/qtables", output_path="agents_preformance_2.csv")