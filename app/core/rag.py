"""
RAG Manager - 支持免费 Embedding 模型和文档标签
"""
import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from app.core.document_tagger import DocumentTagger

load_dotenv()

class RAGManager:
    def __init__(self, data_dir="data", persist_dir="vector_store"):
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        self.embeddings = self._get_embeddings()
        self.vector_store = None
        self.tagger = DocumentTagger()  # 新增：文档标签管理器

    def _get_embeddings(self):
        """
        获取 Embedding 模型（本地 HuggingFace 模型）
        """
        from langchain_community.embeddings import HuggingFaceEmbeddings
        model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "BAAI/bge-large-zh-v1.5")
        print(f"📊 使用本地 Embedding: {model_name}")
        print("💰 完全免费，无需 API Key")
        print("⏳ 首次使用会下载模型（约 500MB），请耐心等待...")
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

    def load_and_index(self):
        """加载 data 目录下的文档并建立索引（带标签）"""
        print(f"Loading documents from {self.data_dir}...")
        
        from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredEPubLoader
        
        # 支持多种文件格式
        loaders = [
            DirectoryLoader(self.data_dir, glob="**/*.pdf", loader_cls=PyPDFLoader),
            DirectoryLoader(self.data_dir, glob="**/*.txt", loader_cls=TextLoader),
            DirectoryLoader(self.data_dir, glob="**/*.md", loader_cls=TextLoader),
            DirectoryLoader(self.data_dir, glob="**/*.epub", loader_cls=UnstructuredEPubLoader),
        ]
        
        documents = []
        for loader in loaders:
            try:
                docs = loader.load()
                documents.extend(docs)
                if docs:
                    print(f"  ✅ Loaded {len(docs)} documents from {loader.glob}")
            except Exception as e:
                print(f"  ⚠️  Warning loading {loader.glob}: {e}")
        
        if not documents:
            print("❌ No documents found.")
            return

        print(f"\n📚 Total documents loaded: {len(documents)}")
        
        # 为文档添加标签
        print(f"🏷️  Adding tags to documents...")
        for doc in documents:
            source = doc.metadata.get("source", "")
            tags = self.tagger.get_tags_for_file(source)
            
            # 扁平化标签数据（Chroma 不支持嵌套字典和列表）
            doc.metadata["book"] = tags.get("book", "未知")
            doc.metadata["author"] = tags.get("author", "未知")
            doc.metadata["dynasty"] = tags.get("dynasty", "未知")
            doc.metadata["genre"] = tags.get("genre", "未知")
            
            # 将列表转换为字符串
            if "category" in tags and isinstance(tags["category"], list):
                doc.metadata["category"] = ", ".join(tags["category"])
            else:
                doc.metadata["category"] = tags.get("category", "其他")
            
            if "keywords" in tags and isinstance(tags["keywords"], list):
                doc.metadata["keywords"] = ", ".join(tags["keywords"])
            else:
                doc.metadata["keywords"] = ""
        
        # 打印标签统计
        tag_stats = {}
        for doc in documents:
            book = doc.metadata.get("book", "未知")
            tag_stats[book] = tag_stats.get(book, 0) + 1
        
        print(f"📊 Documents by book:")
        for book, count in tag_stats.items():
            print(f"  - {book}: {count} documents")

        # 文本切片
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_documents(documents)
        print(f"✂️  Split into {len(texts)} chunks.")

        # 存储到向量数据库
        self.vector_store = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )
        print("✅ Indexing completed and persisted.")
        print(f"💡 所有文档已添加标签，可以使用标签过滤检索结果")

    def get_retriever(self, k=5, filters=None):
        """
        获取检索器
        
        参数:
            k: 检索文档数量，默认 5（增加检索数量可提高召回率）
            filters: 标签过滤条件，如 {"book": "红楼梦"}
        """
        if not self.vector_store:
            # 如果内存里没有，尝试从本地加载
            self.vector_store = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
        
        # 构建检索参数
        search_kwargs = {"k": k}
        
        # 如果有过滤条件，添加到检索参数
        if filters:
            # Chroma 使用 where 参数进行元数据过滤
            # 例如: {"book": "红楼梦"}
            search_kwargs["filter"] = filters
        
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)
    
    def search_by_book(self, query: str, book_name: str, k=5):
        """
        按书名检索
        
        参数:
            query: 查询文本
            book_name: 书名（如 "红楼梦"）
            k: 返回文档数量
        """
        if not self.vector_store:
            self.vector_store = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
        
        # 使用元数据过滤
        results = self.vector_store.similarity_search(
            query,
            k=k,
            filter={"book": book_name}
        )
        
        return results
    
    def get_books_list(self):
        """获取知识库中的所有书籍"""
        return self.tagger.get_books()
    
    def get_tag_statistics(self):
        """获取标签统计信息"""
        return self.tagger.get_statistics()
