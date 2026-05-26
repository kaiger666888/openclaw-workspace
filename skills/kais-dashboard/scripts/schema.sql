-- kais-dashboard SQLite Schema

CREATE TABLE IF NOT EXISTS accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  platform TEXT NOT NULL UNIQUE,     -- xiaohongshu / douyin / bilibili
  account_name TEXT,
  account_id TEXT,
  profile_url TEXT,
  created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS daily_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  platform TEXT NOT NULL,            -- xiaohongshu / douyin / bilibili
  date TEXT NOT NULL,                -- YYYY-MM-DD
  followers INTEGER DEFAULT 0,
  total_views INTEGER DEFAULT 0,
  total_likes INTEGER DEFAULT 0,
  total_comments INTEGER DEFAULT 0,
  total_favorites INTEGER DEFAULT 0,
  total_shares INTEGER DEFAULT 0,
  total_coins INTEGER DEFAULT 0,     -- B站投币
  total_posts INTEGER DEFAULT 0,
  new_followers INTEGER DEFAULT 0,
  new_views INTEGER DEFAULT 0,
  interaction_rate REAL DEFAULT 0,
  raw_json TEXT,
  collected_at TEXT DEFAULT (datetime('now', 'localtime')),
  UNIQUE(platform, date)
);

-- 素材级数据（单条笔记/视频）
CREATE TABLE IF NOT EXISTS content_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  platform TEXT NOT NULL,
  item_id TEXT,
  title TEXT,
  url TEXT,
  publish_date TEXT,
  views INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  favorites INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  coins INTEGER DEFAULT 0,
  collected_at TEXT DEFAULT (datetime('now', 'localtime')),
  UNIQUE(platform, item_id)
);

-- 采集日志
CREATE TABLE IF NOT EXISTS collect_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  platform TEXT NOT NULL,
  action TEXT NOT NULL,              -- collect / error / skip
  message TEXT,
  created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_snapshots_platform_date ON daily_snapshots(platform, date);
CREATE INDEX IF NOT EXISTS idx_content_platform ON content_items(platform);
