# 四大名著知识问答 API 文档

## 基础信息

- **Base URL**: `http://localhost:8888`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8

---

## 接口列表

### 1. 获取配置信息

获取当前系统的模型配置信息。

**接口地址**: `GET /config`

**请求参数**: 无

**响应示例**:
```json
{
  "llm_model": "阿里云 deepseek-v3.2",
  "embedding_model": "BGE-large-zh-v1.5 (本地)",
  "model_provider": "aliyun",
  "enable_direct_retrieval": true
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| llm_model | string | LLM 模型名称 |
| embedding_model | string | Embedding 模型名称 |
| model_provider | string | 模型提供商（aliyun/groq） |
| enable_direct_retrieval | boolean | 是否启用直接检索 |

**错误响应**:
```json
{
  "error": "错误信息"
}
```

---

### 2. 获取书籍列表

获取知识库中所有可用的书籍列表及统计信息。

**接口地址**: `GET /books`

**请求参数**: 无

**响应示例**:
```json
{
  "books": [
    "红楼梦",
    "三国演义",
    "西游记",
    "水浒传"
  ],
  "statistics": {
    "红楼梦": {
      "文档数": 120,
      "标签": ["人物", "诗词", "情节"]
    },
    "三国演义": {
      "文档数": 120,
      "标签": ["战争", "人物", "策略"]
    },
    "西游记": {
      "文档数": 100,
      "标签": ["神话", "人物", "冒险"]
    },
    "水浒传": {
      "文档数": 120,
      "标签": ["人物", "武功", "情节"]
    }
  }
}
```

**响应字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| books | array | 书籍名称列表 |
| statistics | object | 各书籍的统计信息 |

**错误响应**:
```json
{
  "error": "错误信息"
}
```

---

### 3. 聊天接口（流式，支持多轮对话）⭐ 推荐

**接口地址**: `POST /chat`

**Content-Type**: `application/json`

**请求参数**:
```json
{
  "query": "贾宝玉是谁？",
  "book": "红楼梦",
  "history": [
    {
      "role": "user",
      "content": "林黛玉是谁？",
      "timestamp": 1706889600000,
      "book": "红楼梦"
    },
    {
      "role": "assistant",
      "content": "林黛玉是《红楼梦》中的女主角...",
      "timestamp": 1706889602000,
      "book": "红楼梦"
    }
  ]
}
```

**请求字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 用户问题 |
| book | string | 否 | 限定检索的书名（红楼梦/三国演义/西游记/水浒传） |
| history | array | 否 | 对话历史（最近 5 轮，10 条消息） |

**history 数组元素字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| role | string | 是 | 角色（user/assistant） |
| content | string | 是 | 消息内容 |
| timestamp | integer | 否 | 时间戳（毫秒） |
| book | string | 否 | 关联的书籍 |

**响应格式**: Server-Sent Events (SSE)

**响应流程**:
1. 多次发送 `type: text` 消息（流式输出答案）
2. 发送 `type: metadata` 消息（元数据）
3. 发送 `type: done` 消息（结束标记）

**响应示例**:

```
data: {"type": "text", "content": "贾"}

data: {"type": "text", "content": "宝"}

data: {"type": "text", "content": "玉"}

data: {"type": "text", "content": "是"}

data: {"type": "text", "content": "《"}

data: {"type": "text", "content": "红"}

data: {"type": "text", "content": "楼"}

data: {"type": "text", "content": "梦"}

data: {"type": "text", "content": "》"}

data: {"type": "text", "content": "中"}

data: {"type": "text", "content": "的"}

data: {"type": "text", "content": "男"}

data: {"type": "text", "content": "主"}

data: {"type": "text", "content": "角"}

data: {"type": "text", "content": "..."}

data: {"type": "metadata", "query": "贾宝玉是谁？", "book_filter": "红楼梦", "has_context": true, "knowledge_base_used": true, "used_direct_retrieval": false, "used_few_shot": true, "keyword_matched": true, "retrieved_docs_count": 8, "sources": [{"source": "红楼梦", "page": "12", "preview": "贾宝玉，荣国府贾政与王夫人所生的次子..."}]}

data: {"type": "done"}
```

**metadata 字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | 固定值 "metadata" |
| query | string | 用户问题 |
| book_filter | string | 书籍过滤（null 表示全部） |
| has_context | boolean | 是否使用了对话历史 |
| knowledge_base_used | boolean | 是否使用了知识库 |
| used_direct_retrieval | boolean | 是否使用了直接检索 |
| used_few_shot | boolean | 是否使用了 Few-Shot |
| keyword_matched | boolean | 是否命中关键词 |
| retrieved_docs_count | integer | 检索到的文档数量 |
| sources | array | 引用来源列表 |

**sources 数组元素字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| source | string | 文档来源（书名） |
| page | string | 页码 |
| preview | string | 文本预览（前 200 字） |

**错误响应**:
```
data: {"type": "error", "error": "错误信息"}
```

---

### 4. 聊天接口（流式，简化版）

**接口地址**: `GET /chat`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 用户问题 |
| book | string | 否 | 限定检索的书名 |

**请求示例**:
```
GET /chat?query=贾宝玉是谁？&book=红楼梦
```

**响应格式**: Server-Sent Events (SSE)

**响应流程**: 与 POST /chat 相同

**说明**: 
- 不支持多轮对话
- 适用于简单查询场景
- 推荐使用 POST /chat 接口

---

### 5. 更新知识库

手动触发知识库重新索引。

**接口地址**: `GET /ingest`

**请求参数**: 无

**响应示例**:
```json
{
  "status": "success",
  "message": "Documents indexed successfully"
}
```

**错误响应**:
```json
{
  "status": "error",
  "message": "错误信息"
}
```

**说明**: 
- 此操作耗时较长（几分钟）
- 仅在添加新文档或修改配置后使用
- 正常使用无需调用此接口

---

## 客户端集成示例

### Android (Kotlin)

```kotlin
// 1. 获取配置信息
suspend fun getConfig(): ConfigResponse {
    val response = httpClient.get("$baseUrl/config")
    return response.body()
}

// 2. 获取书籍列表
suspend fun getBooks(): BooksResponse {
    val response = httpClient.get("$baseUrl/books")
    return response.body()
}

// 3. 发送聊天消息（流式）
fun sendMessage(
    query: String,
    book: String? = null,
    history: List<Message> = emptyList(),
    onChunk: (String) -> Unit,
    onMetadata: (Metadata) -> Unit,
    onComplete: () -> Unit,
    onError: (String) -> Unit
) {
    val request = ChatRequest(query, book, history)
    
    httpClient.post("$baseUrl/chat") {
        contentType(ContentType.Application.Json)
        setBody(request)
    }.bodyAsChannel().consumeEachLine { line ->
        if (line.startsWith("data: ")) {
            val json = line.substring(6)
            val data = Json.decodeFromString<SSEMessage>(json)
            
            when (data.type) {
                "text" -> onChunk(data.content ?: "")
                "metadata" -> onMetadata(data)
                "done" -> onComplete()
                "error" -> onError(data.error ?: "Unknown error")
            }
        }
    }
}

// 数据模型
data class ConfigResponse(
    val llm_model: String,
    val embedding_model: String,
    val model_provider: String,
    val enable_direct_retrieval: Boolean
)

data class BooksResponse(
    val books: List<String>,
    val statistics: Map<String, BookStats>
)

data class BookStats(
    val 文档数: Int,
    val 标签: List<String>
)

data class ChatRequest(
    val query: String,
    val book: String? = null,
    val history: List<Message> = emptyList()
)

data class Message(
    val role: String,
    val content: String,
    val timestamp: Long? = null,
    val book: String? = null
)

@Serializable
data class SSEMessage(
    val type: String,
    val content: String? = null,
    val error: String? = null,
    // metadata 字段
    val query: String? = null,
    val book_filter: String? = null,
    val has_context: Boolean? = null,
    val knowledge_base_used: Boolean? = null,
    val used_direct_retrieval: Boolean? = null,
    val used_few_shot: Boolean? = null,
    val keyword_matched: Boolean? = null,
    val retrieved_docs_count: Int? = null,
    val sources: List<Source>? = null
)

data class Source(
    val source: String,
    val page: String,
    val preview: String
)
```

### iOS (Swift)

```swift
// 1. 获取配置信息
func getConfig() async throws -> ConfigResponse {
    let url = URL(string: "\(baseURL)/config")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(ConfigResponse.self, from: data)
}

// 2. 获取书籍列表
func getBooks() async throws -> BooksResponse {
    let url = URL(string: "\(baseURL)/books")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(BooksResponse.self, from: data)
}

// 3. 发送聊天消息（流式）
func sendMessage(
    query: String,
    book: String? = nil,
    history: [Message] = [],
    onChunk: @escaping (String) -> Void,
    onMetadata: @escaping (Metadata) -> Void,
    onComplete: @escaping () -> Void,
    onError: @escaping (String) -> Void
) {
    let url = URL(string: "\(baseURL)/chat")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let chatRequest = ChatRequest(query: query, book: book, history: history)
    request.httpBody = try? JSONEncoder().encode(chatRequest)
    
    let task = URLSession.shared.dataTask(with: request) { data, response, error in
        guard let data = data else {
            onError(error?.localizedDescription ?? "Unknown error")
            return
        }
        
        let lines = String(data: data, encoding: .utf8)?.components(separatedBy: "\n\n") ?? []
        for line in lines {
            if line.hasPrefix("data: ") {
                let json = String(line.dropFirst(6))
                if let data = json.data(using: .utf8),
                   let message = try? JSONDecoder().decode(SSEMessage.self, from: data) {
                    switch message.type {
                    case "text":
                        onChunk(message.content ?? "")
                    case "metadata":
                        onMetadata(message)
                    case "done":
                        onComplete()
                    case "error":
                        onError(message.error ?? "Unknown error")
                    default:
                        break
                    }
                }
            }
        }
    }
    task.resume()
}

// 数据模型
struct ConfigResponse: Codable {
    let llm_model: String
    let embedding_model: String
    let model_provider: String
    let enable_direct_retrieval: Bool
}

struct BooksResponse: Codable {
    let books: [String]
    let statistics: [String: BookStats]
}

struct BookStats: Codable {
    let 文档数: Int
    let 标签: [String]
}

struct ChatRequest: Codable {
    let query: String
    let book: String?
    let history: [Message]
}

struct Message: Codable {
    let role: String
    let content: String
    let timestamp: Int64?
    let book: String?
}

struct SSEMessage: Codable {
    let type: String
    let content: String?
    let error: String?
    // metadata 字段
    let query: String?
    let book_filter: String?
    let has_context: Bool?
    let knowledge_base_used: Bool?
    let used_direct_retrieval: Bool?
    let used_few_shot: Bool?
    let keyword_matched: Bool?
    let retrieved_docs_count: Int?
    let sources: [Source]?
}

struct Source: Codable {
    let source: String
    let page: String
    let preview: String
}
```

### React Native (TypeScript)

```typescript
// API 客户端
class KnowledgeBaseAPI {
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:8888') {
    this.baseURL = baseURL;
  }

  // 1. 获取配置信息
  async getConfig(): Promise<ConfigResponse> {
    const response = await fetch(`${this.baseURL}/config`);
    return response.json();
  }

  // 2. 获取书籍列表
  async getBooks(): Promise<BooksResponse> {
    const response = await fetch(`${this.baseURL}/books`);
    return response.json();
  }

  // 3. 发送聊天消息（流式）
  async sendMessage(
    query: string,
    book?: string,
    history: Message[] = [],
    callbacks: {
      onChunk: (text: string) => void;
      onMetadata: (metadata: Metadata) => void;
      onComplete: () => void;
      onError: (error: string) => void;
    }
  ): Promise<void> {
    const response = await fetch(`${this.baseURL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, book, history }),
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      callbacks.onError('Failed to get response reader');
      return;
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const json = line.substring(6);
          try {
            const data = JSON.parse(json) as SSEMessage;

            switch (data.type) {
              case 'text':
                callbacks.onChunk(data.content || '');
                break;
              case 'metadata':
                callbacks.onMetadata(data as Metadata);
                break;
              case 'done':
                callbacks.onComplete();
                break;
              case 'error':
                callbacks.onError(data.error || 'Unknown error');
                break;
            }
          } catch (e) {
            console.error('Failed to parse SSE message:', e);
          }
        }
      }
    }
  }
}

// 类型定义
interface ConfigResponse {
  llm_model: string;
  embedding_model: string;
  model_provider: string;
  enable_direct_retrieval: boolean;
}

interface BooksResponse {
  books: string[];
  statistics: Record<string, BookStats>;
}

interface BookStats {
  文档数: number;
  标签: string[];
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: number;
  book?: string;
}

interface SSEMessage {
  type: 'text' | 'metadata' | 'done' | 'error';
  content?: string;
  error?: string;
}

interface Metadata extends SSEMessage {
  query: string;
  book_filter?: string;
  has_context: boolean;
  knowledge_base_used: boolean;
  used_direct_retrieval: boolean;
  used_few_shot: boolean;
  keyword_matched: boolean;
  retrieved_docs_count: number;
  sources: Source[];
}

interface Source {
  source: string;
  page: string;
  preview: string;
}

// 使用示例
const api = new KnowledgeBaseAPI();

// 获取配置
const config = await api.getConfig();
console.log('LLM:', config.llm_model);

// 获取书籍列表
const books = await api.getBooks();
console.log('可用书籍:', books.books);

// 发送消息
await api.sendMessage(
  '贾宝玉是谁？',
  '红楼梦',
  [],
  {
    onChunk: (text) => console.log('收到文本:', text),
    onMetadata: (metadata) => console.log('元数据:', metadata),
    onComplete: () => console.log('完成'),
    onError: (error) => console.error('错误:', error),
  }
);
```

---

## 注意事项

### 1. 流式响应处理
- 使用 Server-Sent Events (SSE) 格式
- 每条消息以 `data: ` 开头，以 `\n\n` 结尾
- 需要逐行解析 JSON 数据
- 建议使用支持 SSE 的客户端库

### 2. 对话历史管理
- 客户端需要维护对话历史
- 建议保留最近 5 轮（10 条消息）
- 超过限制时从头部删除旧消息
- 每条消息需要包含 role 和 content

### 3. 错误处理
- 所有接口都可能返回错误
- 流式接口通过 `type: error` 返回错误
- 非流式接口通过 `error` 字段返回错误
- 建议实现重试机制

### 4. 性能优化
- 流式响应可以提供更好的用户体验
- 建议在 UI 中实时显示流式文本
- 元数据可以延迟显示（在答案完成后）
- 对话历史不要保存过多（影响性能）

### 5. 书籍筛选
- 书籍名称必须完全匹配（红楼梦/三国演义/西游记/水浒传）
- 不传 book 参数表示搜索全部书籍
- 书籍筛选可以提高检索准确度

---

## 更新日志

### 2026-02-02
- 初始版本
- 支持流式聊天
- 支持多轮对话
- 支持书籍筛选
- 提供配置和书籍列表接口
