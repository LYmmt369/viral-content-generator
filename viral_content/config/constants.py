"""
常量定义

作者: Sunnyeung
版本: 4.1.1
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
RESOURCES_ROOT = PROJECT_ROOT / "resources"
SOURCE_ROOT = PROJECT_ROOT.parent

# Skill 文件路径
SKILL_V3_PATH = RESOURCES_ROOT / "skill.md"
SKILL_FALLBACK_PATH = RESOURCES_ROOT / "skill.md"
PROMPTS_DIR = RESOURCES_ROOT / "prompts"

# 数据目录
DATA_DIR = RESOURCES_ROOT / "data"
STYLES_DIR = DATA_DIR / "styles"
ACCOUNTS_DIR = DATA_DIR / "accounts"
OFFERS_DIR = DATA_DIR / "offers"
TRENDS_DIR = DATA_DIR / "trends"

# 输出目录
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# 支持的平台
SUPPORTED_PLATFORMS = ['openai', 'claude', 'gemini', 'local']
PLATFORM_NAMES = {
    'openai': 'OpenAI',
    'claude': 'Claude',
    'gemini': 'Gemini',
    'local': 'Local'
}

# 平台默认模型
PLATFORM_DEFAULT_MODELS = {
    'openai': 'gpt-4o',
    'claude': 'claude-sonnet-4-20250514',
    'gemini': 'gemini-2.0-flash-exp',
    'local': 'local-model'
}

# 支持的目标平台（内容输出平台）
CONTENT_PLATFORMS = [
    'douyin', 'kuaishou', 'video_account',  # 短视频
    'xiaohongshu', 'weibo',  # 图文
    'wechat', 'zhihu',  # 长文
    'bilibili', 'youtube',  # 长视频
    'podcast',  # 音频
    'all'  # 全平台
]

# 成交目标类型
CONVERSION_GOALS = ['likes', 'comments', 'followers', 'leads', 'sales', 'consult']

# 风格分类
STYLE_CATEGORIES = [
    'tech_creator',
    'business_creator',
    'lifestyle_creator',
    'podcast_host',
    'writer',
    'copywriting',
    'news_commentator',
    'knowledge_creator'
]

# 风格区域
STYLE_REGIONS = ['global', 'china']

# 内容限制
MIN_WORD_COUNT = 500
MAX_WORD_COUNT = 20000
DEFAULT_WORD_COUNT = 6000
DEFAULT_MAX_TOKENS = 16384

# API 配置
MAX_RETRIES = 3
RETRY_DELAY = 1.0

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'viral_content_generator.log'
