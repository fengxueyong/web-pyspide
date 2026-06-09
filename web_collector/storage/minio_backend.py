import io
import logging
from urllib.parse import urljoin

from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)


class MinioStorage:
    """MinIO 对象存储封装"""

    def __init__(self, endpoint, access_key, secret_key, bucket, secure=False):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self.bucket = bucket
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Bucket 不存在则自动创建"""
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
            logger.info(f"创建 bucket: {self.bucket}")

    def upload(self, object_name: str, data: bytes, content_type: str = "") -> str:
        """上传字节数据，返回可访问的 path"""
        length = len(data)
        self.client.put_object(
            self.bucket,
            object_name,
            io.BytesIO(data),
            length=length,
            content_type=content_type,
        )
        return f"{self.bucket}/{object_name}"

    def upload_file(self, object_name: str, file_path: str, content_type: str = "") -> str:
        """上传本地文件"""
        self.client.fput_object(
            self.bucket,
            object_name,
            file_path,
            content_type=content_type,
        )
        return f"{self.bucket}/{object_name}"

    def get_url(self, object_name: str) -> str:
        """获取文件的公开访问路径（返回 MinIO 内部路径，不生成 presigned URL）"""
        return f"{self.bucket}/{object_name}"
