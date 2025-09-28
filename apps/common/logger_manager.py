# apps/common/logger_manager.py
import logging
import os
import queue
import yaml
from typing import Optional
from logging.handlers import TimedRotatingFileHandler, QueueHandler, QueueListener
from apps.common.json_formatter import JSONFormatter


class LoggerManager:
    """
    日志管理类（支持 YAML 配置 + 异步队列）
    - 每个子项目：access / error / app / perf 四类日志（各写各的）
    - 全局：system.log
    - 关键点：每个文件 handler 绑定一个 Filter，只接收匹配 logger 名称的记录，避免“广播到所有文件”
    """

    def __init__(self, config_file: str = "logging.yaml"):
        self._load_config(config_file)

        self.log_queue = queue.Queue(-1)
        self._loggers: dict[str, logging.Logger] = {}
        self._listener: Optional[QueueListener] = None

        self._start_listener()  # 先启动监听器（默认挂上 console）

        # 全局 system logger（只写 system.log）
        self.system_logger = self._create_logger(
            name="system",
            filename="system.log",
            level=self.log_level,
        )

        # （可选）按 YAML 预创建项目日志器
        for project, conf in self.projects.items():
            if conf.get("enabled", False):
                for category in conf.get("categories", []):
                    self.get_project_logger(project, category)

    # ---------- config ----------
    def _load_config(self, config_file: str):
        with open(config_file, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        log_cfg = cfg.get("logging", {})

        self.log_root = log_cfg.get("log_root", "logs")
        self.backup_days = log_cfg.get("backup_days", 7)
        self.log_level = getattr(logging, log_cfg.get("level", "INFO").upper(), logging.INFO)
        self.projects = log_cfg.get("projects", {})

        os.makedirs(self.log_root, exist_ok=True)

    # ---------- listener ----------
    def _start_listener(self):
        # 控制台 handler（stdout），方便本地查看；不加过滤器，让它接收所有日志
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JSONFormatter())

        # 注意：QueueListener(queue, *handlers, respect_handler_level=True)
        self._listener = QueueListener(self.log_queue, console_handler, respect_handler_level=True)
        self._listener.start()

    # ---------- handlers ----------
    def _create_file_handler(
        self,
        filepath: str,
        level: int = logging.INFO,
        filter_name: Optional[str] = None,
    ) -> logging.Handler:
        """
        创建 JSON 格式的文件 handler，并且（可选）只放行指定 logger 名的记录
        """
        handler = TimedRotatingFileHandler(
            filepath,
            when="midnight",
            backupCount=self.backup_days,
            encoding="utf-8",
        )
        handler.setLevel(level)
        handler.setFormatter(JSONFormatter())

        # ✅ 关键：绑定过滤器——只接收来自指定 logger（及其子 logger）的记录
        if filter_name:
            handler.addFilter(logging.Filter(filter_name))

        return handler

    def _create_logger(self, name: str, filename: str, level: int = logging.INFO) -> logging.Logger:
        """
        创建一个 logger：
        - 生产端：Logger -> QueueHandler（把日志投递到队列）
        - 消费端：QueueListener.handlers（文件/控制台）真正写入
        - 文件 handler 绑定 Filter(name)，只接收这个 logger 的记录
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False  # 不向上冒泡，避免根 logger 再处理一次

        # 生产端：入队
        qh = QueueHandler(self.log_queue)
        logger.addHandler(qh)

        # 消费端：为这个 logger 准备一个专属文件 handler，并挂到 listener 上
        file_path = os.path.join(self.log_root, filename)
        file_handler = self._create_file_handler(file_path, level=level, filter_name=name)

        # ✅ QueueListener 没有 addHandler；用“拼接元组”的方式动态追加
        if self._listener:
            self._listener.handlers = self._listener.handlers + (file_handler,)

        return logger

    # ---------- public ----------
    def get_project_logger(self, project: str, category: str) -> logging.Logger:
        """
        获取子项目的指定类别日志器
        logger 名采用：{project}_{category}
        文件路径：logs/{project}/{category}.log
        """
        key = f"{project}_{category}"
        if key in self._loggers:
            return self._loggers[key]

        project_dir = os.path.join(self.log_root, project)
        os.makedirs(project_dir, exist_ok=True)

        filename = os.path.join(project, f"{category}.log")
        level = {
            "access": logging.INFO,
            "error": logging.ERROR,
            "app": logging.INFO,
            "perf": logging.INFO,
        }.get(category, self.log_level)

        logger = self._create_logger(name=key, filename=filename, level=level)
        self._loggers[key] = logger
        return logger

    def stop(self):
        if self._listener:
            self._listener.stop()
