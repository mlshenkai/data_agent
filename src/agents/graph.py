import os
from dotenv import load_dotenv 
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import matplotlib
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import pymysql
from langchain_tavily import TavilySearch
import os
import time
from datetime import datetime
 
# 加载环境变量
load_dotenv(override=True)
 
# ✅ 创建Tavily搜索工具
search_tool = TavilySearch(max_results=5, topic="general")
 
# ✅ 创建SQL查询工具
description = """
当用户需要进行数据库查询工作时，请调用该函数。
该函数用于在指定MySQL服务器上运行一段SQL代码，完成数据查询相关工作，
并且当前函数是使用pymsql连接MySQL数据库。
本函数只负责运行SQL代码并进行数据查询，若要进行数据提取，则使用另一个extract_data函数。
"""
 
# 定义结构化参数模型
class SQLQuerySchema(BaseModel):
    sql_query: str = Field(description=description)
 
# 封装为 LangGraph 工具
@tool(args_schema=SQLQuerySchema)
def sql_inter(sql_query: str) -> str:
    """
    当用户需要进行数据库查询工作时，请调用该函数。
    该函数用于在指定MySQL服务器上运行一段SQL代码，完成数据查询相关工作，
    并且当前函数是使用pymsql连接MySQL数据库。
    本函数只负责运行SQL代码并进行数据查询，若要进行数据提取，则使用另一个extract_data函数。
    :param sql_query: 字符串形式的SQL查ppadfs询语句，用于执行对MySQL中telco_db数据库中各张表进行查询，并获得各表中的各类相关信息
    :return：sql_query在MySQL中的运行结果。   
    """
    # print("正在调用 sql_inter 工具运行 SQL 查询...")
     
    # 加载环境变量
    load_dotenv(override=True)
    host = os.getenv('HOST')
    user = os.getenv('USER')
    mysql_pw = os.getenv('MYSQL_PW')
    db = os.getenv('DB_NAME')
    port = os.getenv('PORT')
     
    # 创建连接
    connection = pymysql.connect(
        host=host,
        user=user,
        passwd=mysql_pw,
        db=db,
        port=int(port),
        charset='utf8'
    )
     
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            results = cursor.fetchall()
            # print("SQL 查询已成功执行，正在整理结果...")
    finally:
        connection.close()
 
    # 将结果以 JSON 字符串形式返回
    return json.dumps(results, ensure_ascii=False)
 
# ✅ 创建数据提取工具
# 定义结构化参数
class ExtractQuerySchema(BaseModel):
    sql_query: str = Field(description="用于从 MySQL 提取数据的 SQL 查询语句。")
    df_name: str = Field(description="指定用于保存结果的 pandas 变量名称（字符串形式）。")
 
# 注册为 Agent 工具
@tool(args_schema=ExtractQuerySchema)
def extract_data(sql_query: str, df_name: str) -> str:
    """
    用于在MySQL数据库中提取一张表到当前Python环境中，注意，本函数只负责数据表的提取，
    并不负责数据查询，若需要在MySQL中进行数据查询，请使用sql_inter函数。
    同时需要注意，编写外部函数的参数消息时，必须是满足json格式的字符串，
    :param sql_query: 字符串形式的SQL查询语句，用于提取MySQL中的某张表。
    :param df_name: 将MySQL数据库中提取的表格进行本地保存时的变量名，以字符串形式表示。
    :return：表格读取和保存结果
    """
    print("正在调用 extract_data 工具运行 SQL 查询...")
     
    load_dotenv(override=True)
    host = os.getenv('HOST')
    user = os.getenv('USER')
    mysql_pw = os.getenv('MYSQL_PW')
    db = os.getenv('DB_NAME')
    port = os.getenv('PORT')
 
    # 创建数据库连接
    connection = pymysql.connect(
        host=host,
        user=user,
        passwd=mysql_pw,
        db=db,
        port=int(port),
        charset='utf8'
    )
 
    try:
        # 执行 SQL 并保存为全局变量
        df = pd.read_sql(sql_query, connection)
        globals()[df_name] = df
        # print("数据成功提取并保存为全局变量：", df_name)
        return f"✅ 成功创建 pandas 对象 `{df_name}`，包含从 MySQL 提取的数据。"
    except Exception as e:
        return f"❌ 执行失败：{e}"
    finally:
        connection.close()
 
# ✅创建Python代码执行工具
# Python代码执行工具结构化参数说明
class PythonCodeInput(BaseModel):
    py_code: str = Field(description="一段合法的 Python 代码字符串，例如 '2 + 2' 或 'x = 3\\ny = x * 2'")
 
@tool(args_schema=PythonCodeInput)
def python_inter(py_code):
    """
    当用户需要编写Python程序并执行时，请调用该函数。
    该函数可以执行一段Python代码并返回最终结果，需要注意，本函数只能执行非绘图类的代码，若是绘图相关代码，则需要调用fig_inter函数运行。
    """   
    g = globals()
    try:
        # 尝试如果是表达式，则返回表达式运行结果
        return str(eval(py_code, g))
    # 若报错，则先测试是否是对相同变量重复赋值
    except Exception as e:
        global_vars_before = set(g.keys())
        try:            
            exec(py_code, g)
        except Exception as e:
            return f"代码执行时报错{e}"
        global_vars_after = set(g.keys())
        new_vars = global_vars_after - global_vars_before
        # 若存在新变量
        if new_vars:
            result = {var: g[var] for var in new_vars}
            # print("代码已顺利执行，正在进行结果梳理...")
            return str(result)
        else:
            # print("代码已顺利执行，正在进行结果梳理...")
            return "已经顺利执行代码"
 
# ✅ 创建绘图工具
# 绘图工具结构化参数说明
class FigCodeInput(BaseModel):
    py_code: str = Field(description="要执行的 Python 绘图代码，必须使用 matplotlib/seaborn 创建图像并赋值给变量")
    fname: str = Field(description="图像对象的变量名，例如 'fig'，用于从代码中提取并保存为图片")
 
@tool(args_schema=FigCodeInput)
def fig_inter(py_code: str, fname: str) -> str:
    """
    当用户需要使用 Python 进行可视化绘图任务时，请调用该函数。
 
    注意：
    1. 所有绘图代码必须创建一个图像对象，并将其赋值为指定变量名（例如 `fig`）。
    2. 必须使用 `fig = plt.figure()` 或 `fig = plt.subplots()`。
    3. 不要使用 `plt.show()`。
    4. 请确保代码最后调用 `fig.tight_layout()`。
    5. 所有绘图代码中，坐标轴标签（xlabel、ylabel）、标题（title）、图例（legend）等文本内容，必须使用英文描述。
 
    示例代码：
    fig = plt.figure(figsize=(10,6))
    plt.plot([1,2,3], [4,5,6])
    fig.tight_layout()
    """
    # print("正在调用fig_inter工具运行Python代码...")
 
    # 保存当前matplotlib后端
    current_backend = matplotlib.get_backend()
    
    # 在macOS上强制使用Agg后端，避免线程问题
    import platform
    if platform.system() == 'Darwin':  # macOS
        matplotlib.use('Agg')
    else:
        matplotlib.use('Agg')  # 其他系统也使用Agg后端
 
    local_vars = {"plt": plt, "pd": pd, "sns": sns}
     
    # 动态设置图片保存路径（支持不同操作系统）
    current_dir = os.getcwd()
    
    # 尝试多个可能的图片保存路径
    possible_paths = [
        os.path.join(current_dir, "frontend", "public", "images"),
        os.path.join(current_dir, "public", "images"),
        os.path.join(current_dir, "images"),
        os.path.join(current_dir, "static", "images")
    ]
    
    images_dir = None
    for path in possible_paths:
        try:
            if os.path.exists(path) or os.access(os.path.dirname(path), os.W_OK):
                images_dir = path
                break
        except:
            continue
    
    # 如果找不到合适的路径，使用当前目录下的images文件夹
    if images_dir is None:
        images_dir = os.path.join(current_dir, "images")
    
    # 创建图片目录
    try:
        os.makedirs(images_dir, exist_ok=True)
    except Exception as e:
        return f"❌ 无法创建图片目录 {images_dir}：{str(e)}"
    
    try:
        g = globals()
        exec(py_code, g, local_vars)
        g.update(local_vars)
 
        fig = local_vars.get(fname, None)
        if fig:
            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{fname}_{timestamp}.png"
            abs_path = os.path.join(images_dir, image_filename)  # ✅ 绝对路径
            rel_path = os.path.join("images", image_filename)    # ✅ 返回相对路径（给前端用）
 
            fig.savefig(abs_path, bbox_inches='tight')
            return f"✅ 图片已保存，路径为: {rel_path}"
        else:
            return "⚠️ 图像对象未找到，请确认变量名正确并为 matplotlib 图对象。"
    except Exception as e:
        return f"❌ 执行失败：{e}"
    finally:
        plt.close('all')
        matplotlib.use(current_backend)
 
# ✅ 创建文件读取工具
# 文件读取工具结构化参数说明
class ReadFileSchema(BaseModel):
    file_path: str = Field(description="文件路径，支持相对路径和绝对路径")
    file_type: str = Field(description="文件类型（可选，自动检测）", default="auto")
    read_params: dict = Field(description="读取参数（可选）", default={})
    df_name: str = Field(description="保存的变量名，用于后续分析")
    preview_lines: int = Field(description="预览行数（可选，0表示不预览）", default=5)
    get_file_info: bool = Field(description="是否获取文件信息", default=True)

@tool(args_schema=ReadFileSchema)
def read_file(file_path: str, file_type: str = "auto", read_params: dict = {}, 
              df_name: str = "", preview_lines: int = 5, get_file_info: bool = True) -> str:
    """
    当用户需要读取本地文件时，请调用该函数。
    该函数支持多种文件格式的读取，包括CSV、Excel、JSON、Parquet、文本文件、XML、HTML、SQL、Pickle等。
    
    支持的文件格式：
    - CSV文件 (.csv)
    - Excel文件 (.xlsx, .xls)
    - JSON文件 (.json)
    - Parquet文件 (.parquet)
    - 文本文件 (.txt)
    - XML文件 (.xml)
    - HTML文件 (.html, .htm)
    - SQL文件 (.sql)
    - Pickle文件 (.pkl, .pickle)
    - 其他pandas支持的格式
    
    新增功能：
    1. 文件预览：显示前N行数据
    2. 文件信息：显示文件大小、修改时间、编码等信息
    3. 更多格式支持：XML、HTML、SQL、Pickle
    4. 增强错误处理：提供更详细的错误信息
    5. 编码自动检测：自动检测文件编码
    
    注意：
    1. 文件路径可以是相对路径或绝对路径
    2. 如果不指定file_type，将根据文件扩展名自动检测
    3. read_params可以包含pandas读取函数的额外参数
    4. 读取的数据将保存为全局变量，变量名为df_name
    5. preview_lines设置预览行数，0表示不预览
    6. get_file_info控制是否显示文件信息
    
    示例：
    - 读取CSV文件：file_path="data.csv", df_name="df", preview_lines=10
    - 读取Excel文件：file_path="data.xlsx", df_name="excel_data", get_file_info=True
    - 读取JSON文件：file_path="data.json", df_name="json_data"
    - 读取XML文件：file_path="data.xml", df_name="xml_data"
    """
    
    try:
        # 处理前端上传的文件路径
        if file_path.startswith("uploads/"):
            # 前端上传的文件在frontend/public/uploads/目录下
            current_dir = os.getcwd()
            # 尝试多个可能的路径
            possible_paths = [
                os.path.join(current_dir, "frontend", "public", file_path),
                os.path.join(current_dir, "public", file_path),
                os.path.join(current_dir, file_path),
            ]
            
            # 找到第一个存在的文件路径
            actual_file_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    actual_file_path = path
                    break
            
            if actual_file_path is None:
                return f"❌ 文件不存在：{file_path}。尝试的路径：{', '.join(possible_paths)}"
            
            file_path = actual_file_path
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return f"❌ 文件不存在：{file_path}"
        
        # 获取文件信息
        file_info = ""
        if get_file_info:
            try:
                stat = os.stat(file_path)
                file_size = stat.st_size
                modified_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                
                # 格式化文件大小
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                elif file_size < 1024 * 1024 * 1024:
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
                else:
                    size_str = f"{file_size / (1024 * 1024 * 1024):.1f} GB"
                
                file_info = f"📁 文件信息：\n- 大小：{size_str}\n- 修改时间：{modified_time}\n"
                
                # 尝试检测编码（仅对文本文件）
                file_extension = os.path.splitext(file_path)[1].lower()
                text_extensions = ['.csv', '.txt', '.json', '.xml', '.html', '.htm', '.sql']
                if file_extension in text_extensions:
                    try:
                        import chardet
                        with open(file_path, 'rb') as f:
                            raw_data = f.read(10000)  # 读取前10KB进行编码检测
                            encoding_result = chardet.detect(raw_data)
                            if encoding_result['encoding']:
                                file_info += f"- 编码：{encoding_result['encoding']} (置信度: {encoding_result['confidence']:.2f})\n"
                    except ImportError:
                        file_info += "- 编码：未检测（需要安装chardet库）\n"
                    except Exception:
                        file_info += "- 编码：检测失败\n"
                
            except Exception as e:
                file_info = f"⚠️ 无法获取文件信息：{str(e)}\n"
        
        # 获取文件扩展名
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # 如果未指定文件类型，根据扩展名自动检测
        if file_type == "auto":
            if file_extension == ".csv":
                file_type = "csv"
            elif file_extension in [".xlsx", ".xls"]:
                file_type = "excel"
            elif file_extension == ".json":
                file_type = "json"
            elif file_extension == ".parquet":
                file_type = "parquet"
            elif file_extension == ".txt":
                file_type = "text"
            elif file_extension == ".xml":
                file_type = "xml"
            elif file_extension in [".html", ".htm"]:
                file_type = "html"
            elif file_extension == ".sql":
                file_type = "sql"
            elif file_extension in [".pkl", ".pickle"]:
                file_type = "pickle"
            else:
                return f"❌ 不支持的文件格式：{file_extension}。支持的格式：CSV, Excel, JSON, Parquet, TXT, XML, HTML, SQL, Pickle"
        
        # 根据文件类型读取数据
        df = None
        read_method = ""
        
        if file_type == "csv":
            df = pd.read_csv(file_path, **read_params)
            read_method = "pd.read_csv()"
        elif file_type == "excel":
            df = pd.read_excel(file_path, **read_params)
            read_method = "pd.read_excel()"
        elif file_type == "json":
            df = pd.read_json(file_path, **read_params)
            read_method = "pd.read_json()"
        elif file_type == "parquet":
            df = pd.read_parquet(file_path, **read_params)
            read_method = "pd.read_parquet()"
        elif file_type == "text":
            df = pd.read_table(file_path, **read_params)
            read_method = "pd.read_table()"
        elif file_type == "xml":
            try:
                df = pd.read_xml(file_path, **read_params)
                read_method = "pd.read_xml()"
            except ImportError:
                return f"❌ 读取XML文件需要安装lxml库。请运行：pip install lxml"
            except Exception as e:
                return f"❌ XML文件读取失败：{str(e)}。请检查XML格式是否正确。"
        elif file_type == "html":
            try:
                tables = pd.read_html(file_path, **read_params)
                if len(tables) == 0:
                    return f"❌ HTML文件中未找到表格数据"
                elif len(tables) == 1:
                    df = tables[0]
                else:
                    df = tables[0]  # 默认取第一个表格
                    file_info += f"⚠️ HTML文件包含{len(tables)}个表格，已加载第一个表格\n"
                read_method = "pd.read_html()"
            except ImportError:
                return f"❌ 读取HTML文件需要安装lxml和beautifulsoup4库。请运行：pip install lxml beautifulsoup4"
            except Exception as e:
                return f"❌ HTML文件读取失败：{str(e)}。请检查HTML格式是否正确。"
        elif file_type == "sql":
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                # SQL文件通常包含查询语句，这里返回SQL内容而不是执行
                return f"✅ 成功读取SQL文件 `{file_path}`\n{file_info}📝 SQL内容：\n```sql\n{sql_content[:1000]}{'...' if len(sql_content) > 1000 else ''}\n```\n💡 提示：SQL文件已读取，请使用sql_inter工具执行其中的查询语句。"
            except Exception as e:
                return f"❌ SQL文件读取失败：{str(e)}"
        elif file_type == "pickle":
            try:
                df = pd.read_pickle(file_path)
                read_method = "pd.read_pickle()"
            except Exception as e:
                return f"❌ Pickle文件读取失败：{str(e)}。请确认文件格式正确。"
        else:
            return f"❌ 不支持的文件类型：{file_type}。支持的类型：csv, excel, json, parquet, text, xml, html, sql, pickle"
        
        # 如果是SQL文件，已经在上面处理并返回
        if file_type == "sql":
            return  # 这行不会执行，但保持代码清晰
        
        # 检查读取结果
        if df is None:
            return f"❌ 数据读取失败，返回空值"
        
        # 构建结果消息
        result_msg = f"✅ 成功读取文件 `{file_path}`（使用{read_method}）\n"
        result_msg += file_info
        result_msg += f"📊 数据概览：\n- 形状：{df.shape}（{df.shape[0]}行，{df.shape[1]}列）\n"
        result_msg += f"- 列名：{list(df.columns)}\n"
        
        # 数据类型信息
        if hasattr(df, 'dtypes'):
            dtype_info = df.dtypes.value_counts()
            result_msg += f"- 数据类型：{dict(dtype_info)}\n"
        
        # 文件预览
        if preview_lines > 0:
            try:
                preview_df = df.head(preview_lines)
                result_msg += f"\n🔍 数据预览（前{preview_lines}行）：\n"
                result_msg += preview_df.to_string(max_cols=10, max_colwidth=20)
                
                if df.shape[0] > preview_lines:
                    result_msg += f"\n... （还有{df.shape[0] - preview_lines}行数据）"
            except Exception as e:
                result_msg += f"\n⚠️ 数据预览失败：{str(e)}"
        
        # 保存为全局变量
        if df_name:
            globals()[df_name] = df
            result_msg += f"\n💾 数据已保存为变量 `{df_name}`，可用于后续分析。"
        else:
            result_msg += f"\n💡 提示：未指定变量名，数据未保存。如需保存请指定df_name参数。"
            
        return result_msg
            
    except FileNotFoundError:
        return f"❌ 文件未找到：{file_path}。请检查文件路径是否正确。"
    except PermissionError:
        return f"❌ 没有权限访问文件：{file_path}。请检查文件权限。"
    except pd.errors.EmptyDataError:
        return f"❌ 文件为空或格式不正确：{file_path}"
    except pd.errors.ParserError as e:
        return f"❌ 文件解析错误：{str(e)}。请检查文件格式是否正确。"
    except UnicodeDecodeError as e:
        return f"❌ 文件编码错误：{str(e)}。请尝试指定正确的编码参数，如：read_params={{'encoding': 'gbk'}}"
    except Exception as e:
        return f"❌ 读取文件时发生未知错误：{str(e)}。请检查文件格式和内容是否正确。"
 
# ✅ 创建优化图片生成工具
# 优化图片生成工具结构化参数说明
class OptimizedFigCodeInput(BaseModel):
    py_code: str = Field(description="要执行的 Python 绘图代码，必须使用 matplotlib/seaborn 创建图像并赋值给变量")
    fname: str = Field(description="图像对象的变量名，例如 'fig'，用于从代码中提取并保存为图片")
    format: str = Field(description="输出格式（png, jpg, jpeg, svg, pdf, webp）", default="png")
    dpi: int = Field(description="图片分辨率", default=300)
    quality: int = Field(description="图片质量（JPG/WebP格式，1-100）", default=95)
    optimize: bool = Field(description="是否优化图片", default=True)
    figsize: str = Field(description="图片尺寸，格式为'width,height'，例如'10,6'", default=None)
    auto_resize: bool = Field(description="是否自动调整图片尺寸以适应内容", default=False)
    webp_quality: int = Field(description="WebP格式专用质量参数（1-100，仅WebP格式使用）", default=85)
    compression_level: int = Field(description="PNG压缩级别（0-9，0无压缩，9最大压缩）", default=6)
    add_metadata: bool = Field(description="是否添加图片元数据", default=True)

@tool(args_schema=OptimizedFigCodeInput)
def optimized_fig_inter(py_code: str, fname: str, format: str = "png", dpi: int = 300, 
                       quality: int = 95, optimize: bool = True, figsize: str = None,
                       auto_resize: bool = False, webp_quality: int = 85, 
                       compression_level: int = 6, add_metadata: bool = True) -> str:
    """
    当用户需要进行高质量图片生成和优化时，请调用该函数。
    这是fig_inter工具的增强版本，提供更多图片质量控制选项和格式支持。
    
    功能特性：
    - 支持多种图片格式（PNG、JPG、JPEG、SVG、PDF、WebP）
    - 图片质量控制（DPI、压缩率、质量参数）
    - 高级压缩优化（支持WebP格式的高效压缩）
    - 动态路径处理（支持不同操作系统）
    - 自定义图片尺寸和自动调整
    - 图片元数据设置
    - 增强错误处理和诊断信息
    
    新增功能：
    1. WebP格式支持：提供更好的压缩比和质量
    2. 自动尺寸调整：根据内容自动优化图片尺寸
    3. 增强压缩算法：针对不同格式的优化策略
    4. 图片元数据：添加创建时间、工具信息等元数据
    5. 详细错误诊断：提供更准确的错误信息和建议
    
    注意：
    1. 所有绘图代码必须创建一个图像对象，并将其赋值为指定变量名（例如 `fig`）。
    2. 必须使用 `fig = plt.figure()` 或 `fig = plt.subplots()`。
    3. 不要使用 `plt.show()`。
    4. 请确保代码最后调用 `fig.tight_layout()`。
    5. 所有绘图代码中，坐标轴标签（xlabel、ylabel）、标题（title）、图例（legend）等文本内容，必须使用英文描述。
    
    参数说明：
    - format: 输出格式，支持 png, jpg, jpeg, svg, pdf, webp
    - dpi: 图片分辨率，默认300
    - quality: JPG/WebP格式的图片质量，1-100，默认95
    - optimize: 是否优化图片，默认True
    - figsize: 图片尺寸，格式为'width,height'，例如'10,6'
    - auto_resize: 是否自动调整图片尺寸以适应内容
    - webp_quality: WebP专用质量参数，通常比JPG质量参数低10-15
    - compression_level: PNG压缩级别，0-9
    - add_metadata: 是否添加图片元数据
    
    示例代码：
    fig = plt.figure(figsize=(10,6))
    plt.plot([1,2,3], [4,5,6])
    fig.tight_layout()
    """
    import matplotlib
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns
    import os
    from datetime import datetime
    
    try:
        # 验证和规范化格式参数
        format = format.lower()
        supported_formats = ['png', 'jpg', 'jpeg', 'svg', 'pdf', 'webp']
        if format not in supported_formats:
            return f"❌ 不支持的图片格式：{format}。支持的格式：{', '.join(supported_formats)}"
        
        # 保存当前matplotlib后端
        current_backend = matplotlib.get_backend()
        matplotlib.use('Agg')
        
        # 设置本地变量
        local_vars = {"plt": plt, "pd": pd, "sns": sns}
        
        # 动态设置图片保存路径（支持不同操作系统）
        current_dir = os.getcwd()
        
        # 尝试多个可能的图片保存路径
        possible_paths = [
            os.path.join(current_dir, "frontend", "public", "images"),
            os.path.join(current_dir, "public", "images"),
            os.path.join(current_dir, "images"),
            os.path.join(current_dir, "static", "images")
        ]
        
        images_dir = None
        for path in possible_paths:
            try:
                if os.path.exists(path) or os.access(os.path.dirname(path), os.W_OK):
                    images_dir = path
                    break
            except:
                continue
        
        # 如果找不到合适的路径，使用当前目录下的images文件夹
        if images_dir is None:
            images_dir = os.path.join(current_dir, "images")
        
        # 创建图片目录
        try:
            os.makedirs(images_dir, exist_ok=True)
        except Exception as e:
            return f"❌ 无法创建图片目录 {images_dir}：{str(e)}"
        
        # 处理图片尺寸参数
        original_figsize = None
        if figsize:
            try:
                width, height = map(float, figsize.split(','))
                original_figsize = (width, height)
                # 在绘图代码中设置图片尺寸
                if 'plt.figure(' not in py_code and 'plt.subplots(' not in py_code:
                    py_code = f"plt.figure(figsize=({width}, {height}))\n" + py_code
            except Exception as e:
                return f"❌ 图片尺寸参数解析失败：{str(e)}。请使用格式 'width,height'，例如 '10,6'"
        
        try:
            # 执行绘图代码
            g = globals()
            exec(py_code, g, local_vars)
            g.update(local_vars)
            
            fig = local_vars.get(fname, None)
            if fig is None:
                available_vars = [k for k, v in local_vars.items() if hasattr(v, 'savefig')]
                if available_vars:
                    return f"⚠️ 未找到变量名 '{fname}' 的图像对象。可用的图像变量：{available_vars}"
                else:
                    return f"❌ 未找到任何图像对象。请确认代码中创建了图像对象并赋值给变量 '{fname}'"
            
            # 验证是否为有效的matplotlib图像对象
            if not hasattr(fig, 'savefig'):
                return f"❌ 变量 '{fname}' 不是有效的 matplotlib 图像对象"
            
            # 自动调整图片尺寸
            if auto_resize:
                try:
                    fig.tight_layout(pad=1.0)
                    # 获取图像的实际边界
                    bbox = fig.get_tightbbox()
                    if bbox and original_figsize:
                        # 根据内容调整尺寸
                        aspect_ratio = bbox.width / bbox.height
                        if aspect_ratio > 1:  # 宽图
                            new_width = original_figsize[0]
                            new_height = new_width / aspect_ratio
                        else:  # 高图
                            new_height = original_figsize[1]
                            new_width = new_height * aspect_ratio
                        fig.set_size_inches(new_width, new_height)
                except Exception as e:
                    # 自动调整失败不影响主流程
                    pass
            
            # 生成带时间戳的图片文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{fname}_{timestamp}.{format}"
            abs_path = os.path.join(images_dir, image_filename)
            rel_path = os.path.join("images", image_filename)
            
            # 根据格式设置保存参数
            save_kwargs = {
                'dpi': dpi,
                'bbox_inches': 'tight',
                'pad_inches': 0.1
            }
            
            # 添加格式特定参数
            if format in ['jpg', 'jpeg']:
                save_kwargs['quality'] = quality
                # JPG不支持透明度
                save_kwargs['facecolor'] = 'white'
            elif format == 'png':
                # matplotlib的savefig不支持optimize参数，需要在后处理中优化
                pass
            elif format == 'webp':
                save_kwargs['quality'] = webp_quality
            elif format == 'pdf':
                save_kwargs['metadata'] = {
                    'Title': f'Generated by optimized_fig_inter',
                    'Creator': 'Data Agent - Enhanced Figure Tool',
                    'CreationDate': datetime.now()
                } if add_metadata else None
            
            # 保存图片
            try:
                fig.savefig(abs_path, **save_kwargs)
            except Exception as e:
                return f"❌ 图片保存失败：{str(e)}。请检查文件路径权限和磁盘空间"
            
            # 获取保存后的文件信息
            try:
                file_size = os.path.getsize(abs_path)
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
            except:
                size_str = "未知"
            
            # 后处理优化（针对支持的格式）
            optimization_info = ""
            if optimize and format in ['png', 'jpg', 'jpeg', 'webp']:
                try:
                    from PIL import Image
                    original_size = os.path.getsize(abs_path)
                    
                    with Image.open(abs_path) as img:
                        # 针对不同格式的优化策略
                        if format == 'png':
                            # PNG格式使用optimize参数，compress_level在某些版本中可能不支持
                            img.save(abs_path, optimize=True)
                        elif format in ['jpg', 'jpeg']:
                            img.save(abs_path, quality=quality, optimize=True)
                        elif format == 'webp':
                            img.save(abs_path, 'WEBP', quality=webp_quality, optimize=True)
                        
                        # 添加元数据
                        if add_metadata and format in ['jpg', 'jpeg']:
                            # 对于JPEG，使用exif添加元数据
                            pass  # 简化版本暂不实现复杂元数据
                    
                    optimized_size = os.path.getsize(abs_path)
                    if optimized_size < original_size:
                        compression_ratio = ((original_size - optimized_size) / original_size) * 100
                        optimization_info = f"\n🗜️ 压缩优化：减少 {compression_ratio:.1f}% 文件大小"
                
                except ImportError:
                    optimization_info = "\n💡 提示：安装Pillow库可获得更好的图片压缩效果"
                except Exception as e:
                    optimization_info = f"\n⚠️ 后处理优化失败：{str(e)}"
            
            # 构建成功消息
            result_msg = f"✅ 高质量图片已生成并保存\n"
            result_msg += f"📁 路径：{rel_path}\n"
            result_msg += f"🎨 格式：{format.upper()}"
            result_msg += f" | 分辨率：{dpi} DPI"
            if format in ['jpg', 'jpeg', 'webp']:
                actual_quality = webp_quality if format == 'webp' else quality
                result_msg += f" | 质量：{actual_quality}"
            result_msg += f" | 大小：{size_str}"
            result_msg += optimization_info
            
            if auto_resize:
                result_msg += f"\n📐 已启用自动尺寸调整"
            
            return result_msg
            
        except SyntaxError as e:
            return f"❌ Python代码语法错误：{str(e)}。请检查代码语法"
        except NameError as e:
            return f"❌ 变量或函数未定义：{str(e)}。请确认所需的库和变量已导入"
        except Exception as e:
            return f"❌ 图片生成过程中发生错误：{str(e)}"
            
    except Exception as e:
        return f"❌ 执行失败：{str(e)}"
    finally:
        plt.close('all')
        matplotlib.use(current_backend)
 
# ✅ 创建提示词模板
prompt = """
你是一名经验丰富的智能数据分析助手，擅长帮助用户高效完成以下任务：

1. **本地文件读取（增强版）：**
   - 当用户需要读取本地文件时，请调用`read_file`工具，该工具支持多种文件格式包括CSV、Excel、JSON、Parquet、文本文件、XML、HTML、SQL、Pickle等。
   - 新增功能：文件预览（preview_lines参数）、文件信息获取（大小、修改时间、编码检测）、自动编码检测。
   - 该工具会自动检测文件格式和编码，支持自定义读取参数，并将数据保存为pandas变量供后续分析使用。
   - 示例：
     * 基础读取：file_path="data.csv", df_name="df"
     * 带预览：file_path="data.xlsx", df_name="excel_data", preview_lines=10
     * XML文件：file_path="data.xml", df_name="xml_data", get_file_info=True
     * SQL文件：file_path="queries.sql"（将显示SQL内容，需用sql_inter执行）
 
2. **数据库查询：**
   - 当用户需要获取数据库中某些数据或进行SQL查询时，请调用`sql_inter`工具，该工具已经内置了pymysql连接MySQL数据库的全部参数，包括数据库名称、用户名、密码、端口等，你只需要根据用户需求生成SQL语句即可。
   - 你需要准确根据用户请求生成SQL语句，例如 `SELECT * FROM 表名` 或包含条件的查询。
 
3. **数据表提取：**
   - 当用户希望将数据库中的表格导入Python环境进行后续分析时，请调用`extract_data`工具。
   - 你需要根据用户提供的表名或查询条件生成SQL查询语句，并将数据保存到指定的pandas变量中。
 
4. **非绘图类任务的Python代码执行：**
   - 当用户需要执行Python脚本或进行数据处理、统计计算时，请调用`python_inter`工具。
   - 仅限执行非绘图类代码，例如变量定义、数据分析等。
 
5. **绘图类Python代码执行（增强版）：**
   - 当用户需要进行可视化展示（如生成图表、绘制分布等）时：
     * 基础绘图：使用`fig_inter`工具（简单快速）
     * 高质量绘图：使用`optimized_fig_inter`工具（推荐）
   - `optimized_fig_inter`新增功能：
     * 支持6种格式：PNG、JPG、JPEG、SVG、PDF、WebP
     * WebP格式：更好的压缩比和质量（webp_quality参数）
     * 自动尺寸调整：auto_resize=True根据内容优化图片尺寸
     * 高级压缩：compression_level控制PNG压缩级别
     * 图片元数据：add_metadata=True添加创建信息
   - 你可以直接读取数据并进行绘图，不需要借助`python_inter`工具读取图片。
   - 你应根据用户需求编写绘图代码，并正确指定绘图对象变量名（如 `fig`）。
   - 当你生成Python绘图代码时必须指明图像的名称，如fig = plt.figure()或fig = plt.subplots()创建图像对象，并赋值为fig。
   - 不要调用plt.show()，否则图像将无法保存。
   - 绘图示例：
     * 基础绘图：format="png", dpi=300
     * 高质量WebP：format="webp", webp_quality=85, optimize=True
     * 自适应尺寸：auto_resize=True, figsize="12,8"
 
6. **网络搜索：**
   - 当用户提出与数据分析无关的问题（如最新新闻、实时信息），请调用`search_tool`工具。
 
**工具使用优先级和最佳实践：**
- 文件读取：优先使用`read_file`工具（支持更多格式和功能）
- 图片生成：优先使用`optimized_fig_inter`工具（质量更高，功能更丰富）
- 如需本地文件数据，请先使用`read_file`工具读取文件，再执行Python分析或绘图
- 如需数据库数据，请先使用`sql_inter`或`extract_data`获取，再执行Python分析或绘图
- 如需绘图，请先确保数据已加载为pandas对象
- 对于大文件，建议先预览（preview_lines=5）确认格式正确
- 对于高质量图片需求，建议使用WebP格式以获得更好的压缩效果
 
**回答要求：**
- 所有回答均使用**简体中文**，清晰、礼貌、简洁。
- 如果调用工具返回结构化JSON数据，你应提取其中的关键信息简要说明，并展示主要结果。
- 若需要用户提供更多信息，请主动提出明确的问题。
- 如果有生成的图片文件，请务必在回答中使用Markdown格式插入图片，如：![图表标题](images/fig.png)
- 不要仅输出图片路径文字。
- 充分利用新功能：文件预览、编码检测、WebP格式、自动尺寸调整等。
 
**风格：**
- 专业、简洁、以数据驱动。
- 不要编造不存在的工具或数据。
- 主动推荐最适合的工具和参数配置。
 
请根据以上原则为用户提供精准、高效的协助。
"""
 
# ✅ 创建工具列表
tools = [search_tool, python_inter, fig_inter, optimized_fig_inter, sql_inter, extract_data, read_file]
 
# ✅ 创建模型
model = ChatOpenAI(model="ep-20250418165946-fjjmv")
 
# ✅ 创建图 （Agent）
graph = create_react_agent(model=model, tools=tools, prompt=prompt)