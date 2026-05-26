#!/usr/bin/env python3
"""
Mixamo 动画批量下载脚本（Without Skin 版本）

用法:
  python3 download_mixamo_animations.py --character Y_Bot --animations walk,run,idle
  python3 download_mixamo_animations.py --character Y_Bot --animations-file animation_list.txt

选项:
  --character CHARACTER   Mixamo 角色名（默认 Y_Bot）
  --animations LIST      逗号分隔的动画名列表
  --animations-file FILE  从文件读取动画名列表（每行一个）
  --output-dir DIR      输出目录（默认 D:/BlenderAgent/animations/motions_anim）
  --headless             无头模式（不显示浏览器）
  --slow                 慢速模式（防止被检测）
  --debug                显示浏览器

注意：
  - 需要 Mixamo cookies（首次运行会打开浏览器让你登录）
  - cookies 保存到 ~/.mixamo_cookies.txt
  - Mixamo 下载需要选 Without Skin + In Place + FBX for Blender (FBX 2019)
"""

import argparse
import json
import os
import subprocess
import sys
import time
import hashlib

DEFAULT_OUTPUT_DIR = r"D:\BlenderAgent\animations\motions_anim"
DEFAULT_CHARACTER = "Y_Bot"
COOKIES_FILE = os.path.expanduser("~/.mixamo_cookies.txt")

# 需要下载的动画列表
DEFAULT_ANIMATIONS = [
    # 行走
    "walking_forward_inplace",
    "walking_backward_inplace",
    "walking_left_inplace",
    "walking_right_inplace",
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


def load_animations(args):
    """加载动画列表"""
    if args.animations:
        return [a.strip() for a in args.animations.split(",") if a.strip()]
    if args.animations_file and os.path.exists(args.animations_file):
        with open(args.animations_file) as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return DEFAULT_ANIMATIONS


def check_node_deps():
    """检查 Node.js 依赖"""
    try:
        subprocess.run(["node", "-e", "require('playwright')"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_playwright():
    """安装 Playwright"""
    print("安装 Playwright...")
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
    subprocess.run(["npx", "playwright", "install", "chromium"], check=True)


def download_with_node(animations, character, output_dir, headless, slow, debug):
    """使用 Node.js + Playwright 下载 Mixamo 动画"""
    script_content = '''
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ANIMATIONS = ANIM_LIST;
const CHARACTER = CHAR;
const OUTPUT_DIR = OUT_DIR;
const HEADLESS = HEAD;
const SLOW = SLOW_FLAG;
const DEBUG = DBG;
const COOKIES_FILE = COOKIE_PATH;

(async () => {
    const browser = await chromium.launch({
        headless: HEADLESS,
        slowMo: SLOW ? 500 : 50,
    });
    const context = await browser.newContext({
        viewport: { width: 1280, height: 800 },
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    });

    // 加载 cookies
    if (fs.existsSync(COOKIES_FILE)) {
        const cookies = JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf-8'));
        await context.addCookies(cookies);
        console.log(`Loaded ${cookies.length} cookies`);
    }

    const page = await context.newPage();

    // 登录检查
    await page.goto('https://www.mixamo.com/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    // 检查是否需要登录
    const loginCheck = await page.$('button[aria-label="Sign In"]') || 
                       await page.$('a[href*="sign"]');
    if (loginCheck) {
        console.log('需要登录！请在浏览器中完成登录...');
        if (!HEADLESS) {
            // 等待用户手动登录
            await page.waitForNavigation({ timeout: 300000 }).catch(() => {});
            await page.waitForTimeout(5000);
        } else {
            console.log('无头模式下无法登录，请先在有头模式下运行一次以保存 cookies');
            await browser.close();
            process.exit(1);
        }
        // 保存 cookies
        const cookies = await context.cookies();
        fs.writeFileSync(COOKIES_FILE, JSON.stringify(cookies, null, 2));
        console.log('Cookies 已保存');
    }

    const results = { success: [], failed: [], skipped: [] };

    for (let i = 0; i < ANIMATIONS.length; i++) {
        const animName = ANIMATIONS[i];
        const paddedNum = String(i + 1).padStart(3, '0');
        console.log(`\\n[${paddedNum}/${ANIMATIONS.length}] 下载: ${animName}`);

        try {
            // 1. 搜索动画
            await page.goto(`https://www.mixamo.com/search/?query=${encodeURIComponent(animName)}`, { waitUntil: 'networkidle' });
            await page.waitForTimeout(2000);

            // 2. 点击第一个搜索结果
            const firstResult = await page.$('.search-result-card');
            if (!firstResult) {
                console.log(`  跳过: 未找到搜索结果`);
                results.skipped.push(animName);
                continue;
            }
            await firstResult.click();
            await page.waitForTimeout(3000);

            // 3. 选择角色（如果角色选择器存在）
            const characterSelect = await page.$('#character-preview-character-select');
            if (characterSelect) {
                await characterSelect.selectOption({ value: CHARACTER });
                await page.waitForTimeout(2000);
            }

            // 4. 等待动画加载
            await page.waitForTimeout(3000);

            // 5. 设置下载选项：Without Skin, In Place, FBX for Blender
            // 找到格式下拉菜单
            const formatSelect = await page.$('#download-type-select');
            if (formatSelect) {
                // Mixamo 的下载格式选项
                // 通常是: "FBX for Blender (.fbx)" 
                // 皮肤选项在另一个 select
            }

            // 6. 下载按钮
            const downloadBtn = await page.$('.download-btn') || await page.$('button[title="Download"]');
            if (!downloadBtn) {
                console.log(`  跳过: 未找到下载按钮`);
                results.skipped.push(animName);
                continue;
            }

            // 7. 设置下载监听（下载 FBX 文件）
            const downloadPromise = new Promise((resolve, reject) => {
                page.on('download', async (download) => {
                    const suggestedFilename = download.suggestedFilename();
                    if (!suggestedFilename.endsWith('.fbx')) {
                        await download.cancel();
                        reject(new Error('非 FBX 文件，取消'));
                        return;
                    }
                    const fileName = `${animName}.fbx`;
                    const savePath = path.join(OUTPUT_DIR, fileName);
                    await download.saveAs(savePath);
                    console.log(`  保存到: ${savePath}`);
                    resolve(savePath);
                });
            });

            await downloadBtn.click();

            // 等待下载完成（最多 60 秒）
            const timeout = setTimeout(() => reject(new Error('下载超时')), 60000);
            try {
                await downloadPromise;
                clearTimeout(timeout);
                results.success.push(animName);
                console.log(`  ✅ 成功`);
            } catch (e) {
                clearTimeout(timeout);
                console.log(`  ❌ 失败: ${e.message}`);
                results.failed.push(animName);
            }

            // 保存 cookies
            const cookies = await context.cookies();
            fs.writeFileSync(COOKIES_FILE, JSON.stringify(cookies, null, 2));

        } catch (e) {
            console.log(`  ❌ 错误: ${e.message}`);
            results.failed.push(animName);
        }

        // 避免被限流
        const delay = SLOW ? 5000 : (3000 + Math.random() * 2000);
        await page.waitForTimeout(delay);
    }

    console.log(`\\n=== 下载完成 ===`);
    console.log(`成功: ${results.success.length}`);
    console.log(`失败: ${results.failed.length}`);
    console.log(`跳过: ${results.skipped.length}`);
    if (results.failed.length > 0) {
        console.log(`失败列表: ${results.failed.join(', ')}`);
    }

    await browser.close();
    process.exit(results.failed.length > 0 ? 1 : 0);
})();
'''.replace(
        'ANIM_LIST', json.dumps(animations),
    ).replace(
        'CHAR', json.dumps(character),
    ).replace(
        'OUT_DIR', output_dir.replace("\\", "\\\\")),
    ).replace(
        'COOKIE_PATH', COOKIES_FILE.replace("\\", "\\\\")),
    ).replace(
        'HEAD', str(headless).lower(),
    ).replace(
        'SLOW_FLAG', str(slow).lower(),
    ).replace(
        'DBG', str(debug).lower(),
    )

    script_path = "/tmp/mixamo_download.js"
    with open(script_path, "w") as f:
        f.write(script_content)

    env = os.environ.copy()
    result = subprocess.run(
        ["node", script_path],
        capture_output=True, text=True, timeout=7200,
        env=env,
    )
    print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    if result.stderr and "error" not in result.stderr.lower()[:100]:
        print("STDERR:", result.stderr[-300:])

    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="下载 Mixamo 动画（Without Skin 版本）")
    parser.add_argument("--character", default=DEFAULT_CHARACTER, help="Mixamo 角色名")
    parser.add_argument("--animations", help="逗号分隔的动画名列表")
    parser.add_argument("--animations-file", help="从文件读取动画名列表")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="输出目录")
    parser.add_argument("--headless", action="store_true", help="无头模式")
    parser.add_argument("--slow", action="store_true", help="慢速模式")
    parser.add_argument("--debug", action="store_true", help="显示浏览器")
    args = parser.parse_args()

    animations = load_animations(args)

    print(f"准备下载 {len(animations)} 个动画到 {args.output_dir}")
    print(f"角色: {args.character}")
    print(f"无头: {args.headless}, 慢速: {args.slow}")
    print()

    os.makedirs(args.output_dir, exist_ok=True)

    if not check_node_deps():
        install_playwright()

    rc = download_with_node(
        animations=animations,
        character=args.character,
        output_dir=args.output_dir,
        headless=args.headless,
        slow=args.slow,
        debug=args.debug,
    )
    return rc


if __name__ == "__main__":
    sys.exit(main())
