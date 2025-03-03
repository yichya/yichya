# coding=utf8

import os
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

def convert_heic_to_jpeg(heic_path, jpeg_path, size=(1280, 960)):
    try:
        img = Image.open(heic_path)
        img = img.resize(size)
        img.save(jpeg_path, "JPEG")
        print(f"转换成功: {heic_path} -> {jpeg_path}")
    except Exception as e:
        print(f"转换失败: {heic_path} - {e}")

def batch_convert_heic_to_jpeg(heic_dir, jpeg_dir):
    if not os.path.exists(jpeg_dir):
        os.makedirs(jpeg_dir)

    for filename in os.listdir(heic_dir):
        if filename.lower().endswith(".heic"):
            heic_path = os.path.join(heic_dir, filename)
            jpeg_filename = os.path.splitext(filename)[0] + ".jpeg"
            jpeg_path = os.path.join(jpeg_dir, jpeg_filename)
            convert_heic_to_jpeg(heic_path, jpeg_path)

if __name__ == "__main__":
    heic_directory = "guilin-experience"  # HEIC 图片所在的文件夹
    jpeg_directory = "guilin-experience"  # JPEG 图片输出文件夹
    batch_convert_heic_to_jpeg(heic_directory, jpeg_directory)
