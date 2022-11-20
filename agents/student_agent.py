# Student agent: Add your own agent here
import numpy as np
from agents.agent import Agent
from store import register_agent
import sys


@register_agent("student_agent")
class StudentAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(StudentAgent, self).__init__()
        self.name = "StudentAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }

    def step(self, chess_board, my_pos, adv_pos, max_step):
        """
        Implement the step function of your agent here.
        You can use the following variables to access the chess board:
        - chess_board: a numpy array of shape (x_max, y_max, 4)
        - my_pos: a tuple of (x, y)
        - adv_pos: a tuple of (x, y)
        - max_step: an integer

        You should return a tuple of ((x, y), dir),
        where (x, y) is the next position of your agent and dir is the direction of the wall
        you want to put on.

        Please check the sample implementation in agents/random_agent.py or agents/human_agent.py for more details.
        """

        # Code here

        # Gets the Y element from my_pos as that is the left and right variable
        max_left = my_pos[1] - max_step
        max_right = my_pos[1] + max_step
        max_up = my_pos[1] - max_step
        max_down = my_pos[0] + max_step

        # Get the size of the grid then subtract one as starting from 0
        grid_size = len(chess_board) - 1

        if max_up < 0:
            max_up = 0

        if max_down > grid_size:
            max_down = grid_size

        if max_left < 0:
            max_left = 0

        if max_right > grid_size:
            max_right = grid_size

        y_pos = np.random.randint(max_left, max_right)

        x_pos = max_step - y_pos

        new_pos = (x_pos, y_pos)

        my_pos = new_pos

        # Randomly select int for direction
        dir = np.random.randint(0, 4)

        # dummy return
        return my_pos, dir
