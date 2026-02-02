"""
Agent 工具集
包含各种实用工具，让 Agent 能够执行更多任务
"""

from langchain_core.tools import tool
from datetime import datetime
import math
import re


@tool
def calculator(expression: str) -> str:
    """
    计算数学表达式。
    
    支持的运算：
    - 基本运算：+, -, *, /, **, %
    - 函数：sqrt(x), pow(x,y), abs(x)
    
    示例：
    - "2 + 2" -> "4"
    - "10 * 5" -> "50"
    - "sqrt(16)" -> "4.0"
    """
    try:
        # 安全的数学表达式求值
        # 只允许数字、运算符和数学函数
        allowed_names = {
            'sqrt': math.sqrt,
            'pow': math.pow,
            'abs': abs,
            'round': round,
            'max': max,
            'min': min,
        }
        
        # 清理表达式
        expression = expression.strip()
        
        # 计算结果
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        
        return f"计算结果：{result}"
    
    except Exception as e:
        return f"计算错误：{str(e)}。请检查表达式格式。"


@tool
def get_current_time(format_type: str = "datetime") -> str:
    """
    获取当前时间和日期。
    
    参数：
    - format_type: 返回格式
      - "datetime": 完整日期时间（默认）
      - "date": 只返回日期
      - "time": 只返回时间
      - "year": 只返回年份
      - "timestamp": Unix 时间戳
    
    示例：
    - get_current_time("datetime") -> "2024-01-30 15:30:45"
    - get_current_time("date") -> "2024-01-30"
    - get_current_time("year") -> "2024"
    """
    now = datetime.now()
    
    if format_type == "datetime":
        return now.strftime("%Y-%m-%d %H:%M:%S")
    elif format_type == "date":
        return now.strftime("%Y-%m-%d")
    elif format_type == "time":
        return now.strftime("%H:%M:%S")
    elif format_type == "year":
        return str(now.year)
    elif format_type == "timestamp":
        return str(int(now.timestamp()))
    else:
        return now.strftime("%Y-%m-%d %H:%M:%S")


@tool
def count_characters(text: str) -> str:
    """
    统计文本的字符数、词数等信息。
    
    返回：
    - 总字符数
    - 中文字符数
    - 英文单词数
    - 数字个数
    
    示例：
    - count_characters("红楼梦有120回") -> "总字符数：7，中文：4，数字：3"
    """
    total_chars = len(text)
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
    digits = len(re.findall(r'\d', text))
    
    return f"""文本统计：
- 总字符数：{total_chars}
- 中文字符：{chinese_chars}
- 英文单词：{english_words}
- 数字个数：{digits}"""


@tool
def text_search(text: str, keyword: str) -> str:
    """
    在文本中搜索关键词，返回包含关键词的句子。
    
    参数：
    - text: 要搜索的文本
    - keyword: 搜索关键词
    
    返回：包含关键词的句子列表
    
    示例：
    - text_search("贾宝玉是红楼梦的主角。林黛玉是女主角。", "主角")
      -> "找到2处：1. 贾宝玉是红楼梦的主角。2. 林黛玉是女主角。"
    """
    if keyword not in text:
        return f"未找到关键词'{keyword}'"
    
    # 按句子分割
    sentences = re.split(r'[。！？\n]', text)
    
    # 找到包含关键词的句子
    matches = [s.strip() for s in sentences if keyword in s and s.strip()]
    
    if not matches:
        return f"未找到包含'{keyword}'的完整句子"
    
    result = f"找到 {len(matches)} 处包含'{keyword}'的句子：\n"
    for i, match in enumerate(matches[:5], 1):  # 最多返回5个
        result += f"{i}. {match}\n"
    
    if len(matches) > 5:
        result += f"...还有 {len(matches) - 5} 处"
    
    return result


@tool
def compare_numbers(num1: float, num2: float) -> str:
    """
    比较两个数字的大小关系。
    
    参数：
    - num1: 第一个数字
    - num2: 第二个数字
    
    返回：比较结果和差值
    
    示例：
    - compare_numbers(10, 5) -> "10 大于 5，差值为 5"
    """
    try:
        num1 = float(num1)
        num2 = float(num2)
        
        diff = abs(num1 - num2)
        
        if num1 > num2:
            return f"{num1} 大于 {num2}，差值为 {diff}"
        elif num1 < num2:
            return f"{num1} 小于 {num2}，差值为 {diff}"
        else:
            return f"{num1} 等于 {num2}"
    
    except Exception as e:
        return f"比较错误：{str(e)}"


# 四大名著相关的专业工具

@tool
def list_four_classics() -> str:
    """
    列出中国四大名著的基本信息。
    
    返回：四大名著的书名、作者、朝代等信息
    """
    classics = """中国四大名著：

1. 《红楼梦》
   - 作者：曹雪芹、高鹗
   - 朝代：清代
   - 主要人物：贾宝玉、林黛玉、薛宝钗等
   - 主题：封建家族的兴衰、爱情悲剧

2. 《三国演义》
   - 作者：罗贯中
   - 朝代：元末明初
   - 主要人物：刘备、关羽、张飞、诸葛亮、曹操等
   - 主题：三国时期的政治军事斗争

3. 《西游记》
   - 作者：吴承恩
   - 朝代：明代
   - 主要人物：孙悟空、唐僧、猪八戒、沙僧等
   - 主题：取经路上的冒险故事

4. 《水浒传》
   - 作者：施耐庵
   - 朝代：元末明初
   - 主要人物：宋江、武松、林冲、鲁智深等
   - 主题：梁山好汉的反抗故事"""
    
    return classics


@tool
def get_book_info(book_name: str) -> str:
    """
    获取指定书籍的详细信息。
    
    参数：
    - book_name: 书名（红楼梦、三国演义、西游记、水浒传）
    
    返回：书籍的详细信息
    """
    books = {
        "红楼梦": {
            "作者": "曹雪芹、高鹗",
            "朝代": "清代",
            "章回数": "120回",
            "主要人物": "贾宝玉、林黛玉、薛宝钗、王熙凤、贾母等",
            "主题": "通过贾府的兴衰，展现封建社会的没落和人性的复杂",
            "别名": "石头记、金玉缘"
        },
        "三国演义": {
            "作者": "罗贯中",
            "朝代": "元末明初",
            "章回数": "120回",
            "主要人物": "刘备、关羽、张飞、诸葛亮、曹操、孙权等",
            "主题": "描写三国时期魏、蜀、吴三国的政治军事斗争",
            "别名": "三国志通俗演义"
        },
        "西游记": {
            "作者": "吴承恩",
            "朝代": "明代",
            "章回数": "100回",
            "主要人物": "孙悟空、唐僧、猪八戒、沙僧、白龙马等",
            "主题": "唐僧师徒四人西天取经的冒险故事",
            "别名": "西游释厄传"
        },
        "水浒传": {
            "作者": "施耐庵",
            "朝代": "元末明初",
            "章回数": "120回（或100回）",
            "主要人物": "宋江、武松、林冲、鲁智深、李逵等108将",
            "主题": "梁山好汉的反抗故事和兄弟情义",
            "别名": "忠义水浒传"
        }
    }
    
    # 模糊匹配书名
    for key in books.keys():
        if book_name in key or key in book_name:
            book = books[key]
            result = f"《{key}》详细信息：\n"
            for k, v in book.items():
                result += f"- {k}：{v}\n"
            return result
    
    return f"未找到'{book_name}'的信息。请输入：红楼梦、三国演义、西游记或水浒传。"


@tool
def query_character_relationship(char1: str, char2: str, book_name: str = "") -> str:
    """
    查询两个人物之间的关系。当用户询问两个人物的关系、联系、交往等信息时，必须使用此工具。
    
    适用场景：
    - 用户问"A和B是什么关系"
    - 用户问"A和B的关系"
    - 用户问"A与B有什么联系"
    - 用户提到两个人物名字并询问他们之间的关系
    
    参数：
    - char1: 第一个人物名字
    - char2: 第二个人物名字
    - book_name: 书名（可选，如：红楼梦、三国演义等）
    
    返回：两个人物之间的关系描述
    
    示例：
    - query_character_relationship("贾宝玉", "林黛玉") -> "贾宝玉和林黛玉是表兄妹关系，两人青梅竹马..."
    - query_character_relationship("刘备", "关羽", "三国演义") -> "刘备和关羽是结义兄弟..."
    """
    from app.core.rag import RAGManager
    
    try:
        print("\n" + "="*80)
        print("🔍 人物关系查询工具")
        print("="*80)
        print(f"📝 查询参数：")
        print(f"   - 人物1: {char1}")
        print(f"   - 人物2: {char2}")
        print(f"   - 书名: {book_name if book_name else '未指定'}")
        print()
        
        # 初始化 RAG
        print("🔧 初始化 RAG 检索器...")
        rag = RAGManager()
        retriever = rag.get_retriever()
        print("✅ RAG 检索器初始化完成")
        print()
        
        # 构建查询语句
        if book_name:
            query = f"{book_name} {char1} {char2} 关系"
        else:
            query = f"{char1} {char2} 关系"
        
        print(f"🔎 构建查询语句: \"{query}\"")
        print()
        
        # 检索相关文档
        print("📚 开始检索知识库...")
        docs = retriever.invoke(query)
        print(f"✅ 检索完成，找到 {len(docs)} 个相关文档")
        print()
        
        if not docs:
            print("❌ 未找到相关文档")
            print("="*80 + "\n")
            return f"未找到关于 {char1} 和 {char2} 关系的信息。"
        
        # 显示检索到的文档信息
        print("📄 检索到的文档详情：")
        for i, doc in enumerate(docs[:3], 1):
            source = doc.metadata.get('source', '未知')
            page = doc.metadata.get('page', '未知')
            content_preview = doc.page_content[:100].replace('\n', ' ')
            print(f"   {i}. 来源: {source}, 页码: {page}")
            print(f"      预览: {content_preview}...")
        print()
        
        # 提取相关内容
        print("📝 提取前 3 个最相关的文档内容...")
        context = "\n\n".join([doc.page_content for doc in docs[:3]])
        print(f"✅ 提取完成，总字符数: {len(context)}")
        print()
        
        # 检查是否真的包含两个人物
        print("🔍 验证内容是否包含两个人物...")
        char1_found = char1 in context
        char2_found = char2 in context
        print(f"   - {char1}: {'✅ 找到' if char1_found else '❌ 未找到'}")
        print(f"   - {char2}: {'✅ 找到' if char2_found else '❌ 未找到'}")
        print()
        
        if not char1_found and not char2_found:
            print("❌ 内容中没有同时提到两个人物")
            print("="*80 + "\n")
            return f"知识库中没有同时提到 {char1} 和 {char2} 的内容。"
        
        # 返回检索结果
        print("✂️ 截取内容（最多 500 字符）...")
        result = f"关于 {char1} 和 {char2} 的关系：\n\n{context[:500]}"
        
        if len(context) > 500:
            result += "...\n\n（内容较长，已截取部分）"
            print(f"✅ 内容已截取（原长度: {len(context)} -> 截取后: 500）")
        else:
            print(f"✅ 内容无需截取（长度: {len(context)}）")
        
        print()
        print("🎉 人物关系查询完成！")
        print("="*80 + "\n")
        
        return result
    
    except Exception as e:
        print(f"❌ 查询出错: {str(e)}")
        print("="*80 + "\n")
        return f"查询人物关系时出错：{str(e)}"


# 导出所有工具
def get_all_tools():
    """获取所有可用的工具"""
    return [
        calculator,
        get_current_time,
        count_characters,
        text_search,
        compare_numbers,
        list_four_classics,
        get_book_info,
        query_character_relationship,  # 新增
    ]


# 工具使用示例
if __name__ == "__main__":
    print("=== 工具测试 ===\n")
    
    # 测试计算器
    print("1. 计算器测试：")
    print(calculator.invoke({"expression": "2 + 2"}))
    print(calculator.invoke({"expression": "sqrt(16)"}))
    print()
    
    # 测试时间工具
    print("2. 时间工具测试：")
    print(get_current_time.invoke({"format_type": "datetime"}))
    print(get_current_time.invoke({"format_type": "date"}))
    print()
    
    # 测试四大名著工具
    print("3. 四大名著工具测试：")
    print(list_four_classics.invoke({}))
    print()
    print(get_book_info.invoke({"book_name": "红楼梦"}))
