class Ball:
    def __init__(self, x, y, vx, vy, radius=5):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.radius = radius

    def move(self, board_width=None, board_height=None):
        self.x += self.vx
        self.y += self.vy
        # 恢复经典Pong：不限制球的运动范围，碰到上下边界由check_wall_collision处理

    def check_wall_collision(self, height):
        if self.y - self.radius < 0 or self.y + self.radius > height:
            self.vy = -self.vy

    def check_paddle_collision(self, paddle):
        # 球拍为竖直矩形，判断球是否与球拍矩形重叠
        px, py, pw, ph = paddle.x, paddle.y, paddle.width, paddle.height
        # 球的中心在球拍矩形范围内
        if (px <= self.x <= px + pw and py <= self.y <= py + ph):
            self.vx = -self.vx  # 水平速度反向
            # 根据碰撞点调整垂直速度（简单实现：中心碰撞vy不变，边缘碰撞vy略变）
            offset = (self.y - (py + ph/2)) / (ph/2)
            self.vy += offset * 2  # 可调参数
            return True
        return False