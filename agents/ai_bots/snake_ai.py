"""
贪吃蛇专用AI智能体
"""

import random
import numpy as np
from agents.base_agent import BaseAgent

class SnakeAI(BaseAgent):
    """贪吃蛇AI智能体"""
    
    def __init__(self, name="SnakeAI", player_id=1):
        super().__init__(name, player_id)
    
    def get_action(self, observation, env):
        """获取动作"""
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            return None
        
        # 获取当前蛇的信息
        game = env.game
        if self.player_id == 1:
            snake = game.snake1
            current_direction = game.direction1
        else:
            snake = game.snake2
            current_direction = game.direction2
        
        if not snake:
            return random.choice(valid_actions)
        
        head = snake[0]
        
        # 寻找最近的食物
        if game.foods:
            target_food = self._find_nearest_food(head, game.foods)
            best_action = self._move_towards_target(head, target_food, current_direction, game)
            
            # 检查这个动作是否安全
            if self._is_safe_action(best_action, head, game):
                return best_action
        
        # 如果没有安全的路径到食物，寻找安全的移动
        safe_actions = []
        for action in valid_actions:
            if self._is_safe_action(action, head, game):
                safe_actions.append(action)
        
        if safe_actions:
            return random.choice(safe_actions)
        
        # 如果没有安全动作，随机选择
        return random.choice(valid_actions)
    
    def _find_nearest_food(self, head, foods):
        """找到最近的食物"""
        min_distance = float('inf')
        nearest_food = foods[0]
        
        for food in foods:
            distance = abs(head[0] - food[0]) + abs(head[1] - food[1])
            if distance < min_distance:
                min_distance = distance
                nearest_food = food
        
        return nearest_food
    
    def _move_towards_target(self, head, target, current_direction, game):
        """向目标移动"""
        head_x, head_y = head
        target_x, target_y = target
        
        # 计算到目标的方向
        dx = target_x - head_x
        dy = target_y - head_y
        
        # 优先级：距离较远的轴优先
        if abs(dx) > abs(dy):
            if dx > 0:
                return (1, 0)  # 下
            elif dx < 0:
                return (-1, 0)  # 上
        
        if dy > 0:
            return (0, 1)  # 右
        elif dy < 0:
            return (0, -1)  # 左
        
        # 如果已经在目标位置，保持当前方向
        return current_direction
    
    def _is_safe_action(self, action, head, game):
        """检查动作是否安全"""
        # action已经是方向元组 (dx, dy)
        direction = action
        new_head = (head[0] + direction[0], head[1] + direction[1])
        
        # 检查边界
        if (new_head[0] < 0 or new_head[0] >= game.board_size or
            new_head[1] < 0 or new_head[1] >= game.board_size):
            return False
        
        # 检查是否撞到蛇身
        if new_head in game.snake1[:-1] or new_head in game.snake2[:-1]:
            return False
        
        return True


class SmartSnakeAI(BaseAgent):
    """更智能的贪吃蛇AI（A*+安全性评估+对手预测+策略优化）"""
    
    def __init__(self, name="SmartSnakeAI", player_id=1):
        super().__init__(name, player_id)
    
    def get_action(self, observation, env):
        """A*寻路+安全性评估+对手预测+策略优化"""
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            return None
        game = env.game
        if self.player_id == 1:
            snake = game.snake1
            current_direction = game.direction1
            opponent_snake = game.snake2
        else:
            snake = game.snake2
            current_direction = game.direction2
            opponent_snake = game.snake1
        if not snake:
            return random.choice(valid_actions)
        head = snake[0]
        opponent_head = opponent_snake[0] if opponent_snake else None
        # 1. A*寻路到最近食物
        if game.foods:
            target_food = self._find_nearest_food(head, game.foods)
            path = self._a_star_pathfinding(head, target_food, game, opponent_head)
            if path and len(path) > 1:
                next_pos = path[1]
                action = self._pos_to_action(head, next_pos)
                # 2. 安全性评估：落点空间足够大且不会和对手头部正面冲突
                if (action in valid_actions and
                    self._is_safe_action(action, head, game, opponent_head) and
                    self._space_after_move(head, action, game, opponent_head) >= max(5, len(snake))):
                    return action
        # 3. 策略优化：选择最大生存空间的安全动作
        best_action = None
        max_space = -1
        for action in valid_actions:
            if self._is_safe_action(action, head, game, opponent_head):
                space = self._space_after_move(head, action, game, opponent_head)
                if space > max_space:
                    max_space = space
                    best_action = action
        if best_action:
            return best_action
        # 4. 实在无路，随机
        return random.choice(valid_actions)

    def _find_nearest_food(self, head, foods):
        min_distance = float('inf')
        nearest_food = foods[0]
        for food in foods:
            distance = abs(head[0] - food[0]) + abs(head[1] - food[1])
            if distance < min_distance:
                min_distance = distance
                nearest_food = food
        return nearest_food

    def _a_star_pathfinding(self, start, goal, game, opponent_head=None):
        from heapq import heappush, heappop
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        def get_neighbors(pos):
            x, y = pos
            neighbors = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < game.board_size and 0 <= ny < game.board_size):
                    # 允许撞到尾部（尾部会移动），但不能撞到身体
                    if ((nx, ny) not in game.snake1[:-1] and 
                        (nx, ny) not in game.snake2[:-1]):
                        # 对手预测：避免和对手头部正面冲突
                        if opponent_head and (nx, ny) == opponent_head:
                            continue
                        neighbors.append((nx, ny))
            return neighbors
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        while open_set:
            current = heappop(open_set)[1]
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            for neighbor in get_neighbors(current):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    heappush(open_set, (f_score[neighbor], neighbor))
        return None

    def _pos_to_action(self, current_pos, next_pos):
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        return (dx, dy)

    def _is_safe_action(self, action, head, game, opponent_head=None):
        direction = action
        new_head = (head[0] + direction[0], head[1] + direction[1])
        # 边界
        if (new_head[0] < 0 or new_head[0] >= game.board_size or
            new_head[1] < 0 or new_head[1] >= game.board_size):
            return False
        # 撞到身体
        if new_head in game.snake1[:-1] or new_head in game.snake2[:-1]:
            return False
        # 对手预测：避免和对手头部正面冲突
        if opponent_head and new_head == opponent_head:
            return False
        return True

    def _space_after_move(self, head, action, game, opponent_head=None):
        """BFS评估落点可达空间（安全性评估）"""
        from collections import deque
        visited = set()
        queue = deque()
        new_head = (head[0] + action[0], head[1] + action[1])
        queue.append(new_head)
        visited.add(new_head)
        body_blocks = set(game.snake1[:-1] + game.snake2[:-1])
        if opponent_head:
            body_blocks.add(opponent_head)
        count = 0
        while queue:
            pos = queue.popleft()
            count += 1
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = pos[0]+dx, pos[1]+dy
                npos = (nx, ny)
                if (0 <= nx < game.board_size and 0 <= ny < game.board_size and
                    npos not in visited and npos not in body_blocks):
                    visited.add(npos)
                    queue.append(npos)
        return count 