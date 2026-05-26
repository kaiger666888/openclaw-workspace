#!/usr/bin/env python3
"""generate-dashboard.py - 从 SQLite 生成精美 HTML 看板"""
import json, sqlite3, html as html_mod, os, sys

DB = os.path.expanduser("~/.openclaw/workspace/data/dashboard/dashboard.db")
OUT = os.path.expanduser("~/.openclaw/workspace/data/dashboard/index.html")

def query_json(sql):
    r = sqlite3.connect(DB).execute(sql).fetchone()
    return json.loads(r[0]) if r and r[0] else []

def fmt(n):
    n = int(n) if isinstance(n, (int,float)) else 0
    return f"{n/10000:.1f}万" if n >= 10000 else f"{n:,}"

def pctc(v):
    v = float(v) if v else 0
    return "good" if v >= 50 else "warn" if v >= 20 else "bad"

def star_h(v, mx=5):
    r = round(float(v)) if v else 0
    return "★" * r + '<span class="stars-dim">' + "★" * (mx-r) + "</span>"

def sj(s):
    try: return json.loads(s) if isinstance(s, str) else (s or {})
    except: return {}

def esc(t): return html_mod.escape(str(t))

snaps = query_json("""SELECT json_group_array(json_object(
    'platform',platform,'date',date,'followers',followers,
    'total_views',total_views,'total_likes',total_likes,
    'total_comments',total_comments,'total_favorites',total_favorites,
    'total_shares',total_shares,'total_coins',total_coins,
    'total_posts',total_posts,'new_followers',new_followers,
    'new_views',new_views,'interaction_rate',interaction_rate,'raw_json',raw_json
)) FROM daily_snapshots ORDER BY date DESC, platform""")

items = query_json("""SELECT json_group_array(json_object(
    'platform',platform,'item_id',item_id,'title',title,'url',url,
    'publish_date',publish_date,'views',views,'likes',likes,
    'comments',comments,'favorites',favorites,'shares',shares,
    'coins',coins,'collected_at',collected_at,'raw_json',raw_json
)) FROM content_items ORDER BY publish_date DESC""")

pN = {"xiaohongshu":"📕 小红书","douyin":"🎵 抖音","bilibili":"📺 B站"}
pT = {"xiaohongshu":"小红书","douyin":"抖音","bilibili":"B站"}
tC = {"xiaohongshu":"tag-xhs","douyin":"tag-dy","bilibili":"tag-bili"}

tv = sum(s.get("total_views",0) for s in snaps)
tl = sum(s.get("total_likes",0) for s in snaps)
tc = sum(s.get("total_comments",0) for s in snaps)
ts_ = sum(s.get("total_shares",0) for s in snaps)

def analysis_html(item, d):
    p = item["platform"]
    rows = []
    if p == "xiaohongshu":
        ccr = float(str(d.get("cover_click_rate","0")).replace("%","") or "0")
        br = float(str(d.get("bounce_2s_rate","0")).replace("%","") or "0")
        cr = float(str(d.get("completion_rate","0")).replace("%","") or "0")
        exp = d.get("exposure",0) or 0
        nf = d.get("new_followers")
        nf_s = f"+{nf}" if nf is not None else "—"
        ctr_vs = d.get("cover_click_rate_vs","")
        cr_vs = d.get("completion_rate_vs","")
        ccr_label = "✅ 优秀" if ccr>15 else "⚠️ 需优化" if ccr>8 else "❌ 待改进"
        br_label = "✅ 开头好" if br<30 else "⚠️ 部分离开" if br<50 else "❌ 需优化"
        ctr_desc = f"{ctr_vs} {ccr_label}" if ctr_vs else ccr_label
        br_desc = br_label
        cr_desc = cr_vs if cr_vs else ""
        exp_desc = f"观看/曝光={round(item['views']/exp*100,1)}%" if exp and item['views'] else ""
        rows = [
            ("👁️","封面点击率", pctc(ccr), d.get("cover_click_rate","—"), ctr_desc),
            ("⏱️","2秒退出率", "good" if br<30 else "warn" if br<50 else "bad", d.get("bounce_2s_rate","—"), br_desc),
            ("🎬","完播率", pctc(cr), d.get("completion_rate","—"), cr_desc),
            ("⏳","均观看时长", "", d.get("avg_watch_duration","—"), f"粉丝占比 {d.get('view_fans_ratio','—')}"),
            ("👥","涨粉", "", nf_s, f"曝光粉丝占比 {d.get('fans_ratio','—')}"),
            ("📡","曝光数", "", str(exp) if exp else "—", exp_desc),
        ]
    elif p == "douyin":
        b2s = float(str(d.get("bounce_2s_rate","0")).replace("%","") or "0")
        c5s = float(str(d.get("completion_5s_rate","0")).replace("%","") or "0")
        ctr_v = float(str(d.get("click_rate","0")).replace("%","") or "0")
        rows = [
            ("👁️","点击率", "good" if ctr_v>5 else "bad", d.get("click_rate","—"), "封面吸引力"),
            ("⏱️","2秒跳出率", "good" if b2s<35 else "warn" if b2s<50 else "bad", d.get("bounce_2s_rate","—"), "✅ 开头不错" if b2s<35 else "⚠️ 需改进"),
            ("🎬","5秒完播率", pctc(c5s), d.get("completion_5s_rate","—"), "内容留存"),
            ("⏳","均播放时长", "", d.get("avg_play_duration","—"), "97秒总时长"),
            ("📊","播放量", "", f"{item['views']} · {d.get('play_vs_avg','')}", f"抖音精选 {d.get('douyin_selected_views',0)}"),
        ]
    elif p == "bilibili":
        b3s = float(str(d.get("bounce_3s_rate","0")).replace("%","") or "0")
        ir_v = float(str(d.get("interaction_rate","0")).replace("%","") or "0")
        ap_pct = d.get("avg_play_pct",0) or 0
        rows = [
            ("👁️","封标点击率", "", star_h(d.get("cover_click_rate_stars",0)) + " " + str(d.get("cover_click_rate_stars","—")), "超55%同类"),
            ("⏱️","3秒跳出率", "warn" if b3s<50 else "bad", d.get("bounce_3s_rate","—"), star_h(d.get("bounce_3s_stars",0))),
            ("💬","互动率", pctc(ir_v), d.get("interaction_rate","—"), star_h(d.get("interaction_stars",0))),
            ("👥","播转粉率", "bad", d.get("play_to_fan_rate","—"), star_h(d.get("play_to_fan_stars",0))),
            ("⏳","平均播放进度", "warn" if ap_pct>30 else "bad", f"{d.get('avg_play_progress','—')} ({ap_pct}%)", star_h(d.get("avg_play_stars",0))),
            ("🚦","游客占比", "warn", d.get("tourist_ratio","—"), "新账号正常，需提升粉丝留存"),
            ("📡","流量状态", "good", d.get("traffic_status","—"), "无违规限流"),
        ]
    
    return "".join(
        f'<div class="analysis-item"><div class="ai-label"><span class="ai-icon">{icon}</span> {label}</div>'
        f'<div class="ai-value {cls}">{esc(val)}</div><div class="ai-desc">{esc(desc)}</div></div>\n'
        for icon, label, cls, val, desc in rows
    )

# Build content cards
content_html = ""
for item in items:
    d = sj(item.get("raw_json","{}"))
    ir = ((item["likes"]+item["comments"]+item["favorites"]+item["shares"])/item["views"]*100) if item["views"] else 0
    c = tC[item["platform"]]
    url_h = f'<a href="{item.get("url","")}" target="_blank" style="color:var(--cyan);text-decoration:none">🔗 链接</a>' if item.get("url") else ""
    content_html += f'''<div class="content-card">
<div class="content-card-header"><div style="display:flex;align-items:flex-start">
<span class="platform-tag {c}">{pT[item["platform"]]}</span>
<div class="title-area"><h3>{esc(item["title"])}</h3>
<div class="meta-row"><span>📅 {item["publish_date"]}</span> {url_h}</div></div></div></div>
<div class="content-card-body">
<div class="stats-grid">
<div class="stat-cell"><div class="stat-label">👁️ 播放</div><div class="stat-val">{item["views"]}</div></div>
<div class="stat-cell"><div class="stat-label">👍 点赞</div><div class="stat-val">{item["likes"]}</div></div>
<div class="stat-cell"><div class="stat-label">💬 评论</div><div class="stat-val">{item["comments"]}</div></div>
<div class="stat-cell"><div class="stat-label">⭐ 收藏</div><div class="stat-val">{item["favorites"]}</div></div>
<div class="stat-cell"><div class="stat-label">🔗 分享</div><div class="stat-val">{item["shares"]}</div></div>
<div class="stat-cell"><div class="stat-label">📊 互动率</div><div class="stat-val">{ir:.1f}%</div></div>
</div>
<div class="analysis-grid">{analysis_html(item, d)}</div>
</div></div>\n'''

# Platform cards
pclass = {"xiaohongshu":"xhs","douyin":"dy","bilibili":"bili"}
pcards = ""
for s in snaps:
    c = pclass[s["platform"]]
    pcards += f'<div class="card platform-card {c}"><div class="pn">{pN[s["platform"]]}</div><div class="value">{fmt(s.get("total_views",0))}</div><div class="change">观看 · 互动率 {s.get("interaction_rate",0) or 0:.1f}%</div></div>\n'

# Advices
advices = []
for item in items:
    d = sj(item.get("raw_json","{}"))
    p = item["platform"]
    if p == "xiaohongshu":
        br = float(str(d.get("bounce_2s_rate","0")).replace("%","") or "0")
        cr = float(str(d.get("completion_rate","0")).replace("%","") or "0")
        ccr = float(str(d.get("cover_click_rate","0")).replace("%","") or "0")
        if br > 50:
            advices.append(("high","🔴",f"[小红书] {item['title']} — 2秒退出率过高({d.get('bounce_2s_rate')})",
                "60%用户5秒内离开。建议：①3秒加入视觉冲击或悬念 ②直接展示最精彩画面 ③避免冗长片头"))
        if cr < 10 and d.get("diagnosis_available"):
            advices.append(("mid","🟡",f"[小红书] {item['title']} — 完播率偏低({d.get('completion_rate')})",
                "建议缩短视频时长，或在前半段设置钩子保持用户注意力"))
        if ccr > 30:
            advices.append(("low","🟢",f"[小红书] {item['title']} — 封面表现优秀({d.get('cover_click_rate')})",
                "封面点击率显著高于同类，可复制此封面风格。但完播率偏低，内容需优化。"))
    elif p == "douyin":
        b2s = float(str(d.get("bounce_2s_rate","0")).replace("%","") or "0")
        if b2s > 40:
            advices.append(("mid","🟡",f"[抖音] {item['title']} — 2秒跳出率偏高({d.get('bounce_2s_rate')})",
                "抖音算法强依赖前3秒留存，建议优化开头前3秒画面，直接进入高潮。"))
        advices.append(("mid","🟡",f"[抖音] {item['title']} — 点击率为0%",
            "可能视频未获得推荐流量。建议发布时选择合适的话题标签，尝试DOU+投放获取初始流量。"))
    elif p == "bilibili":
        advices.append(("high","🔴",f"[B站] {item['title']} — 3秒跳出率57.1%",
            "超过一半用户3秒内离开。B站用户偏好有信息量的内容，建议：①3秒展示核心观点 ②使用字幕和弹幕引导 ③控制节奏不要太慢"))
        advices.append(("high","🔴",f"[B站] {item['title']} — 播转粉率为0%",
            "有播放无转化。建议：①结尾加引导关注话术 ②创建系列内容培养回访习惯 ③在简介/评论区引导"))
        advices.append(("mid","🟡",f"[B站] {item['title']} — 粉丝观看率0%",
            "100%流量来自游客，建议固定更新频率，通过系列内容积累核心粉丝。"))

advices.append(("mid","💡","跨平台策略建议",
    "同一内容《梦游天姥吟留别》三平台表现差异大：小红书封面点击率最高但完播率低，抖音跳出率最高，B站播放最低。建议各平台定制封面和开头。"))
advices.append(("low","🎯","内容方向建议",
    "《老婆的生气周期分析报告》互动数据相对好(点赞粉丝占比50%)，生活化/共鸣类内容有潜力，可继续探索此类选题。"))
advices.sort(key=lambda x: {"high":0,"mid":1,"low":2}.get(x[0],1))

advice_html = "".join(
    f'<div class="advice-item"><div class="advice-icon">{a[1]}</div>'
    f'<div class="advice-text"><div class="at">{esc(a[2])}</div><div class="ad">{esc(a[3])}</div></div>'
    f'<span class="advice-priority priority-{a[0]}">{"优先" if a[0]=="high" else "建议" if a[0]=="mid" else "优化"}</span></div>\n'
    for a in advices
)

# Chart data arrays
views_arr = json.dumps([s.get("total_views",0) for s in snaps])
likes_arr = json.dumps([s.get("total_likes",0) for s in snaps])
comments_arr = json.dumps([s.get("total_comments",0) for s in snaps])
favs_arr = json.dumps([s.get("total_favorites",0) for s in snaps])
shares_arr = json.dumps([s.get("total_shares",0) for s in snaps])

import datetime
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

full = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>📊 创作者数据看板 - 梦境词话</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
:root{{--bg:#0a0a0f;--bg2:#12121a;--card:#1a1a2e;--card-h:#1f1f35;--bdr:#2a2a4a;--t1:#e8e8f0;--t2:#8888a8;--tm:#55556a;--red:#ff4757;--cyan:#00d2ff;--pink:#ff6b9d;--blue:#00a1d6;--green:#2ed573;--yellow:#ffd43b;--orange:#ff9f43;--purple:#a29bfe;--radius:16px}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',-apple-system,sans-serif;background:var(--bg);color:var(--t1);min-height:100vh;line-height:1.6}}
.header{{background:linear-gradient(135deg,var(--bg2),#16213e);padding:20px 32px;border-bottom:1px solid var(--bdr);display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:100;backdrop-filter:blur(20px)}}
.header h1{{font-size:22px;font-weight:700;color:#fff;display:flex;align-items:center;gap:10px}}
.header .meta{{font-size:13px;color:var(--tm);margin-top:2px}}
.header-right{{display:flex;gap:12px;align-items:center}}
.btn{{padding:8px 18px;border-radius:10px;border:1px solid var(--bdr);background:var(--card);color:var(--t1);font-size:13px;cursor:pointer;transition:all .2s;font-family:inherit;display:flex;align-items:center;gap:6px}}
.btn:hover{{background:var(--card-h);border-color:var(--cyan)}}
.refresh-dot{{width:8px;height:8px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
.container{{max-width:1440px;margin:0 auto;padding:24px}}
.section{{margin-bottom:28px}}
.section-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}}
.section-header h2{{font-size:18px;font-weight:600;display:flex;align-items:center;gap:8px}}
.section-header .badge{{font-size:11px;padding:3px 10px;border-radius:20px;background:var(--card);border:1px solid var(--bdr);color:var(--t2)}}
.cards-row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px}}
.card{{background:var(--card);border-radius:var(--radius);padding:20px;border:1px solid var(--bdr);transition:all .2s}}
.card:hover{{border-color:#3a3a5a;transform:translateY(-1px);box-shadow:0 4px 24px rgba(0,0,0,.3)}}
.card .label{{font-size:12px;color:var(--tm);text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px}}
.card .value{{font-size:28px;font-weight:700;color:#fff;line-height:1.2}}
.platform-card{{position:relative;overflow:hidden}}
.platform-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px}}
.platform-card.xhs::before{{background:var(--red)}}.platform-card.dy::before{{background:var(--cyan)}}.platform-card.bili::before{{background:var(--blue)}}
.platform-card .pn{{font-size:14px;font-weight:600;margin-bottom:4px}}
.platform-card.xhs .pn{{color:var(--red)}}.platform-card.dy .pn{{color:var(--cyan)}}.platform-card.bili .pn{{color:var(--blue)}}
.charts-grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.chart-box{{background:var(--card);border-radius:var(--radius);padding:20px;border:1px solid var(--bdr)}}
.chart-box h3{{font-size:14px;font-weight:500;color:var(--t2);margin-bottom:12px}}
.content-card{{background:var(--card);border-radius:var(--radius);border:1px solid var(--bdr);margin-bottom:14px;overflow:hidden;transition:all .2s}}
.content-card:hover{{border-color:#3a3a5a}}
.content-card-header{{padding:18px 24px;border-bottom:1px solid var(--bdr)}}
.content-card-header .title-area h3{{font-size:15px;font-weight:600;color:#fff;margin-bottom:4px}}
.content-card-header .meta-row{{display:flex;gap:16px;font-size:12px;color:var(--tm)}}
.platform-tag{{font-size:11px;font-weight:600;padding:3px 10px;border-radius:6px;margin-right:12px;flex-shrink:0}}
.tag-xhs{{background:rgba(255,71,87,.15);color:var(--red)}}.tag-dy{{background:rgba(0,210,255,.15);color:var(--cyan)}}.tag-bili{{background:rgba(0,161,214,.15);color:var(--blue)}}
.content-card-body{{padding:18px 24px}}
.stats-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(100px,1fr));gap:12px;margin-bottom:16px}}
.stat-cell .stat-label{{font-size:11px;color:var(--tm)}}.stat-cell .stat-val{{font-size:16px;font-weight:600;color:var(--t1)}}
.analysis-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-top:14px;padding-top:14px;border-top:1px solid var(--bdr)}}
.analysis-item{{background:rgba(255,255,255,.02);border-radius:10px;padding:12px 16px;border:1px solid rgba(255,255,255,.04)}}
.analysis-item .ai-label{{font-size:11px;color:var(--tm);margin-bottom:4px;display:flex;align-items:center;gap:4px}}
.analysis-item .ai-value{{font-size:14px;font-weight:600;color:var(--t1)}}
.analysis-item .ai-desc{{font-size:11px;color:var(--t2);margin-top:2px}}
.good{{color:var(--green)}}.warn{{color:var(--yellow)}}.bad{{color:var(--red)}}.stars-dim{{color:var(--tm)}}
.advice-card{{background:linear-gradient(135deg,rgba(0,210,255,.05),rgba(162,155,254,.05));border:1px solid rgba(0,210,255,.15);border-radius:var(--radius);padding:24px}}
.advice-card h3{{font-size:16px;font-weight:600;margin-bottom:16px;display:flex;align-items:center;gap:8px}}
.advice-item{{display:flex;gap:12px;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.04)}}
.advice-item:last-child{{border-bottom:none}}
.advice-icon{{font-size:18px;flex-shrink:0;margin-top:2px}}
.advice-text{{flex:1}}.advice-text .at{{font-size:13px;font-weight:600;color:var(--t1);margin-bottom:2px}}.advice-text .ad{{font-size:12px;color:var(--t2);line-height:1.5}}
.advice-priority{{font-size:10px;padding:2px 8px;border-radius:4px;flex-shrink:0;margin-top:2px}}
.priority-high{{background:rgba(255,71,87,.15);color:var(--red)}}.priority-mid{{background:rgba(255,159,67,.15);color:var(--orange)}}.priority-low{{background:rgba(46,213,115,.15);color:var(--green)}}
@media(max-width:768px){{.container{{padding:16px}}.charts-grid{{grid-template-columns:1fr}}.cards-row{{grid-template-columns:repeat(2,1fr)}}}}
::-webkit-scrollbar{{width:6px}}::-webkit-scrollbar-track{{background:transparent}}::-webkit-scrollbar-thumb{{background:var(--bdr);border-radius:3px}}
</style></head><body>
<div class="header"><div><h1>📊 创作者数据看板</h1><div class="meta">梦境词话 · 更新: {NOW}</div></div><div class="header-right"><div class="refresh-dot"></div><button class="btn" onclick="location.reload()">🔄 刷新</button></div></div>
<div class="container">

<div class="section"><div class="section-header"><h2>🌐 全平台总览</h2></div>
<div class="cards-row">
<div class="card"><div class="label">全平台播放</div><div class="value">{fmt(tv)}</div></div>
<div class="card"><div class="label">总互动</div><div class="value">{fmt(tl+tc+ts_)}</div><div class="change neutral">👍{tl} · 💬{tc} · 🔗{ts_}</div></div>
<div class="card"><div class="label">作品数</div><div class="value">{len(items)}</div></div>
</div>
<div class="cards-row" style="margin-top:14px">{pcards}</div>
</div>

<div class="section"><div class="section-header"><h2>📈 平台数据对比</h2></div>
<div class="charts-grid">
<div class="chart-box"><h3>播放量对比</h3><canvas id="c1"></canvas></div>
<div class="chart-box"><h3>互动数据对比</h3><canvas id="c2"></canvas></div>
</div></div>

<div class="section"><div class="section-header"><h2>🔍 稿件详细分析</h2><span class="badge">含 AI 诊断</span></div>
{content_html}</div>

<div class="section"><div class="section-header"><h2>💡 智能分析与建议</h2></div>
<div class="advice-card"><h3>🤖 AI 分析引擎</h3>{advice_html}</div></div>

</div>
<script>
const opts={{responsive:true,plugins:{{legend:{{labels:{{color:"#888",font:{{size:12}}}}}}}},scales:{{x:{{ticks:{{color:"#555"}},grid:{{color:"#1a1a2e"}}}},y:{{ticks:{{color:"#555"}},grid:{{color:"#1a1a2e"}}}}}}}};
new Chart(document.getElementById("c1"),{{type:"bar",data:{{labels:["小红书","抖音","B站"],datasets:[{{label:"播放",data:{views_arr},backgroundColor:["#ff4757","#00d2ff","#00a1d6"],borderRadius:6}}]}},options:{{...opts,plugins:{{legend:{{display:false}}}}}}}});
new Chart(document.getElementById("c2"),{{type:"bar",data:{{labels:["小红书","抖音","B站"],datasets:[{{label:"点赞",data:{likes_arr},backgroundColor:"#ff6b9d",borderRadius:4}},{{label:"评论",data:{comments_arr},backgroundColor:"#a29bfe",borderRadius:4}},{{label:"收藏",data:{favs_arr},backgroundColor:"#ffd43b",borderRadius:4}},{{label:"分享",data:{shares_arr},backgroundColor:"#2ed573",borderRadius:4}}]}},options:opts}});
</scr""+"ipt></body></html>'''

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(full)
print(f"✅ 看板已生成: {OUT}")
print(f"📊 {len(items)} 个作品 + {len(advices)} 条 AI 建议")
