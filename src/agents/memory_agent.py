import logging
from typing import Dict, Any, List
from datetime import datetime
import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class MemoryAgent:
    def __init__(self):
        # Initialize Chroma client and collection
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection("agent_memory")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model for embeddings
        
        # In-memory stores for quick access (synced with Chroma)
        self.conversation_memory: List[Dict[str, Any]] = []  # Full history with metadata
        self.knowledge_base: Dict[str, Dict[str, Any]] = {}  # Persistent facts by topic
        self.agent_states: Dict[str, List[Dict[str, Any]]] = {"research": [], "analysis": [], "memory": []}  # Per-agent learning

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle store/retrieve/update based on message type."""
        action = message.get("action", "store")  # e.g., "store", "retrieve", "search"
        if action == "store":
            return self._store(message)
        elif action == "retrieve":
            return self._retrieve(message)
        else:
            logger.warning(f"Unknown memory action: {action}")
            return {"error": "Invalid action"}

    def _store(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store structured record with vector embedding in Chroma."""
        content = data.get("content", "")
        if not content:
            return {"status": "error", "message": "No content to store"}

        # Generate embedding
        embedding = self.embedding_model.encode(content).tolist()

        # Structured record
        record = {
            "timestamp": datetime.now().isoformat(),
            "topics": ",".join(data.get("topics", [])),  # Convert list to string
            "source": data.get("source", "unknown"),
            "agent": data.get("agent", "unknown"),
            "confidence": data.get("confidence", 0.5),
            "content": content
        }

        # Store in Chroma with flattened metadata
        self.collection.add(
            ids=[f"record_{len(self.conversation_memory)}"],
            embeddings=[embedding],
            metadatas=[{k: str(v) if not isinstance(v, (int, float, bool)) else v for k, v in record.items()}]
        )

        # Sync with in-memory stores
        self.conversation_memory.append(record)
        topic = record["topics"].split(",")[0] if record["topics"] else "general"  # Use first topic
        self.knowledge_base[topic] = record
        self.agent_states[data.get("agent", "memory")].append({"learned": record})
        logger.info(f"Stored: {topic} with embedding")
        return {"status": "stored", "record": record}

    def _retrieve(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve by keywords/topics using vector similarity."""
        keywords = query.get("keywords", [])
        if not keywords:
            return {"results": self.conversation_memory[-3:]}  # Fallback: Last 3 records

        # Generate query embedding
        query_text = " ".join(keywords)
        query_embedding = self.embedding_model.encode(query_text).tolist()

        # Vector search in Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=3  # Top 3 similar results
        )

        # Process results with error handling
        matches = []
        if results['metadatas'] and results['metadatas'][0]:  # Check if metadatas exists and is not empty
            for idx, meta in enumerate(results['metadatas'][0]):
                record = {k: v for k, v in meta.items()}  # Flatten metadata back
                similarity = results['distances'][0][idx] if results['distances'] and results['distances'][0] else 1.0  # Default similarity if None
                matches.append({"record": record, "similarity": similarity})
        else:
            logger.warning(f"No vector matches found for {keywords}, falling back to in-memory last 3 records")
            matches = [{"record": rec, "similarity": 1.0} for rec in self.conversation_memory[-3:]]  # Fallback

        logger.info(f"Retrieved {len(matches)} matches for {keywords}")
        return {"results": matches}