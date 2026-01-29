"""
RAG Manager - 支持免费 Embedding 模型
"""
import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

class RAGManager:
    def __init__(self, data_dir="data", persist_dir="vector_store"):
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        self.embeddings = self._get_embeddings()
        self.vector_store = None

    def _get_embeddings(self):
        """
        获取 Embedding 模型
        
        支持的类型：
        - aliyun: 阿里云 text-embedding-v3（付费）
        - local: 本地 HuggingFace 模型（免费）
        """
        embedding_type = os.getenv("EMBEDDING_TYPE", "local").lower()
        
        if embedding_type == "aliyun":
            from langchain_community.embeddings import DashScopeEmbeddings
            print("📊 使用阿里云 Embedding: text-embedding-v3")
            print("💰 按 Token 计费")
            return DashScopeEmbeddings(
                model=os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
            )
        
        elif embedding_type == "local":
            from langchain_community.embeddings import HuggingFaceEmbeddings
            model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            print(f"📊 使用本地 Embedding: {model_name}")
            print("💰 完全免费，无需 API Key")
            print("⏳ 首次使用会下载模型（约 500MB），请耐心等待...")
            return HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        
        else:
            raise ValueError(f"不支持的 Embedding 类型: {embedding_type}")

    def load_and_index(self):
        """加载 data 目录下的文档并建立索引"""
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

    def get_retriever(self):
        """获取检索器"""
        if not self.vector_store:
            # 如果内存里没有，尝试从本地加载
            self.vector_store = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
        return self.vector_store.as_retriever(search_kwargs={"k": 3})
