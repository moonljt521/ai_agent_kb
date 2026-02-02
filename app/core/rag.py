import os
import glob
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from app.core.embeddings import get_embeddings, get_embedding_info
from dotenv import load_dotenv

load_dotenv()

class RAGManager:
    def __init__(self, data_dir="data", persist_dir="vector_store"):
        self.data_dir = data_dir
        self.persist_dir = persist_dir
        
        # 使用统一的 Embedding 获取函数（支持多种提供商）
        self.embeddings = get_embeddings()
        
        # 打印 Embedding 信息
        info = get_embedding_info()
        if info.get("is_local"):
            print(f"💡 提示：使用本地模型，首次运行会自动下载")
        
        self.vector_store = None

    def load_and_index(self):
        """加载 data 目录下的文档并建立索引"""
        print(f"Loading documents from {self.data_dir}...")
        
        documents = []
        
        # 加载 PDF
        try:
            pdf_loader = DirectoryLoader(self.data_dir, glob="**/*.pdf", loader_cls=PyPDFLoader)
            pdf_docs = pdf_loader.load()
            documents.extend(pdf_docs)
            if pdf_docs:
                print(f"  ✅ Loaded {len(pdf_docs)} PDF documents")
        except Exception as e:
            print(f"  ⚠️  Warning loading PDF: {e}")
        
        # 加载 TXT
        try:
            txt_loader = DirectoryLoader(self.data_dir, glob="**/*.txt", loader_cls=TextLoader)
            txt_docs = txt_loader.load()
            documents.extend(txt_docs)
            if txt_docs:
                print(f"  ✅ Loaded {len(txt_docs)} TXT documents")
        except Exception as e:
            print(f"  ⚠️  Warning loading TXT: {e}")
        
        # 加载 MD
        try:
            md_loader = DirectoryLoader(self.data_dir, glob="**/*.md", loader_cls=TextLoader)
            md_docs = md_loader.load()
            documents.extend(md_docs)
            if md_docs:
                print(f"  ✅ Loaded {len(md_docs)} MD documents")
        except Exception as e:
            print(f"  ⚠️  Warning loading MD: {e}")
        
        # 加载 EPUB（使用 ebooklib）
        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup
            
            epub_files = glob.glob(os.path.join(self.data_dir, "**/*.epub"), recursive=True)
            epub_count = 0
            
            for epub_file in epub_files:
                try:
                    print(f"  📖 Processing EPUB: {os.path.basename(epub_file)}")
                    book = epub.read_epub(epub_file)
                    content = []
                    
                    # 提取所有文本内容
                    for item in book.get_items():
                        if item.get_type() == ebooklib.ITEM_DOCUMENT:
                            soup = BeautifulSoup(item.get_content(), 'html.parser')
                            text = soup.get_text()
                            if text.strip():
                                content.append(text.strip())
                    
                    # 合并内容并创建文档
                    if content:
                        full_text = '\n\n'.join(content)
                        doc = Document(
                            page_content=full_text,
                            metadata={"source": epub_file, "format": "epub"}
                        )
                        documents.append(doc)
                        epub_count += 1
                        print(f"  ✅ Loaded EPUB: {os.path.basename(epub_file)} ({len(full_text)} chars)")
                except Exception as e:
                    print(f"  ⚠️  Error loading {os.path.basename(epub_file)}: {e}")
            
            if epub_count > 0:
                print(f"  ✅ Total EPUB files loaded: {epub_count}")
        except ImportError:
            print(f"  ⚠️  ebooklib not installed, skipping EPUB files")
        except Exception as e:
            print(f"  ⚠️  Warning loading EPUB: {e}")
        
        if not documents:
            print("❌ No documents found.")
            return

        print(f"\n📚 Total documents loaded: {len(documents)}")

        # 文本切片
        print(f"✂️  Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_documents(documents)
        print(f"✂️  Split into {len(texts)} chunks.")

        # 存储到向量数据库
        print(f"🔄 Building vector index (this may take a few minutes)...")
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
