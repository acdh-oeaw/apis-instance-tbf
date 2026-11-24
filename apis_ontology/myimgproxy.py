import os

from imgproxy import ImgProxy


class MyImgProxy:
    """Wrapper module for the ImgProxy library"""

    def __init__(self, *args, **kwargs):
        self.key = os.getenv("IMGPROXY_KEY")
        self.salt = os.getenv("IMGPROXY_SALT")
        self.proxy_host = "https://imgproxy.acdh.oeaw.ac.at"

    def imgproxy(self, path):
        """Generate an imgproxy instance for a specific image path"""
        path = f"s3://for-imgproxy/{path}"
        return ImgProxy(path, proxy_host=self.proxy_host, key=self.key, salt=self.salt)

    def image(self, path):
        """return an url to the original image residing at `path`"""
        return self.imgproxy(path)()

    def image_resized(self, path, width=150, height=200):
        """return a resized version of the image at `path`"""
        return self.imgproxy(path)(width=width, height=height, resizing_type="fit")
