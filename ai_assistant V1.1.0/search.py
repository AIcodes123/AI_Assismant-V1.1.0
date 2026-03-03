"""
网络搜索模块 - 模拟搜索功能
"""
import time
import random
from datetime import datetime


class WebSearch:
    def __init__(self):
        self.enabled = True
        self.cache = {}
        self.history = []

        # 模拟知识库
        self.knowledge = {
            "python": {
                "title": "Python编程语言",
                "content": "高级编程语言，简洁易读，用于Web开发、数据科学、人工智能等领域。",
                "sources": ["Python官网", "GitHub", "Stack Overflow"]
            },
            "ai": {
                "title": "人工智能",
                "content": "模拟人类智能的技术，包括机器学习、深度学习、自然语言处理等。",
                "sources": ["AI研究论文", "技术博客", "行业报告"]
            },
            "ml": {
                "title": "机器学习",
                "content": "让计算机从数据中学习模式，无需显式编程。分为监督学习、无监督学习、强化学习。",
                "sources": ["Coursera", "机器学习书籍", "研究论文"]
            },
            "编程": {
                "title": "编程基础",
                "content": "编程是将算法转化为计算机指令的过程。需要逻辑思维和解决问题的能力。",
                "sources": ["编程教程", "在线课程", "实践项目"]
            },
            "学习": {
                "title": "学习方法",
                "content": "有效学习需要明确目标、系统规划、实践应用和持续反思。",
                "sources": ["教育研究", "学习科学", "成功案例"]
            }
        }

    def search(self, query, limit=5):
        """搜索查询"""
        if not self.enabled:
            return "搜索功能已禁用"

        # 检查缓存
        if query in self.cache:
            return self.cache[query]

        # 模拟搜索延迟
        time.sleep(0.5)

        # 记录搜索
        self.history.append({
            "query": query,
            "time": datetime.now().strftime("%H:%M:%S"),
            "results": limit
        })

        # 生成结果
        results = self._find_results(query, limit)

        # 缓存
        self.cache[query] = results

        return results

    def _find_results(self, query, limit):
        """查找结果"""
        query_lower = query.lower()

        # 查找匹配的主题
        matches = []
        for topic, info in self.knowledge.items():
            if topic in query_lower:
                matches.append((topic, info))

        # 如果没有直接匹配，使用关键词匹配
        if not matches:
            words = query_lower.split()
            for topic, info in self.knowledge.items():
                if any(word in topic for word in words):
                    matches.append((topic, info))

        # 如果还是没有，返回通用结果
        if not matches:
            matches = list(self.knowledge.items())[:2]

        # 构建结果
        result = f"🔍 搜索 '{query}' 的结果:\n\n"

        for i, (topic, info) in enumerate(matches[:limit], 1):
            result += f"{i}. {info['title']}\n"
            result += f"   内容: {info['content']}\n"
            result += f"   来源: {', '.join(info['sources'])}\n\n"

        # 添加搜索建议
        result += "💡 搜索建议:\n"
        result += "• 使用更具体的关键词\n"
        result += "• 检查拼写是否正确\n"
        result += "• 尝试不同的提问方式\n"

        return result

    def enable(self):
        """启用搜索"""
        self.enabled = True
        return True

    def disable(self):
        """禁用搜索"""
        self.enabled = False
        return True

    def toggle(self):
        """切换状态"""
        self.enabled = not self.enabled
        return self.enabled

    def clear_cache(self):
        """清除缓存"""
        self.cache.clear()
        return True

    def get_history(self):
        """获取搜索历史"""
        return self.history[-10:]  # 最近10条

    def get_stats(self):
        """获取统计信息"""
        return {
            "enabled": self.enabled,
            "cache_size": len(self.cache),
            "history_count": len(self.history),
            "knowledge_base": len(self.knowledge)
        }


# 全局搜索实例
_searcher = WebSearch()


def search(query, limit=5):
    """搜索"""
    return _searcher.search(query, limit)


def enable_search():
    """启用"""
    return _searcher.enable()


def disable_search():
    """禁用"""
    return _searcher.disable()


def toggle_search():
    """切换"""
    return _searcher.toggle()


def is_enabled():
    """是否启用"""
    return _searcher.enabled


def get_info():
    """获取信息"""
    return _searcher.get_stats()