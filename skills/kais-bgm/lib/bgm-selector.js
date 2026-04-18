/**
 * kais-bgm-selector — BGM 选择模块
 * ES Module
 *
 * 功能：
 * - 内置 BGM 风格库（紧张/温馨/悲伤/欢快/史诗/悬疑...）
 * - 根据场景情感自动推荐 BGM
 * - 支持：从本地音乐库选择 或 生成提示词（给音乐生成 AI）
 */

// ─── BGM 风格库 ──────────────────────────────────────────

const BGM_STYLES = {
  tense: {
    id: 'tense',
    name: '紧张',
    nameEn: 'tense',
    keywords: ['紧张', '紧迫', '危机', '追赶', '倒计时', '对峙'],
    tempo: 'fast',
    instruments: ['弦乐急奏', '打击乐', '电子脉冲'],
    mood: '紧迫感，节奏加速',
    prompt: 'tense cinematic soundtrack, fast strings, percussion hits, building tension, suspenseful',
    compatibleGenres: ['惊悚', '动作', '悬疑'],
  },
  warm: {
    id: 'warm',
    name: '温馨',
    nameEn: 'warm',
    keywords: ['温馨', '温暖', '家', '亲情', '友情', '日常', '陪伴'],
    tempo: 'slow',
    instruments: ['钢琴', '木吉他', '弦乐柔和'],
    mood: '温暖柔和，轻柔节奏',
    prompt: 'warm gentle piano, acoustic guitar, soft strings, heartwarming, emotional',
    compatibleGenres: ['温情', '日常', '治愈'],
  },
  sad: {
    id: 'sad',
    name: '悲伤',
    nameEn: 'sad',
    keywords: ['悲伤', '离别', '失去', '回忆', '遗憾', '孤独', '哭泣'],
    tempo: 'slow',
    instruments: ['钢琴独奏', '大提琴', '风铃'],
    mood: '低沉忧伤，缓慢流淌',
    prompt: 'sad melancholic piano solo, cello, emotional, sorrowful, heartbreak',
    compatibleGenres: ['悲剧', '文艺', '剧情'],
  },
  happy: {
    id: 'happy',
    name: '欢快',
    nameEn: 'happy',
    keywords: ['欢快', '开心', '庆祝', '成功', '喜悦', '搞笑', '轻松'],
    tempo: 'medium-fast',
    instruments: ['尤克里里', '口哨', '轻快鼓点'],
    mood: '轻松愉悦，节奏明快',
    prompt: 'upbeat happy ukulele, whistling, cheerful drums, feel-good, bright',
    compatibleGenres: ['喜剧', '青春', '日常'],
  },
  epic: {
    id: 'epic',
    name: '史诗',
    nameEn: 'epic',
    keywords: ['史诗', '宏大', '壮丽', '战斗', '出征', '英雄', '震撼'],
    tempo: 'medium',
    instruments: ['交响乐团', '铜管', '合唱', '战鼓'],
    mood: '磅礴大气，层层递进',
    prompt: 'epic orchestral, brass, choir, war drums, heroic, grandiose',
    compatibleGenres: ['奇幻', '战争', '史诗'],
  },
  mystery: {
    id: 'mystery',
    name: '悬疑',
    nameEn: 'mystery',
    keywords: ['悬疑', '神秘', '诡异', '暗流', '阴谋', '秘密', '推理'],
    tempo: 'slow-medium',
    instruments: ['低音提琴', '电子合成器', '钢琴高音'],
    mood: '神秘莫测，暗流涌动',
    prompt: 'mysterious dark ambient, low strings, synth pads, eerie piano, detective',
    compatibleGenres: ['悬疑', '推理', '恐怖'],
  },
  romantic: {
    id: 'romantic',
    name: '浪漫',
    nameEn: 'romantic',
    keywords: ['浪漫', '爱情', '约会', '告白', '心动', '甜蜜'],
    tempo: 'slow',
    instruments: ['钢琴', '小提琴', '竖琴'],
    mood: '柔美浪漫，甜蜜悠扬',
    prompt: 'romantic piano, violin, harp, love theme, tender, sweet melody',
    compatibleGenres: ['爱情', '青春', '甜宠'],
  },
  action: {
    id: 'action',
    name: '动作',
    nameEn: 'action',
    keywords: ['动作', '打斗', '追逐', '爆炸', '速度', '激烈'],
    tempo: 'fast',
    instruments: ['电吉他', '电子鼓', '贝斯'],
    mood: '激烈刺激，快速推进',
    prompt: 'action rock, electric guitar riffs, electronic drums, intense, high energy',
    compatibleGenres: ['动作', '冒险', '科幻'],
  },
  horror: {
    id: 'horror',
    name: '恐怖',
    nameEn: 'horror',
    keywords: ['恐怖', '惊吓', '黑暗', '鬼', '噩梦', '尖叫'],
    tempo: 'irregular',
    instruments: ['不协和弦', '低频嗡鸣', '突然的音效'],
    mood: '不安恐惧，突然惊吓',
    prompt: 'horror dark ambient, dissonant chords, low frequency drone, jump scare, nightmare',
    compatibleGenres: ['恐怖', '惊悚', '黑暗'],
  },
  peaceful: {
    id: 'peaceful',
    name: '宁静',
    nameEn: 'peaceful',
    keywords: ['宁静', '平静', '安详', '晨曦', '自然', '冥想'],
    tempo: 'slow',
    instruments: ['长笛', '竖琴', '自然环境音'],
    mood: '平和安静，自然舒展',
    prompt: 'peaceful ambient, flute, harp, nature sounds, zen, meditation, calm',
    compatibleGenres: ['文艺', '治愈', '纪录'],
  },
};

// ─── 文件夹分类→BGM 风格映射 ─────────────────────────────
// 针对中文分类目录名，优先级高于文件名匹配

const CATEGORY_STYLE_MAP = {
  '史诗':     'epic',
  '恐怖':     'horror',
  '浪漫伤感': ['romantic', 'sad'], // 双映射，靠后续评分区分
  '浪漫':     'romantic',
  '伤感':     'sad',
  '欢快':     'happy',
  '喜剧':     'happy',
  '钢琴':     'warm',
  '小提琴':   'warm',
  '摇滚':     'action',
  '电子':     'action',
  '节奏':     'action',
  '复古':     'mystery',
  '积极':     'happy',
  '世界':     'peaceful',
  '混杂':     null,       // 混杂分类不映射，走文件名匹配
  '高分':     null,
};

// ─── 情感→BGM 映射 ──────────────────────────────────────

const EMOTION_STYLE_MAP = {
  '紧张': 'tense',
  '紧迫': 'tense',
  '危机': 'tense',
  '对峙': 'tense',
  '温馨': 'warm',
  '温暖': 'warm',
  '家': 'warm',
  '亲情': 'warm',
  '友情': 'warm',
  '悲伤': 'sad',
  '离别': 'sad',
  '失去': 'sad',
  '遗憾': 'sad',
  '回忆': 'sad',
  '孤独': 'sad',
  '欢快': 'happy',
  '开心': 'happy',
  '庆祝': 'happy',
  '喜悦': 'happy',
  '搞笑': 'happy',
  '轻松': 'happy',
  '史诗': 'epic',
  '宏大': 'epic',
  '壮丽': 'epic',
  '战斗': 'epic',
  '英雄': 'epic',
  '震撼': 'epic',
  '悬疑': 'mystery',
  '神秘': 'mystery',
  '诡异': 'mystery',
  '暗流': 'mystery',
  '推理': 'mystery',
  '浪漫': 'romantic',
  '爱情': 'romantic',
  '心动': 'romantic',
  '甜蜜': 'romantic',
  '告白': 'romantic',
  '动作': 'action',
  '追逐': 'action',
  '打斗': 'action',
  '爆炸': 'action',
  '速度': 'action',
  '恐怖': 'horror',
  '惊吓': 'horror',
  '黑暗': 'horror',
  '噩梦': 'horror',
  '绝望': 'horror',
  '愤怒': 'horror',
  '焦虑': 'horror',
  '宁静': 'peaceful',
  '平静': 'peaceful',
  '安详': 'peaceful',
  '冥想': 'peaceful',
  '释然': 'peaceful',
  '希望': 'peaceful',
  '感动': 'romantic',
};

// ─── 选择逻辑 ────────────────────────────────────────────

/**
 * 根据场景情感推荐 BGM 风格
 * @param {string} scene - 场景描述
 * @param {string} emotion - 情感标签
 * @param {number} duration - 场景时长（秒）
 * @returns {{ style: object, score: number, prompt: string }[]}
 */
export function selectBGMStyle(scene = '', emotion = '', duration = 10) {
  const combined = `${emotion} ${scene}`;
  const scores = {};

  // 关键词匹配
  for (const [keyword, styleId] of Object.entries(EMOTION_STYLE_MAP)) {
    if (combined.includes(keyword)) {
      scores[styleId] = (scores[styleId] || 0) + 1;
    }
  }

  // 风格关键词二次匹配
  for (const [id, style] of Object.entries(BGM_STYLES)) {
    for (const kw of style.keywords) {
      if (combined.includes(kw)) {
        scores[id] = (scores[id] || 0) + 2;
      }
    }
  }

  // 排序
  const ranked = Object.entries(scores)
    .sort(([, a], [, b]) => b - a)
    .map(([id, score]) => {
      const style = BGM_STYLES[id];
      return {
        style,
        score,
        prompt: style.prompt,
        tempo: style.tempo,
        duration,
      };
    });

  // 如果没匹配到，默认温馨
  if (ranked.length === 0) {
    return [{
      style: BGM_STYLES.warm,
      score: 0,
      prompt: BGM_STYLES.warm.prompt,
      tempo: 'slow',
      duration,
    }];
  }

  return ranked;
}

/**
 * 扫描本地音乐目录，构建音乐库
 * 支持 mp3/wav/flac/ogg/aac/m4a 格式
 * 可选：自动用 ffprobe 提取时长
 * 
 * @param {string} musicDir - 音乐目录路径
 * @param {object} options
 * @param {boolean} options.probeDuration - 是否用 ffprobe 提取时长（默认 true）
 * @param {string[]} options.extensions - 允许的扩展名
 * @returns {Promise<Array<{path: string, filename: string, duration: number, tags: string[]}>>}
 */
export async function scanMusicLibrary(musicDir, options = {}) {
  const { probeDuration = true, extensions = ['mp3', 'wav', 'flac', 'ogg', 'aac', 'm4a'] } = options;
  const { readdir, stat } = await import('node:fs/promises');
  const { join } = await import('node:path');
  const { promisify } = await import('node:util');
  
  let execFileAsync;
  try { execFileAsync = promisify((await import('node:child_process')).execFile); } catch { execFileAsync = null; }

  const entries = await readdir(musicDir, { withFileTypes: true }).catch(() => []);
  const results = [];

  for (const entry of entries) {
    if (entry.isDirectory()) {
      // 递归扫描子目录
      const sub = await scanMusicLibrary(join(musicDir, entry.name), options);
      results.push(...sub);
      continue;
    }

    const ext = entry.name.split('.').pop()?.toLowerCase();
    if (!extensions.includes(ext)) continue;

    const filePath = join(musicDir, entry.name);
    const item = { path: filePath, filename: entry.name, duration: 0, tags: [] };

    // 从文件名提取标签
    item.tags = entry.name
      .replace(/\.[^.]+$/, '')           // 去扩展名
      .replace(/[-_\s]+/g, ' ')        // 统一分隔符
      .split(' ')
      .filter(w => w.length > 1)       // 去掉单字符
      .map(w => w.toLowerCase());

    // 用 ffprobe 提取时长
    if (probeDuration && execFileAsync) {
      try {
        const { stdout } = await execFileAsync('ffprobe', [
          '-v', 'error', '-show_entries', 'format=duration',
          '-of', 'default=noprint_wrappers=1:nokey=1', filePath,
        ], { timeout: 5000 });
        item.duration = parseFloat(stdout.trim()) || 0;
      } catch {
        // ffprobe 失败则保持 0
      }
    }

    results.push(item);
  }

  return results;
}

/**
 * 选择 BGM 文件（从本地音乐库）
 * 优先级：category 映射 > 文件名标签匹配 > 随机
 *
 * @param {string} emotion - 情感标签
 * @param {string} scene - 场景描述
 * @param {Array<{path: string, tags: string[], duration: number, category?: string}>} library
 * @param {object} options
 * @param {number} options.minDuration - 最短时长（秒），默认 0
 * @param {number} options.maxDuration - 最长时长（秒），默认 Infinity
 * @param {number} options.topN - 返回前 N 个候选，默认 1
 * @returns {object|object[]} 最佳匹配的 BGM（topN>1 时返回数组）
 */
export function selectBGM(scene, emotion, library = [], options = {}) {
  if (!library.length) return null;

  const { minDuration = 0, maxDuration = Infinity, topN = 1 } = options;

  // 获取推荐风格（按匹配度排序）
  const recommendations = selectBGMStyle(scene, emotion);
  if (!recommendations.length) {
    const filtered = library.filter(i => i.duration >= minDuration && i.duration <= maxDuration);
    return topN === 1 ? (filtered[0] || null) : filtered.slice(0, topN);
  }

  const targetStyles = recommendations.map(r => r.style);

  // 时长过滤
  const candidates = library.filter(i => i.duration >= minDuration && i.duration <= maxDuration);

  // 评分
  const scored = candidates.map(item => {
    let score = 0;

    // === 第1优先级：category 映射（权重最高）===
    if (item.category) {
      for (const [catKey, styleIds] of Object.entries(CATEGORY_STYLE_MAP)) {
        if (item.category.includes(catKey)) {
          const ids = Array.isArray(styleIds) ? styleIds : (styleIds ? [styleIds] : []);
          for (const styleId of ids) {
            const rank = targetStyles.findIndex(s => s.id === styleId);
            if (rank >= 0) {
              score += 20 - rank * 5;
            }
          }
          break;
        }
      }
    }

    // === 第2优先级：文件名标签匹配 ===
    for (const tag of item.tags || []) {
      for (let si = 0; si < targetStyles.length; si++) {
        const style = targetStyles[si];
        const weight = 10 - si * 3; // 第1风格权重=10，第2=7...
        // 精确匹配 style name（中英文）
        if (style.name === tag || style.nameEn === tag) score += weight;
        // 关键词匹配
        for (const kw of style.keywords) {
          if (tag.includes(kw) || kw.includes(tag)) score += weight * 0.6;
        }
      }
    }

    // === 第3优先级：时长匹配加分（越接近目标时长越好）===
    const targetDuration = recommendations[0].duration || 30;
    if (item.duration > 0) {
      const diff = Math.abs(item.duration - targetDuration);
      if (diff < 5) score += 3;
      else if (diff < 15) score += 2;
      else if (diff < 30) score += 1;
    }

    return { ...item, score };
  }).sort((a, b) => b.score - a.score);

  // 如果最高分都是 0（完全没匹配），从所有候选中随机选
  if (scored.length && scored[0].score === 0) {
    const shuffled = [...scored].sort(() => Math.random() - 0.5);
    return topN === 1 ? shuffled[0] : shuffled.slice(0, topN);
  }

  return topN === 1 ? scored[0] : scored.slice(0, topN);
}

/**
 * 生成 BGM 提示词（给音乐生成 AI 使用）
 * @param {string} scene - 场景描述
 * @param {string} emotion - 情感标签
 * @param {number} duration - 时长
 * @returns {string} BGM 生成提示词
 */
export function generateBGMPrompt(scene, emotion, duration = 30) {
  const recommendations = selectBGMStyle(scene, emotion, duration);
  if (!recommendations.length) return 'ambient background music, 30 seconds';

  const best = recommendations[0];
  return `${best.prompt}, ${duration} seconds, cinematic quality, seamless loop`;
}

/**
 * 获取所有 BGM 风格
 * @returns {object[]}
 */
export function listBGMStyles() {
  return Object.values(BGM_STYLES);
}

// ─── 场景情感曲线扩展 ──────────────────────────────────

const EMOTION_INTENSITY_MAP = {
  '紧张': 0.8, '紧迫': 0.9, '危机': 0.95, '对峙': 0.85,
  '温馨': 0.4, '温暖': 0.35, '家': 0.3, '亲情': 0.5, '友情': 0.4,
  '悲伤': 0.7, '离别': 0.75, '失去': 0.8, '回忆': 0.5, '遗憾': 0.6,
  '欢快': 0.6, '开心': 0.7, '庆祝': 0.8, '喜悦': 0.75, '搞笑': 0.5,
  '史诗': 0.9, '宏大': 0.85, '壮丽': 0.8, '战斗': 0.95, '英雄': 0.9,
  '悬疑': 0.6, '神秘': 0.5, '诡异': 0.7, '暗流': 0.5,
  '浪漫': 0.5, '爱情': 0.6, '心动': 0.7, '甜蜜': 0.4, '告白': 0.7,
  '动作': 0.9, '打斗': 0.95, '追逐': 0.85, '爆炸': 0.95,
  '恐怖': 0.85, '惊吓': 0.95, '黑暗': 0.7, '噩梦': 0.8,
  '宁静': 0.2, '平静': 0.15, '安详': 0.1, '冥想': 0.1,
  '愤怒': 0.9, '绝望': 0.85, '希望': 0.5, '感动': 0.6,
  '孤独': 0.6, '焦虑': 0.7, '释然': 0.3, '震撼': 0.85,
};

/**
 * 从 scenario.json 生成 BGM 策略
 * 与 kais-movie-agent Phase 2 产出物对接
 *
 * @param {object} scenario - scenario.json 内容
 * @param {object} options
 * @param {boolean} options.preferLocal - 优先本地选曲（默认 true）
 * @param {number} options.aiThreshold - intensity >= 此值时用 AI 生成（默认 0.8）
 * @returns {object} bgm-strategy.json
 */
export function generateBGMScript(scenario, options = {}) {
  const { preferLocal = true, aiThreshold = 0.8 } = options;

  const globalStyle = selectBGMStyle(
    `${scenario.genre || ''} ${scenario.visual_intent || ''} ${scenario.logline || ''}`,
    scenario.genre || '',
    scenario.duration_seconds || 60
  );

  const shots = [];
  let prevEmotion = null;

  for (const act of scenario.acts || []) {
    for (const scene of act.scenes || []) {
      // 提取场景情感（从 dialogue emotion 或 action 描述）
      const sceneEmotions = [];
      if (scene.dialogue) {
        for (const d of scene.dialogue) {
          if (d.emotion) sceneEmotions.push(d.emotion);
        }
      }
      // 从 action 描述提取情感关键词
      const actionEmotions = extractEmotions(scene.action || '');
      const allEmotions = [...sceneEmotions, ...actionEmotions];

      // 主情感 = 出现最多的，或从 act 的 emotional_arc 推断
      const primaryEmotion = mostFrequent(allEmotions) ||
        extractEmotions(act.emotional_arc || '')[0] ||
        '宁静';

      const styleRec = selectBGMStyle(scene.action || '', primaryEmotion, 10);
      const intensity = EMOTION_INTENSITY_MAP[primaryEmotion] || 0.4;
      const emotionDelta = prevEmotion ? Math.abs(intensity - (EMOTION_INTENSITY_MAP[prevEmotion] || 0.5)) : 0;

      shots.push({
        id: scene.scene_id,
        location: scene.location || '',
        emotion: primaryEmotion,
        intensity: Math.round(intensity * 100) / 100,
        style: styleRec[0]?.style?.id || 'peaceful',
        bgm_action: (intensity >= aiThreshold && !preferLocal) ? 'generate' : 'select',
        prompt: generateBGMPrompt(scene.action || '', primaryEmotion, 30),
        needs_transition: emotionDelta > 0.3,
        transition_type: emotionDelta > 0.3 ? (intensity > (EMOTION_INTENSITY_MAP[prevEmotion] || 0.5) ? 'build_up' : 'fade_down') : 'none',
      });

      prevEmotion = primaryEmotion;
    }
  }

  // 全局主题推断
  const topStyle = globalStyle[0]?.style?.id || 'peaceful';
  const themePrompt = globalStyle[0]?.prompt || 'ambient cinematic';

  return {
    version: '1.0',
    generated_at: new Date().toISOString(),
    project_title: scenario.title || 'untitled',
    global_theme: {
      style: topStyle,
      prompt: themePrompt,
      genre: scenario.genre || '',
    },
    total_shots: shots.length,
    ai_generate_count: shots.filter(s => s.bgm_action === 'generate').length,
    local_select_count: shots.filter(s => s.bgm_action === 'select').length,
    shots,
  };
}

/**
 * 从文本中提取情感关键词
 */
function extractEmotions(text) {
  if (!text) return [];
  const found = [];
  for (const keyword of Object.keys(EMOTION_STYLE_MAP)) {
    if (text.includes(keyword)) found.push(keyword);
  }
  return found;
}

/**
 * 返回数组中出现最多的元素
 */
function mostFrequent(arr) {
  if (!arr.length) return null;
  const counts = {};
  for (const item of arr) counts[item] = (counts[item] || 0) + 1;
  let max = arr[0], maxCount = 0;
  for (const [k, v] of Object.entries(counts)) {
    if (v > maxCount) { max = k; maxCount = v; }
  }
  return max;
}

export { BGM_STYLES as BGM_LIBRARY, BGM_STYLES, EMOTION_STYLE_MAP };
export default { selectBGMStyle, selectBGM, generateBGMPrompt, listBGMStyles, generateBGMScript };
