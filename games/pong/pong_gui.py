import sys
import os
import urllib.request
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pygame
from games.pong import PongEnv
from agents.ai_bots.search_bot import SearchBot  # 添加SearchBot导入
# 删除AI导入

# 自动下载音效
sound_url = "https://cdn.jsdelivr.net/gh/AI-Resource/pong-assets/pong.wav"
sound_path = os.path.join(os.path.dirname(__file__), "pong.wav")
if not os.path.exists(sound_path):
    print("正在下载Pong音效...")
    try:
        urllib.request.urlretrieve(sound_url, sound_path)
        print("音效下载完成！")
    except Exception as e:
        print("音效下载失败：", e)

pygame.mixer.init()
try:
    sound_pong = pygame.mixer.Sound(sound_path)
except Exception as e:
    print("音效文件加载失败，将无音效。", e)
    sound_pong = None

# 按钮类
default_font = None
class Button:
    def __init__(self, rect, text, font, color, text_color):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.color = color
        self.text_color = text_color
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        txt = self.font.render(self.text, True, self.text_color)
        txt_rect = txt.get_rect(center=self.rect.center)
        screen.blit(txt, txt_rect)
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]

# 初始化
pygame.init()
env = PongEnv()
state = env.reset()

PANEL_WIDTH = 300  # 增加面板宽度从280到300，适应更宽的球桌
WIDTH, HEIGHT = env.game.width + PANEL_WIDTH, env.game.height  # 移除+100，让球桌占满高度
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong 双人对战")
clock = pygame.time.Clock()
default_font = pygame.font.SysFont(None, 32)

# 按钮颜色
BTN_NEW_COLOR = (102, 204, 255)      # 天蓝色
BTN_PAUSE_COLOR = (255, 204, 0)     # 橙黄色
BTN_RESUME_COLOR = (0, 204, 102)    # 绿色
BTN_QUIT_COLOR = (255, 102, 102)    # 红色

# 按钮实例化（调整位置，适应新的面板宽度）
btn_new = Button(rect=(WIDTH-280, 60, 260, 50), text="New Game", font=default_font, color=BTN_NEW_COLOR, text_color=(0,0,0))
btn_pause = Button(rect=(WIDTH-280, 130, 260, 50), text="Pause", font=default_font, color=BTN_PAUSE_COLOR, text_color=(0,0,0))
btn_quit = Button(rect=(WIDTH-280, 200, 260, 50), text="Quit", font=default_font, color=BTN_QUIT_COLOR, text_color=(0,0,0))
btn_ai = Button(rect=(WIDTH-280, 270, 260, 50), text="AI Mode", font=default_font, color=(150, 150, 150), text_color=(0,0,0))

# AI模式变量
MODE_HUMAN = "human"
MODE_AI = "ai"
game_mode = MODE_HUMAN  # 默认双人
ai_agent = SearchBot(player_id=2)  # AI控制玩家2

paused = False
game_over = False
winner = None

last_vx, last_vy = env.game.ball.vx, env.game.ball.vy
score_pause = 0  # 进球后暂停帧数

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if btn_new.rect.collidepoint(mouse_pos):
                state = env.reset()
                paused = False
                game_over = False
                winner = None
                score_pause = 0
            if btn_pause.rect.collidepoint(mouse_pos):
                if not game_over:
                    paused = not paused
            if btn_quit.rect.collidepoint(mouse_pos):
                pygame.quit()
                sys.exit(0)
            if btn_ai.rect.collidepoint(mouse_pos):
                if game_mode == MODE_HUMAN:
                    game_mode = MODE_AI
                    btn_ai.text = "Human Mode"
                    btn_ai.color = (100, 200, 100)
                    # 切换到AI模式时，重新开一局
                    state = env.reset()
                    paused = False
                    game_over = False
                    winner = None
                    score_pause = 0
                else:
                    game_mode = MODE_HUMAN
                    btn_ai.text = "AI Mode"
                    btn_ai.color = (150, 150, 150)
                    # 切换到人类模式时，重新开一局
                    state = env.reset()
                    paused = False
                    game_over = False
                    winner = None
                    score_pause = 0
    # 玩家输入
    keys = pygame.key.get_pressed()
    action1 = 0
    if keys[pygame.K_w]:
        action1 = -1
    elif keys[pygame.K_s]:
        action1 = 1
    action1_x = 0
    if keys[pygame.K_a]:
        action1_x = -1
    elif keys[pygame.K_d]:
        action1_x = 1
    # 玩家2输入（AI模式或键盘控制）
    if game_mode == MODE_AI:
        # AI控制玩家2
        try:
            observation = env.game.get_state()
            action2 = ai_agent.get_action(observation, env)
            action2_x = 0  # AI不进行左右移动
        except Exception as e:
            print(f"AI控制异常: {e}")
            action2 = 0
            action2_x = 0
    else:
        # 人类控制玩家2
        action2 = 0
        if keys[pygame.K_UP]:
            action2 = -1
        elif keys[pygame.K_DOWN]:
            action2 = 1
        action2_x = 0
        if keys[pygame.K_LEFT]:
            action2_x = -1
        elif keys[pygame.K_RIGHT]:
            action2_x = 1

    if not paused and not game_over:
        if score_pause > 0:
            score_pause -= 1
            # 进球暂停期间不推进游戏
        else:
            state, done, winner = env.step(action1, action2, action1_x, action2_x)
            if done:
                game_over = True
            # 检查是否刚刚进球（球重置到中间）
            if hasattr(env.game, 'ball') and env.game.ball.x == env.game.width // 2 and env.game.ball.y == env.game.height // 2:
                # 但不是新开局
                if env.game.score1 > 0 or env.game.score2 > 0:
                    score_pause = 60  # 1秒暂停（60帧）

    # 撞击音效
    if sound_pong and hasattr(env.game, 'last_collision') and env.game.last_collision == "paddle":
        sound_pong.play()
    last_vx, last_vy = env.game.ball.vx, env.game.ball.vy

    # 绘制主游戏区
    screen.fill((0,0,0))
    pygame.draw.circle(screen, (255,255,255), (int(env.game.ball.x), int(env.game.ball.y)), env.game.ball.radius)
    pygame.draw.rect(screen, (0,255,0), (env.game.paddle1.x, env.game.paddle1.y, env.game.paddle1.width, env.game.paddle1.height), border_radius=6)
    pygame.draw.rect(screen, (0,0,255), (env.game.paddle2.x, env.game.paddle2.y, env.game.paddle2.width, env.game.paddle2.height), border_radius=6)

    # 绘制面板
    pygame.draw.rect(screen, (40,40,40), (env.game.width, 0, PANEL_WIDTH, HEIGHT))
    # 分数
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"{env.game.score1} : {env.game.score2}", True, (255,255,0))
    screen.blit(score_text, (env.game.width+110, 10))  # 调整分数位置，适应新面板宽度
    # 状态
    status = "Paused" if paused else ("Game Over" if game_over else ("Ready" if score_pause > 0 else "Playing"))
    status_text = font.render(f"状态: {status}", True, (255,255,255))
    screen.blit(status_text, (env.game.width+30, 350))  # 调整状态位置
    # 结果
    if game_over:
        winner_color = (0,255,0) if winner == 1 else (0,0,255)
        result_text = font.render(f"Winner: Player {winner}", True, winner_color)
        screen.blit(result_text, (env.game.width+30, 400))  # 调整结果位置

    # 按钮
    btn_new.draw(screen)
    # Pause/Resume按钮变色变字
    if paused:
        btn_pause.text = "Resume"
        btn_pause.color = BTN_RESUME_COLOR
    else:
        btn_pause.text = "Pause"
        btn_pause.color = BTN_PAUSE_COLOR
    btn_pause.draw(screen)
    btn_quit.draw(screen)
    btn_ai.draw(screen)  # 添加AI按钮绘制

    # 规则简述
    rule_font = pygame.font.SysFont(None, 24)
    current_mode = "AI对战" if game_mode == MODE_AI else "双人对战"
    rules = [
        "规则简述：",
        f"当前模式: {current_mode}",
        "1. 玩家1: W/S控制上下",
        "2. 玩家2: ↑/↓控制上下" if game_mode == MODE_HUMAN else "2. 玩家2: AI自动控制",
        "3. 球撞左右墙即得分",
        "4. 先得5分者获胜",
        "5. 可随时暂停/重开/退出",
        "6. 点击AI Mode切换模式",
        "7. 球桌左右各留2cm边距"
    ]
    for i, line in enumerate(rules):
        txt = rule_font.render(line, True, (200,200,200))
        screen.blit(txt, (env.game.width+20, 470 + i*28))  # 调整规则说明位置

    # 进球后暂停提示
    if score_pause > 0:
        ready_font = pygame.font.SysFont(None, 48)
        txt = ready_font.render("Ready!", True, (255,255,0))
        screen.blit(txt, (WIDTH//2-60, HEIGHT//2-30))

    pygame.display.flip()
    clock.tick(60)