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

        # dummy return
        return my_pos, dir

    def get_steps(self, chess_board, my_pos, adv_pos, max_steps):
        """
        Find all steps the agent can reach.

        Parameters
        ----------
        my_pos: tuple
            Position the agent starts at
        adv_pos: tuple
            Position the agent will move too
        """
        # Size of the board, assume always square
        board_size = len(chess_board[0])

        # List of valid positions to return
        steps_allowed = []

        # Temporary positions
        adv_row = adv_pos[0]
        adv_col = adv_pos[1]
        
        # Iterate through rows
        for i in range(board_size):
            # Iterate through columns
            for j in range(board_size):
                # List of directions where a barrier could be valid
                border_dir = []
                if i < adv_row:
                    border_dir.append("r")
                elif i > adv_row:
                    border_dir.append("l")
                if j < adv_col:
                    border_dir.append("u")
                elif j > adv_col:
                    border_dir.append("d")
                for dir in border_dir:
                    if self.check_valid_step(chess_board, my_pos, (i, j), adv_pos, dir, max_steps):
                        steps_allowed.append(tuple([i, j, self.dir_map[dir]]))
        return steps_allowed
