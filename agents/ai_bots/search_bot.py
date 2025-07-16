from agents.base_agent import BaseAgent
import random
import math

class SearchBot(BaseAgent):
    """搜索算法AI Bot（A*、BFS等），用于Pong游戏"""
    def __init__(self, search_algorithm='bfs', name="SearchBot", player_id=2):
        super().__init__(name, player_id)
        self.search_type = search_algorithm

    def get_action(self, observation, env):
        # 预测球的落点，移动球拍拦截
        target_y = self.predict_ball_landing_y(observation, env)
        paddle_y = observation['paddle2'][1] if self.player_id == 2 else observation['paddle1'][1]
        paddle_height = env.game.paddle2.height if self.player_id == 2 else env.game.paddle1.height
        # 简单策略：球拍中心对准球落点
        center_y = paddle_y + paddle_height // 2
        if abs(center_y - target_y) < 3:
            return 0  # 不动
        elif center_y < target_y:
            return 1  # 向下
        else:
            return -1  # 向上

    def predict_ball_landing_y(self, observation, env):
        # 预测球的y坐标在到达本方球拍时的位置
        ball_x, ball_y, ball_vx, ball_vy = observation['ball']
        width = env.game.width
        height = env.game.height
        radius = env.game.ball.radius
        # 预测球运动，直到到达本方球拍x
        if self.player_id == 2:
            target_x = env.game.paddle2.x
            direction = 1
        else:
            target_x = env.game.paddle1.x + env.game.paddle1.width
            direction = -1
        x, y, vx, vy = ball_x, ball_y, ball_vx, ball_vy
        while (direction == 1 and x < target_x) or (direction == -1 and x > target_x):
            x += vx
            y += vy
            # 碰到上下边界反弹
            if y - radius < 0 or y + radius > height:
                vy = -vy
                y = max(radius, min(height - radius, y))
        return int(y)

    def random_action(self, env):
        # 随机动作（-1, 0, 1）
        return random.choice([-1, 0, 1]) 