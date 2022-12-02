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

    def heuristicsDecisions(chessboard, my_pos, adv_pos):
        heuristic=0
        return heuristic

    def get_steps(self, chess_board, my_pos, adv_pos, max_steps):
        """
        Find all steps the agent can reach.

        Parameters
        ----------
        my_pos : tuple
            Position of the agent
        adv_pos : tuple
            Position of the adversary
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

    def mini_max(self, board, my_pos, adv_pos, depth, max_depth, max_reached, max_step, alpha, beta, score_lim):
        """
        Implimentation of minimax

        Paramaters
        ----------
        my_pos : tuple
            Position of the agent
        adv_pos : tuple
            Position of the adversary
        depth : int
            Depth
        max_depth : int
            Maximum depth
        max_reached : bool
            Stop from searching forever
        max_step : int
            Maximum number of steps that can be moved
        alpha :
            Alpha for mini_max algorithm
        beta :
            Beta for mini_max algorithm
        score_lim : int
            Limit so that mini_max finishes
        """
        # The mini_max score
        score = score_lim - self.evaluate(board, my_pos, adv_pos)
        
        # Has the game been won
        end = self.check_endgame(board, my_pos, adv_pos)

        # Terminal
        if depth == max_depth:
            return score

        if end[0]:
            my_score = end[1]
            adv_score = end[2]
            if my_score > adv_score and max_reached:
                return score_lim
            elif my_score > adv_score and not max_reached:
                return -score_lim
            elif my_score < adv_score and max_reached:
                return -score_lim
            elif my_score < adv_score and not max_reached:
                return score_lim
            else:
                return 0

        if (max_reached):
            best = -score_lim

            steps = self.get_steps(board, my_pos, adv_pos, max_step)
            for step in steps:
                board[step[0], step[1], step[2]] = True

                best = max(best, self.mini_max(board, not max_reached, (step[0], step[1]), adv_pos, (depth + 1), max_depth, max_step))

                board[step[0], step[1], step[2]] = False

                # Prune
                alpha = max(alpha, best)
                if beta <= alpha:
                    break

            return best

        else:
            best = score_lim

            steps = self.get_steps(board, my_pos, adv_pos, max_step)
            for step in steps:
                board[step[0], step[1], step[2]] = True

                best = min(best, self.minimax(board, not max_reached, (step[0], step[1]), adv_pos, depth+1,
                                              max_depth, max_step, alpha, beta))

                board[step[0], step[1], step[2]] = False

                # Prune
                beta = min(beta, best)
                if beta <= alpha:
                    break

            return best