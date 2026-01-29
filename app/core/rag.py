import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from dotenv import load_dotenv

load_dotenv()

class RAGManager:
    def __init__(self, data_dir="data", persist_dir="vector_store"):
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        # 使用阿里云的 Embedding 模型
        self.embeddings = DashScopeEmbeddings(
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
        )
        self.vector_store = None

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
