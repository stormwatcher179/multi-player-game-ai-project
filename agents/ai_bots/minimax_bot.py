import time
from agents.base_agent import BaseAgent
import copy

class MinimaxBot(BaseAgent):
    def __init__(self, name="MinimaxBot", player_id=1, max_depth=2):
        super().__init__(name, player_id)
        self.max_depth = max_depth

    def get_action(self, observation, env):
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            return None

        # 动态深度调整：空位越少，搜索越深
        empty_count = len(valid_actions)
        if empty_count > 30:
            depth = 2
        elif empty_count > 15:
            depth = 3
        else:
            depth = 4

        start_time = time.time()
        time_limit = 1.0  # 1秒

        best_score = float('-inf')
        best_action = valid_actions[0]
        for action in valid_actions:
            if time.time() - start_time > time_limit:
                break
            game_copy = env.game.clone()
            game_copy.step(action)
            score = self.minimax(game_copy, depth - 1, False, float('-inf'), float('inf'), start_time, time_limit)
            if score > best_score:
                best_score = score
                best_action = action
        return best_action

    def minimax(self, game, depth, maximizing, alpha, beta, start_time, time_limit):
        if time.time() - start_time > time_limit:
            return 0  # 超时直接返回
        if depth == 0 or game.is_terminal():
            winner = game.get_winner()
            if winner == self.player_id:
                return 10000
            elif winner is not None:
                return -10000
            else:
                return self.evaluate(game)  # 非终局用启发式评估

        valid_actions = game.get_valid_actions()
        if not valid_actions:
            return 0
        
        if maximizing:
            max_score = float('-inf')
            for action in valid_actions:
                game_copy = game.clone()
                game_copy.step(action)
                score = self.minimax(game_copy, depth - 1, False, alpha, beta, start_time, time_limit)
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break  # beta剪枝
            return max_score
        else:
            min_score = float('inf')
            for action in valid_actions:
                game_copy = game.clone()
                game_copy.step(action)
                score = self.minimax(game_copy, depth - 1, True, alpha, beta, start_time, time_limit)
                min_score = min(min_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break  # alpha剪枝
            return min_score

    def evaluate(self, game):
        board = game.board
        player = self.player_id
        opponent = 2 if player == 1 else 1
        board_size = game.board_size
        center = board_size // 2
        def count_n_in_a_row(board, player, n):
            count = 0
            for i in range(board_size):
                for j in range(board_size):
                    if board[i, j] != player:
                        continue
                    for dx, dy in [(1,0),(0,1),(1,1),(1,-1)]:
                        c = 1
                        for k in range(1, n):
                            x, y = i+dx*k, j+dy*k
                            if 0<=x<board_size and 0<=y<board_size and board[x, y]==player:
                                c += 1
                            else:
                                break
                        if c == n:
                            # 检查两端是否被堵死
                            x1, y1 = i-dx, j-dy
                            x2, y2 = i+dx*n, j+dy*n
                            blocked = 0
                            if not (0<=x1<board_size and 0<=y1<board_size) or (board[x1, y1] != 0):
                                blocked += 1
                            if not (0<=x2<board_size and 0<=y2<board_size) or (board[x2, y2] != 0):
                                blocked += 1
                            if blocked < 2:
                                count += 1
            return count
        def center_score(board, player):
            score = 0
            for i in range(board_size):
                for j in range(board_size):
                    if board[i, j] == player:
                        score += max(7 - abs(i - center), 0) + max(7 - abs(j - center), 0)
            return score
        score = 0
        score += 100000 * count_n_in_a_row(board, player, 5)
        score += 10000 * count_n_in_a_row(board, player, 4)
        score += 1000 * count_n_in_a_row(board, player, 3)
        score += 10 * center_score(board, player)
        score -= 10000 * count_n_in_a_row(board, opponent, 4)
        score -= 1000 * count_n_in_a_row(board, opponent, 3)
        return score

    def count_consecutive(self, game, player):
        board = game.board
        count = 0
        for i in range(game.board_size):
            for j in range(game.board_size):
                if board[i, j] == player:
                    for dx, dy in [(1,0),(0,1),(1,1),(1,-1)]:
                        c = 1
                        for k in range(1, game.win_length):
                            x, y = i+dx*k, j+dy*k
                            if 0<=x<game.board_size and 0<=y<game.board_size and board[x, y]==player:
                                c += 1
                            else:
                                break
                        count += c
        return count 