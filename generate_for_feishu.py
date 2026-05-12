import os
import sys
import base64
from PIL import Image
import io

def get_mime_type(image_path):
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.webp': 'image/webp',
        '.gif': 'image/gif'
    }
    return mime_types.get(ext, 'image/png')

def compress_image(image_path, quality=85, max_size=(1920, 1080)):
    """压缩图片，返回压缩后的二进制数据"""
    try:
        with Image.open(image_path) as img:
            # 限制最大尺寸
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            # 转换为RGB（去除透明通道）
            if img.mode in ('RGBA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])
                else:
                    background.paste(img)
                img = background
            
            # 保存为JPEG
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            return buffer.getvalue()
    except Exception as e:
        print(f"压缩失败，使用原图: {e}")
        with open(image_path, 'rb') as f:
            return f.read()

def generate_html(image_dir, output_file='feishu.html', quality=85):
    """生成HTML文件，可以直接复制粘贴到飞书"""
    if not os.path.isdir(image_dir):
        print(f"错误：目录 '{image_dir}' 不存在")
        return
    
    image_patterns = ['{}.png', '{}.jpg', '{}.jpeg', '{}.webp', '{}.gif', 
                      'image_{}.png', 'image_{}.jpg', 'image_{}.jpeg', 'image_{}.webp', 'image_{}.gif']
    
    html_parts = []
    html_parts.append('<!DOCTYPE html>')
    html_parts.append('<html>')
    html_parts.append('<head>')
    html_parts.append('<meta charset="UTF-8">')
    html_parts.append('<title>飞书文档</title>')
    html_parts.append('<style>')
    html_parts.append('body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 20px; }')
    html_parts.append('h2 { color: #333; margin-top: 30px; margin-bottom: 15px; font-size: 18px; }')
    html_parts.append('img { max-width: 100%; height: auto; display: block; margin: 10px 0; border-radius: 4px; }')
    html_parts.append('</style>')
    html_parts.append('</head>')
    html_parts.append('<body>')
    
    found_count = 0
    
    for i in range(1, 16):
        found = False
        for pattern in image_patterns:
            image_path = os.path.join(image_dir, pattern.format(i))
            if os.path.exists(image_path):
                # 压缩图片
                image_data = compress_image(image_path, quality=quality)
                # 转换为base64
                encoded = base64.b64encode(image_data).decode('utf-8')
                mime_type = 'image/jpeg'  # 压缩后都是JPEG
                
                html_parts.append(f'<h2>Step{i}</h2>')
                html_parts.append(f'<img src="data:{mime_type};base64,{encoded}" alt="Step{i}">')
                
                found = True
                found_count += 1
                break
        
        if not found:
            print(f"警告：Step {i} 的图片未找到")
    
    html_parts.append('</body>')
    html_parts.append('</html>')
    
    output_path = os.path.join(image_dir, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_parts))
    
    print(f"\n✅ HTML文件已生成：{output_path}")
    print(f"📊 共处理 {found_count} 张图片")
    print(f"\n💡 使用方法：")
    print(f"   1. 用浏览器打开 {output_file}")
    print(f"   2. 全选内容 (Ctrl+A)")
    print(f"   3. 复制 (Ctrl+C)")
    print(f"   4. 粘贴到飞书文档 (Ctrl+V)")
    print(f"\n⚠️  如果还是太大，可以：")
    print(f"   - 降低质量：python generate_for_feishu.py ./images --quality 70")
    print(f"   - 更低质量：python generate_for_feishu.py ./images --quality 50")

def generate_markdown_simple(image_dir, output_file='output.md'):
    """生成简单的Markdown文件（使用相对路径）"""
    if not os.path.isdir(image_dir):
        print(f"错误：目录 '{image_dir}' 不存在")
        return
    
    image_patterns = ['{}.png', '{}.jpg', '{}.jpeg', '{}.webp', '{}.gif',
                      'image_{}.png', 'image_{}.jpg', 'image_{}.jpeg', 'image_{}.webp', 'image_{}.gif']
    
    markdown_content = ""
    found_count = 0
    
    for i in range(1, 16):
        found = False
        for pattern in image_patterns:
            image_path = os.path.join(image_dir, pattern.format(i))
            if os.path.exists(image_path):
                filename = os.path.basename(image_path)
                markdown_content += f"## Step{i}\n\n"
                markdown_content += f"![Step{i}]({filename})\n\n"
                found = True
                found_count += 1
                break
        
        if not found:
            print(f"警告：Step {i} 的图片未找到")
    
    output_path = os.path.join(image_dir, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"\n✅ Markdown文件已生成：{output_path}")
    print(f"📊 共处理 {found_count} 张图片")
    print(f"\n💡 使用方法：")
    print(f"   1. 在Obsidian或其他支持本地图片的编辑器中打开")
    print(f"   2. 复制内容粘贴到飞书（部分飞书版本支持自动上传本地图片）")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方法：")
        print("  python generate_for_feishu.py <图片目录路径> [选项]")
        print()
        print("模式选项：")
        print("  --html           生成HTML文件（默认，推荐）")
        print("  --md             生成Markdown文件（使用相对路径）")
        print()
        print("其他选项：")
        print("  --quality <值>   图片压缩质量 1-100（默认：85）")
        print()
        print("示例：")
        print("  python generate_for_feishu.py ./images")
        print("  python generate_for_feishu.py ./images --quality 70")
        print("  python generate_for_feishu.py ./images --md")
        sys.exit(1)
    
    image_dir = sys.argv[1]
    mode = 'html'  # 默认html模式
    quality = 85
    
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--html':
            mode = 'html'
        elif arg == '--md':
            mode = 'md'
        elif arg == '--quality':
            if i + 1 < len(sys.argv):
                quality = int(sys.argv[i + 1])
                i += 1
        i += 1
    
    if mode == 'html':
        generate_html(image_dir, quality=quality)
    else:
        generate_markdown_simple(image_dir)