"""
图片生成模块 - 稳定扩散模型
"""
import os
import sys
import time
import hashlib
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import numpy as np


class ImageGenerator:
    def __init__(self):
        self.enabled = True
        self.output_dir = "generated_images"
        self.model_loaded = False
        self.use_real_model = False

        # 创建目录
        os.makedirs(self.output_dir, exist_ok=True)

        # 检查依赖
        self._check_deps()

    def _check_deps(self):
        """检查依赖"""
        try:
            import torch
            import diffusers
            self.has_torch = True
            self.has_diffusers = True
            self.device = self._get_device()
            print(f"图片生成: 检测到 {self.device} 设备")
        except ImportError:
            self.has_torch = False
            self.has_diffusers = False
            self.device = "cpu"
            print("图片生成: 使用简单模式 (未安装 torch/diffusers)")

    def _get_device(self):
        """获取设备"""
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        except:
            return "cpu"

    def load_model(self):
        """加载模型"""
        if self.model_loaded:
            return True

        if not self.has_diffusers:
            return False

        try:
            print("正在加载图片生成模型...")

            from diffusers import StableDiffusionPipeline
            import torch

            # 模型选择
            model_name = "runwayml/stable-diffusion-v1-5"

            # 精度选择
            if self.device == "cuda":
                dtype = torch.float16
            else:
                dtype = torch.float32

            # 加载
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                model_name,
                torch_dtype=dtype,
                safety_checker=None,
                requires_safety_checker=False
            )

            # 移动到设备
            self.pipeline.to(self.device)

            # 优化
            if self.device == "cuda":
                self.pipeline.enable_attention_slicing()

            self.model_loaded = True
            self.use_real_model = True
            print(f"✓ 模型加载成功 ({self.device})")
            return True

        except Exception as e:
            print(f"模型加载失败: {e}")
            return False

    def generate(self, prompt, width=408, height=408, steps=25):
        """生成图片"""
        if not self.enabled:
            return "图片生成已禁用"

        print(f"生成图片: {prompt[:50]}...")

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"img_{timestamp}_{prompt_hash}.png"
        filepath = os.path.join(self.output_dir, filename)

        # 尝试真实模型
        if self.load_model() and self.use_real_model:
            try:
                return self._generate_real(prompt, width, height, steps, filepath)
            except Exception as e:
                print(f"真实生成失败: {e}，使用简单模式")
                self.use_real_model = False

        # 简单模式
        return self._generate_simple(prompt, width, height, filepath)

    def _generate_real(self, prompt, width, height, steps, filepath):
        """真实模型生成"""
        import torch

        print(f"使用稳定扩散模型生成 ({self.device})...")

        # 生成
        with torch.no_grad():
            image = self.pipeline(
                prompt=prompt,
                width=width,
                height=height,
                num_inference_steps=steps,
                guidance_scale=7.5,
                num_images_per_prompt=1
            ).images[0]

        # 保存
        image.save(filepath, "PNG")

        # 结果
        size_kb = os.path.getsize(filepath) / 1024

        result = "🖼️ 图片生成成功!\n"
        result += f"📁 文件: {filepath}\n"
        result += f"📐 尺寸: {width}x{height}\n"
        result += f"💾 大小: {size_kb:.1f}KB\n"
        result += f"⚡ 设备: {self.device}\n"
        result += f"🎨 提示: {prompt[:60]}..."

        return result

    def _generate_simple(self, prompt, width, height, filepath):
        """简单模式生成"""
        print("使用简单模式生成...")

        # 创建图像
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)

        # 根据提示选择主题
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ["天空", "蓝天", "白云", "太阳"]):
            self._draw_sky(draw, width, height)
        elif any(word in prompt_lower for word in ["夜晚", "星空", "月亮", "星星"]):
            self._draw_night(draw, width, height)
        elif any(word in prompt_lower for word in ["风景", "山水", "自然", "山脉"]):
            self._draw_landscape(draw, width, height)
        elif any(word in prompt_lower for word in ["科技", "未来", "数字", "代码"]):
            self._draw_tech(draw, width, height)
        elif any(word in prompt_lower for word in ["抽象", "艺术", "色彩", "图案"]):
            self._draw_abstract(draw, width, height)
        else:
            self._draw_default(draw, width, height, prompt)

        # 添加文字
        self._add_text(img, draw, prompt, width, height)

        # 保存
        img.save(filepath, "PNG")

        result = "🎨 图片生成完成 (简单模式)\n"
        result += f"📁 文件: {filepath}\n"
        result += f"📐 尺寸: {width}x{height}\n"
        result += f"💡 提示: {prompt[:60]}...\n"
        result += "ℹ️ 如需更高质量，请安装 torch 和 diffusers"

        return result

    def _draw_sky(self, draw, width, height):
        """绘制天空"""
        # 渐变天空
        for y in range(height):
            blue = 135 + int(120 * (y / height))
            color = (100, 149, blue)
            draw.line([(0, y), (width, y)], fill=color)

        # 太阳
        center_x, center_y = width // 2, height // 3
        radius = 35
        for x in range(center_x - radius, center_x + radius):
            for y in range(center_y - radius, center_y + radius):
                if (x - center_x) ** 2 + (y - center_y) ** 2 <= radius ** 2:
                    draw.point((x, y), fill=(255, 255, 150))

        # 云朵
        import random
        for _ in range(5):
            x = random.randint(50, width - 50)
            y = random.randint(50, height // 2)
            size = random.randint(20, 40)
            draw.ellipse([x, y, x + size, y + size // 2], fill=(255, 255, 255, 200))

    def _draw_night(self, draw, width, height):
        """绘制夜晚"""
        # 深蓝色夜空
        draw.rectangle([0, 0, width, height], fill=(10, 10, 50))

        # 星星
        import random
        for _ in range(80):
            x = random.randint(0, width - 1)
            y = random.randint(0, height * 2 // 3)
            size = random.randint(1, 3)
            brightness = random.randint(200, 255)
            color = (brightness, brightness, brightness)
            draw.ellipse([x, y, x + size, y + size], fill=color)

        # 月亮
        moon_x, moon_y = width * 3 // 4, height // 4
        moon_r = 30
        draw.ellipse([moon_x - moon_r, moon_y - moon_r,
                      moon_x + moon_r, moon_y + moon_r],
                     fill=(255, 255, 200))

    def _draw_landscape(self, draw, width, height):
        """绘制风景"""
        # 天空
        for y in range(height // 2):
            blue = 135 + int(90 * (y / (height // 2)))
            color = (100, 149, blue)
            draw.line([(0, y), (width, y)], fill=color)

        # 山脉
        import random
        points = [(0, height)]

        for i in range(1, 6):
            x = width * i // 5
            base_y = height // 2
            variation = random.randint(-40, 40)
            points.append((x, base_y + variation))

        points.append((width, height))
        draw.polygon(points, fill=(34, 139, 34))

        # 河流
        river_y = height * 3 // 4
        draw.rectangle([width // 4, river_y,
                        width * 3 // 4, river_y + 20],
                       fill=(30, 144, 255))

    def _draw_tech(self, draw, width, height):
        """绘制科技主题"""
        # 深色背景
        draw.rectangle([0, 0, width, height], fill=(0, 20, 40))

        # 网格线
        for i in range(0, width, 40):
            draw.line([(i, 0), (i, height)], fill=(0, 100, 200, 100), width=1)

        for i in range(0, height, 40):
            draw.line([(0, i), (width, i)], fill=(0, 100, 200, 100), width=1)

        # 数据点
        import random
        for _ in range(30):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            r = random.randint(2, 6)
            color = random.choice([(0, 255, 255), (255, 0, 255), (255, 255, 0)])
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color)

    def _draw_abstract(self, draw, width, height):
        """绘制抽象艺术"""
        import random

        # 随机颜色背景
        bg_color = (random.randint(0, 100),
                    random.randint(0, 100),
                    random.randint(100, 255))
        draw.rectangle([0, 0, width, height], fill=bg_color)

        # 随机形状
        for _ in range(15):
            shape = random.choice(['circle', 'rect', 'line', 'poly'])
            color = (random.randint(0, 255),
                     random.randint(0, 255),
                     random.randint(0, 255))

            if shape == 'circle':
                x = random.randint(0, width)
                y = random.randint(0, height)
                r = random.randint(10, 60)
                draw.ellipse([x - r, y - r, x + r, y + r],
                             fill=color, outline=None)

            elif shape == 'rect':
                x1 = random.randint(0, width - 100)
                y1 = random.randint(0, height - 100)
                x2 = x1 + random.randint(20, 100)
                y2 = y1 + random.randint(20, 100)
                draw.rectangle([x1, y1, x2, y2], fill=color)

            elif shape == 'line':
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)
                x2 = random.randint(0, width)
                y2 = random.randint(0, height)
                width_line = random.randint(1, 8)
                draw.line([x1, y1, x2, y2], fill=color, width=width_line)

    def _draw_default(self, draw, width, height, prompt):
        """默认绘制"""
        # 渐变背景
        color1 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        color2 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

    def _add_text(self, img, draw, prompt, width, height):
        """添加文字"""
        try:
            # 尝试加载字体
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()

            # 文字内容
            text = f"AI生成: {prompt[:25]}..." if len(prompt) > 25 else f"AI生成: {prompt}"

            # 计算文字大小
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except:
                text_width = len(text) * 8
                text_height = 20

            # 背景框
            padding = 8
            draw.rectangle([
                padding, height - text_height - 2 * padding,
                         text_width + 2 * padding, height - padding
            ], fill=(0, 0, 0, 180))

            # 文字
            draw.text(
                (2 * padding, height - text_height - padding),
                text, font=font, fill=(255, 255, 255)
            )

        except:
            pass  # 如果添加文字失败，跳过

    def enable(self):
        """启用"""
        self.enabled = True
        return True

    def disable(self):
        """禁用"""
        self.enabled = False
        return True

    def cleanup(self):
        """清理"""
        if hasattr(self, 'pipeline') and self.pipeline:
            del self.pipeline

        if self.has_torch:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


# 全局实例
_gen = ImageGenerator()


def create_image(prompt, width=408, height=408):
    """生成图片接口"""
    return _gen.generate(prompt, width, height)


def enable_gen():
    """启用"""
    return _gen.enable()


def disable_gen():
    """禁用"""
    return _gen.disable()


def cleanup():
    """清理"""
    _gen.cleanup()


def get_status():
    """获取状态"""
    return {
        "enabled": _gen.enabled,
        "model_loaded": _gen.model_loaded,
        "device": _gen.device,
        "use_real": _gen.use_real_model
    }