# RESTful API 设计原则

REST (Representational State Transfer) 是一种软件架构风格，用于设计网络应用程序的 API。

## 核心概念

### 资源 (Resource)
资源是 REST 架构的核心，代表系统中的业务对象。每个资源都有唯一的 URI 标识。

**例子**:
- `/users` - 用户集合
- `/users/123` - 特定用户
- `/users/123/orders` - 用户的订单

### 统一接口 (Uniform Interface)
使用标准的 HTTP 方法对资源进行操作：

- **GET** - 获取资源
- **POST** - 创建资源
- **PUT** - 更新资源（完整替换）
- **PATCH** - 部分更新资源
- **DELETE** - 删除资源

### 无状态性 (Stateless)
每个请求必须包含服务器处理所需的所有信息。服务器不保存客户端的会话状态。

**优点**:
- 易于扩展（可水平扩展）
- 提高可靠性
- 简化服务器实现

### 表述 (Representation)
资源可以有多种表述形式：
- JSON（最常用）
- XML
- HTML
- 纯文本

## 设计流程

设计一个 RESTful API 需要遵循以下步骤：

### 第一步：识别资源
分析业务需求，确定系统中的核心资源。

**方法**:
1. 从用户故事中提取名词
2. 识别资源的层级关系
3. 确定资源的属性

### 第二步：定义 URI
为每个资源设计清晰的 URI 结构。

**原则**:
- 使用名词，不用动词
- 使用复数形式
- 层级清晰，不超过 3 层

**好的例子**:
- `/articles`
- `/articles/42/comments`

**坏的例子**:
- `/getArticles`
- `/article`
- `/articles/42/comments/15/author/profile`

### 第三步：选择 HTTP 方法
根据操作类型选择合适的 HTTP 方法。

| 操作 | HTTP 方法 | URI | 说明 |
|------|-----------|-----|------|
| 获取列表 | GET | `/articles` | 返回文章列表 |
| 获取单个 | GET | `/articles/42` | 返回特定文章 |
| 创建 | POST | `/articles` | 创建新文章 |
| 完整更新 | PUT | `/articles/42` | 替换整篇文章 |
| 部分更新 | PATCH | `/articles/42` | 修改部分字段 |
| 删除 | DELETE | `/articles/42` | 删除文章 |

### 第四步：设计响应格式
定义统一的响应格式和状态码使用规范。

**成功响应**:
```json
{
  "data": { /* 资源数据 */ },
  "meta": {
    "timestamp": "2026-02-25T15:00:00Z"
  }
}
```

**错误响应**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "标题不能为空",
    "details": [
      {"field": "title", "message": "required"}
    ]
  }
}
```

## 最佳实践

### 版本控制
在 URI 中包含版本号：`/v1/articles` 或通过 Header: `Accept: application/vnd.api+json;version=1`

### 分页
对于集合资源，支持分页参数：
- `?page=2&limit=20`
- 响应中包含分页元数据

### 过滤和排序
支持查询参数：
- `?status=published` - 过滤
- `?sort=-created_at` - 排序（-表示降序）

### HATEOAS
在响应中包含相关链接，实现超媒体驱动：
```json
{
  "data": { "id": 42, "title": "..." },
  "links": {
    "self": "/articles/42",
    "author": "/users/1",
    "comments": "/articles/42/comments"
  }
}
```

## 常见错误

1. **在 URI 中使用动词** - `/getUsers` ❌
2. **忽略 HTTP 语义** - 用 GET 修改数据 ❌
3. **过度嵌套** - `/a/b/c/d/e` ❌
4. **返回不一致的响应格式** ❌
5. **忽略错误处理** - 总是返回 200 ❌

## 总结

RESTful API 设计的核心是：
1. 以资源为中心
2. 遵循 HTTP 语义
3. 保持接口简洁一致
4. 考虑可扩展性和可维护性

---

*本文档用于知识可视化系统测试*
