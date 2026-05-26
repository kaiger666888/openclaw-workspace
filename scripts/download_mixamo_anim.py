#!/usr/bin/env python3
"""
Mixamo 动画批量下载 — Without Skin 版本
第一次运行需要登录（会打开浏览器），之后用保存的 cookies 自动下载。
"""
import asyncio
import json
import os
import sys

from playwright.async_api import async_playwright

OUTPUT_DIR = r"D:\BlenderAgent\animations\motions_anim"
COOKIES_FILE = os.path.expanduser("~/.mixamo_cookies.json")
CHARACTER = "Y_Bot"  # 下载时用的角色（不影响动画数据）

# 常用动画列表
ANIMATIONS = [
    # 行走
    "walking_forward_inplace",
    "walking_backward_inplace",
    "walking_left_inplace",
    "walking_right_inplace",
    "walking_inplace",
    # 跑步
    "running_inplace",
    "running_forward_inplace",
    "running_backward_inplace",
    # 待机
    "idle",
    "idle_inplace",
    "standing_idle",
    "breathing_idle",
    # 战斗
    "fighting_idle",
    "boxing_idle",
    # 情绪
    "happy_idle",
    "sad_idle",
    "angry_idle",
    "surprised_idle",
    # 特殊
    "dancing_the_running_man_inplace",
    "talking_inplace",
    "clap_while_standing",
    "waving",
    "jump_inplace",
    "sitting_idle",
    "crouch_idle_inplace",
    "dying_from_standing_idle",
    "victory",
    "laughing_standing",
    "yelling_in_anger",
]


async def ensure_login(page, context):
    """确保已登录 Mixamo，必要时等待手动登录"""
    await page.goto("https://www.mixamo.com/", wait_until="networkidle")
    await asyncio.sleep(2)

    # 检查是否已登录（已登录时会有搜索框和头像）
    logged_in = await page.query_selector('input[type="search"]') is not None
    if logged_in:
        print("✅ 已登录（cookies 有效）")
        return True

    # 需要登录
    print("⚠️  需要登录 Mixamo")
    print("   请在弹出的浏览器中完成登录...")
    print("   登录完成后脚本会自动继续\n")

    # 等待登录完成（检测搜索框出现）
    for _ in range(120):
        await asyncio.sleep(2)
        if await page.query_selector('input[type="search"]'):
            print("✅ 登录成功！")
            # 保存 cookies
            cookies = await context.cookies()
            with open(COOKIES_FILE, "w") as f:
                json.dump(cookies, f, indent=2)
            print(f"   Cookies 已保存到 {COOKIES_FILE}")
            return True

    print("❌ 登录超时（2分钟）")
    return False


async def download_animation(page, anim_name):
    """下载单个动画"""
    print(f"  搜索: {anim_name}")

    # 搜索
    await page.goto(f"https://www.mixamo.com/search/?query={anim_name}", wait_until="networkidle")
    await asyncio.sleep(3)

    # 点击第一个结果
    cards = await page.query_selector_all(".search-result-card")
    if not cards:
        # 尝试其他选择器
        cards = await page.query_selector_all("a[href*='/characters/']")
    if not cards:
        print(f"  ⏭️  未找到，跳过")
        return False

    await cards[0].click()
    await asyncio.sleep(3)

    # 选择角色
    char_select = await page.query_selector("#character-preview-character-select")
    if char_select:
        # 尝试选择 Y_Bot
        options = await char_select.query_selector_all("option")
        for opt in options:
            val = await opt.get_attribute("value")
            if val and CHARACTER.lower() in val.lower():
                await char_select.select_option(value=val)
                await asyncio.sleep(2)
                break
        else:
            # 选择第一个可用角色
            if options:
                await char_select.select_option(index=0)
                await asyncio.sleep(2)

    # 点击下载按钮
    dl_btn = await page.query_selector(".download-btn") or await page.query_selector("button[title='Download']")
    if not dl_btn:
        # 尝试其他选择器
        dl_btn = await page.query_selector("a[href='#download']")
    if not dl_btn:
        print(f"  ⏭️  无下载按钮，跳过")
        return False

    # 设置下载监听
    output_path = os.path.join(OUTPUT_DIR, f"{anim_name}.fbx")

    # 用 page 的 download 事件处理
    async with page.expect_download(timeout=60000) as download_info:
        await dl_btn.click()

    download = download_info.value
    suggested = download.suggested_filename()

    if not suggested.endswith(".fbx"):
        await download.cancel()
        print(f"  ⏭️  非 FBX 文件（{suggested}），跳过")
        return False

    await download.save_as(output_path)
    print(f"  ✅ 已保存: {output_path}")
    return True


async def main():
    # 从命令行参数读取动画列表（可选）
    animations = ANIMATIONS
    if len(sys.argv) > 1:
        animations = [a.strip() for a in sys.argv[1:] if a.strip()]

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 统计已下载
    existing = set(f.replace(".fbx", "") for f in os.listdir(OUTPUT_DIR) if f.endswith(".fbx"))
    to_download = [a for a in animations if a not in existing]

    print(f"共 {len(animations)} 个动画，已存在 {len(existing)}，需下载 {len(to_download)}")
    print(f"输出目录: {OUTPUT_DIR}")
    print()

    if not to_download:
        print("所有动画已存在，无需下载")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 需要有头模式登录
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            accept_downloads=True,
        )

        # 加载 cookies
        if os.path.exists(COOKIES_FILE):
            with open(COOKIES_FILE) as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
            print(f"已加载 {len(cookies)} 个 cookies")

        page = await context.new_page()

        # 确保登录
        if not await ensure_login(page, context):
            await browser.close()
            return

        # 下载每个动画
        success = 0
        failed = 0

        for i, anim in enumerate(to_download, 1):
            print(f"\n[{i}/{len(to_download)}] {anim}")
            try:
                if await download_animation(page, anim):
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"  ❌ 错误: {e}")
                failed += 1

            # 防限流
            await asyncio.sleep(2 + __import__("random").random() * 3)

        print(f"\n{'='*40}")
        print(f"下载完成: ✅ {success} 成功, ❌ {failed} 失败")

        # 刷新 cookies
        cookies = await context.cookies()
        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies, f, indent=2)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
