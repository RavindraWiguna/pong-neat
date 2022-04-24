from collections import Counter
import pygame
from pong import Game, GameInformation
import os
import neat
from neatUtils import visualize
from numpy import argmax
import time
import pickle

'''
A Class of a single Pong Game
'''
class PongGame:
    def __init__(self, window, width, height, fps) -> None:
        self.game = Game(window, width, height)
        self.FPS = fps
        # just for the sake to make the variable name shorter
        self.left_paddle = self.game.left_paddle
        self.right_paddle = self.game.right_paddle
        self.ball = self.game.ball

    def test_ai(self, net:neat.nn.FeedForwardNetwork):
        isRunning = True
        clock = pygame.time.Clock()
        while(isRunning):
            for event in pygame.event.get():
                if(event.type == pygame.QUIT):
                    isRunning = False
                    break

            # Human Movement
            keys = pygame.key.get_pressed()
            if(keys[pygame.K_UP]):
                self.game._paddle_movement_handler(True, True)
            elif(keys[pygame.K_DOWN]):
                self.game._paddle_movement_handler(True, False)

            # Computer Movement (input -> ball y, ball vel y, paddle y, paddle-ball x distance)
            comp_out = net.activate([self.ball.y, self.ball.vel[1], self.right_paddle.y, abs(self.right_paddle.x - self.ball.x)])
            comp_move = argmax(comp_out)
            if(comp_move==1):
                # move up
                self.game._paddle_movement_handler(False, True)
            elif(comp_move==2):
                self.game._paddle_movement_handler(False, False)

            # Update the game conditions
            game_info = self.game.loop()
            # print(game_info.left_score, game_info.right_score)
            # Draw the game's frame
            self.game.draw()
            pygame.display.update()
            # sleep if needed to keep game running at 60 fps
            clock.tick(self.FPS)
        
        pygame.quit()
    
    def move_ai_paddle(self, 
                       net1:neat.nn.FeedForwardNetwork, 
                       net2:neat.nn.FeedForwardNetwork, 
                       genome1:neat.DefaultGenome, genome2:neat.DefaultGenome):
        players = [(net1, genome1, self.left_paddle, True), (net2, genome2, self.right_paddle, False)]
        for net, genome, paddle, isLeft, in players:
            output = net.activate([self.ball.y, self.ball.vel[1], paddle.y, abs(paddle.x - self.ball.x)])
            comp_move = argmax(output)
            isValid = True
            if(comp_move==1):
                # move up
                isValid = self.game._paddle_movement_handler(isLeft, True)
            elif(comp_move==2):
                isValid = self.game._paddle_movement_handler(isLeft, False)

            genome.fitness -= not isValid

    def calculate_fitness(self, 
                          genome1:neat.DefaultGenome, 
                          genome2:neat.DefaultGenome, 
                          game_info:GameInformation, duration):
        score_diff = 0
        genome1.fitness += game_info.left_hits + duration + score_diff
        genome2.fitness += game_info.right_hits + duration - score_diff



    def train_ai(self, genome1, genome2, config, isDraw=False):
        isRunning = True
        max_hits = 50
        isDone = False
        # Create the neural networks
        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        net2 = neat.nn.FeedForwardNetwork.create(genome2, config)

        start_time = time.time()
        while(isRunning):
            for event in pygame.event.get():
                if(event.type == pygame.QUIT):
                    isRunning = False
                    # we dont set is done to true because it is force to close
                    break
            
            self.move_ai_paddle(net1, net2, genome1, genome2)

            # Update the game conditions
            game_info = self.game.loop()
            # print(game_info.left_score, game_info.right_score)
            # Draw the game's frame
            if(isDraw):
                self.game.draw(False)   
                pygame.display.update()
            
            if game_info.left_score == 1 or game_info.right_score == 1 or game_info.left_hits >= max_hits:
                duration = time.time() - start_time
                self.calculate_fitness(genome1, genome2,game_info, duration)
                isDone = True
                isRunning = False
                # believe in no break _/|\_
        
        # pygame.quit()
        return isDone


def eval_genomes(genomes, config):
    print("training genomes")
    """
    Run each genome against eachother one time to determine the fitness.
    """
    dict_fitness = Counter() # default value is 0 if never assigned
    width, height = 640, 480
    win = pygame.display.set_mode((width, height))
    for i, (genome_id1, genome1) in enumerate(genomes):
        # print the percentages of this net training progress
        print(round(i/len(genomes) * 100), end=" ")
        genome1.fitness = dict_fitness[genome_id1]
        # loop for genome in the index i+1 till end 
        # (don't worry it wont cause index error cause genomes[i+1: ] will always return a list, either with some items or none)
        for genome_id2, genome2 in genomes[i+1:]:
            genome2.fitness = dict_fitness[genome_id2]
            pong = PongGame(win, width, height, 240)
            peaceful_exit = pong.train_ai(genome1, genome2, config, False)
            dict_fitness[genome_id1] = genome1.fitness
            dict_fitness[genome_id2] = genome2.fitness
            if(not peaceful_exit):
                quit()
        
        print(f'current fitness for {genome_id1}: {genome1.fitness}')
            

def run(config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 300 generations.
    winner = p.run(eval_genomes, 300)

    # Save the winner
    with open("best_genome.pickle", "wb") as saver:    
        pickle.dump(winner, saver, pickle.HIGHEST_PROTOCOL)
        print("WINNER IS SAVED on best_genome.pickle")
    
    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))
    
    # Show output of the most fit genome against training data.
    # print('\nOutput:')
    # winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

    # node_names = {-1:'A', -2: 'B', 0:'A XOR B'}
    # visualize.draw_net(config, winner, True, node_names=node_names)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)

    # To load from last check point (in case the training is stopped syre)
    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
    # p.run(eval_genomes, 10)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, './neatUtils/config-feedforward')
    # run(config_path)
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_path)

    winner_pickle = open(os.path.join(local_dir, "best_genome.pickle"), "rb")
    winner = pickle.load(winner_pickle)
    width, height = 640, 480
    win = pygame.display.set_mode((width, height))
    pong = PongGame(win, width, height, 60)
    
    net = neat.nn.FeedForwardNetwork.create(winner, config)
    pong.test_ai(net)


