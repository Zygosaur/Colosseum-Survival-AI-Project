# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
import sys
import random

@register_agent("student_agent")
class StudentAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(StudentAgent, self).__init__()
        self.name = "StudentAgent"
        self.autoplay = True
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
        my_pos = self.get_position(chess_board, my_pos, adv_pos, max_step)
        dir = self.get_direction(chess_board, my_pos, adv_pos, max_step, my_pos)
        
        # dummy return
        return my_pos, dir
    
    def get_position(self, chess_board, my_pos, adv_pos, max_step):
        # 
        n = chess_board.shape[0]
        manhattan_dis = [[0 for r in range(n)] for c in range(n)] 
        min_dis = 9999
        position = [my_pos[0], my_pos[1]]

        for i in range(0,n):
            for j in range(0,n):
                for dir in range(4):
                    temp_pos = (i,j)
                    if self.check_valid_step(chess_board,my_pos,temp_pos,adv_pos,dir,max_step):
                        distance = self.heuristic_decisions(chess_board, temp_pos,adv_pos)
                        manhattan_dis[i][j] = distance
                        if distance < min_dis:
                            min_dis = distance
                            position[0] = i
                            position[1] = j
        return position
    
    def get_direction(self, chess_board, my_pos, adv_pos, max_step, position):
        valid_dir = []
        for dir in range(4):
            if self.check_valid_step(chess_board,my_pos,tuple(position),adv_pos,dir,max_step):
                valid_dir.append(dir)
                my_pos = tuple(position)
                break

        # Place the barrier facing the opponent
        # Randomly choose the direction of the variable if the above is unavailable
        if adv_pos[1] > position[1] and 0 in valid_dir:
            dir = 0
        elif adv_pos[0] > position[0] and 1 in valid_dir:
            dir = 1
        elif adv_pos[1] < position[1] and 2 in valid_dir:
            dir = 2
        elif adv_pos[0] > position[0] and 3 in valid_dir:
            dir = 3
        else:
            dir = random.choice(valid_dir )
        return dir

    def check_endgame(self, chess_board, my_pos, adv_pos):
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
        board_size = chess_board.shape[0]
        moves = ((-1, 0), (0, 1), (1, 0), (0, -1))

        # Union-Find
        father = dict()
        for r in range(board_size):
            for c in range(board_size):
                father[(r, c)] = (r, c)

        def find(pos):
            if father[pos] != pos:
                father[pos] = find(father[pos])
            return father[pos]

        def union(pos1, pos2):
            father[pos1] = pos2

        for r in range(board_size):
            for c in range(board_size):
                for dir, move in enumerate(
                    moves[1:3]
                ):  # Only check down and right
                    if chess_board[r, c, dir + 1]:
                        continue
                    pos_a = find((r, c))
                    pos_b = find((r + move[0], c + move[1]))
                    if pos_a != pos_b:
                        union(pos_a, pos_b)

        for r in range(board_size):
            for c in range(board_size):
                find((r, c))
        p0_r = find(tuple(my_pos))
        p1_r = find(tuple(adv_pos))
        p0_score = list(father.values()).count(p0_r)
        p1_score = list(father.values()).count(p1_r)
        if p0_r == p1_r:
            return False, p0_score, p1_score
        return True, p0_score, p1_score
    
    def check_valid_step(self, chess_board, start_pos, end_pos, adv_pos, barrier_dir, max_step):
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

        if chess_board[r, c, barrier_dir]:
            return False
        if start_pos[0] == end_pos[0] and start_pos[1] == end_pos[1]:
            return True

        # BFS
        state_queue = [(start_pos, 0)]
        visited = {tuple(start_pos)}
        is_reached = False
        while state_queue and not is_reached:
            cur_pos, cur_step = state_queue.pop(0)
            r, c = cur_pos
            if cur_step == max_step:
                break
            for dir, move in enumerate(((-1, 0), (0, 1), (1, 0), (0, -1))):
                if chess_board[r, c, dir]:
                    continue

                next_pos = (cur_pos[0]+move[0], cur_pos[1]+move[1])
                next_equals_adv = next_pos[0] == adv_pos[0] and next_pos[1] == adv_pos[1]
                next_equals_end = next_pos[0] == end_pos[0] and next_pos[1] == end_pos[1]
                if next_equals_adv or tuple(next_pos) in visited:
                    continue
                if next_equals_end:
                    is_reached = True
                    break

                visited.add(tuple(next_pos))
                state_queue.append((next_pos, cur_step + 1))

        return is_reached

    def heuristic_decisions(self, chess_board, my_pos, adv_pos):

        n = chess_board.shape[0]
        heuristic = 9999

        # Determines if the game has ended
        if self.check_endgame(chess_board, my_pos, adv_pos)[0]:
            return -9999

        # Finds the Manhattan distance between the my_pos and adv_pos
        x = abs(adv_pos[0] - my_pos[0])
        y = abs(adv_pos[0] - my_pos[1])
        heuristic = x + y

        # Checks the number of barriers around our current position
        
        barriers_around = 0
        for dir in range(4):
            if chess_board[my_pos[0],my_pos[1],dir]== True:
                barriers_around += 1

        # If there are 3 barriers around us, return 9999
        if barriers_around ==3:   
            return 9999  

        # If there are 2 barriers around us, it isn't fatal but it's not ideal
        # The heuristic would be slightly higher
        if barriers_around == 2:
            heuristic = heuristic *50
        

        return heuristic

    def get_all_steps(self, chess_board, my_pos, adv_pos, max_step):
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
        board_size = chess_board.shape[0]

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
                    border_dir.append(1)
                elif i > adv_row:
                    border_dir.append(3)
                if j < adv_col:
                    border_dir.append(0)
                elif j > adv_col:
                    border_dir.append(2)
                for dir in border_dir:
                    if self.check_valid_step(chess_board, my_pos, (i, j), adv_pos, dir, max_step):
                        steps_allowed.append(tuple([i, j, self.dir_map[dir]]))
        return steps_allowed