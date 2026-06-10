import datetime

from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, JSON, Index,
)
from sqlalchemy.orm import relationship

from .engine import Base


class ProxyConfig(Base):
    """代理配置"""
    __tablename__ = "t_proxy_config"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="代理配置ID")
    name = Column(String(128), nullable=False, comment="配置名称")
    proxy_http = Column(String(512), nullable=True, comment="HTTP代理地址")
    proxy_https = Column(String(512), nullable=True, comment="HTTPS代理地址")
    username = Column(String(256), nullable=True, comment="认证用户名")
    password = Column(String(512), nullable=True, comment="认证密码")
    create_time = Column(DateTime, nullable=True, default=datetime.datetime.utcnow, comment="创建时间")
    update_time = Column(DateTime, nullable=True, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, comment="更新时间")

    tasks = relationship("ScrapTask", back_populates="proxy_config")


class ScrapTask(Base):
    """抓取任务"""
    __tablename__ = "t_scrap_task"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="抓取任务ID")
    website = Column(String(2048), nullable=False, comment="网址")
    website_hash = Column(String(32), nullable=False, comment="网址MD5，用于索引和去重")
    res_type = Column(String(64), nullable=False, default="all", comment="资源类型：all-全部, text/article-文本/文章, pic-图片, doc-文档, audio-音频, video-视频")
    scrap_time = Column(DateTime, nullable=True, comment="爬取时间")
    cancel_time = Column(DateTime, nullable=True, comment="取消时间")
    depth = Column(Integer, nullable=False, default=1, comment="抓取深度：1/2/3")
    link_follow = Column(Integer, nullable=False, default=0, comment="是否跟随链接：0-否, 1-是")
    save_method = Column(String(16), nullable=False, default="download", comment="保存方式：only_record-仅记录元数据, download-下载文件")
    status = Column(String(16), nullable=False, default="running", comment="任务状态：running-运行中, finished-已完成, cancel-已取消")
    res_number = Column(Integer, nullable=False, default=0, comment="抓取资源数")
    extension = Column(JSON, nullable=True, comment="扩展字段（JSON），可空")
    proxy_id = Column(Integer, nullable=False, default=-1, comment="代理配置ID，-1表示不走代理")

    __table_args__ = (
        Index("idx_task_query", "website_hash", "res_type", "depth", "link_follow", "save_method"),
    )

    resources = relationship("Resource", back_populates="task")
    proxy_config = relationship("ProxyConfig", back_populates="tasks")


class Resource(Base):
    """抓取资源"""
    __tablename__ = "t_resources"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="资源ID")
    scrap_task_id = Column(Integer, ForeignKey("t_scrap_task.id"), nullable=False, comment="抓取任务ID")
    website = Column(String(2048), nullable=False, comment="冗余字段，关联任务网址")
    res_link = Column(Text, nullable=True, comment="资源链接")
    parent_link = Column(Text, nullable=False, default="-1", comment="父链接，-1表示第一层")
    res_type = Column(String(32), nullable=False, comment="资源类型：text/article-文本/文章, pic-图片, doc-文档, audio-音频, video-视频")
    object_id = Column(String(256), nullable=True, comment="MongoDB/MinIO 对象标识")
    res_size = Column(BigInteger, nullable=False, default=0, comment="资源大小（字节）")
    create_time = Column(DateTime, nullable=True, default=datetime.datetime.utcnow, comment="创建时间")
    update_time = Column(DateTime, nullable=True, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, comment="更新时间")
    extension = Column(JSON, nullable=True, comment="扩展字段（JSON），可空")

    __table_args__ = (
        Index("idx_task_resource", "scrap_task_id", "res_link",
              mysql_length={"res_link": 255}),
    )

    task = relationship("ScrapTask", back_populates="resources")
