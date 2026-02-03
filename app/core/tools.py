"""
Agent 工具集
包含各种实用工具，让 Agent 能够执行更多任务
"""

from langchain_core.tools import tool
from datetime import datetime
import math
import re
from typing import Optional
import os


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


@tool
def generate_id_photo(
    image_path: str,
    size: str = "1寸",
    background: str = "白色",
    remove_background: bool = True
) -> str:
    """
    生成证件照。用户上传照片后，可以生成指定尺寸和背景颜色的证件照。
    
    适用场景：
    - 用户要求生成证件照
    - 用户提到"1寸"、"2寸"等尺寸
    - 用户要求更换背景颜色
    
    参数：
    - image_path: 上传的图片路径（必需）。如果用户消息中包含"【系统提示】用户已上传图片，路径为：xxx"，请从中提取路径。
    - size: 证件照尺寸，支持：1寸、小1寸、2寸、小2寸、大1寸、护照、身份证、驾驶证、社保卡、教师资格证
    - background: 背景颜色，支持：白色、蓝色、红色、浅蓝
    - remove_background: 是否自动移除原背景（默认 True）
    
    返回：生成的证件照信息和下载链接
    
    重要提示：
    - 必须先确认用户已上传图片（消息中包含图片路径信息）
    - 如果没有图片路径，请提示用户先上传图片
    
    示例：
    - generate_id_photo("app/static/uploads/upload_123.jpg", "1寸", "白色") -> "已生成1寸白底证件照..."
    - generate_id_photo("app/static/uploads/upload_456.jpg", "2寸", "蓝色") -> "已生成2寸蓝底证件照..."
    """
    # 使用 HivisionIDPhotos 专业证件照生成器
    import os
    import json
    from app.core.id_photo_hivision import HivisionIDPhotoGenerator
    from PIL import Image
    
    try:
        # 调试：打印原始参数
        print(f"\n🔍 原始参数:")
        print(f"   image_path 类型: {type(image_path)}")
        print(f"   image_path 值: {repr(image_path[:100] if isinstance(image_path, str) else image_path)}")
        
        # 如果 image_path 是 JSON 字符串，尝试解析
        if isinstance(image_path, str) and image_path.strip().startswith('{'):
            print(f"   检测到 JSON 格式，尝试解析...")
            try:
                params = json.loads(image_path)
                image_path = params.get('image_path', image_path)
                size = params.get('size', size)
                background = params.get('background', background)
                remove_background = params.get('remove_background', remove_background)
                print(f"   ✅ JSON 解析成功")
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON 解析失败: {e}")
                pass  # 如果解析失败，继续使用原始值
        
        # 标准化背景颜色名称（支持中英文）
        background_map = {
            "白色": "white", "白": "white", "白底": "white",
            "蓝色": "blue", "蓝": "blue", "蓝底": "blue",
            "红色": "red", "红": "red", "红底": "red",
            "浅蓝": "light_blue", "浅蓝色": "light_blue",
        }
        background = background_map.get(background, background)
        
        print("\n" + "="*80)
        print("📸 证件照生成工具")
        print("="*80)
        print(f"📝 生成参数：")
        print(f"   - 图片路径: {image_path}")
        print(f"   - 尺寸: {size}")
        print(f"   - 背景: {background}")
        print(f"   - 移除背景: {remove_background}")
        print()
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            error_msg = f"""❌ 生成证件照失败：未找到图片文件 "{image_path}"。

请确认图片已正确上传。您可以：
1. 在右侧"证件照生成"区域上传照片
2. 上传成功后，再次告诉我您需要的证件照规格

例如："生成1寸白底证件照" 或 "生成2寸蓝底证件照"
"""
            return error_msg
        
        # 加载图片
        print(f"📂 加载图片...")
        input_image = Image.open(image_path)
        print(f"✅ 图片加载成功，尺寸: {input_image.size}")
        print()
        
        # 初始化生成器（使用 HivisionIDPhotos 专业实现）
        print(f"🔧 初始化生成器...")
        try:
            generator = HivisionIDPhotoGenerator()
            print(f"✅ 生成器初始化成功")
            print(f"   HivisionIDPhotos 可用: {generator.hivision_available}")
        except Exception as init_error:
            print(f"❌ 生成器初始化失败: {init_error}")
            import traceback
            traceback.print_exc()
            raise
        
        # 检查 rembg 是否可用
        rembg_available = False
        try:
            import rembg
            rembg_available = True
        except ImportError:
            pass
        
        # 生成证件照
        print(f"📸 开始生成证件照...")
        result_image, filepath = generator.generate(
            input_image,
            size_name=size,
            background_color=background,
            remove_bg=remove_background and rembg_available
        )
        
        # 生成下载链接（使用独立文件服务器）
        filename = os.path.basename(filepath)
        download_url = f"http://localhost:8000/photos/{filename}"
        
        print()
        print("🎉 证件照生成完成！")
        print("="*80 + "\n")
        
        # 准备背景提示
        bg_note = ""
        if remove_background and not rembg_available:
            bg_note = "\n\n⚠️ 注意：背景移除功能不可用（rembg 未完全安装），生成的照片保留了原始背景。如需更换背景，请安装完整依赖。"
        
        # 返回结果（包含绝对路径用于 Gradio 显示）
        result = f"""✅ Successfully generated {size} ID photo with {background} background!

📏 Size Info:
- Spec: {size}
- Pixels: {result_image.size[0]} x {result_image.size[1]} px
- Background: {background}

📥 Download: {download_url}

[IMAGE_PATH:{filepath}]{bg_note}

💡 Tip: You can request other sizes or background colors.
"""
        
        return result
        
    except Exception as e:
        print(f"❌ 生成失败: {str(e)}")
        print("="*80 + "\n")
        return f"❌ 生成证件照时出错：{str(e)}"


@tool
def list_id_photo_specs() -> str:
    """
    列出所有支持的证件照规格和背景颜色。
    
    返回：支持的尺寸和颜色列表
    """
    from app.core.id_photo_hivision import HivisionIDPhotoGenerator
    
    specs = """📸 证件照生成规格

### 支持的尺寸：
"""
    
    for size_name, (width, height) in HivisionIDPhotoGenerator.SIZES.items():
        specs += f"- **{size_name}**: {width} x {height} px\n"
    
    specs += "\n### 支持的背景颜色：\n"
    
    for color_name in HivisionIDPhotoGenerator.BACKGROUND_COLORS.keys():
        specs += f"- {color_name}\n"
    
    specs += """
### 使用方法：
1. 上传您的照片
2. 告诉我需要的尺寸（如"1寸"、"2寸"）
3. 选择背景颜色（如"白色"、"蓝色"）
4. 系统会自动生成并提供下载链接

💡 提示：系统会自动检测人脸位置并进行智能裁剪。
"""
    
    return specs


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
        query_character_relationship,
        generate_id_photo,  # 新增
        list_id_photo_specs,  # 新增
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
