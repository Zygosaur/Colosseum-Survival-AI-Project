# Student agent: Add your own agent here
import numpy as np
from agents.agent import Agent
from store import register_agent
import sys
import logging


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

    def check_endgame(self):
        """
        Check if the game ends and compute the current score of the agents.

        Returns
        -------
        is_endgame : bool
            Whether the game ends.
        player_1_score : int
            The score of player 1.
        player_2_score : int
            The score of player 2.
        """
        # Union-Find
        father = dict()
        for r in range(self.board_size):
            for c in range(self.board_size):
                father[(r, c)] = (r, c)

        def find(pos):
            if father[pos] != pos:
                father[pos] = find(father[pos])
            return father[pos]

        def union(pos1, pos2):
            father[pos1] = pos2

        for r in range(self.board_size):
            for c in range(self.board_size):
                for dir, move in enumerate(
                    self.moves[1:3]
                ):  # Only check down and right
                    if self.chess_board[r, c, dir + 1]:
                        continue
                    pos_a = find((r, c))
                    pos_b = find((r + move[0], c + move[1]))
                    if pos_a != pos_b:
                        union(pos_a, pos_b)

        for r in range(self.board_size):
            for c in range(self.board_size):
                find((r, c))
        p0_r = find(tuple(self.p0_pos))
        p1_r = find(tuple(self.p1_pos))
        p0_score = list(father.values()).count(p0_r)
        p1_score = list(father.values()).count(p1_r)
        if p0_r == p1_r:
            return False, p0_score, p1_score
        player_win = None
        win_blocks = -1
        if p0_score > p1_score:
            player_win = 0
            win_blocks = p0_score
        elif p0_score < p1_score:
            player_win = 1
            win_blocks = p1_score
        else:
            player_win = -1  # Tie
        if player_win >= 0:
            logging.info(
                f"Game ends! Player {self.player_names[player_win]} wins having control over {win_blocks} blocks!"
            )
        else:
            logging.info("Game ends! It is a Tie!")
        return True, p0_score, p1_score
    
    def check_valid_step(self, start_pos, end_pos, barrier_dir):
        """
        Check if the step the agent takes is valid (reachable and within max steps).

        Parameters
        ----------
        start_pos : tuple
            The start position of the agent.
        end_pos : np.ndarray
            The end position of the agent.
        barrier_dir : int
            The direction of the barrier.
        """
        # Endpoint already has barrier or is boarder
        r, c = end_pos
        if self.chess_board[r, c, barrier_dir]:
            return False
        if np.array_equal(start_pos, end_pos):
            return True

        # Get position of the adversary
        adv_pos = self.p0_pos if self.turn else self.p1_pos

        # BFS
        state_queue = [(start_pos, 0)]
        visited = {tuple(start_pos)}
        is_reached = False
        while state_queue and not is_reached:
            cur_pos, cur_step = state_queue.pop(0)
            r, c = cur_pos
            if cur_step == self.max_step:
                break
            for dir, move in enumerate(self.moves):
                if self.chess_board[r, c, dir]:
                    continue

                next_pos = cur_pos + move
                if np.array_equal(next_pos, adv_pos) or tuple(next_pos) in visited:
                    continue
                if np.array_equal(next_pos, end_pos):
                    is_reached = True
                    break

                visited.add(tuple(next_pos))
                state_queue.append((next_pos, cur_step + 1))

        return is_reached

    def heuristic_decisions(chess_board, my_pos, adv_pos):

        # Determines if the game has ended
        if self.check_endgame(chess_board, my_pos, adv_pos)[0] == True:
            return -10000
        
        # Finds the distance between the my_pos and adv_pos
        x = abs(adv_pos[0] - my_pos[0])
        y = abs(adv_pos[0] - my_pos[1])
        heuristic = x + y

        # Checks the number of barriers around our current position
        # If a box is forming around us, return 10000
        barriers_around = 0
        for dir in range(4):
            if chess_board[my_pos[0],my_pos[1],dir]:
                barriers_around += 1
        if barriers_around >=2:   
            return 10000       
        

        return heuristic

    def get_steps(self, chess_board, my_pos, adv_pos, max_steps):
        """
        Find all steps the agent can reach.

        Parameters
        ----------
        my_pos : tuple
            Position the agent starts at
        adv_pos : tuple
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
