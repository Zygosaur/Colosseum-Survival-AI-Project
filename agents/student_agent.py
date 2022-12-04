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
        """
        Outputs the final position and direction of the next move of the agent.

        Parameters
        ----------
        chess_board : np.ndarray
            The current chess board.
        my_pos : tuple
            The position of the agent.
        adv_pos : tuple
            The position of the opponent.
        max_step : int
            The maximum step we can make.
        
        Returns
        -------
        my_pos : tuple
            The next position of the agent.
        dir : int
            The direction the barrier will be place in the next move of the agent.
        """
        # Code here
        next_pos = self.get_position(chess_board, my_pos, adv_pos, max_step)
        dir = self.get_direction(chess_board, my_pos, adv_pos, max_step, next_pos)
        my_pos = next_pos
        # dummy return
        return my_pos, dir
    
    def get_position(self, chess_board, my_pos, adv_pos, max_step):
        """
        Gets the position of the best move to make according to the heuristics.

        Parameters
        ----------
        chess_board : np.ndarray
            The current chess board.
        my_pos : tuple
            The position of the agent.
        adv_pos : tuple
            The position of the opponent.
        max_step : int
            The maximum step we can make.

        Returns
        -------
        position : tuple
            The best position.
        """
        n = chess_board.shape[0]
        heuristic = [[0 for r in range(n)] for c in range(n)] 
        best_heuristic = 9999
        position = [my_pos[0], my_pos[1]]

        #Iterates through all steps, checks if they are valid, then gives them a heuristic.
        for i in range(0,n):
            for j in range(0,n):
                for dir in range(4):
                    temp_pos = (i,j)
                    if self.check_valid_step(my_pos,temp_pos,adv_pos,chess_board,dir,max_step):
                        temp_heuristic = self.heuristic_decisions(chess_board, temp_pos,adv_pos)
                        heuristic[i][j] = temp_heuristic
                        if temp_heuristic < best_heuristic:
                            best_heuristic = temp_heuristic
                            position[0] = i
                            position[1] = j
        position = tuple(position)
        return position
    
    def get_direction(self, chess_board, my_pos, adv_pos, max_step,position):
        """
        Gets the best direction to place the barrier in the next move.

        Parameters
        ----------
        chess_board : np.adarray
            The current chess board.
        my_pos : tuple
            The position of the agent.
        adv_pos : tuple
            The position of the opponent.
        max_step : int
            The maximum step we can make.
        position : tuple
            The position of the next move.

        Returns
        -------
        dir : int
            The best direction to place the barrier.
        """
        # Checks the valid directions to place a barrier
        valid_dir = []
        for dir in range(4):
            if self.check_valid_step(my_pos, position, adv_pos, chess_board, dir,max_step):
                valid_dir.append(dir)
        
        x_diff = adv_pos[0] - position[0]
        y_diff = adv_pos[1] - position[1]
        # Place the barrier facing the opponent
        # Randomly choose the direction of the variable if the above is unavailable
        if y_diff > 0 and abs(y_diff) < max_step and 1 in valid_dir:
            dir = 1
        elif x_diff > 0 and abs(x_diff) < max_step and 2 in valid_dir:
            dir = 2
        elif y_diff < 0 and abs(y_diff) < max_step and 3 in valid_dir:
            dir = 3
        elif x_diff < 0 and abs(x_diff) < max_step and 0 in valid_dir:
            dir = 0
        else:
            dir = random.choice(valid_dir )
        return dir
    
    def check_valid_step(self, start_pos, end_pos, adv_pos, chess_board, barrier_dir, max_step):
        """
        Check if the step the agent takes is valid (reachable and within max steps).

        Parameters
        ----------
        start_pos : tuple
            The start position of the agent.
        end_pos : tuple
            The end position of the agent.
        adv_pos : tuple
            The position of the opponent.
        chess_board : np.ndarray
            The current chess board.
        barrier_dir : int
            The direction of the barrier.
        max_step : int
            The maximum step we can make.

        Returns
        -------
        is_reached : bool
            Whether the step is reachable.
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
                next_adv = next_pos[0] == adv_pos[0] and next_pos[1] == adv_pos[1]
                next_end = next_pos[0] == end_pos[0] and next_pos[1] == end_pos[1]
                if next_adv or tuple(next_pos) in visited:
                    continue
                if next_end:
                    is_reached = True
                    break

                visited.add(tuple(next_pos))
                state_queue.append((next_pos, cur_step + 1))

        return is_reached

    def heuristic_decisions(self, chess_board, my_pos, adv_pos):
        """
        Determines the heuristic for each move. 
        The smaller the heuristic, the better.

        Parameters
        ----------
        chess_board : np.ndarray
            The current chess board.
        my_pos : tuple
            The position of the agent.
        adv_pos : tuple
            The position of the opponent.
        
        Returns
        -------
        heuristic : int
            The heuristic for the move.

        """

        n = chess_board.shape[0]
        heuristic = 9999

        # Finds the Manhattan distance between the my_pos and adv_pos
        x = abs(adv_pos[0] - my_pos[0])
        y = abs(adv_pos[0] - my_pos[1])
        heuristic = x + y

        # Checks the number of barriers around our current position
        barriers_around = 0
        for dir in range(4):
            if chess_board[my_pos[0],my_pos[1],dir]== True:
                barriers_around += 1

        # If there are 2 or more barriers around us, return 9999
        if barriers_around >= 2:   
            return 9999  
        

        return heuristic