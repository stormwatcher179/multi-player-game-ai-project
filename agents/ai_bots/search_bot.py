from agents.base_agent import BaseAgent
import random
import math

class SearchBot(BaseAgent):
    """搜索算法AI Bot（A*、BFS等），用于Pong游戏"""
    def __init__(self, search_algorithm='bfs', name="SearchBot", player_id=2):
        super().__init__(name, player_id)
        self.search_type = search_algorithm

    def get_action(self, observation, env):
        try:
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
        except Exception as e:
            # 如果AI出现异常，返回随机动作
            print(f"AI异常: {e}")
            return self.random_action(env)

    def predict_ball_landing_y(self, observation, env):
        # 预测球的y坐标在到达本方球拍时的位置
        ball_x, ball_y, ball_vx, ball_vy = observation['ball']
        width = env.game.width
        height = env.game.height
        radius = env.game.ball.radius
        
        # 安全检查：如果球没有水平速度，返回当前球拍位置
        if abs(ball_vx) < 0.1:
            if self.player_id == 2:
                return env.game.paddle2.y + env.game.paddle2.height // 2
            else:
                return env.game.paddle1.y + env.game.paddle1.height // 2
        
        # 预测球运动，直到到达本方球拍x
        if self.player_id == 2:
            target_x = env.game.paddle2.x
            direction = 1
        else:
            target_x = env.game.paddle1.x + env.game.paddle1.width
            direction = -1
        
        x, y, vx, vy = ball_x, ball_y, ball_vx, ball_vy
        steps = 0
        max_steps = 1000  # 防止无限循环
        
        while ((direction == 1 and x < target_x) or (direction == -1 and x > target_x)) and steps < max_steps:
            x += vx
            y += vy
            steps += 1
            
            # 碰到上下边界反弹
            if y - radius < 0 or y + radius > height:
                vy = -vy
                y = max(radius, min(height - radius, y))
            
            # 移除左右边界反弹，球撞墙即得分
            # 如果球超出左右边界，停止预测
            if x - radius <= 75 or x + radius >= width - 75:
                break
        
        # 如果超过最大步数，返回当前球拍中心位置
        if steps >= max_steps:
            if self.player_id == 2:
                return env.game.paddle2.y + env.game.paddle2.height // 2
            else:
                return env.game.paddle1.y + env.game.paddle1.height // 2
        
        return int(y)

    def random_action(self, env):
        # 随机动作（-1, 0, 1）
        return random.choice([-1, 0, 1]) 