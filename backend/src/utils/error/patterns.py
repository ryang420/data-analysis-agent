"""
错误模式匹配表

统一管理所有错误关键词到错误码的映射，避免在多个函数中重复定义匹配逻辑。
"""

from typing import List, Tuple, Optional
from .codes import ErrorCode


ErrorPattern = Tuple[List[str], int, str]

ERROR_PATTERNS: List[ErrorPattern] = [
    # ==================== 数据库相关错误 ====================
    (['adminshutdown', 'terminating connection due to administrator command'],
     ErrorCode.INTEGRATION_DB_ADMIN_SHUTDOWN, "数据库连接被管理员关闭"),
    (['ssl connection has been closed unexpectedly'],
     ErrorCode.INTEGRATION_DB_SSL_CLOSED, "数据库SSL连接意外关闭"),
    (['pooltimeout', "couldn't get a connection"],
     ErrorCode.INTEGRATION_DB_POOL_TIMEOUT, "数据库连接池超时"),
    (['the connection is closed'],
     ErrorCode.INTEGRATION_DB_CONNECTION, "数据库连接已关闭"),
    (['psycopg2', 'postgresql'],
     ErrorCode.INTEGRATION_DB_QUERY, "数据库错误"),

    # ==================== 网络相关错误 ====================
    (['broken pipe', 'errno 32'],
     ErrorCode.API_NETWORK_BROKEN_PIPE, "网络管道断开"),
    (['remoteprotocolerror'],
     ErrorCode.API_NETWORK_REMOTE_PROTOCOL, "远程协议错误"),
    (['error while downloading'],
     ErrorCode.RESOURCE_S3_DOWNLOAD_FAILED, "文件下载失败"),
    (['nosuchkey', 'specified key does not exist'],
     ErrorCode.RESOURCE_S3_DOWNLOAD_FAILED, "S3对象不存在"),
    (['max retries exceeded', 'connectionpool'],
     ErrorCode.API_NETWORK_CONNECTION, "网络连接失败"),
    (['server error', '500 internal server error'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "服务器500错误"),

    # ==================== Pydantic/验证相关错误 ====================
    (['pydanticinvalidforjsonschema', 'cannot generate a jsonschema'],
     ErrorCode.VALIDATION_PYDANTIC_SCHEMA, "Pydantic JSON Schema生成失败"),
    (['unable to generate pydantic-core schema'],
     ErrorCode.VALIDATION_PYDANTIC_SCHEMA, "Pydantic Schema生成失败"),
    (['model-field-overridden'],
     ErrorCode.VALIDATION_PYDANTIC_SCHEMA, "Pydantic字段覆盖错误"),

    # ==================== 正则表达式错误 ====================
    (['bad escape'],
     ErrorCode.CODE_SYNTAX_REGEX_ESCAPE, "正则表达式转义错误"),

    # ==================== 浏览器/WebDriver 错误 ====================
    (['webdriverexception'],
     ErrorCode.CONFIG_WEBDRIVER_FAILED, "WebDriver启动失败"),
    (["executable doesn't exist", 'browsertype.launch'],
     ErrorCode.CONFIG_BROWSER_NOT_FOUND, "浏览器可执行文件不存在"),
    (['chrome failed to start'],
     ErrorCode.CONFIG_WEBDRIVER_FAILED, "Chrome启动失败"),
    (['unable to obtain driver'],
     ErrorCode.CONFIG_WEBDRIVER_FAILED, "无法获取WebDriver"),

    # ==================== 视频相关错误 ====================
    (['视频文件不存在'],
     ErrorCode.RESOURCE_FILE_NOT_FOUND, "视频文件不存在"),
    (['剪映草稿文件不存在'],
     ErrorCode.RESOURCE_FILE_NOT_FOUND, "剪映草稿文件不存在"),
    (['视频片段生成失败', '所有视频片段生成失败'],
     ErrorCode.RESOURCE_VIDEO_SEGMENT_FAILED, "视频片段生成失败"),
    (['没有生成任何视频片段', '未能成功生成任何视频片段', '没有可用的视频片段'],
     ErrorCode.RESOURCE_VIDEO_SEGMENT_FAILED, "无可用视频片段"),
    (['下载视频失败', '视频下载失败'],
     ErrorCode.RESOURCE_VIDEO_DOWNLOAD_FAILED, "视频下载失败"),
    (['视频预处理失败'],
     ErrorCode.RESOURCE_FFMPEG_FAILED, "视频预处理失败"),
    (['ffmpeg'],
     ErrorCode.RESOURCE_FFMPEG_FAILED, "FFmpeg处理失败"),

    # ==================== 图片相关错误 ====================
    (['无法下载图片', '下载图片失败'],
     ErrorCode.RESOURCE_IMAGE_DOWNLOAD_FAILED, "图片下载失败"),
    (['图片url列表为空'],
     ErrorCode.VALIDATION_INPUT_EMPTY, "图片URL列表为空"),
    (['所有图片都无法访问'],
     ErrorCode.RESOURCE_IMAGE_DOWNLOAD_FAILED, "图片无法访问"),
    (['输入的图片url无法访问'],
     ErrorCode.RESOURCE_IMAGE_DOWNLOAD_FAILED, "图片URL无法访问"),

    # ==================== TTS 相关错误 ====================
    (['腾讯云 tts', '腾讯云tts'],
     ErrorCode.API_AUDIO_GEN_FAILED, "腾讯云TTS生成失败"),

    # ==================== 飞书相关错误 ====================
    (['获取草稿列表失败'],
     ErrorCode.INTEGRATION_FEISHU_API_FAILED, "飞书获取草稿列表失败"),
    (['feishu', '飞书'],
     ErrorCode.INTEGRATION_FEISHU_API_FAILED, "飞书API错误"),

    # ==================== Webhook 错误 ====================
    (['获取webhook密钥失败'],
     ErrorCode.CONFIG_API_KEY_MISSING, "Webhook密钥获取失败"),

    # ==================== LLM/API 相关错误 ====================
    (['total tokens', 'exceed'],
     ErrorCode.API_LLM_TOKEN_LIMIT, "Token总数超限"),
    (['input length', 'exceeds'],
     ErrorCode.API_LLM_TOKEN_LIMIT, "输入长度超限"),
    (['llm model received multi-modal messages'],
     ErrorCode.API_LLM_INVALID_REQUEST, "LLM不支持多模态消息"),
    (['invalid messages'],
     ErrorCode.API_LLM_INVALID_REQUEST, "消息格式无效"),
    (['modelnotopen', 'has not activated the model'],
     ErrorCode.API_LLM_MODEL_NOT_FOUND, "模型未开通"),
    (['model not found'],
     ErrorCode.API_LLM_MODEL_NOT_FOUND, "模型未找到"),
    (['资源点不足', 'errbalanceoverdue'],
     ErrorCode.BUSINESS_QUOTA_INSUFFICIENT, "资源点不足"),
    (['errtoomanyrequest', '触发限流', 'rate limit'],
     ErrorCode.API_LLM_RATE_LIMIT, "请求频率限制"),

    # ==================== 递归限制错误 ====================
    (['recursion limit', 'graph_recursion_limit'],
     ErrorCode.RUNTIME_RECURSION_LIMIT, "递归深度超限"),

    # ==================== 类型/代码错误 ====================
    (['structuredtool', 'not callable'],
     ErrorCode.CODE_TYPE_NOT_CALLABLE, "StructuredTool对象不可调用"),
    (['object is not callable'],
     ErrorCode.CODE_TYPE_NOT_CALLABLE, "对象不可调用"),
    (['zerodivisionerror', 'division by zero'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "除零错误"),
    (['unicodedecodeerror', 'unicodeencodeerror'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "编码错误"),
    (['too many values to unpack', 'not enough values to unpack'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "解包错误"),
    (['is not defined'],
     ErrorCode.CODE_NAME_NOT_DEFINED, "变量未定义"),
    (['cannot access local variable'],
     ErrorCode.CODE_NAME_NOT_DEFINED, "局部变量未定义"),
    (['got an unexpected keyword argument'],
     ErrorCode.CODE_TYPE_EXTRA_ARG, "函数参数错误"),
    (["can't compare offset-naive and offset-aware datetimes"],
     ErrorCode.CODE_TYPE_WRONG_ARG, "时区类型不兼容"),

    # ==================== AttributeError 模式 ====================
    (["'str' object has no attribute"],
     ErrorCode.CODE_ATTR_WRONG_TYPE, "字符串类型错误"),
    (["'nonetype' object has no attribute"],
     ErrorCode.CODE_ATTR_WRONG_TYPE, "对象为None"),
    (["'dict' object has no attribute"],
     ErrorCode.CODE_ATTR_WRONG_TYPE, "字典类型错误"),
    (["'list' object has no attribute"],
     ErrorCode.CODE_ATTR_WRONG_TYPE, "列表类型错误"),
    (['model_dump'],
     ErrorCode.CODE_ATTR_MODEL_DUMP, "对象类型错误"),
    (['object has no attribute'],
     ErrorCode.CODE_ATTR_NOT_FOUND, "属性不存在"),

    # ==================== 集成服务错误 ====================
    (['integration not found', 'code=190000006'],
     ErrorCode.INTEGRATION_SERVICE_UNAVAILABLE, "集成服务未找到"),
    (['integration credential', 'failed'],
     ErrorCode.INTEGRATION_CREDENTIAL_INVALID, "集成凭证请求失败"),
    (['imap', '失败'],
     ErrorCode.INTEGRATION_SERVICE_UNAVAILABLE, "邮件连接失败"),
    (['邮件', '失败'],
     ErrorCode.INTEGRATION_SERVICE_UNAVAILABLE, "邮件操作失败"),

    # ==================== 文件相关错误 ====================
    (['读取excel失败'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "Excel读取失败"),
    (['解压文件失败', '解压失败'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "解压文件失败"),
    (['openpyxl does not support'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "Excel格式不支持"),
    (['文件不存在', 'file not found', 'not exist'],
     ErrorCode.RESOURCE_FILE_NOT_FOUND, "文件不存在"),

    # ==================== URL 相关错误 ====================
    (['url不支持直接使用', '临时签名url'],
     ErrorCode.API_NETWORK_URL_INVALID, "临时签名URL不支持"),
    (['链接已过期', 'url已过期'],
     ErrorCode.API_NETWORK_URL_INVALID, "链接已过期"),

    # ==================== 输入验证错误 ====================
    (['输入验证失败'],
     ErrorCode.VALIDATION_INPUT_INVALID, "输入验证失败"),
    (['没有有效的', '可供处理'],
     ErrorCode.VALIDATION_INPUT_EMPTY, "无有效输入"),
    (['未找到任何对话内容'],
     ErrorCode.VALIDATION_INPUT_EMPTY, "内容为空"),

    # ==================== 业务数据错误 ====================
    (['无法从搜索结果中提取'],
     ErrorCode.BUSINESS_DATA_NOT_FOUND, "数据提取失败"),
    (['未识别到', '无法识别'],
     ErrorCode.BUSINESS_DATA_NOT_FOUND, "识别失败"),
    (['最大搜索调用次数限制'],
     ErrorCode.BUSINESS_QUOTA_EXCEEDED, "搜索调用次数超限"),

    # ==================== 抖音相关错误 ====================
    (['抖音需要登录', 'douyin', 'cookie'],
     ErrorCode.CONFIG_API_KEY_MISSING, "抖音需要登录cookies"),
    (['解析抖音链接失败', '无法从抖音'],
     ErrorCode.BUSINESS_DATA_NOT_FOUND, "抖音链接解析失败"),

    # ==================== 通用失败模式 (优先级较低，放在最后) ====================
    (['抓取页面失败', '爬取', '失败'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "页面抓取失败"),
    (['大模型调用失败', 'llm', 'connection'],
     ErrorCode.API_NETWORK_CONNECTION, "大模型调用连接失败"),
    (['测试异常'],
     ErrorCode.RUNTIME_EXECUTION_FAILED, "测试异常"),
]

TRACEBACK_EXCEPTION_PATTERNS: List[ErrorPattern] = [
    # ==================== Python 内置异常 (从 Traceback 中提取) ====================
    (['typeerror:', 'got an unexpected keyword argument'],
     ErrorCode.CODE_TYPE_EXTRA_ARG, "函数参数错误"),
    (['typeerror:', 'missing', 'argument'],
     ErrorCode.CODE_TYPE_MISSING_ARG, "缺少必需参数"),
    (['typeerror:', 'not callable'],
     ErrorCode.CODE_TYPE_NOT_CALLABLE, "对象不可调用"),
    (['typeerror:', 'not iterable'],
     ErrorCode.CODE_TYPE_NOT_ITERABLE, "对象不可迭代"),
    (['typeerror:', 'not subscriptable'],
     ErrorCode.CODE_TYPE_NOT_SUBSCRIPTABLE, "对象不支持下标访问"),
    (['typeerror:'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "类型错误"),

    (['valueerror:', '视频'],
     ErrorCode.RESOURCE_VIDEO_PROCESS_FAILED, "视频处理错误"),
    (['valueerror:', '图片', 'image'],
     ErrorCode.RESOURCE_IMAGE_PROCESS_FAILED, "图片处理错误"),
    (['valueerror:'],
     ErrorCode.VALIDATION_FIELD_VALUE, "值错误"),

    (['keyerror:'],
     ErrorCode.CODE_KEY_NOT_FOUND, "键不存在"),
    (['indexerror:'],
     ErrorCode.CODE_INDEX_OUT_OF_RANGE, "索引越界"),

    (['attributeerror:', 'model_dump'],
     ErrorCode.CODE_ATTR_MODEL_DUMP, "对象类型错误"),
    (['attributeerror:', "'nonetype'"],
     ErrorCode.CODE_ATTR_WRONG_TYPE, "对象为None"),
    (['attributeerror:'],
     ErrorCode.CODE_ATTR_NOT_FOUND, "属性不存在"),

    (['nameerror:', 'unboundlocalerror:'],
     ErrorCode.CODE_NAME_NOT_DEFINED, "名称未定义"),
    (['modulenotfounderror:', 'importerror:'],
     ErrorCode.CODE_NAME_IMPORT_ERROR, "模块导入错误"),
    (['filenotfounderror:'],
     ErrorCode.RESOURCE_FILE_NOT_FOUND, "文件不存在"),

    (['oserror:', 'ioerror:', 'cannot open resource'],
     ErrorCode.RESOURCE_FILE_READ_ERROR, "文件读取错误"),
    (['permissionerror:'],
     ErrorCode.RESOURCE_FILE_READ_ERROR, "权限错误"),

    (['timeouterror:', 'asyncio.timeouterror'],
     ErrorCode.RUNTIME_TIMEOUT, "执行超时"),
    (['runtimeerror:'],
     ErrorCode.RUNTIME_EXECUTION_FAILED, "运行时错误"),
    (['recursionerror:'],
     ErrorCode.RUNTIME_RECURSION_LIMIT, "递归深度超限"),
    (['memoryerror:'],
     ErrorCode.RUNTIME_MEMORY_ERROR, "内存错误"),

    # ==================== Pydantic 验证错误 ====================
    (['validationerror:', 'field required', 'missing'],
     ErrorCode.VALIDATION_FIELD_REQUIRED, "必填字段缺失"),
    (['validationerror:', 'input should be'],
     ErrorCode.VALIDATION_FIELD_TYPE, "字段类型错误"),
    (['validationerror:'],
     ErrorCode.VALIDATION_FIELD_CONSTRAINT, "验证失败"),

    # ==================== API 相关错误 ====================
    (['apierror:', 'model not found'],
     ErrorCode.API_LLM_MODEL_NOT_FOUND, "模型不存在"),
    (['apierror:', 'rate limit'],
     ErrorCode.API_LLM_RATE_LIMIT, "请求频率超限"),
    (['apierror:', 'token', 'limit'],
     ErrorCode.API_LLM_TOKEN_LIMIT, "Token超限"),
    (['apierror:', '401', 'unauthorized'],
     ErrorCode.API_LLM_AUTH_FAILED, "API认证失败"),
    (['apierror:', 'downloading', 'download'],
     ErrorCode.RESOURCE_S3_DOWNLOAD_FAILED, "下载失败"),
    (['apierror:'],
     ErrorCode.API_LLM_REQUEST_FAILED, "API请求失败"),

    # ==================== LangGraph 错误 ====================
    (['invalidupdateerror', 'expected dict'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "节点返回类型错误"),
    (['invalidupdateerror'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "节点返回值无效"),
    (['graphrecursionerror'],
     ErrorCode.RUNTIME_RECURSION_LIMIT, "LangGraph递归限制"),

    # ==================== 网络错误 ====================
    (['connectionerror:', 'connectionrefusederror:'],
     ErrorCode.API_NETWORK_CONNECTION, "网络连接错误"),
    (['httperror:'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "HTTP错误"),
    (['httpx.', 'connecterror'],
     ErrorCode.API_NETWORK_CONNECTION, "HTTPX连接错误"),
    (['httpx.', 'timeout'],
     ErrorCode.API_NETWORK_TIMEOUT, "HTTPX超时错误"),
    (['remoteprotocolerror'],
     ErrorCode.API_NETWORK_REMOTE_PROTOCOL, "远程协议错误"),

    # ==================== 其他错误 ====================
    (['zerodivisionerror:'],
     ErrorCode.CODE_TYPE_WRONG_ARG, "除零错误"),
    (['assertionerror:'],
     ErrorCode.VALIDATION_FIELD_VALUE, "断言错误"),
    (['subprocesserror:', 'returned non-zero exit status'],
     ErrorCode.RUNTIME_SUBPROCESS_FAILED, "子进程执行失败"),
]

CUSTOM_EXCEPTION_PATTERNS: List[ErrorPattern] = [
    # ==================== 视频相关 ====================
    (['视频生成失败'],
     ErrorCode.API_VIDEO_GEN_FAILED, "视频生成失败"),
    (['视频片段', '没有生成任何视频片段'],
     ErrorCode.RESOURCE_VIDEO_SEGMENT_FAILED, "视频片段生成失败"),
    (['视频下载', '无法下载任何视频片段'],
     ErrorCode.RESOURCE_VIDEO_DOWNLOAD_FAILED, "视频下载失败"),
    (['failed to merge video', 'failed to create video'],
     ErrorCode.RESOURCE_FFMPEG_FAILED, "视频合并失败"),
    (['视频合成失败', '视频合并失败'],
     ErrorCode.RESOURCE_FFMPEG_FAILED, "视频合成失败"),

    # ==================== 图片相关 ====================
    (['无法下载图片', '图片下载'],
     ErrorCode.RESOURCE_IMAGE_DOWNLOAD_FAILED, "图片下载失败"),
    (['敏感内容', 'sensitive'],
     ErrorCode.API_LLM_CONTENT_FILTER, "内容被安全过滤"),
    (['提交文生图任务失败'],
     ErrorCode.API_IMAGE_GEN_FAILED, "文生图任务失败"),
    (['图片识别失败'],
     ErrorCode.RESOURCE_IMAGE_PROCESS_FAILED, "图片识别失败"),

    # ==================== 下载相关 ====================
    (['下载失败', 'download fail'],
     ErrorCode.RESOURCE_S3_DOWNLOAD_FAILED, "下载失败"),
    (['所有下载策略都失败'],
     ErrorCode.RESOURCE_S3_DOWNLOAD_FAILED, "所有下载策略失败"),

    # ==================== API 相关 ====================
    (['api', 'fail', '失败'],
     ErrorCode.API_LLM_REQUEST_FAILED, "API调用失败"),
    (['llm调用失败', '大模型调用失败'],
     ErrorCode.API_LLM_REQUEST_FAILED, "LLM调用失败"),
    (['pixabay'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "Pixabay API失败"),
    (['和风天气', 'qweather'],
     ErrorCode.API_NETWORK_HTTP_ERROR, "和风天气API失败"),

    # ==================== 解析相关 ====================
    (['解析失败', 'parse fail'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "解析失败"),
    (['无法解析', 'json'],
     ErrorCode.VALIDATION_JSON_DECODE, "JSON解析失败"),

    # ==================== 配置相关 ====================
    (['请在config', '请设置环境变量'],
     ErrorCode.CONFIG_ENV_MISSING, "配置缺失"),
    (['access key', 'api_key'],
     ErrorCode.CONFIG_API_KEY_MISSING, "API Key缺失"),

    # ==================== 文件相关 ====================
    (['不支持的文件类型'],
     ErrorCode.RESOURCE_FILE_FORMAT_ERROR, "不支持的文件类型"),
    (['上传', '失败'],
     ErrorCode.RESOURCE_S3_UPLOAD_FAILED, "上传失败"),

    # ==================== 通用失败 ====================
    (['失败', 'failed', 'error'],
     ErrorCode.BUSINESS_NODE_FAILED, "执行失败"),
]


def match_error_pattern(
    error_str: str,
    patterns: List[ErrorPattern] = None,
    require_all: bool = False
) -> Tuple[Optional[int], Optional[str]]:
    """
    使用模式表匹配错误消息
    
    Args:
        error_str: 错误消息字符串
        patterns: 要使用的模式表，默认使用 ERROR_PATTERNS
        require_all: 是否要求所有关键词都匹配（默认只需匹配一个）
    
    Returns:
        (error_code, error_message) 或 (None, None) 如果没有匹配
    """
    if patterns is None:
        patterns = ERROR_PATTERNS
    
    error_lower = error_str.lower()
    
    for keywords, code, msg_template in patterns:
        if require_all:
            if all(kw.lower() in error_lower for kw in keywords):
                return code, f"{msg_template}: {error_str[:200]}"
        else:
            if any(kw.lower() in error_lower for kw in keywords):
                return code, f"{msg_template}: {error_str[:200]}"
    
    return None, None


def match_traceback_pattern(error_str: str) -> Tuple[Optional[int], Optional[str]]:
    """匹配 Traceback 中的异常类型"""
    return match_error_pattern(error_str, TRACEBACK_EXCEPTION_PATTERNS)


def match_custom_exception_pattern(error_str: str) -> Tuple[Optional[int], Optional[str]]:
    """匹配自定义 Exception 的模式"""
    return match_error_pattern(error_str, CUSTOM_EXCEPTION_PATTERNS)
