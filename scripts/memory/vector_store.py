"""
Vector Store Module for Auto Company Memory System

Provides persistent storage and semantic search for:
- Decisions (with outcomes)
- Mistakes (with lessons learned)
- Successes (with patterns)
- Insights (market/technical knowledge)

Uses file-based storage with optional ChromaDB upgrade path.
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Memory types
MEMORY_TYPES = ['decisions', 'mistakes', 'successes', 'insights']


@dataclass
class MemoryEntry:
    """Base memory entry structure"""
    id: str
    type: str
    content: str
    timestamp: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        return cls(**data)


class MemoryStore:
    """
    Persistent memory store with semantic search capability.
    
    Uses file-based JSON storage by default, with optional ChromaDB
    backend for enhanced semantic search when available.
    """
    
    def __init__(self, base_path: str = "./memories/vector-db"):
        self.base_path = Path(base_path)
        self._ensure_directories()
        self._chroma_client = None
        self._embedding_model = None
        self._use_chroma = False
        
        # Try to initialize ChromaDB (optional)
        self._try_init_chroma()
    
    def _ensure_directories(self):
        """Create necessary directories"""
        for mem_type in MEMORY_TYPES:
            (self.base_path / mem_type).mkdir(parents=True, exist_ok=True)
    
    def _try_init_chroma(self):
        """Try to initialize ChromaDB backend (optional enhancement)"""
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            
            # Initialize ChromaDB
            chroma_path = self.base_path / "chroma"
            self._chroma_client = chromadb.PersistentClient(path=str(chroma_path))
            
            # Initialize embedding model
            self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Create collections for each memory type
            for mem_type in MEMORY_TYPES:
                self._chroma_client.get_or_create_collection(name=mem_type)
            
            self._use_chroma = True
            logger.info("ChromaDB backend initialized successfully")
            
        except ImportError:
            logger.info("ChromaDB not available, using file-based storage")
            self._use_chroma = False
        except Exception as e:
            logger.warning(f"ChromaDB initialization failed: {e}, using file-based storage")
            self._use_chroma = False
    
    def _generate_id(self, content: str, mem_type: str) -> str:
        """Generate unique ID for memory entry"""
        hash_input = f"{mem_type}:{content}:{datetime.now().isoformat()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text (if ChromaDB available)"""
        if self._embedding_model:
            try:
                return self._embedding_model.encode(text).tolist()
            except Exception as e:
                logger.warning(f"Embedding generation failed: {e}")
        return None
    
    def _save_to_file(self, entry: MemoryEntry):
        """Save memory entry to JSON file"""
        file_path = self.base_path / entry.type / f"{entry.id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(entry.to_dict(), f, indent=2, ensure_ascii=False)
    
    def _load_from_file(self, mem_type: str, entry_id: str) -> Optional[MemoryEntry]:
        """Load memory entry from JSON file"""
        file_path = self.base_path / mem_type / f"{entry_id}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return MemoryEntry.from_dict(json.load(f))
        return None
    
    def _list_entries(self, mem_type: str) -> List[MemoryEntry]:
        """List all entries of a memory type"""
        entries = []
        type_path = self.base_path / mem_type
        for file_path in type_path.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    entries.append(MemoryEntry.from_dict(json.load(f)))
            except Exception as e:
                logger.warning(f"Failed to load {file_path}: {e}")
        return sorted(entries, key=lambda x: x.timestamp, reverse=True)
    
    # ==================== Public API ====================
    
    def store_decision(
        self,
        decision: str,
        outcome: str = "pending",
        reasoning: str = "",
        agents_involved: List[str] = None,
        revenue_impact: float = 0,
        project: str = "",
        cycle: int = 0
    ) -> str:
        """
        Store a decision with its context.
        
        Args:
            decision: The decision made
            outcome: "success", "failure", or "pending"
            reasoning: Why this decision was made
            agents_involved: List of agent IDs involved
            revenue_impact: Revenue impact (positive or negative)
            project: Associated project name
            cycle: Cycle number when decision was made
            
        Returns:
            Memory entry ID
        """
        entry_id = self._generate_id(decision, "decisions")
        content = f"Decision: {decision}\nReasoning: {reasoning}\nOutcome: {outcome}"
        
        entry = MemoryEntry(
            id=entry_id,
            type="decisions",
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata={
                "decision": decision,
                "outcome": outcome,
                "reasoning": reasoning,
                "agents_involved": agents_involved or [],
                "revenue_impact": revenue_impact,
                "project": project,
                "cycle": cycle
            },
            embedding=self._get_embedding(content)
        )
        
        self._save_to_file(entry)
        
        # Also store in ChromaDB if available
        if self._use_chroma:
            try:
                collection = self._chroma_client.get_collection("decisions")
                collection.add(
                    ids=[entry_id],
                    documents=[content],
                    metadatas=[entry.metadata],
                    embeddings=[entry.embedding] if entry.embedding else None
                )
            except Exception as e:
                logger.warning(f"ChromaDB storage failed: {e}")
        
        logger.info(f"Stored decision: {entry_id}")
        return entry_id
    
    def store_mistake(
        self,
        mistake: str,
        lesson: str,
        prevention: str = "",
        cost: float = 0,
        project: str = "",
        cycle: int = 0
    ) -> str:
        """
        Store a mistake with lessons learned.
        
        Args:
            mistake: What went wrong
            lesson: What was learned
            prevention: How to prevent in future
            cost: Cost of the mistake (time/money)
            project: Associated project name
            cycle: Cycle number when mistake occurred
            
        Returns:
            Memory entry ID
        """
        entry_id = self._generate_id(mistake, "mistakes")
        content = f"Mistake: {mistake}\nLesson: {lesson}\nPrevention: {prevention}"
        
        entry = MemoryEntry(
            id=entry_id,
            type="mistakes",
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata={
                "mistake": mistake,
                "lesson": lesson,
                "prevention": prevention,
                "cost": cost,
                "project": project,
                "cycle": cycle
            },
            embedding=self._get_embedding(content)
        )
        
        self._save_to_file(entry)
        
        if self._use_chroma:
            try:
                collection = self._chroma_client.get_collection("mistakes")
                collection.add(
                    ids=[entry_id],
                    documents=[content],
                    metadatas=[entry.metadata],
                    embeddings=[entry.embedding] if entry.embedding else None
                )
            except Exception as e:
                logger.warning(f"ChromaDB storage failed: {e}")
        
        logger.info(f"Stored mistake: {entry_id}")
        return entry_id
    
    def store_success(
        self,
        success: str,
        pattern: str,
        key_factors: List[str] = None,
        revenue_impact: float = 0,
        project: str = "",
        cycle: int = 0
    ) -> str:
        """
        Store a success with its pattern.
        
        Args:
            success: What succeeded
            pattern: The pattern that led to success
            key_factors: Key factors that contributed
            revenue_impact: Revenue impact
            project: Associated project name
            cycle: Cycle number when success occurred
            
        Returns:
            Memory entry ID
        """
        entry_id = self._generate_id(success, "successes")
        content = f"Success: {success}\nPattern: {pattern}\nKey Factors: {', '.join(key_factors or [])}"
        
        entry = MemoryEntry(
            id=entry_id,
            type="successes",
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata={
                "success": success,
                "pattern": pattern,
                "key_factors": key_factors or [],
                "revenue_impact": revenue_impact,
                "project": project,
                "cycle": cycle
            },
            embedding=self._get_embedding(content)
        )
        
        self._save_to_file(entry)
        
        if self._use_chroma:
            try:
                collection = self._chroma_client.get_collection("successes")
                collection.add(
                    ids=[entry_id],
                    documents=[content],
                    metadatas=[entry.metadata],
                    embeddings=[entry.embedding] if entry.embedding else None
                )
            except Exception as e:
                logger.warning(f"ChromaDB storage failed: {e}")
        
        logger.info(f"Stored success: {entry_id}")
        return entry_id
    
    def store_insight(
        self,
        insight: str,
        category: str,
        source: str = "",
        confidence: float = 0.5,
        project: str = "",
        cycle: int = 0
    ) -> str:
        """
        Store an insight (market/technical knowledge).
        
        Args:
            insight: The insight content
            category: "market", "technical", "product", "business"
            source: Where this insight came from
            confidence: Confidence level (0-1)
            project: Associated project name
            cycle: Cycle number when insight was discovered
            
        Returns:
            Memory entry ID
        """
        entry_id = self._generate_id(insight, "insights")
        content = f"Insight: {insight}\nCategory: {category}\nSource: {source}"
        
        entry = MemoryEntry(
            id=entry_id,
            type="insights",
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata={
                "insight": insight,
                "category": category,
                "source": source,
                "confidence": confidence,
                "project": project,
                "cycle": cycle
            },
            embedding=self._get_embedding(content)
        )
        
        self._save_to_file(entry)
        
        if self._use_chroma:
            try:
                collection = self._chroma_client.get_collection("insights")
                collection.add(
                    ids=[entry_id],
                    documents=[content],
                    metadatas=[entry.metadata],
                    embeddings=[entry.embedding] if entry.embedding else None
                )
            except Exception as e:
                logger.warning(f"ChromaDB storage failed: {e}")
        
        logger.info(f"Stored insight: {entry_id}")
        return entry_id
    
    def query_similar(
        self,
        query: str,
        memory_type: str = None,
        n_results: int = 5,
        project: str = None
    ) -> List[Dict[str, Any]]:
        """
        Query for similar memories.
        
        Args:
            query: Search query
            memory_type: Filter by type (decisions/mistakes/successes/insights)
            n_results: Maximum number of results
            project: Filter by project
            
        Returns:
            List of matching memory entries with similarity scores
        """
        results = []
        
        # Use ChromaDB for semantic search if available
        if self._use_chroma and self._embedding_model:
            query_embedding = self._embedding_model.encode(query).tolist()
            
            types_to_search = [memory_type] if memory_type else MEMORY_TYPES
            
            for mem_type in types_to_search:
                try:
                    collection = self._chroma_client.get_collection(mem_type)
                    where_filter = None
                    if project:
                        where_filter = {"project": project}
                    
                    search_results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=n_results,
                        where=where_filter
                    )
                    
                    for i, doc in enumerate(search_results['documents'][0]):
                        results.append({
                            "id": search_results['ids'][0][i],
                            "type": mem_type,
                            "content": doc,
                            "metadata": search_results['metadatas'][0][i],
                            "distance": search_results['distances'][0][i] if 'distances' in search_results else 0
                        })
                except Exception as e:
                    logger.warning(f"ChromaDB query failed for {mem_type}: {e}")
        
        # Fallback to keyword search
        if not results:
            types_to_search = [memory_type] if memory_type else MEMORY_TYPES
            query_lower = query.lower()
            
            for mem_type in types_to_search:
                for entry in self._list_entries(mem_type):
                    if project and entry.metadata.get("project") != project:
                        continue
                    
                    # Simple keyword matching
                    if query_lower in entry.content.lower():
                        results.append({
                            "id": entry.id,
                            "type": entry.type,
                            "content": entry.content,
                            "metadata": entry.metadata,
                            "distance": 0  # No semantic distance in file mode
                        })
                        
                        if len(results) >= n_results:
                            break
                
                if len(results) >= n_results:
                    break
        
        return results[:n_results]
    
    def get_relevant_experience(
        self,
        current_situation: str,
        include_mistakes: bool = True,
        include_successes: bool = True,
        include_decisions: bool = True,
        n_results: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get relevant past experiences for a situation.
        
        Args:
            current_situation: Description of current situation
            include_mistakes: Include past mistakes
            include_successes: Include past successes
            include_decisions: Include past decisions
            n_results: Max results per category
            
        Returns:
            Dict with categorized relevant experiences
        """
        results = {}
        
        if include_mistakes:
            results['mistakes'] = self.query_similar(
                current_situation, "mistakes", n_results
            )
        
        if include_successes:
            results['successes'] = self.query_similar(
                current_situation, "successes", n_results
            )
        
        if include_decisions:
            results['decisions'] = self.query_similar(
                current_situation, "decisions", n_results
            )
        
        return results
    
    def get_stats(self) -> Dict[str, int]:
        """Get memory statistics"""
        stats = {}
        for mem_type in MEMORY_TYPES:
            stats[mem_type] = len(self._list_entries(mem_type))
        stats['total'] = sum(stats.values())
        stats['chroma_enabled'] = self._use_chroma
        return stats
    
    def export_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Export all memories for backup"""
        export = {}
        for mem_type in MEMORY_TYPES:
            export[mem_type] = [e.to_dict() for e in self._list_entries(mem_type)]
        return export


# Singleton instance
_store_instance: Optional[MemoryStore] = None


def get_memory_store(base_path: str = None) -> MemoryStore:
    """Get or create the memory store singleton"""
    global _store_instance
    if _store_instance is None:
        _store_instance = MemoryStore(base_path or os.environ.get(
            'MEMORY_VECTOR_DB_PATH', 
            './memories/vector-db'
        ))
    return _store_instance


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory Store CLI")
    parser.add_argument("command", choices=["stats", "export", "query"])
    parser.add_argument("--type", choices=MEMORY_TYPES, help="Memory type filter")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--n", type=int, default=5, help="Number of results")
    
    args = parser.parse_args()
    
    store = get_memory_store()
    
    if args.command == "stats":
        stats = store.get_stats()
        print(json.dumps(stats, indent=2))
    
    elif args.command == "export":
        export = store.export_all()
        print(json.dumps(export, indent=2, ensure_ascii=False))
    
    elif args.command == "query":
        if not args.query:
            print("Error: --query required for query command")
            exit(1)
        results = store.query_similar(args.query, args.type, args.n)
        print(json.dumps(results, indent=2, ensure_ascii=False))