import math

from PIL import Image


def add_logo(src_img: Image, logo_img: Image, dst_img: str, dst_format: str = None, top: int = 30,
             right: int = 55) -> None:
    """
    给图像添加logo
    :param src_img: 背景图像（Image类型对象）
    :param logo_img: logo图像（Image类型对象）
    :param dst_img: 处理后的图片存储路径
    :param dst_format: 存储图片类型（‘JPEG’、‘JPG’、‘PNG’）
    :param top:  logo距离源图顶部的像素距离（单位：px）
    :param right: logo距离源图右边界的像素距离（单位：px）
    :return: None
    """
    # 获取背景图宽和高
    (W, H) = src_img.size
    (w, h) = logo_img.size
    layer = Image.new('RGBA', src_img.size, (255, 255, 255, 0))
    layer.paste(logo_img, (W - w - right, top))
    result = Image.composite(layer, src_img, layer)
    result.save(dst_img, dst_format, quality=100)


if __name__ == '__main__':
    # 背景图像
    img = Image.open('image/bg.jpg')
    # logo图像（需要保证像素大小要比src_img要小）
    logo = Image.open('logo/logo.png')
    # 获取背景图宽和高
    (W, H) = img.size
    (w, h) = logo.size
    scale = 0.3
    logo.thumbnail(size=map(math.floor, (w * scale, h * scale)),
                   resample=Image.ANTIALIAS)
    (w, h) = logo.size
    top = H - h - 30
    right = 52
    add_logo(img, logo, 'out/bg.png', dst_format='PNG', top=top, right=right)
