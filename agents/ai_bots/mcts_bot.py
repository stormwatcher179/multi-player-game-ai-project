"""
MCTS Bot
使用蒙特卡洛树搜索算法
"""

import time
import random
import math
from typing import Dict, List, Tuple, Any, Optional
from agents.base_agent import BaseAgent
import config
import copy


class MCTSNode:
    """MCTS节点"""
    
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.untried_actions = self._get_untried_actions()
    
    def _get_untried_actions(self):
        """获取未尝试的动作"""
        if hasattr(self.state, 'get_valid_actions'):
            return self.state.get_valid_actions()
        return []
    
    def is_fully_expanded(self):
        """检查是否完全展开"""
        return len(self.untried_actions) == 0
    
    def is_terminal(self):
        """检查是否为终止节点"""
        if hasattr(self.state, 'is_terminal'):
            return self.state.is_terminal()
        return False
    
    def get_winner(self):
        """获取获胜者"""
        if hasattr(self.state, 'get_winner'):
            return self.state.get_winner()
        return None
    
    def clone_state(self):
        """克隆状态"""
        if hasattr(self.state, 'clone'):
            return self.state.clone()
        return self.state


class MCTSBot(BaseAgent):
    """MCTS Bot"""
    
    def __init__(self, name: str = "MCTSBot", player_id: int = 1, 
                 simulation_count: int = 100):
        super().__init__(name, player_id)
        self.simulation_count = simulation_count
        
        # 从配置获取参数
        ai_config = config.AI_CONFIGS.get('mcts', {})
        self.simulation_count = ai_config.get('simulation_count', simulation_count)
        self.timeout = ai_config.get('timeout', 10)
    
    def get_action(self, observation: Any, env: Any) -> Any:
        """
        使用MCTS选择动作（完整树结构版）
        """
        root = MCTSNode(env.game.clone())
        for _ in range(self.simulation_count):
            node = self._select(root)
            if not node.is_terminal() and not node.is_fully_expanded():
                node = self._expand(node)
            result = self._simulate(node)
            self._backpropagate(node, result)
        # 选择访问次数最多的子节点的动作
        if not root.children:
            return None
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.action

    def _select(self, node):
        while not node.is_terminal() and node.is_fully_expanded() and node.children:
            node = self._uct_select(node)
        return node

    def _uct_select(self, node):
        C = 1.41
        best_score = -float('inf')
        best_child = None
        for child in node.children:
            if child.visits == 0:
                uct = float('inf')
            else:
                uct = (child.value / child.visits +
                       C * math.sqrt(math.log(node.visits + 1) / child.visits))
            if uct > best_score:
                best_score = uct
                best_child = child
        return best_child

    def _expand(self, node):
        action = node.untried_actions.pop()
        next_state = node.state.clone()
        next_state.step(action)
        child = MCTSNode(next_state, parent=node, action=action)
        node.children.append(child)
        return child

    def _simulate(self, node):
        state = node.state.clone()
        while not state.is_terminal():
            actions = state.get_valid_actions()
            if not actions:
                break
            action = random.choice(actions)
            state.step(action)
        winner = state.get_winner()
        if winner == self.player_id:
            return 1
        elif winner is not None:
            return -1
        else:
            return 0

    def _backpropagate(self, node, result):
        while node is not None:
            node.visits += 1
            node.value += result
            node = node.parent

    def reset(self):
        """重置MCTS Bot"""
        super().reset()
    
    def get_info(self) -> Dict[str, Any]:
        """获取MCTS Bot信息"""
        info = super().get_info()
        info.update({
            'type': 'MCTS',
            'description': '使用完整蒙特卡洛树搜索的Bot',
            'strategy': f'MCTS with {self.simulation_count} simulations',
            'timeout': self.timeout
        })
        return info 