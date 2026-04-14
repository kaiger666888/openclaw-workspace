#!/usr/bin/env python3
"""
Markdown 转 Notion 块格式转换器
将 Markdown 文本转换为 Notion API 兼容的 JSON 块格式

用法:
    python3 markdown-to-notion.py <markdown文件> <输出json文件>
    python3 markdown-to-notion.py --content "markdown内容" <输出json文件>
"""

import re
import sys
import json
from typing import List, Dict, Any, Optional


def parse_markdown_line(line: str) -> Optional[Dict[str, Any]]:
    """解析单行 Markdown 并返回对应的 Notion 块"""
    
    line = line.rstrip()
    
    if not line.strip():
        return None
    
    # 一级标题
    if line.startswith('# '):
        return {
            "type": "heading_1",
            "heading_1": {
                "rich_text": parse_rich_text(line[2:])
            }
        }
    
    # 二级标题
    if line.startswith('## '):
        return {
            "type": "heading_2",
            "heading_2": {
                "rich_text": parse_rich_text(line[3:])
            }
        }
    
    # 三级标题
    if line.startswith('### '):
        return {
            "type": "heading_3",
            "heading_3": {
                "rich_text": parse_rich_text(line[4:])
            }
        }
    
    # 四级标题
    if line.startswith('#### '):
        return {
            "type": "heading_3",  # Notion 只有3级标题
            "heading_3": {
                "rich_text": parse_rich_text(line[5:])
            }
        }
    
    # 分隔线
    if re.match(r'^-{3,}$|^\*{3,}$|^_{3,}$', line.strip()):
        return {"type": "divider", "divider": {}}
    
    # 待办事项（必须在无序列表之前检查，因为 - [ ] 也以 - 开头）
    # - [ ] 未完成  → line[3] = ' '
    # - [x] 已完成  → line[3] = 'x'
    if line.startswith('- [ ] ') or line.startswith('- [x] '):
        checked = line[3] == 'x'
        content = line[6:]
        return {
            "type": "to_do",
            "to_do": {
                "rich_text": parse_rich_text(content),
                "checked": checked
            }
        }
    
    # 无序列表
    if line.startswith('- ') or line.startswith('* '):
        content = line[2:]
        return {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": parse_rich_text(content)
            }
        }
    
    # 有序列表
    match = re.match(r'^\d+\.\s+(.+)$', line)
    if match:
        return {
            "type": "numbered_list_item",
            "numbered_list_item": {
                "rich_text": parse_rich_text(match.group(1))
            }
        }
    
    # 引用
    if line.startswith('> '):
        return {
            "type": "quote",
            "quote": {
                "rich_text": parse_rich_text(line[2:])
            }
        }
    
    # 代码块（多行处理需要特殊逻辑）
    if line.startswith('```'):
        return None  # 由调用者处理
    
    # 表格行（特殊处理）
    if line.startswith('|') and '|' in line[1:]:
        return None  # 由调用者处理
    
    # 普通段落
    return {
        "type": "paragraph",
        "paragraph": {
            "rich_text": parse_rich_text(line)
        }
    }


def parse_rich_text(text: str) -> List[Dict[str, Any]]:
    """解析包含 Markdown 格式的文本为 Notion rich_text 格式"""
    rich_text = []
    
    # 简单实现：将整个文本作为一个文本块
    # TODO: 可以扩展支持 **粗体**、*斜体*、`代码`、[链接](url) 等
    
    # 处理链接 [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    last_end = 0
    
    for match in re.finditer(link_pattern, text):
        # 添加链接前的文本
        if match.start() > last_end:
            before = text[last_end:match.start()]
            rich_text.extend(parse_inline_formatting(before))
        
        # 添加链接
        link_text = match.group(1)
        link_url = match.group(2)
        rich_text.append({
            "type": "text",
            "text": {"content": link_text, "link": {"url": link_url}}
        })
        
        last_end = match.end()
    
    # 添加最后的文本
    if last_end < len(text):
        remaining = text[last_end:]
        rich_text.extend(parse_inline_formatting(remaining))
    
    return rich_text if rich_text else [{"type": "text", "text": {"content": text}}]


def parse_inline_formatting(text: str) -> List[Dict[str, Any]]:
    """解析行内格式（粗体、斜体、代码、纯URL）为 Notion rich_text"""
    if not text:
        return []

    result = []

    # 组合模式：粗体+斜体、粗体、斜体、行内代码、纯URL
    # 注意顺序很重要：先匹配更长的模式
    patterns = [
        # 粗体+斜体 ***text*** 或 ___text___
        (r'\*\*\*(.+?)\*\*\*', {"bold": True, "italic": True}),
        (r'___(.+?)___', {"bold": True, "italic": True}),
        # 粗体 **text** 或 __text__
        (r'\*\*(.+?)\*\*', {"bold": True}),
        (r'__(.+?)__', {"bold": True}),
        # 斜体 *text* 或 _text_ (注意避免匹配 _xxx_ 中间的下划线)
        (r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', {"italic": True}),
        (r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', {"italic": True}),
        # 行内代码 `code`
        (r'`([^`]+)`', {"code": True}),
        # 纯 URL (http:// 或 https://)
        (r'(https?://[^\s\)]+)', {"link": True}),
    ]

    # 使用单个正则表达式匹配所有格式
    combined_pattern = r'(\*\*\*.+?\*\*\*|___.+?___|\*\*.+?\*\*|__.+?__|(?<!\*)\*(?!\*).+?(?<!\*)\*(?!\*)|(?<!_)_(?!_).+?(?<!_)_(?!_)|`[^`]+`|https?://[^\s\)]+)'

    last_end = 0

    for match in re.finditer(combined_pattern, text):
        # 添加匹配前的普通文本
        if match.start() > last_end:
            before = text[last_end:match.start()]
            if before:
                result.append({"type": "text", "text": {"content": before}})

        matched = match.group(0)

        # 判断是哪种格式
        if matched.startswith('***') and matched.endswith('***'):
            content = matched[3:-3]
            result.append({
                "type": "text",
                "text": {"content": content},
                "annotations": {"bold": True, "italic": True}
            })
        elif matched.startswith('___') and matched.endswith('___'):
            content = matched[3:-3]
            result.append({
                "type": "text",
                "text": {"content": content},
                "annotations": {"bold": True, "italic": True}
            })
        elif matched.startswith('**') and matched.endswith('**'):
            content = matched[2:-2]
            result.append({
                "type": "text",
                "text": {"content": content},
                "annotations": {"bold": True}
            })
        elif matched.startswith('__') and matched.endswith('__'):
            content = matched[2:-2]
            result.append({
                "type": "text",
                "text": {"content": content},
                "annotations": {"bold": True}
            })
        elif matched.startswith('`') and matched.endswith('`'):
            content = matched[1:-1]
            result.append({
                "type": "text",
                "text": {"content": content},
                "annotations": {"code": True}
            })
        elif matched.startswith('*') and matched.endswith('*'):
            content = matched[1:-1]
            result.append({
                "type": "text",
                "text": {"content": content},
                "annotations": {"italic": True}
            })
        elif matched.startswith('_') and matched.endswith('_'):
            content = matched[1:-1]
            result.append({
                "type": "text",
                "text": {"content": content},
                "annotations": {"italic": True}
            })
        elif matched.startswith('http://') or matched.startswith('https://'):
            # 纯 URL，转换为 Notion 链接
            result.append({
                "type": "text",
                "text": {"content": matched, "link": {"url": matched}}
            })
        else:
            # 未知格式，作为普通文本
            result.append({"type": "text", "text": {"content": matched}})

        last_end = match.end()

    # 添加最后的文本
    if last_end < len(text):
        remaining = text[last_end:]
        if remaining:
            result.append({"type": "text", "text": {"content": remaining}})

    return result if result else [{"type": "text", "text": {"content": text}}]


def convert_markdown_to_blocks(markdown: str) -> List[Dict[str, Any]]:
    """将 Markdown 文本转换为 Notion 块列表"""
    blocks = []
    lines = markdown.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 处理代码块
        if line.strip().startswith('```'):
            code_lines = []
            language = line.strip()[3:].strip() or "plain text"
            i += 1
            
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            
            code_content = '\n'.join(code_lines)
            if code_content:
                blocks.append({
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": code_content}}],
                        "language": language
                    }
                })
            i += 1
            continue
        
        # 处理表格
        if line.strip().startswith('|') and '|' in line[1:]:
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                # 跳过分隔行
                if re.match(r'^\|[\s\-:|]+\|$', lines[i].strip()):
                    i += 1
                    continue
                table_lines.append(lines[i])
                i += 1
            
            # 转换为 Notion 表格格式
            if table_lines:
                # 解析表格行
                table_rows = []
                num_columns = 0
                
                for idx, table_line in enumerate(table_lines):
                    # 分割单元格：| cell1 | cell2 | cell3 |
                    cells_raw = table_line.split('|')
                    # 去掉首尾空元素
                    cells = []
                    for j, cell in enumerate(cells_raw):
                        if j == 0 or j == len(cells_raw) - 1:
                            continue  # 跳过首尾的空字符串
                        cells.append(cell.strip())
                    
                    # 记录列数（从第一行）
                    if idx == 0:
                        num_columns = len(cells)
                    
                    # 创建单元格 rich_text
                    row_cells = []
                    for cell in cells:
                        # 解析单元格内容（支持行内格式）
                        cell_rich_text = parse_rich_text(cell)
                        row_cells.append(cell_rich_text)
                    
                    # 创建表格行
                    table_rows.append({
                        "type": "table_row",
                        "table_row": {
                            "cells": row_cells
                        }
                    })
                
                # 创建表格块
                if table_rows and num_columns > 0:
                    blocks.append({
                        "type": "table",
                        "table": {
                            "table_width": num_columns,
                            "has_column_header": True,
                            "has_row_header": False,
                            "children": table_rows
                        }
                    })
            continue
        
        # 普通行
        block = parse_markdown_line(line)
        if block:
            blocks.append(block)
        
        i += 1
    
    return blocks


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("错误: 参数不足")
        sys.exit(1)
    
    if sys.argv[1] == '--content':
        markdown = sys.argv[2]
        output_file = sys.argv[3]
    else:
        markdown_file = sys.argv[1]
        output_file = sys.argv[2]
        
        try:
            with open(markdown_file, 'r', encoding='utf-8') as f:
                markdown = f.read()
        except Exception as e:
            print(f"❌ 读取 Markdown 文件失败: {e}")
            sys.exit(1)
    
    # 转换为 Notion 块
    blocks = convert_markdown_to_blocks(markdown)
    
    # 输出 JSON 格式
    output = {"children": blocks}
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"✅ 转换成功: {len(blocks)} 个块 → {output_file}")
    except Exception as e:
        print(f"❌ 写入 JSON 文件失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
