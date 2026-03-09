"""
Memory Retriever Module for Auto Company

Builds enhanced prompts for agents by injecting relevant
historical experiences from the memory store.
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path
import logging

try:
    from .vector_store import get_memory_store, MemoryStore
except ImportError:
    from vector_store import get_memory_store, MemoryStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryRetriever:
    """
    Retrieves relevant memories and builds enhanced prompts.
    
    Injects historical context into agent prompts to improve
    decision quality and avoid repeating past mistakes.
    """
    
    def __init__(self, memory_store: MemoryStore = None):
        self.store = memory_store or get_memory_store()
        self.max_memories_per_type = 3
        self.max_total_length = 2000  # Characters
    
    def _format_memory_for_prompt(self, memory: Dict[str, Any]) -> str:
        """Format a single memory for inclusion in prompt"""
        mem_type = memory.get('type', 'unknown')
        metadata = memory.get('metadata', {})
        
        if mem_type == 'mistakes':
            return f"⚠️ Past Mistake: {metadata.get('mistake', 'N/A')}\n   Lesson: {metadata.get('lesson', 'N/A')}"
        
        elif mem_type == 'successes':
            return f"✅ Past Success: {metadata.get('success', 'N/A')}\n   Pattern: {metadata.get('pattern', 'N/A')}"
        
        elif mem_type == 'decisions':
            outcome = metadata.get('outcome', 'pending')
            outcome_emoji = '✅' if outcome == 'success' else '❌' if outcome == 'failure' else '⏳'
            return f"{outcome_emoji} Past Decision: {metadata.get('decision', 'N/A')}\n   Outcome: {outcome}"
        
        elif mem_type == 'insights':
            return f"💡 Insight ({metadata.get('category', 'general')}): {metadata.get('insight', 'N/A')}"
        
        return f"📝 {memory.get('content', 'N/A')[:100]}"
    
    def _truncate_memories(self, memories: List[str], max_length: int) -> List[str]:
        """Truncate memory list to fit within length limit"""
        result = []
        total_length = 0
        
        for mem in memories:
            if total_length + len(mem) <= max_length:
                result.append(mem)
                total_length += len(mem)
            else:
                break
        
        return result
    
    def build_enhanced_prompt(
        self,
        agent: str,
        task: str,
        current_context: Dict[str, Any] = None,
        include_mistakes: bool = True,
        include_successes: bool = True,
        include_decisions: bool = True,
        include_insights: bool = True,
        project: str = None
    ) -> str:
        """
        Build an enhanced prompt with relevant historical context.
        
        Args:
            agent: Agent ID (e.g., 'ceo-bezos')
            task: Task description
            current_context: Current situation context
            include_mistakes: Include past mistakes
            include_successes: Include past successes
            include_decisions: Include past decisions
            include_insights: Include insights
            project: Filter by project
            
        Returns:
            Enhanced prompt string with historical context
        """
        # Build search query from task and context
        query_parts = [task]
        if current_context:
            for key, value in current_context.items():
                if isinstance(value, str):
                    query_parts.append(value)
                elif isinstance(value, list):
                    query_parts.extend(str(v) for v in value[:3])
        
        query = " ".join(query_parts)
        
        # Retrieve relevant memories
        relevant = self.store.get_relevant_experience(
            query,
            include_mistakes=include_mistakes,
            include_successes=include_successes,
            include_decisions=include_decisions,
            n_results=self.max_memories_per_type
        )
        
        # Add insights
        if include_insights:
            relevant['insights'] = self.store.query_similar(
                query, "insights", self.max_memories_per_type, project
            )
        
        # Build enhanced prompt
        sections = []
        
        # Header
        sections.append("## 📚 Relevant Historical Context\n")
        sections.append(f"*Retrieved for {agent}'s task: {task[:50]}...*\n")
        
        # Mistakes to avoid
        if relevant.get('mistakes'):
            sections.append("\n### ⚠️ Mistakes to Avoid\n")
            for mem in relevant['mistakes'][:self.max_memories_per_type]:
                sections.append(f"- {self._format_memory_for_prompt(mem)}\n")
        
        # Successes to replicate
        if relevant.get('successes'):
            sections.append("\n### ✅ Success Patterns to Replicate\n")
            for mem in relevant['successes'][:self.max_memories_per_type]:
                sections.append(f"- {self._format_memory_for_prompt(mem)}\n")
        
        # Past decisions
        if relevant.get('decisions'):
            sections.append("\n### 📋 Related Past Decisions\n")
            for mem in relevant['decisions'][:self.max_memories_per_type]:
                sections.append(f"- {self._format_memory_for_prompt(mem)}\n")
        
        # Insights
        if relevant.get('insights'):
            sections.append("\n### 💡 Relevant Insights\n")
            for mem in relevant['insights'][:self.max_memories_per_type]:
                sections.append(f"- {self._format_memory_for_prompt(mem)}\n")
        
        # Combine and truncate if needed
        enhanced = "".join(sections)
        
        if len(enhanced) > self.max_total_length:
            enhanced = enhanced[:self.max_total_length] + "\n... (truncated)"
        
        return enhanced
    
    def build_concise_context(
        self,
        task: str,
        project: str = None
    ) -> str:
        """
        Build a concise context string for quick reference.
        
        Args:
            task: Task description
            project: Filter by project
            
        Returns:
            Concise context string
        """
        relevant = self.store.get_relevant_experience(
            task,
            include_mistakes=True,
            include_successes=True,
            include_decisions=False,
            n_results=2
        )
        
        lines = []
        
        if relevant.get('mistakes'):
            for mem in relevant['mistakes'][:2]:
                meta = mem.get('metadata', {})
                lines.append(f"⚠️ Avoid: {meta.get('mistake', '')[:50]}")
        
        if relevant.get('successes'):
            for mem in relevant['successes'][:2]:
                meta = mem.get('metadata', {})
                lines.append(f"✅ Pattern: {meta.get('pattern', '')[:50]}")
        
        return "\n".join(lines) if lines else ""
    
    def get_agent_specific_memories(
        self,
        agent: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get memories specifically involving an agent.
        
        Args:
            agent: Agent ID
            limit: Maximum results
            
        Returns:
            List of memories involving this agent
        """
        results = []
        
        for mem_type in ['decisions', 'mistakes', 'successes']:
            for entry in self.store._list_entries(mem_type):
                metadata = entry.metadata
                if agent in metadata.get('agents_involved', []):
                    results.append(entry.to_dict())
                    if len(results) >= limit:
                        return results
        
        return results
    
    def get_project_memories(
        self,
        project: str,
        limit: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all memories for a specific project.
        
        Args:
            project: Project name
            limit: Maximum results per type
            
        Returns:
            Dict of memories by type
        """
        results = {}
        
        for mem_type in ['decisions', 'mistakes', 'successes', 'insights']:
            memories = []
            for entry in self.store._list_entries(mem_type):
                if entry.metadata.get('project') == project:
                    memories.append(entry.to_dict())
                    if len(memories) >= limit:
                        break
            results[mem_type] = memories
        
        return results


# Singleton instance
_retriever_instance: Optional[MemoryRetriever] = None


def get_retriever(memory_store: MemoryStore = None) -> MemoryRetriever:
    """Get or create the memory retriever singleton"""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = MemoryRetriever(memory_store)
    return _retriever_instance


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory Retriever CLI")
    parser.add_argument("command", choices=["context", "agent", "project"])
    parser.add_argument("--task", help="Task description")
    parser.add_argument("--agent", help="Agent ID")
    parser.add_argument("--project", help="Project name")
    
    args = parser.parse_args()
    
    retriever = get_retriever()
    
    if args.command == "context":
        if not args.task:
            print("Error: --task required for context command")
            exit(1)
        context = retriever.build_concise_context(args.task, args.project)
        print(context or "No relevant context found")
    
    elif args.command == "agent":
        if not args.agent:
            print("Error: --agent required for agent command")
            exit(1)
        memories = retriever.get_agent_specific_memories(args.agent)
        print(json.dumps(memories, indent=2, ensure_ascii=False))
    
    elif args.command == "project":
        if not args.project:
            print("Error: --project required for project command")
            exit(1)
        memories = retriever.get_project_memories(args.project)
        print(json.dumps(memories, indent=2, ensure_ascii=False))