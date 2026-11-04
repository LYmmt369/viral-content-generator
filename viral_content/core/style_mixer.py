"""
风格混合器
v4.0 - 风格基因组合引擎

作者: Sunnyeung
版本: 4.1.4
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

from pathlib import Path
from typing import Any

import yaml


class StyleMixer:
    """风格混合器

    功能：
    1. 加载风格基因库
    2. 风格兼容性检查
    3. 风格权重分配
    4. 风格特征提取和组合
    """

    def __init__(self, styles_dir: Path | None = None):
        """初始化风格混合器

        Args:
            styles_dir: 风格配置目录
        """
        self._styles_dir: Path | None = None
        self._style_cache: dict[str, dict[str, Any]] = {}
        self._compatibility_matrix: dict[str, dict[str, float]] = {}

        if styles_dir:
            self.styles_dir = styles_dir

    @property
    def styles_dir(self) -> Path:
        """获取风格配置目录"""
        if self._styles_dir is None:
            from viral_content.config.constants import STYLES_DIR
            self._styles_dir = STYLES_DIR
        return self._styles_dir

    @styles_dir.setter
    def styles_dir(self, value: Path):
        """设置风格配置目录"""
        self._styles_dir = Path(value)
        self._style_cache.clear()

    def load_styles(self) -> dict[str, dict[str, Any]]:
        """加载所有风格配置

        Returns:
            风格字典 {style_id: style_config}
        """
        if self._style_cache:
            return self._style_cache

        yaml_files = list(self.styles_dir.glob("*.yaml"))

        for yaml_file in yaml_files:
            with open(yaml_file, "r", encoding="utf-8") as f:
                try:
                    data = yaml.safe_load(f)
                except yaml.YAMLError:
                    continue

            if not data or "styles" not in data:
                continue

            for style in data["styles"]:
                style_id = style.get("id", "")
                if style_id:
                    self._style_cache[style_id] = style

        return self._style_cache

    def get_style(self, style_id: str) -> dict[str, Any] | None:
        """获取单个风格配置

        Args:
            style_id: 风格ID

        Returns:
            风格配置字典，不存在返回None
        """
        if not self._style_cache:
            self.load_styles()

        return self._style_cache.get(style_id)

    def get_styles_by_category(self, category: str) -> list[dict[str, Any]]:
        """按分类获取风格

        Args:
            category: 风格分类

        Returns:
            风格列表
        """
        if not self._style_cache:
            self.load_styles()

        return [
            style for style in self._style_cache.values()
            if style.get("category") == category
        ]

    def check_compatibility(self, style1: str, style2: str) -> float:
        """检查两个风格的兼容性

        Args:
            style1: 风格1的ID
            style2: 风格2的ID

        Returns:
            兼容性评分 (0-1)
        """
        cache_key = f"{style1}:{style2}"
        if cache_key in self._compatibility_matrix:
            return self._compatibility_matrix[cache_key]

        s1 = self.get_style(style1)
        s2 = self.get_style(style2)

        if not s1 or not s2:
            return 0.0

        # 基于分类的兼容性评分
        cat1 = s1.get("category", "")
        cat2 = s2.get("category", "")

        # 高兼容组合
        high_compat_pairs = [
            ("tech_creator", "writer"),
            ("business_commentator", "copywriting"),
            ("podcast_host", "writer"),
        ]

        # 中兼容组合
        mid_compat_pairs = [
            ("tech_creator", "business_commentator"),
            ("lifestyle_blogger", "copywriting"),
        ]

        for pair in high_compat_pairs:
            if (cat1, cat2) == pair or (cat2, cat1) == pair:
                score = 0.9
                self._compatibility_matrix[cache_key] = score
                return score

        for pair in mid_compat_pairs:
            if (cat1, cat2) == pair or (cat2, cat1) == pair:
                score = 0.6
                self._compatibility_matrix[cache_key] = score
                return score

        # 默认中等兼容
        score = 0.5
        self._compatibility_matrix[cache_key] = score
        return score

    def mix_styles(
        self,
        style_ids: list[str],
        weights: dict[str, float] | None = None
    ) -> dict[str, Any]:
        """混合多个风格

        Args:
            style_ids: 风格ID列表
            weights: 风格权重字典 {style_id: weight}

        Returns:
            混合后的风格配置
        """
        if not style_ids:
            return {}

        styles = [self.get_style(sid) for sid in style_ids]
        styles = [s for s in styles if s]

        if not styles:
            return {}

        # 默认权重分配：主风格70%，辅风格30%
        if weights is None:
            weights = {}
            if len(styles) == 1:
                weights[style_ids[0]] = 1.0
            elif len(styles) == 2:
                weights[style_ids[0]] = 0.7
                weights[style_ids[1]] = 0.3
            else:
                # 多个风格时递减分配
                remaining = 1.0
                for i, sid in enumerate(style_ids[:-1]):
                    w = remaining * 0.7
                    weights[sid] = w
                    remaining -= w
                weights[style_ids[-1]] = remaining

        # 归一化权重
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}

        # 提取混合特征
        mixed = self._extract_mixed_features(styles, weights)

        return {
            "mixed_style": True,
            "component_styles": style_ids,
            "source_styles": styles,
            "weights": weights,
            "features": mixed,
        }

    def _extract_mixed_features(
        self,
        styles: list[dict[str, Any]],
        weights: dict[str, float]
    ) -> dict[str, Any]:
        """提取混合特征

        Args:
            styles: 风格列表
            weights: 权重字典

        Returns:
            混合特征字典
        """
        features = {
            "tone": [],
            "hook_patterns": [],
            "logic_patterns": [],
            "emotion_curve": {},
            "avoid": [],
        }

        for i, style in enumerate(styles):
            style_id = style.get("id", "")
            weight = weights.get(style_id, 0)

            # 提取语气
            if "style_dna" in style and isinstance(style["style_dna"], dict):
                tone = style["style_dna"].get("tone", "")
                if tone:
                    features["tone"].append((tone, weight))

            # 提取钩子模式
            hooks = style.get("hook_patterns", [])
            if isinstance(hooks, list):
                for hook in hooks[:3]:
                    features["hook_patterns"].append((hook, weight))

            # 提取逻辑模式
            logic = style.get("logic_patterns", [])
            if isinstance(logic, list):
                for pattern in logic[:2]:
                    features["logic_patterns"].append((pattern, weight))

            # 提取情绪曲线
            emotion = style.get("emotion_curve", {})
            if isinstance(emotion, dict):
                for key, value in emotion.items():
                    if key not in features["emotion_curve"]:
                        features["emotion_curve"][key] = value

            # 提取避免事项
            avoid = style.get("avoid", [])
            if isinstance(avoid, list):
                for item in avoid:
                    if item not in features["avoid"]:
                        features["avoid"].append(item)

        return features

    def get_prompt_context(self, mixed_style: dict[str, Any]) -> str:
        """获取混合风格的提示词上下文

        Args:
            mixed_style: 混合风格配置

        Returns:
            格式化的风格信息字符串
        """
        if not mixed_style or not mixed_style.get("mixed_style"):
            return ""

        parts = []

        component_styles = mixed_style.get("component_styles", [])
        if component_styles:
            parts.append(f"**混合风格**: {', '.join(component_styles)}")

        weights = mixed_style.get("weights", {})
        if weights:
            weight_str = ", ".join(f"{k}: {v:.1%}" for k, v in weights.items())
            parts.append(f"**风格权重**: {weight_str}")

        features = mixed_style.get("features", {})

        if features.get("tone"):
            tones = [f"{t} ({w:.0%})" for t, w in features["tone"][:2]]
            parts.append(f"**语气**: {', '.join(tones)}")

        if features.get("hook_patterns"):
            hooks = [h for h, w in features["hook_patterns"][:3]]
            parts.append("**钩子模式**:\n" + "\n".join(f"  - {h}" for h in hooks))

        if features.get("avoid"):
            parts.append("**避免事项**:\n" + "\n".join(f"  - {a}" for a in features["avoid"][:3]))

        return "\n\n".join(parts)

    def list_available_styles(self) -> list[str]:
        """列出所有可用的风格ID

        Returns:
            风格ID列表
        """
        if not self._style_cache:
            self.load_styles()

        return list(self._style_cache.keys())

    def search_styles(self, keyword: str) -> list[dict[str, Any]]:
        """搜索风格

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的风格列表
        """
        if not self._style_cache:
            self.load_styles()

        keyword_lower = keyword.lower()

        return [
            style for style in self._style_cache.values()
            if keyword_lower in style.get("id", "").lower() or
               keyword_lower in style.get("label", "").lower() or
               keyword_lower in style.get("category", "").lower()
        ]


def get_style_mixer(styles_dir: Path | None = None) -> StyleMixer:
    """便捷函数：获取风格混合器

    Args:
        styles_dir: 风格配置目录

    Returns:
        StyleMixer实例
    """
    return StyleMixer(styles_dir)
