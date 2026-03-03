#!/usr/bin/env python3
"""
知识库问答加载器 - 完全独立，不依赖任何其他文件
专门加载 qa_database.json 文件，提供问答服务
"""
import json
import os
import random
from pathlib import Path


class QADatabase:
    """问答知识库加载器"""

    def __init__(self, db_path=None):
        if db_path is None:
            # 默认路径：data/knowledge/qa_database.json
            self.db_path = Path(__file__).parent / "data" / "knowledge" / "qa_database.json"
        else:
            self.db_path = Path(db_path)

        self.qa_data = {}
        self.qa_index = {}  # 关键词索引
        self.load()

    def load(self):
        """加载问答库"""
        try:
            if not self.db_path.exists():
                print(f"⚠ 问答库不存在: {self.db_path}")
                print(f"请创建目录: {self.db_path.parent}")
                return False

            with open(self.db_path, 'r', encoding='utf-8') as f:
                self.qa_data = json.load(f)

            # 建立关键词索引
            self._build_index()
            total = self.qa_data.get('total_qa', 0)
            print(f"✅ 问答库加载成功: {total} 个问题")
            return True

        except Exception as e:
            print(f"❌ 问答库加载失败: {e}")
            return False

    def _build_index(self):
        """建立关键词索引"""
        self.qa_index = {}
        questions = self.qa_data.get('questions', {})

        for category, qa_list in questions.items():
            for qa in qa_list:
                # 提取问题中的关键词
                question = qa['question'].lower()
                # 去掉问号，分割成词
                words = question.replace('？', '').replace('?', '').split()
                for word in words:
                    if len(word) > 1:  # 忽略单字
                        if word not in self.qa_index:
                            self.qa_index[word] = []
                        self.qa_index[word].append(qa)

    def find_answer(self, question):
        """查找答案"""
        question = question.lower().strip()

        # 1. 直接匹配完整问题
        for category, qa_list in self.qa_data.get('questions', {}).items():
            for qa in qa_list:
                if qa['question'].lower() in question or question in qa['question'].lower():
                    return qa['answer']

        # 2. 关键词匹配
        words = question.replace('？', '').replace('?', '').split()
        candidates = []

        for word in words:
            if len(word) > 1 and word in self.qa_index:
                candidates.extend(self.qa_index[word])

        if candidates:
            # 去重并返回最匹配的
            seen = set()
            unique_candidates = []
            for qa in candidates:
                qid = qa['id']
                if qid not in seen:
                    seen.add(qid)
                    unique_candidates.append(qa)

            # 返回第一个匹配
            return unique_candidates[0]['answer']

        return None

    def get_random_question(self):
        """随机获取一个问题"""
        categories = list(self.qa_data.get('questions', {}).keys())
        if not categories:
            return None

        category = random.choice(categories)
        qa_list = self.qa_data['questions'][category]
        return random.choice(qa_list)

    def search_questions(self, keyword):
        """搜索问题"""
        results = []
        keyword = keyword.lower()

        for category, qa_list in self.qa_data.get('questions', {}).items():
            for qa in qa_list:
                if keyword in qa['question'].lower():
                    results.append({
                        'id': qa['id'],
                        'question': qa['question'],
                        'category': category
                    })

        return results[:10]

    def get_stats(self):
        """获取统计信息"""
        return {
            'version': self.qa_data.get('version', '未知'),
            'total_qa': self.qa_data.get('total_qa', 0),
            'categories': self.qa_data.get('categories', {}),
            'index_size': len(self.qa_index)
        }


def main():
    """独立运行测试"""
    print("=" * 50)
    print("📚 知识库问答系统 - 独立测试")
    print("=" * 50)

    # 初始化问答库
    qa = QADatabase()

    if not qa.qa_data:
        print("\n❌ 问答库加载失败")
        print("\n请按以下步骤操作：")
        print("1. 在当前目录下创建文件夹: data/knowledge/")
        print("2. 将 qa_database.json 放入该文件夹")
        print("3. 重新运行本程序")
        return

    # 显示统计信息
    stats = qa.get_stats()
    print(f"\n📊 知识库统计:")
    print(f"  版本: {stats['version']}")
    print(f"  总问题数: {stats['total_qa']}")
    print(f"  分类: {', '.join(stats['categories'].keys())}")
    print(f"  关键词索引: {stats['index_size']} 个")

    # 交互式问答
    print("\n" + "=" * 50)
    print("💬 交互式问答模式")
    print("输入问题获取答案，输入 'random' 随机问题，输入 'quit' 退出")
    print("=" * 50)

    while True:
        try:
            question = input("\n你: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break

            if question.lower() == 'random':
                qa_item = qa.get_random_question()
                if qa_item:
                    print(f"\nQ: {qa_item['question']}")
                    print(f"A: {qa_item['answer']}")
                continue

            if not question:
                continue

            answer = qa.find_answer(question)

            if answer:
                print(f"\nA: {answer}")
            else:
                print("\nA: 抱歉，知识库中暂时没有这个问题的答案。")

        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    main()
