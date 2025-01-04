import oss2
import os
from datetime import datetime

class OssHelper:
    def __init__(self):
        # 从环境变量获取 OSS 配置
        self.access_key_id = os.getenv('OSS_ACCESS_KEY_ID')
        self.access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET')
        self.endpoint = os.getenv('OSS_ENDPOINT')
        self.bucket_name = os.getenv('OSS_BUCKET_NAME')
        
        # 创建 Bucket 实例
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)

    def upload_file(self, file_path, remote_path=None):
        """上传文件到 OSS"""
        try:
            if remote_path is None:
                remote_path = os.path.basename(file_path)

            # 上传文件
            with open(file_path, 'rb') as f:
                self.bucket.put_object(remote_path, f)

            # 生成文件的URL（默认有效期为1小时）
            url = self.bucket.sign_url('GET', remote_path, 3600)
            return url

        except Exception as e:
            print(f"上传文件到OSS失败: {str(e)}")
            raise