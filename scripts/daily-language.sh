#!/bin/bash

# Daily Language Learning Script
# 生成每日英语德语学习内容并添加到Notion

# 临时文件路径
TEMP_FILE="/tmp/language-content-$(date +%Y-%m-%d).md"

echo "开始生成每日语言学习内容..."

# 生成学习内容
cat > "$TEMP_FILE" << 'EOF'
# Daily Language Learning - '"$(date +%Y-%m-%d)"'

## 每日一句 (Daily Sentence)

**English:** *The only way to do great work is to love what you do.* - Steve Jobs

**Deutsch:** *Wer Sprache nicht liebt, kann kein guter Übersetzer sein.* - Goethe

## 语法要点 (Grammar Points)

### English: Present Perfect vs. Simple Past

**Detailed Explanation:**
- **Present Perfect**: 用于表示发生在过去但对现在有影响或持续到现在的动作，使用 "have/has + past participle"
- **Simple Past**: 用于表示在特定过去时间完成的动作，使用 "past tense form"

**Examples:**
- Present Perfect: *I have visited Paris three times.* (强调访问过几次，可能还会去)
- Simple Past: *I visited Paris last year.* (强调去年发生过这件事)

**Common Errors to Avoid:**
- ❌ "I have seen him yesterday." (错误，yesterday 是具体过去时间)
- ✅ "I saw him yesterday."
- ✅ "I have seen him recently."

### Deutsch: Modalverben mit Infinitiv I (Modal Verbs with Infinitive)

**Detailed Explanation:**
德语情态动词后直接使用动词原形（Infinitiv I），而不是分词。

**Modalverben können:**
- **können** - 能够，会
- **wollen** - 想要
- **sollen** - 应该，应当
- **mögen** - 喜欢
- **dürfen** - 允许
- **müssen** - 必须

**Verbkonjugation:**

| Person | können | wollen | sollen | mögen | dürfen | müssen |
|--------|--------|--------|--------|-------|--------|--------|
| ich    | kann    | will    | soll    | mag   | darf    | muss   |
| du     | kannst  | willst  | sollst  | magst | darfst  | musst  |
| er/sie/es | kann  | will    | soll    | mag   | darf    | muss   |
| wir    | können  | wollen  | sollen  | mögen | dürfen  | müssen |
| ihr    | könnt   | wollt   | sollt   | mögt  | dürft   | müsst  |
| sie/Sie | können  | wollen  | sollen  | mögen | dürfen  | müssen |

**Beispiele:**
- *Ich kann Deutsch sprechen.* (我会说德语)
- *Sie wollen ein Buch lesen.* (他们想读一本书)
- *Du sollst früher aufstehen.* (你应该早点起床)
- *Wir dürfen hier nicht parken.* (我们不允许在这里停车)

## 重点词汇 (Key Vocabulary)

### English Vocabulary

| Word | Phonetic | Type | Meaning | Example Sentence |
|------|----------|------|---------|------------------|
| **perspective** | /pərˈspektɪv/ | Noun | 观点，视角 | From my perspective, this is the best solution. |
| **resilient** | /rɪˈzɪliənt/ | Adjective | 有弹性的，适应力强的 | Children are remarkably resilient in difficult situations. |
| **accumulate** | /əˈkjuːmjəleɪt/ | Verb | 积累，聚集 | Over time, dust accumulates on the shelves. |
| **versatile** | /ˈvɜːrsətaɪl/ | Adjective | 多才多艺的，多功能的 | This knife is surprisingly versatile for cooking. |
| **consequence** | /ˈkɑːnsɪkwəns/ | Noun | 后果，结果 | Every action has its consequences. |

### Deutsch Vokabeln

| Wort | Type | Bedeutung | Beispiel |
|------|------|-----------|----------|
| **beeindruckend** | Adjektiv | 令人印象深刻的 | Die Aussicht vom Berg ist beeindruckend. |
| **entwickeln** | Verb | 发展，开发 | Das Unternehmen entwickelt neue Technologien. |
| **bewusst** | Adjektiv | 有意识的，故意的 | Sie hat bewusst die Wahrheit verschwiegen. |
| **erfolgreich** | Adjektiv | 成功的 | Das Projekt war sehr erfolgreich. |
| **bedeuten** | Verb | 意味着 | Was bedeutet dieses Wort? |

## 学习小贴士 (Learning Tips)

### English Tips:
1. **Focus on pronunciation**: Pay attention to vowel sounds and stress patterns
2. **Use mnemonics**: Create mental images to remember difficult vocabulary
3. **Practice daily**: Even 15 minutes of consistent practice is more effective than long sessions
4. **Listen actively**: Watch English movies with subtitles to improve listening skills
5. **Speak without fear**: Make mistakes - they're learning opportunities

### Deutsch Tipps:
1. **Master der/die/das**: Spend extra time learning noun genders
2. **Practice cases**: Learn nominative, accusative, dative, and genitive case usage
3. **Use verb tables**: Practice conjugating regularly and irregularly
4. **Listen to music**: German songs can help improve pronunciation
5. **Read children's books**: Start with simple texts and gradually increase difficulty

### 共同建议 (Common Tips):
- **建立学习习惯** (Build learning habits): 固定时间学习，保持连续性
- **使用间隔重复** (Use spaced repetition): 每天复习，每周强化
- **寻找语伴** (Find language partners): 实际对话提高口语能力
- **记录学习进度** (Track progress): 记录学到的内容和感受
- **保持耐心** (Stay patient): 语言学习是马拉松，不是短跑

---
*完成时间: '"$(date "+%Y-%m-%d %H:%M")"*
*下次学习: 明天同一时间*
EOF

echo "内容生成完成，开始获取Notion页面..."

# 获取或创建语言学习页面
PAGE_ID=$(notion-cli page list --ancestor "2f811082-af8e-8035-a849-eabd27cadac3" | grep -oE '[a-f0-9-]{36}' | head -1)

if [ -z "$PAGE_ID" ]; then
    echo "未找到现有页面，尝试创建新页面..."
    PAGE_ID=$(notion-cli page create --parent "2f811082-af8e-8035-a849-eabd27cadac3" --title "每日语言学习" | grep -oE '[a-f0-9-]{36}')
fi

if [ -z "$PAGE_ID" ]; then
    echo "错误: 无法获取页面ID"
    rm -f "$TEMP_FILE"
    exit 1
fi

echo "使用页面ID: $PAGE_ID"

# 使用追加脚本添加内容
/home/kai/.openclaw/workspace/scripts/lib/notion-append-blocks.sh "$PAGE_ID" "$TEMP_FILE"

# 清理临时文件
rm -f "$TEMP_FILE"

echo "每日语言学习内容添加完成"