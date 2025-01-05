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
        
        # 更彻底地处理代理设置
        proxy_related_vars = [
            'HTTP_PROXY', 'HTTPS_PROXY', 
            'http_proxy', 'https_proxy',
            'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE'  # 相关的证书设置也可能影响代理
        ]
        
        # 临时清除所有代理相关的环境变量
        saved_env = {}
        for var in proxy_related_vars:
            if var in os.environ:
                saved_env[var] = os.environ[var]
                del os.environ[var]
        
        try:
            auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            self.bucket = oss2.Bucket(
                auth, 
                self.endpoint, 
                self.bucket_name,
                proxies={'http': None, 'https': None}  # 显式禁用所有代理
            )
        finally:
            # 恢复环境变量
            for var, value in saved_env.items():
                os.environ[var] = value

    def upload_file(self, file_path, remote_path=None):
        """上传文件到 OSS"""
        if remote_path is None:
            remote_path = os.path.basename(file_path)

        try:
            # 使用二进制方式读取整个文件内容
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 直接上传内容，避免流式传输可能带来的异步问题
            result = self.bucket.put_object(remote_path, content)
            
            if result.status == 200:
                # 生成文件的URL（默认有效期为1小时）
                url = self.bucket.sign_url('GET', remote_path, 3600)
                return url
            else:
                raise Exception(f"Upload failed with status: {result.status}")

        except Exception as e:
            print(f"上传文件到OSS失败: {str(e)}")
            # 添加更详细的错误信息
            print(f"详细错误信息: {type(e).__name__}")
            raise

        print(f"Endpoint: {self.endpoint}")
        print(f"Bucket: {self.bucket_name}")
        print(f"File size: {os.path.getsize(file_path)}")