#!/usr/bin/env python3
"""
热点风格成交引擎 - 命令行工具 v4.0
从"爆款内容生成器"升级为"热点风格成交引擎"

核心公式：
任何热点话题 + 任意账号定位 + 任意业务目标 + 任意平台格式 + 可组合风格基因 = 高赞、高互动、高成交内容包

作者: Sunnyeung
版本: 4.0.0
许可: MIT License
GitHub: https://github.com/Sunnyeung369/viral-content-generator
"""

import argparse
import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入核心引擎
from viral_content.core import (
    AccountFingerprint,
    PromptCompiler,
    StyleMixer,
)
from viral_content.core.experiment import Candidate, CandidateRanker
from viral_content.core.quality_gate import QualityGate

# 导入生成器（复用v3.1）
from viral_content.generators.factory import create_generator
from viral_content.utils.observability import configure_json_logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('viral_content_generator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 常量定义
SUPPORTED_PLATFORMS = {
    'openai': 'OpenAI',
    'claude': 'Claude',
    'gemini': 'Gemini',
}

CONTENT_PLATFORMS = {
    'wechat': '公众号',
    'video': '视频号',
    'xiaohongshu': '小红书',
    'zhihu': '知乎',
    'douyin': '抖音',
    'bilibili': 'B站',
    'weibo': '微博',
}

CONVERSION_GOALS = ['likes', 'comments', 'leads', 'sales']

DEFAULT_MODEL = 'claude-3-5-sonnet-20241022'
DEFAULT_MAX_TOKENS = 8192
DEFAULT_TEMPERATURE = 0.7


class HotTopicInput:
    """热点输入处理器"""

    @staticmethod
    def from_file(file_path: Path) -> list[dict[str, Any]]:
        """从文件加载热点数据

        Args:
            file_path: 文件路径（支持JSON/YAML）

        Returns:
            热点列表
        """
        if not file_path.exists():
            raise FileNotFoundError(f"热点文件不存在: {file_path}")

        suffix = file_path.suffix.lower()

        with open(file_path, 'r', encoding='utf-8') as f:
            if suffix == '.json':
                data = json.load(f)
            elif suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                raise ValueError(f"不支持的文件格式: {suffix}")

        if isinstance(data, dict) and 'trends' in data:
            return data['trends']
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("热点数据格式错误")

    @staticmethod
    def from_text(text: str) -> list[dict[str, Any]]:
        """从文本创建热点数据

        Args:
            text: 热点文本

        Returns:
            热点列表
        """
        return [{
            'id': f'trend_{int(datetime.now(timezone.utc).timestamp())}',
            'topic': text.strip(),
            'description': text.strip(),
            'source': 'manual_input',
            'url': '',
            'metrics': {'热度': 0, '讨论量': 0},
            'keywords': [],
            'category': '',
        }]


class ViralContentCLI:
    """热点风格成交引擎CLI"""

    def __init__(self):
        self.compiler = PromptCompiler()
        self.style_mixer = StyleMixer()

    def generate(
        self,
        topic: str,
        style: str | None = None,
        style_mix: str | None = None,
        account: Path | None = None,
        offer: Path | None = None,
        goal: str = 'leads',
        content_platforms: list[str] | None = None,
        ai_platform: str = 'claude',
        model: str | None = None,
        api_key: str | None = None,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        stream: bool = False,
        output_path: Path | None = None,
        variants: int = 1,
        enable_scoring: bool = False,
    ) -> str:
        """生成内容

        Args:
            topic: 热点话题
            style: 单一风格ID
            style_mix: 风格混合（逗号分隔的style_id列表）
            account: 账号配置文件路径
            offer: 产品配置文件路径
            goal: 成交目标（likes/comments/leads/sales）
            content_platforms: 内容平台列表
            ai_platform: AI平台（openai/claude/gemini）
            model: 模型名称
            api_key: API密钥
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式输出
            output_path: 输出路径
            variants: 生成变体数量
            enable_scoring: 是否启用评分

        Returns:
            生成的内容
        """
        # 1. 建立可追踪实验身份
        experiment_id = uuid.uuid4().hex[:12]
        # 2. 加载配置
        style_config = None
        if style:
            style_config = self.style_mixer.get_style(style)
        elif style_mix:
            style_ids = [s.strip() for s in style_mix.split(',')]
            style_config = self.style_mixer.mix_styles(style_ids)

        account_config = None
        if account:
            account_fingerprint = AccountFingerprint(account)
            account_config = account_fingerprint.to_dict()

        offer_config = None
        if offer:
            with open(offer, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                offer_config = data.get('offer', {}) if isinstance(data, dict) else {}

        # 3. 确定内容平台
        if content_platforms is None or not content_platforms:
            content_platforms = ['wechat']
        if len(content_platforms) != 1:
            raise ValueError("一次生成只接收一个内容平台，请分别运行命令")

        # 4. 构建系统提示词
        system_prompt = self.compiler.build_system_prompt(
            topic=topic,
            style_config=style_config,
            account_config=account_config,
            offer_config=offer_config,
            goal=goal,
            platform=content_platforms[0],
        )

        # 5. 创建生成器
        generator = create_generator(
            platform=ai_platform,
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            stream=stream,
        )

        # 5. 生成内容
        user_prompt = f"请根据以上配置，为主题「{topic}」生成一篇{CONTENT_PLATFORMS.get(content_platforms[0], content_platforms[0])}内容。"

        logger.info("开始生成内容...")
        # 5. 生成候选并按目标选择最佳版本
        candidate_count = max(1, min(int(variants or 1), 8))
        candidates = []
        for index in range(candidate_count):
            generator.config.user_prompt = user_prompt + (f"\n这是第 {index + 1} 个候选，请使用不同的切入角度。" if candidate_count > 1 else "")
            result = generator.generate()
            candidate = result.content
            gate = QualityGate().check(candidate, require_cta=goal in {"leads", "sales"})
            score = self._quick_score(candidate, goal)
            # 有硬性问题的候选降权，但仍保留以便诊断
            rank_score = score if gate.passed else score - 3.0
            candidates.append((rank_score, candidate, gate))
            if gate.warnings:
                logger.warning("候选 %d 发布前检查: %s", index + 1, "；".join(gate.warnings))

        eligible = [Candidate(content=c, quality_score=score, passed_gate=True, index=i) for i, (score, c, g) in enumerate(candidates) if g.passed]
        if not eligible:
            raise ValueError("所有候选均未通过检查，未保存内容")
        ranked = CandidateRanker(goal, platform=content_platforms[0]).rank(eligible)
        content = ranked[0].content
        logger.info("已从 %d 个候选中选择一个通过检查的版本", candidate_count)

        # 6. 可选评分
        if enable_scoring:
            logger.info(f"长度参考值: {self._quick_score(content, goal)}/10（不代表内容质量或发布效果）")

        # 9. 保存输出
        if output_path:
            self._save_output(content, output_path, topic, goal, content_platforms[0], experiment_id=experiment_id, candidate_count=candidate_count)

        return content

    def batch_generate(
        self,
        hot_topics: list[dict[str, Any]],
        **kwargs
    ) -> list[dict[str, Any]]:
        """批量生成内容

        Args:
            hot_topics: 热点列表
            **kwargs: 生成参数

        Returns:
            生成结果列表
        """
        results = []

        for i, trend in enumerate(hot_topics):
            logger.info(f"正在处理第 {i+1}/{len(hot_topics)} 个热点: {trend.get('topic', '')}")

            topic = trend.get('topic', trend.get('description', ''))

            try:
                content = self.generate(
                    topic=topic,
                    **kwargs
                )

                results.append({
                    'trend': trend,
                    'content': content,
                    'success': True,
                })

            except Exception as e:  # noqa: BLE001 - normalize boundary errors for stable CLI/API behavior
                logger.error(f"生成失败: {e}")
                results.append({
                    'trend': trend,
                    'content': None,
                    'success': False,
                    'error': str(e),
                })

        return results

    def _quick_score(self, content: str, goal: str) -> float:
        """快速评分

        Args:
            content: 内容
            goal: 成交目标

        Returns:
            评分 (0-10)
        """
        # 简单的长度和结构评分
        word_count = len(content)

        if word_count < 100:
            return 3.0
        elif word_count < 300:
            return 5.0
        elif word_count < 800:
            return 7.0
        else:
            return 8.0

    def _save_output(self, content: str, output_path: Path, topic: str, goal: str, platform: str, *, experiment_id: str = "", candidate_count: int = 1):
        """保存输出

        Args:
            content: 内容
            output_path: 输出路径
            topic: 话题
            goal: 成交目标
            platform: 平台
        """
        output_path = Path(output_path)

        # 如果是目录，生成文件名
        if output_path.is_dir():
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            filename = f"{goal}_{platform}_{timestamp}.md"
            output_path = output_path / filename

        # 确保目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {topic}\n\n")
            f.write(f"**实验 ID**: {experiment_id}\n")
            f.write(f"**候选数量**: {candidate_count}\n")
            f.write(f"**生成时间**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**成交目标**: {goal}\n")
            f.write(f"**目标平台**: {platform}\n\n")
            f.write("---\n\n")
            f.write(content)

        logger.info(f"内容已保存到: {output_path}")


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='热点风格成交引擎 v4.0 - 生成高赞、高互动、高成交内容',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:

  # 基础用法（向后兼容v3.1）
  python viral_content_cli.py "AI Agent Runtime崩溃" --style tech_explainer_global

  # v4.0 完整用法
  python viral_content_cli.py \\
    --topic "AI Agent Runtime崩溃" \\
    --account data/accounts/ai_consultant.yaml \\
    --offer data/offers/consulting.yaml \\
    --goal leads \\
    --platform xiaohongshu \\
    --style-mix "tech_explainer_global,business_savage_china" \\
    --output outputs/

  # 批量生成
  python viral_content_cli.py \\
    --trends-file hot_topics.json \\
    --account data/accounts/ai_consultant.yaml \\
    --goal leads

  # 多平台输出
  python viral_content_cli.py \\
    --topic "AI工具使用技巧" \\
    --platform douyin xiaohongshu wechat \\
    --goal likes
        '''
    )

    # 核心参数
    parser.add_argument(
        'topic',
        nargs='?',
        help='热点话题（与--trends-file二选一）'
    )
    parser.add_argument('--topic', dest='topic_option', help='主题（也可使用位置参数）')

    parser.add_argument(
        '--trends-file',
        type=Path,
        help='热点数据文件（JSON/YAML格式）'
    )

    # 风格参数
    parser.add_argument(
        '--style',
        help='单一风格ID（如：tech_explainer_global）'
    )

    parser.add_argument(
        '--style-mix',
        help='风格混合（逗号分隔，如：style1,style2,style3）'
    )

    # 账号和产品
    parser.add_argument(
        '--account',
        type=Path,
        help='账号配置文件路径'
    )

    parser.add_argument(
        '--offer',
        type=Path,
        help='产品配置文件路径'
    )

    # 成交目标
    parser.add_argument(
        '--goal',
        choices=CONVERSION_GOALS,
        default='leads',
        help='成交目标（默认: leads）'
    )

    # 平台参数
    parser.add_argument(
        '--platform',
        dest='platforms',
        choices=list(CONTENT_PLATFORMS.keys()),
        nargs='+',
        help='内容平台（可多选）'
    )

    parser.add_argument(
        '--ai-platform',
        choices=list(SUPPORTED_PLATFORMS.keys()),
        default='claude',
        help='AI平台（默认: claude）'
    )

    # 模型参数
    parser.add_argument(
        '--model',
        help='模型名称（覆盖默认模型）'
    )

    parser.add_argument(
        '--api-key',
        help='API密钥（或设置环境变量）'
    )

    parser.add_argument(
        '--temperature',
        type=float,
        default=DEFAULT_TEMPERATURE,
        help='温度参数（默认: 0.7）'
    )

    parser.add_argument(
        '--max-tokens',
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help='最大token数（默认: 8192）'
    )

    # 输出参数
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='输出目录或文件路径'
    )

    parser.add_argument(
        '--variants',
        type=int,
        default=1,
        help='生成变体数量（默认: 1）'
    )

    parser.add_argument(
        '--stream',
        action='store_true',
        help='启用流式输出'
    )

    parser.add_argument(
        '--score',
        action='store_true',
        help='启用内容评分'
    )

    # 工具参数
    parser.add_argument(
        '--list-styles',
        action='store_true',
        help='列出所有可用风格'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 4.1.0'
    )

    args = parser.parse_args()
    if args.topic and args.topic_option and args.topic != args.topic_option:
        parser.error('主题位置参数与 --topic 不一致')
    args.topic = args.topic_option or args.topic
    return args


def main():
    request_id = configure_json_logging()
    logger.info("request_started request_id=%s", request_id)
    """主函数"""
    args = parse_arguments()

    # 列出风格
    if args.list_styles:
        mixer = StyleMixer()
        styles = mixer.load_styles()
        print("可用风格列表:")
        print("=" * 60)
        for style_id, style in styles.items():
            print(f"- {style_id}: {style.get('label', '')} ({style.get('category', '')})")
        return 0

    # 检查输入
    if not args.topic and not args.trends_file:
        logger.error("必须指定 --topic 或 --trends-file")
        return 1

    # 创建CLI实例
    cli = ViralContentCLI()

    # 批量生成
    if args.trends_file:
        try:
            hot_topics = HotTopicInput.from_file(args.trends_file)
            logger.info(f"加载了 {len(hot_topics)} 个热点")
        except Exception as e:  # noqa: BLE001 - normalize boundary errors for stable CLI/API behavior
            logger.error(f"加载热点文件失败: {e}")
            return 1

        results = cli.batch_generate(
            hot_topics=hot_topics,
            style=args.style,
            style_mix=args.style_mix,
            account=args.account,
            offer=args.offer,
            goal=args.goal,
            content_platforms=args.platforms,
            ai_platform=args.ai_platform,
            model=args.model,
            api_key=args.api_key,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            stream=args.stream,
            output_path=args.output,
            enable_scoring=args.score,
        )

        # 输出结果
        success_count = sum(1 for r in results if r.get('success'))
        logger.info(f"批量生成完成: {success_count}/{len(results)} 成功")
        return 0

    # 单一生成
    try:
        content = cli.generate(
            topic=args.topic,
            style=args.style,
            style_mix=args.style_mix,
            account=args.account,
            offer=args.offer,
            goal=args.goal,
            content_platforms=args.platforms,
            ai_platform=args.ai_platform,
            model=args.model,
            api_key=args.api_key,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            stream=args.stream,
            output_path=args.output,
            variants=args.variants,
            enable_scoring=args.score,
        )

        # 输出到stdout
        if not args.stream:
            print("\n" + "=" * 60)
            print(content)
            print("=" * 60 + "\n")

        return 0

    except Exception:
        logger.exception("生成失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())
