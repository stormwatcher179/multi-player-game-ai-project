"""
人类智能体
处理人类玩家的输入
"""

import time
from typing import Dict, List, Tuple, Any, Optional
from ..base_agent import BaseAgent


class HumanAgent(BaseAgent):
    """人类智能体"""
    def update_stats(self, *args, **kwargs):
        pass

    def __init__(self, name: str = "Human", player_id: int = 1):
        super().__init__(name, player_id)
    
    def get_action(self, observation: Any, env: Any) -> Any:
        """
        获取人类玩家的动作
        
        Args:
            observation: 当前观察
            env: 环境对象
            
        Returns:
            人类玩家选择的动作
        """
        start_time = time.time()
        
        # 显示当前游戏状态
        self._display_game_state(observation, env)
        
        # 获取有效动作
        valid_actions = env.get_valid_actions()
        
        # 获取人类输入
        action = self._get_human_input(valid_actions, env)
        
        # 更新统计
        move_time = time.time() - start_time
        self.total_moves += 1
        self.total_time += move_time
        
        return action
    
    def _display_game_state(self, observation: Any, env: Any):
        """显示游戏状态"""
        print(f"\n=== {self.name} 的回合 ===")
        print(f"玩家ID: {self.player_id}")
        
        # 显示棋盘
        if hasattr(env, 'render'):
            env.render(mode='human')
        
        # 显示有效动作数量
        valid_actions = env.get_valid_actions()
        print(f"可用位置数量: {len(valid_actions)}")
    
    def _get_human_input(self, valid_actions: List[Any], env: Any) -> Any:
        """获取人类输入"""
        # 判断是否为贪吃蛇环境
        if env.__class__.__name__.lower().startswith("snakeenv"):
            # 方向输入映射
            input_map = {
                'w': (-1, 0), 'up': (-1, 0),
                's': (1, 0),  'down': (1, 0),
                'a': (0, -1), 'left': (0, -1),
                'd': (0, 1),  'right': (0, 1)
            }
            print("可选动作:", valid_actions)
            while True:
                move = input(f"玩家{self.player_id}请输入方向（w/a/s/d 或 up/left/down/right）: ").strip().lower()
                if move in ['quit', 'q', 'exit']:
                    print("用户主动退出游戏。")
                    raise KeyboardInterrupt  # 或 sys.exit(0)
                if move in input_map and input_map[move] in valid_actions:
                    return input_map[move]
                print("无效输入，请重新输入。")
        else:
            print("当前棋盘：")
            env.render()
            print(f"可选动作: {valid_actions}")
            while True:
                move = input(f"玩家{self.player_id}请输入落子位置(如 0,0): ")
                if move in ['quit', 'q', 'exit']:
                    print("用户主动退出游戏。")
                    raise KeyboardInterrupt  # 或 sys.exit(0)
                try:
                    row, col = map(int, move.strip().split(','))
                    if (row, col) in valid_actions:
                        return (row, col)
                    else:
                        print("无效位置，请重新输入。")
                except Exception:
                    # 根据游戏类型获取不同的输入
                    if hasattr(env, 'board_size'):  # 五子棋
                        action = self._get_gomoku_input(env.board_size)
                    else:
                        # 默认输入格式
                        action = self._get_default_input(valid_actions)
                
                    # 验证输入
                    if action in valid_actions:
                        return action
                    else:
                        print(f"无效动作: {action}")
                        print("请重新输入")
                    
                except (ValueError, IndexError) as e:
                    print(f"输入错误: {e}")
                    print("请重新输入")
    
    def _get_gomoku_input(self, board_size: int) -> Tuple[int, int]:
        """获取五子棋输入"""
        print(f"请输入行和列 (0-{board_size-1}):")
        
        # 获取行
        while True:
            try:
                row_input = input("行: ").strip()
                if row_input.lower() == 'quit':
                    raise KeyboardInterrupt
                row = int(row_input)
                if 0 <= row < board_size:
                    break
                else:
                    print(f"行必须在 0-{board_size-1} 之间")
            except ValueError:
                print("请输入有效的数字")
        
        # 获取列
        while True:
            try:
                col_input = input("列: ").strip()
                if col_input.lower() == 'quit':
                    raise KeyboardInterrupt
                col = int(col_input)
                if 0 <= col < board_size:
                    break
                else:
                    print(f"列必须在 0-{board_size-1} 之间")
            except ValueError:
                print("请输入有效的数字")
        
        return (row, col)
    
    def _get_default_input(self, valid_actions: List[Any]) -> Any:
        """获取默认输入"""
        print("可用动作:")
        for i, action in enumerate(valid_actions):
            print(f"{i}: {action}")
        
        while True:
            try:
                choice = input("请选择动作编号: ").strip()
                if choice.lower() == 'quit':
                    raise KeyboardInterrupt
                index = int(choice)
                if 0 <= index < len(valid_actions):
                    return valid_actions[index]
                else:
                    print(f"编号必须在 0-{len(valid_actions)-1} 之间")
            except ValueError:
                print("请输入有效的数字")
    
    def reset(self):
        """重置人类智能体"""
        super().reset()
        # 人类智能体不需要特殊重置
    
    def get_info(self) -> Dict[str, Any]:
        """获取人类智能体信息"""
        info = super().get_info()
        info.update({
            'type': 'Human',
            'description': '人类玩家，通过键盘输入进行游戏'
        })
        return info 