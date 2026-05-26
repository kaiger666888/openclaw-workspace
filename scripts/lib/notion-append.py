#!/usr/bin/env python3
"""
Notion 内容追加工具（Markdown 格式）
解决 2000 字符限制和引号转义问题

⚠️ 警告：此工具追加 Markdown 文本，不符合 Notion 格式标准
推荐使用 JSON 块格式：notion-cli block append --children-file <json-file> <page-id>

用法:
    python3 notion-append.py <页面ID> <内容文件>
    python3 notion-append.py <页面ID> --content <内容>
"""

import subprocess
import sys
import os

NOTION_CLI = "/home/kai/.local/bin/notion-cli"
CHUNK_SIZE = 1900  # 留100字符余量


def append_to_notion(page_id: str, content: str, verbose: bool = True) -> bool:
    """
    将内容追加到 Notion 页面，自动处理分段
    
    ⚠️ 注意：此函数追加 Markdown 文本，不符合 Notion 格式标准
    推荐使用 JSON 块格式创建页面
    
    Args:
        page_id: Notion 页面ID
        content: 要追加的内容
        verbose: 是否输出详细信息
    
    Returns:
        True 如果成功，False 如果失败
    """
    # 清理环境变量
    env = os.environ.copy()
    env.pop('NODE_OPTIONS', None)
    
    content_len = len(content)
    
    # 如果内容不长，直接追加
    if content_len <= CHUNK_SIZE:
        if verbose:
            print(f"📝 追加内容 ({content_len}字符)...")
        
        result = subprocess.run(
            [NOTION_CLI, 'page', 'append', '--content', content, page_id],
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            if verbose:
                print(f"✅ {result.stdout.strip()}")
            return True
        else:
            print(f"❌ 追加失败: {result.stderr}")
            return False
    
    # 分段追加
    total_parts = (content_len + CHUNK_SIZE - 1) // CHUNK_SIZE
    
    if verbose:
        print(f"📝 内容较长 ({content_len}字符)，将分{total_parts}段追加...")
    
    start = 0
    part_num = 1
    
    while start < content_len:
        end = start + CHUNK_SIZE
        if end > content_len:
            end = content_len
        
        # 在段落边界分割
        if end < content_len:
            chunk = content[start:end]
            # 找到最后一个换行符
            last_newline = chunk.rfind('\n')
            if last_newline > CHUNK_SIZE // 2:
                end = start + last_newline + 1
                chunk = content[start:end]
        else:
            chunk = content[start:end]
        
        if verbose:
            print(f"  📄 第{part_num}/{total_parts}段 ({len(chunk)}字符)...")
        
        result = subprocess.run(
            [NOTION_CLI, 'page', 'append', '--content', chunk, page_id],
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ 第{part_num}段追加失败: {result.stderr}")
            return False
        
        if verbose:
            print(f"  ✅ 完成")
        
        start = end
        part_num += 1
    
    if verbose:
        print(f"✅ 所有内容追加完成 ({total_parts}段)")
    return True


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("错误: 参数不足")
        sys.exit(1)
    
    page_id = sys.argv[1]
    
    if sys.argv[2] == '--content':
        # 从命令行参数读取内容
        content = ' '.join(sys.argv[3:])
    else:
        # 从文件读取内容
        content_file = sys.argv[2]
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"❌ 文件不存在: {content_file}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            sys.exit(1)
    
    if not content.strip():
        print("❌ 内容为空")
        sys.exit(1)
    
    success = append_to_notion(page_id, content)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
