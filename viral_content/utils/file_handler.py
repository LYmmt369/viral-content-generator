"""
文件处理模块
v4.0 - 统一的文件读写和处理

作者: Sunnyeung
版本: 4.1.3
许可: MIT License
GitHub: https://github.com/LYmmt369/viral-content-generator
"""

import json
import logging
from pathlib import Path
from typing import Any, ClassVar

import yaml

from ..exceptions.custom import FileOperationError

logger = logging.getLogger(__name__)


class FileHandler:
    """文件处理器"""

    # 支持的格式
    SUPPORTED_FORMATS: ClassVar[set[str]] = {".yaml", ".yml", ".json", ".txt", ".md"}

    @staticmethod
    def read_yaml(file_path: str | Path) -> dict[str, Any]:
        """读取YAML文件

        Args:
            file_path: 文件路径

        Returns:
            解析后的字典

        Raises:
            FileOperationError: 读取失败
        """
        path = Path(file_path)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            logger.debug(f"Loaded YAML from {path}")
            return data

        except yaml.YAMLError as e:
            raise FileOperationError(f"YAML parsing error in {path}: {e}")
        except FileNotFoundError:
            raise FileOperationError(f"File not found: {path}")
        except Exception as e:  # noqa: BLE001 - normalize filesystem and parser errors
            raise FileOperationError(f"Failed to read {path}: {e}")

    @staticmethod
    def write_yaml(
        file_path: str | Path,
        data: dict[str, Any],
        create_dirs: bool = True
    ) -> None:
        """写入YAML文件

        Args:
            file_path: 文件路径
            data: 要写入的数据
            create_dirs: 是否创建父目录
        """
        path = Path(file_path)

        try:
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                yaml.safe_dump(
                    data,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False
                )

            logger.debug(f"Wrote YAML to {path}")

        except Exception as e:  # noqa: BLE001 - normalize filesystem and parser errors
            raise FileOperationError(f"Failed to write {path}: {e}")

    @staticmethod
    def read_json(file_path: str | Path) -> dict[str, Any]:
        """读取JSON文件

        Args:
            file_path: 文件路径

        Returns:
            解析后的字典
        """
        path = Path(file_path)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"Loaded JSON from {path}")
            return data

        except json.JSONDecodeError as e:
            raise FileOperationError(f"JSON parsing error in {path}: {e}")
        except FileNotFoundError:
            raise FileOperationError(f"File not found: {path}")
        except Exception as e:  # noqa: BLE001 - normalize filesystem and parser errors
            raise FileOperationError(f"Failed to read {path}: {e}")

    @staticmethod
    def write_json(
        file_path: str | Path,
        data: dict[str, Any],
        create_dirs: bool = True,
        indent: int = 2
    ) -> None:
        """写入JSON文件

        Args:
            file_path: 文件路径
            data: 要写入的数据
            create_dirs: 是否创建父目录
            indent: 缩进空格数
        """
        path = Path(file_path)

        try:
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)

            logger.debug(f"Wrote JSON to {path}")

        except Exception as e:  # noqa: BLE001 - normalize filesystem and parser errors
            raise FileOperationError(f"Failed to write {path}: {e}")

    @staticmethod
    def read_text(file_path: str | Path) -> str:
        """读取文本文件

        Args:
            file_path: 文件路径

        Returns:
            文件内容
        """
        path = Path(file_path)

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            logger.debug(f"Loaded text from {path}")
            return content

        except FileNotFoundError:
            raise FileOperationError(f"File not found: {path}")
        except Exception as e:  # noqa: BLE001 - normalize filesystem and parser errors
            raise FileOperationError(f"Failed to read {path}: {e}")

    @staticmethod
    def write_text(
        file_path: str | Path,
        content: str,
        create_dirs: bool = True
    ) -> None:
        """写入文本文件

        Args:
            file_path: 文件路径
            content: 文件内容
            create_dirs: 是否创建父目录
        """
        path = Path(file_path)

        try:
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.debug(f"Wrote text to {path}")

        except Exception as e:  # noqa: BLE001 - normalize filesystem and parser errors
            raise FileOperationError(f"Failed to write {path}: {e}")

    @staticmethod
    def file_exists(file_path: str | Path) -> bool:
        """检查文件是否存在

        Args:
            file_path: 文件路径

        Returns:
            是否存在
        """
        return Path(file_path).exists()

    @staticmethod
    def ensure_dir(dir_path: str | Path) -> Path:
        """确保目录存在

        Args:
            dir_path: 目录路径

        Returns:
            Path对象
        """
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def get_file_extension(file_path: str | Path) -> str:
        """获取文件扩展名

        Args:
            file_path: 文件路径

        Returns:
            扩展名（含点，如 .yaml）
        """
        return Path(file_path).suffix.lower()

    @staticmethod
    def is_supported_format(file_path: str | Path) -> bool:
        """检查文件格式是否支持

        Args:
            file_path: 文件路径

        Returns:
            是否支持
        """
        return FileHandler.get_file_extension(file_path) in FileHandler.SUPPORTED_FORMATS


class YamlFileLoader:
    """YAML文件加载器（支持模块路径）"""

    def __init__(self, base_dir: str | Path | None = None):
        """初始化加载器

        Args:
            base_dir: 基础目录
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()

    def load(self, relative_path: str) -> dict[str, Any]:
        """加载YAML文件

        Args:
            relative_path: 相对路径

        Returns:
            解析后的字典
        """
        file_path = self.base_dir / relative_path
        return FileHandler.read_yaml(file_path)

    def load_all(self, directory: str, pattern: str = "*.yaml") -> list[dict[str, Any]]:
        """加载目录下所有YAML文件

        Args:
            directory: 目录路径（相对）
            pattern: 文件匹配模式

        Returns:
            文件内容列表
        """
        dir_path = self.base_dir / directory
        results = []

        for file_path in dir_path.glob(pattern):
            try:
                data = FileHandler.read_yaml(file_path)
                results.append(data)
            except Exception as e:  # noqa: BLE001 - normalize filesystem and parser errors
                logger.warning(f"Failed to load {file_path}: {e}")
                continue

        return results


class PromptTemplateLoader:
    """提示词模板加载器"""

    def __init__(self, prompts_dir: str | Path | None = None):
        """初始化加载器

        Args:
            prompts_dir: 提示词目录
        """
        self.prompts_dir = Path(prompts_dir) if prompts_dir else Path("prompts")

    def load_template(self, template_name: str) -> str:
        """加载提示词模板

        Args:
            template_name: 模板名称（不含扩展名）

        Returns:
            模板内容
        """
        # 尝试 .md 和 .txt
        for ext in [".md", ".txt"]:
            file_path = self.prompts_dir / f"{template_name}{ext}"
            if file_path.exists():
                return FileHandler.read_text(file_path)

        raise FileOperationError(f"Template not found: {template_name}")

    def list_templates(self) -> list[str]:
        """列出所有模板

        Returns:
            模板名称列表
        """
        templates = []
        for file_path in self.prompts_dir.glob("*.md"):
            templates.append(file_path.stem)
        for file_path in self.prompts_dir.glob("*.txt"):
            if file_path.stem not in templates:
                templates.append(file_path.stem)
        return sorted(templates)


class OutputWriter:
    """输出文件写入器"""

    def __init__(self, output_dir: str | Path | None = None):
        """初始化写入器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir) if output_dir else Path("outputs")

    def write_result(
        self,
        content: str,
        filename: str,
        subfolder: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> Path:
        """写入生成结果

        Args:
            content: 内容
            filename: 文件名
            subfolder: 子文件夹
            metadata: 元数据（将保存为同名 JSON）

        Returns:
            保存的文件路径
        """
        # 确定输出路径
        if subfolder:
            output_path = self.output_dir / subfolder / filename
        else:
            output_path = self.output_dir / filename

        # 写入内容
        FileHandler.write_text(output_path, content)

        # 写入元数据
        if metadata:
            meta_path = output_path.with_suffix(".meta.json")
            FileHandler.write_json(meta_path, metadata)

        logger.info(f"Output written to {output_path}")
        return output_path

    def write_batch(
        self,
        results: list[dict[str, Any]],
        batch_name: str
    ) -> list[Path]:
        """批量写入结果

        Args:
            results: 结果列表（每项含 content, filename, metadata）
            batch_name: 批次名称

        Returns:
            保存的文件路径列表
        """
        batch_dir = self.output_dir / batch_name
        FileHandler.ensure_dir(batch_dir)

        paths = []
        for i, result in enumerate(results):
            filename = result.get("filename", f"output_{i+1}.md")
            content = result.get("content", "")
            metadata = result.get("metadata")

            path = self.write_result(
                content=content,
                filename=filename,
                subfolder=batch_name,
                metadata=metadata
            )
            paths.append(path)

        return paths
