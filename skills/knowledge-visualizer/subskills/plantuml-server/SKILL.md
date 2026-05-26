# PlantUML Server 集成

将 PlantUML 代码渲染为 SVG 图片。

## 职责

**输入**: PlantUML 代码
**输出**: SVG 图片

## 实现方案

### 方案一：使用公共 PlantUML Server

```bash
# 编码 PlantUML 为 URL
ENCODED=$(echo "$PLANTUML_CODE" | python3 -c "
import sys
import zlib
import base64

data = sys.stdin.read()
compressed = zlib.compress(data.encode('utf-8'), 9)
encoded = base64.b64encode(compressed).decode('ascii')
# PlantUML 使用特殊编码
result = ''
for c in encoded:
    if c == '+':
        result += '-'
    elif c == '/':
        result += '_'
    elif c == '=':
        continue
    else:
        result += c
print(result)
")

# 下载 SVG
curl -s "https://www.plantuml.com/plantuml/svg/~1$ENCODED" -o output.svg
```

### 方案二：本地 PlantUML Server (推荐)

```bash
# 使用 Docker 启动本地服务
docker run -d -p 8080:8080 plantuml/plantuml-server:jetty

# 调用本地服务
curl -X POST \
  -H "Content-Type: text/plain" \
  --data-binary "@diagram.puml" \
  http://localhost:8080/svg \
  -o output.svg
```

### 方案三：PlantUML JAR (离线)

```bash
# 安装 Java 和 PlantUML
sudo apt install default-jdk
wget https://github.com/plantuml/plantuml/releases/download/v1.2024.3/plantuml-1.2024.3.jar

# 生成 SVG
java -jar plantuml.jar -tsvg diagram.puml
```

## 函数实现

```bash
#!/bin/bash

# 渲染 PlantUML 为 SVG
render_plantuml() {
  local input="$1"
  local output="${2:-output.svg}"
  local server="${PLANTUML_SERVER:-http://localhost:8080}"

  # 检查服务是否可用
  if curl -s "$server/svg" > /dev/null 2>&1; then
    # 本地服务器
    curl -X POST \
      -H "Content-Type: text/plain" \
      --data-binary "@$input" \
      "$server/svg" \
      -o "$output"
  else
    # 公共服务器
    local encoded=$(encode_plantuml "$input")
    curl -s "https://www.plantuml.com/plantuml/svg/~1$encoded" -o "$output"
  fi

  echo "$output"
}

# PlantUML 编码
encode_plantuml() {
  python3 << 'PYEOF'
import sys
import zlib
import base64

data = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
compressed = zlib.compress(data.encode('utf-8'), 9)
encoded = base64.b64encode(compressed).decode('ascii')

# PlantUML URL 编码
result = ''
for c in encoded:
    if c == '+':
        result += '-'
    elif c == '/':
        result += '_'
    elif c == '=':
        continue
    else:
        result += c
print(result)
PYEOF
}
```

## Node.js 实现

```javascript
const fs = require('fs');
const zlib = require('zlib');
const axios = require('axios');

async function renderPlantUML(plantumlCode, outputPath) {
  // 编码
  const deflated = zlib.deflateRawSync(plantumlCode, { level: 9 });
  const encoded = encode64(deflated);

  // 请求 SVG
  const url = `https://www.plantuml.com/plantuml/svg/~1${encoded}`;
  const response = await axios.get(url);

  fs.writeFileSync(outputPath, response.data);
  return outputPath;
}

// PlantUML 特殊 base64 编码
function encode64(buffer) {
  const chars = '0123456789ABCDEF...'; // 完整字符集
  let result = '';
  // ... 编码逻辑
  return result;
}
```

## 使用示例

```bash
# 基础用法
./plantuml-server.sh render diagram.puml output.svg

# 批量渲染
for puml in plantuml/*.puml; do
  ./plantuml-server.sh render "$puml" "svg/$(basename $puml .puml).svg"
done
```

## 错误处理

```bash
render_plantuml() {
  local input="$1"
  local output="$2"

  if ! curl -f -s -X POST ... -o "$output"; then
    echo "ERROR: PlantUML 渲染失败"
    return 1
  fi

  # 验证 SVG
  if ! grep -q '<svg' "$output"; then
    echo "ERROR: 输出不是有效的 SVG"
    return 1
  fi
}
```

---

*版本: 0.1.0*
