import random
from agents.base_agent import BaseAgent
import numpy as np

class RuleBasedGomokuBot(BaseAgent):
    def get_action(self, observation, env):
        board = observation if isinstance(observation, np.ndarray) else observation['board']
        player = getattr(self, 'player_id', 1)
        opponent = 2 if player == 1 else 1
        board_size = board.shape[0]
        valid_actions = env.get_valid_actions()
        center = (board_size // 2, board_size // 2)

        # 1. 自己五连
        for move in valid_actions:
            if self._forms_n_in_a_row(board, move, player, 5):
                return move
        # 2. 对手五连
        for move in valid_actions:
            if self._forms_n_in_a_row(board, move, opponent, 5):
                return move
        # 3. 自己四连
        for move in valid_actions:
            if self._forms_n_in_a_row(board, move, player, 4):
                return move
        # 4. 对手四连
        for move in valid_actions:
            if self._forms_n_in_a_row(board, move, opponent, 4):
                return move
        # 5. 自己三连
        for move in valid_actions:
            if self._forms_n_in_a_row(board, move, player, 3):
                return move
        # 6. 对手三连
        for move in valid_actions:
            if self._forms_n_in_a_row(board, move, opponent, 3):
                return move
        # 7. 中心优先
        if center in valid_actions:
            return center
        # 8. 其次选距离中心最近的点
        def dist2center(move):
            return (move[0] - center[0]) ** 2 + (move[1] - center[1]) ** 2
        valid_actions.sort(key=dist2center)
        return valid_actions[0]

    def _forms_n_in_a_row(self, board, move, player, n):
        # 检查在move落子后，player能否形成n连
        board_size = board.shape[0]
        row, col = move
        if board[row, col] != 0:
            return False
        directions = [(1,0),(0,1),(1,1),(1,-1)]
        for dx, dy in directions:
            count = 1
            for d in [1, -1]:
                for k in range(1, n):
                    x = row + dx * k * d
                    y = col + dy * k * d
                    if 0 <= x < board_size and 0 <= y < board_size and board[x, y] == player:
                        count += 1
                    else:
                        break
            if count >= n:
                return True
        return False 