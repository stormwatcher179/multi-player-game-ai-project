from .physics import Ball
import random

class Paddle:
    def __init__(self, x, y, width=10, height=60):
        self.x, self.y = x, y
        self.width, self.height = width, height

    def move(self, dy, board_height):
        self.y = max(0, min(board_height - self.height, self.y + dy))

    def move_x(self, dx, board_width):
        self.x = max(0, min(board_width - self.width, self.x + dx))

class PongGame:
    def __init__(self, width=600, height=400):
        self.width, self.height = width, height
        self.reset()
        self.last_collision = None
        self.serve_player = random.choice([1, 2])  # 1左发，2右发

    def reset(self):
        self.ball = Ball(self.width//2, self.height//2, vx=3, vy=2)
        self.paddle1 = Paddle(10, self.height//2 - 30)
        self.paddle2 = Paddle(self.width-20, self.height//2 - 30)
        self.score1 = self.score2 = 0
        self.done = False
        self.last_collision = None
        self.serve_player = random.choice([1, 2])  # 新开局随机发球

    def step(self, action1, action2, action1_x=0, action2_x=0):
        self.last_collision = None  # 每帧重置
        # action1, action2: -1(上), 0(不动), 1(下)
        self.paddle1.move(action1*5, self.height)
        self.paddle2.move(action2*5, self.height)
        # 移除左右移动，球拍只能上下移动
        self.ball.move(self.width, self.height)
        self.ball.check_wall_collision(self.height)
        # 球拍碰撞
        if self.ball.vx < 0:
            if self.ball.check_paddle_collision(self.paddle1):
                self.ball.x = self.paddle1.x + self.paddle1.width + self.ball.radius  # 防止穿透
                self.last_collision = "paddle"
        else:
            if self.ball.check_paddle_collision(self.paddle2):
                self.ball.x = self.paddle2.x - self.ball.radius  # 防止穿透
                self.last_collision = "paddle"
        # 得分与重置
        if self.ball.x < 0:
            self.score2 += 1
            self.serve_player = 1 if self.serve_player == 2 else 2  # 轮换发球
            self.reset_ball()
        elif self.ball.x > self.width:
            self.score1 += 1
            self.serve_player = 1 if self.serve_player == 2 else 2  # 轮换发球
            self.reset_ball()
        # 胜负判定
        if self.score1 >= 5:
            self.done = True
            self.winner = 1
        elif self.score2 >= 5:
            self.done = True
            self.winner = 2
        else:
            self.done = False
            self.winner = None

    def reset_ball(self):
        # serve_player==1左发，==2右发
        direction = 1 if self.serve_player == 2 else -1
        vx = 3 * direction
        vy = random.choice([-2, -1, 1, 2])
        self.ball = Ball(self.width//2, self.height//2, vx=vx, vy=vy)

    def get_state(self):
        return {
            'ball': (self.ball.x, self.ball.y, self.ball.vx, self.ball.vy),
            'paddle1': (self.paddle1.x, self.paddle1.y),
            'paddle2': (self.paddle2.x, self.paddle2.y),
            'score1': self.score1,
            'score2': self.score2
        }

    def is_terminal(self):
        return self.done

    def get_winner(self):
        return self.winner