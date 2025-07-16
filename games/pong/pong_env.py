from .pong_game import PongGame

class PongEnv:
    def __init__(self):
        self.game = PongGame()

    def reset(self):
        self.game.reset()
        return self.game.get_state()

    def step(self, action1, action2, action1_x=0, action2_x=0):
        self.game.step(action1, action2, action1_x, action2_x)
        return self.game.get_state(), self.game.is_terminal(), self.game.get_winner()