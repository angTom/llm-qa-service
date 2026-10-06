

import logging
from pathlib import Path
from typing import ClassVar, Dict


class Logger:
    """
    全局统一日志管理器
    """
    # 缓存已经创建的logger实例，防止重复添加handler
    _cache: ClassVar[Dict[str, logging.Logger]] = {}
    def __init__(self, name: str,log_file: str, log_dir: str | None=None, level: int=logging.INFO):
        """
        初始化日志管理器
        :param name: 日志名称
        :param log_file: 日志文件名
        :param log_dir: 日志目录
        """
        # 获取一个日志管理器
        self.logger = logging.getLogger(name)
        # 设置日志级别
        self.logger.setLevel(level)
        # 防止重复添加日志处理器
        if self.logger.hasHandlers():  # 判断日志处理器是否已添加
            # 添加的话直接返回
            return

        # 判断传入的日志目录是否存在,如果为None则使用默认目录
        # 将格式转为Path对象,方便使用
        if log_dir is None:  # 如果日志目录为None,则使用默认目录
            log_dir = Path("./logs")
        else:  # 如果日志目录不为None,则使用传入的目录
            log_dir = Path(log_dir)
        try:
            if not log_dir.exists():
                # 如果文件目录不存在,则自动创建
                log_dir.mkdir(parents=True, exist_ok=True)
            elif not log_dir.is_dir(): # 如果文件目录存在,但非目录,则报错
                raise NotADirectoryError(f"路径{log_dir} 是一个普通文件,无法作为目录使用")
        except (OSError, PermissionError, NotADirectoryError):

            raise

        # 拼接文件名
        log_path = log_dir / log_file

        # 定义日志的输出格式
        formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S")

        # 控制台输出
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler) # 添加处理器

        # 文件输出
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter) # 设置格式
        self.logger.addHandler(file_handler) # 添加处理器

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        类方法，直接 Logger.get_logger(__name__) 获取logger，单例缓存
        """
        if name not in cls._cache:
            # 实例化并缓存
            instance = Logger(name=name,log_file=f"{name}.log")
            cls._cache[name] = instance
        return cls._cache[name].logger
