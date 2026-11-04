"""
Skill 文件加载器（带缓存）

作者: Sunnyeung
版本: 4.1.6
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

import logging
import threading
from pathlib import Path

from viral_content.config.constants import SKILL_FALLBACK_PATH, SKILL_V3_PATH
from viral_content.exceptions.custom import SkillLoadError

logger = logging.getLogger(__name__)


class SkillLoader:
    """Skill文件加载器，支持缓存和热重载"""

    _instance = None
    _lock = threading.Lock()
    _cached_content: str | None = None
    _cached_mtime: float | None = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, force_reload: bool = False) -> str:
        """
        加载Skill内容（带缓存）

        Args:
            force_reload: 强制重新加载

        Returns:
            str: Skill文件内容

        Raises:
            SkillLoadError: 当Skill文件不存在或无法读取时
        """
        try:
            # 检查缓存
            if not force_reload and self._cached_content is not None:
                current_mtime = SKILL_V3_PATH.stat().st_mtime
                if current_mtime == self._cached_mtime:
                    logger.debug("使用缓存的Skill内容")
                    return self._cached_content

            # 加载文件
            if SKILL_V3_PATH.exists():
                content = self._load_file(SKILL_V3_PATH)
                self._update_cache(content, SKILL_V3_PATH)
                logger.info(f"成功加载Skill文件: {SKILL_V3_PATH}")
                return content
            elif SKILL_FALLBACK_PATH.exists():
                content = self._load_file(SKILL_FALLBACK_PATH)
                self._update_cache(content, SKILL_FALLBACK_PATH)
                logger.warning(f"使用回退Skill文件: {SKILL_FALLBACK_PATH}")
                return content
            else:
                raise SkillLoadError("找不到Skill文件")

        except SkillLoadError:
            raise
        except Exception as e:  # noqa: BLE001 - normalize filesystem and parser errors
            logger.error(f"加载Skill文件失败: {e}")
            raise SkillLoadError(f"加载Skill文件失败: {e}")

    def _load_file(self, path: Path) -> str:
        """加载单个文件"""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _update_cache(self, content: str, path: Path) -> None:
        """更新缓存"""
        self._cached_content = content
        self._cached_mtime = path.stat().st_mtime

    def clear_cache(self) -> None:
        """清除缓存"""
        self._cached_content = None
        self._cached_mtime = None


# 全局Skill加载器实例
skill_loader = SkillLoader()


def load_skill(force_reload: bool = False) -> str:
    """便捷函数：加载Skill内容"""
    return skill_loader.load(force_reload)
