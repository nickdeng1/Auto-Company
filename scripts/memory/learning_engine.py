"""
Learning Engine Module for Auto Company

Automatically extracts learnings from cycle logs and stores
them in the memory system for future reference.
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
import logging

try:
    from .vector_store import get_memory_store, MemoryStore
except ImportError:
    from vector_store import get_memory_store, MemoryStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LearningEngine:
    """
    Extracts learnings from cycle logs and activities.
    
    Analyzes:
    - Decisions made and their outcomes
    - Mistakes and failures
    - Success patterns
    - Insights discovered
    
    Stores them in the memory system for future reference.
    """
    
    # Patterns for extracting learnings
    DECISION_PATTERNS = [
        r'(?:decision|decided|chose|selected):\s*(.+?)(?:\n|$)',
        r'(?:GO|NO-GO|CONDITIONAL GO):\s*(.+?)(?:\n|$)',
        r'(?:approved|rejected):\s*(.+?)(?:\n|$)',
    ]
    
    MISTAKE_PATTERNS = [
        r'(?:failed|error|mistake|issue|problem|blocked):\s*(.+?)(?:\n|$)',
        r'(?:timeout|crash|exception):\s*(.+?)(?:\n|$)',
        r'(?:missing|lacking|insufficient):\s*(.+?)(?:\n|$)',
    ]
    
    SUCCESS_PATTERNS = [
        r'(?:success|completed|passed|deployed|shipped):\s*(.+?)(?:\n|$)',
        r'(?:✅|PASS|DONE):\s*(.+?)(?:\n|$)',
        r'(?:working|functional|operational):\s*(.+?)(?:\n|$)',
    ]
    
    INSIGHT_PATTERNS = [
        r'(?:insight|finding|discovery|observation):\s*(.+?)(?:\n|$)',
        r'(?:market|competitor|trend):\s*(.+?)(?:\n|$)',
        r'(?:recommendation|suggestion):\s*(.+?)(?:\n|$)',
    ]
    
    def __init__(
        self,
        memory_store: MemoryStore = None,
        logs_path: str = "./logs",
        reports_path: str = "./memories/learning-reports"
    ):
        self.store = memory_store or get_memory_store()
        self.logs_path = Path(logs_path)
        self.reports_path = Path(reports_path)
        self.reports_path.mkdir(parents=True, exist_ok=True)
    
    def _extract_patterns(
        self,
        text: str,
        patterns: List[str]
    ) -> List[str]:
        """Extract matches from text using patterns"""
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            matches.extend(found)
        return [m.strip() for m in matches if m.strip()]
    
    def _parse_activities(self, activities_path: Path) -> List[Dict[str, Any]]:
        """Parse activities.jsonl file"""
        activities = []
        if activities_path.exists():
            with open(activities_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            activities.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        return activities
    
    def _extract_cycle_number(self, log_content: str) -> int:
        """Extract cycle number from log content"""
        match = re.search(r'cycle[:\s]+(\d+)', log_content, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0
    
    def _extract_project_name(self, log_content: str) -> str:
        """Extract project name from log content"""
        # Look for project references
        patterns = [
            r'projects?[:\s]+([a-zA-Z0-9_-]+)',
            r'([a-zA-Z0-9_-]+)[:\s]+(api|service|app|project)',
        ]
        for pattern in patterns:
            match = re.search(pattern, log_content, re.IGNORECASE)
            if match:
                return match.group(1).lower()
        return ""
    
    def learn_from_cycle_log(self, log_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract learnings from a cycle log file.
        
        Args:
            log_path: Path to the cycle log file
            
        Returns:
            Dict of extracted learnings by type
        """
        log_file = Path(log_path)
        if not log_file.exists():
            logger.warning(f"Log file not found: {log_path}")
            return {"decisions": [], "mistakes": [], "successes": [], "insights": []}
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cycle = self._extract_cycle_number(content)
        project = self._extract_project_name(content)
        
        learnings = {
            "decisions": [],
            "mistakes": [],
            "successes": [],
            "insights": []
        }
        
        # Extract decisions
        for decision in self._extract_patterns(content, self.DECISION_PATTERNS):
            learnings["decisions"].append({
                "decision": decision,
                "outcome": "pending",  # Will be updated later
                "project": project,
                "cycle": cycle
            })
        
        # Extract mistakes
        for mistake in self._extract_patterns(content, self.MISTAKE_PATTERNS):
            learnings["mistakes"].append({
                "mistake": mistake,
                "lesson": "",  # To be filled manually or inferred
                "project": project,
                "cycle": cycle
            })
        
        # Extract successes
        for success in self._extract_patterns(content, self.SUCCESS_PATTERNS):
            learnings["successes"].append({
                "success": success,
                "pattern": "",  # To be filled
                "project": project,
                "cycle": cycle
            })
        
        # Extract insights
        for insight in self._extract_patterns(content, self.INSIGHT_PATTERNS):
            learnings["insights"].append({
                "insight": insight,
                "category": "general",
                "project": project,
                "cycle": cycle
            })
        
        return learnings
    
    def learn_from_activities(
        self,
        activities: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract learnings from activities list.
        
        Args:
            activities: List of activity records
            
        Returns:
            Dict of extracted learnings by type
        """
        learnings = {
            "decisions": [],
            "mistakes": [],
            "successes": [],
            "insights": []
        }
        
        for activity in activities:
            action = activity.get("action", "")
            output = activity.get("output", "")
            agent = activity.get("agent", "")
            cycle = activity.get("cycle", 0)
            file_path = activity.get("file", "")
            
            # Extract project from file path
            project = ""
            if file_path:
                parts = file_path.split("/")
                if "projects" in parts:
                    idx = parts.index("projects")
                    if idx + 1 < len(parts):
                        project = parts[idx + 1]
            
            # Decision actions
            if action == "decision":
                learnings["decisions"].append({
                    "decision": output,
                    "agents_involved": [agent],
                    "project": project,
                    "cycle": cycle
                })
            
            # Build/deploy failures
            elif action in ["build", "deploy"] and ("fail" in output.lower() or "error" in output.lower()):
                learnings["mistakes"].append({
                    "mistake": output,
                    "lesson": "",
                    "project": project,
                    "cycle": cycle
                })
            
            # Successful builds/deployments
            elif action in ["build", "deploy"] and ("success" in output.lower() or "pass" in output.lower()):
                learnings["successes"].append({
                    "success": output,
                    "pattern": "",
                    "project": project,
                    "cycle": cycle
                })
            
            # Analysis results as insights
            elif action == "analyze" and output:
                learnings["insights"].append({
                    "insight": output,
                    "category": "analysis",
                    "project": project,
                    "cycle": cycle
                })
        
        return learnings
    
    def store_learnings(
        self,
        learnings: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, List[str]]:
        """
        Store extracted learnings in memory store.
        
        Args:
            learnings: Dict of learnings by type
            
        Returns:
            Dict of stored memory IDs by type
        """
        stored_ids = {
            "decisions": [],
            "mistakes": [],
            "successes": [],
            "insights": []
        }
        
        # Store decisions
        for item in learnings.get("decisions", []):
            memory_id = self.store.store_decision(
                decision=item.get("decision", ""),
                outcome=item.get("outcome", "pending"),
                reasoning=item.get("reasoning", ""),
                agents_involved=item.get("agents_involved", []),
                revenue_impact=item.get("revenue_impact", 0),
                project=item.get("project", ""),
                cycle=item.get("cycle", 0)
            )
            stored_ids["decisions"].append(memory_id)
        
        # Store mistakes
        for item in learnings.get("mistakes", []):
            memory_id = self.store.store_mistake(
                mistake=item.get("mistake", ""),
                lesson=item.get("lesson", "To be determined"),
                prevention=item.get("prevention", ""),
                cost=item.get("cost", 0),
                project=item.get("project", ""),
                cycle=item.get("cycle", 0)
            )
            stored_ids["mistakes"].append(memory_id)
        
        # Store successes
        for item in learnings.get("successes", []):
            memory_id = self.store.store_success(
                success=item.get("success", ""),
                pattern=item.get("pattern", "To be documented"),
                key_factors=item.get("key_factors", []),
                revenue_impact=item.get("revenue_impact", 0),
                project=item.get("project", ""),
                cycle=item.get("cycle", 0)
            )
            stored_ids["successes"].append(memory_id)
        
        # Store insights
        for item in learnings.get("insights", []):
            memory_id = self.store.store_insight(
                insight=item.get("insight", ""),
                category=item.get("category", "general"),
                source=item.get("source", ""),
                confidence=item.get("confidence", 0.5),
                project=item.get("project", ""),
                cycle=item.get("cycle", 0)
            )
            stored_ids["insights"].append(memory_id)
        
        return stored_ids
    
    def process_cycle(
        self,
        log_path: str = None,
        activities_path: str = None
    ) -> Dict[str, Any]:
        """
        Process a complete cycle and extract all learnings.
        
        Args:
            log_path: Path to cycle log file
            activities_path: Path to activities.jsonl
            
        Returns:
            Summary of processed learnings
        """
        all_learnings = {
            "decisions": [],
            "mistakes": [],
            "successes": [],
            "insights": []
        }
        
        # Learn from log file
        if log_path:
            log_learnings = self.learn_from_cycle_log(log_path)
            for key in all_learnings:
                all_learnings[key].extend(log_learnings.get(key, []))
        
        # Learn from activities
        if activities_path:
            activities = self._parse_activities(Path(activities_path))
            activity_learnings = self.learn_from_activities(activities)
            for key in all_learnings:
                all_learnings[key].extend(activity_learnings.get(key, []))
        
        # Store all learnings
        stored_ids = self.store_learnings(all_learnings)
        
        # Generate summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "learnings_extracted": {
                k: len(v) for k, v in all_learnings.items()
            },
            "memories_stored": {
                k: len(v) for k, v in stored_ids.items()
            },
            "memory_ids": stored_ids
        }
        
        logger.info(f"Processed cycle: {summary['learnings_extracted']}")
        return summary
    
    def generate_learning_report(
        self,
        period: str = "weekly",
        output_path: str = None
    ) -> str:
        """
        Generate a learning report for a period.
        
        Args:
            period: "weekly" or "monthly"
            output_path: Optional output file path
            
        Returns:
            Report content as markdown string
        """
        stats = self.store.get_stats()
        
        # Get recent memories
        recent_decisions = self.store._list_entries("decisions")[:10]
        recent_mistakes = self.store._list_entries("mistakes")[:10]
        recent_successes = self.store._list_entries("successes")[:10]
        recent_insights = self.store._list_entries("insights")[:10]
        
        # Build report
        lines = [
            f"# Auto Company Learning Report ({period.title()})",
            f"",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"",
            "## 📊 Memory Statistics",
            f"",
            f"| Type | Count |",
            f"|------|-------|",
        ]
        
        for mem_type, count in stats.items():
            if mem_type != 'chroma_enabled':
                lines.append(f"| {mem_type.title()} | {count} |")
        
        # Recent decisions
        if recent_decisions:
            lines.extend([
                "",
                "## 📋 Recent Decisions",
                ""
            ])
            for entry in recent_decisions[:5]:
                meta = entry.metadata
                outcome = meta.get('outcome', 'pending')
                emoji = '✅' if outcome == 'success' else '❌' if outcome == 'failure' else '⏳'
                lines.append(f"- {emoji} **{meta.get('decision', 'N/A')[:80]}**")
                lines.append(f"  - Outcome: {outcome}")
                lines.append(f"  - Project: {meta.get('project', 'N/A')}")
        
        # Recent mistakes
        if recent_mistakes:
            lines.extend([
                "",
                "## ⚠️ Recent Mistakes & Lessons",
                ""
            ])
            for entry in recent_mistakes[:5]:
                meta = entry.metadata
                lines.append(f"- **{meta.get('mistake', 'N/A')[:80]}**")
                lines.append(f"  - Lesson: {meta.get('lesson', 'N/A')}")
                lines.append(f"  - Prevention: {meta.get('prevention', 'N/A')}")
        
        # Recent successes
        if recent_successes:
            lines.extend([
                "",
                "## ✅ Recent Successes",
                ""
            ])
            for entry in recent_successes[:5]:
                meta = entry.metadata
                lines.append(f"- **{meta.get('success', 'N/A')[:80]}**")
                lines.append(f"  - Pattern: {meta.get('pattern', 'N/A')}")
        
        # Recent insights
        if recent_insights:
            lines.extend([
                "",
                "## 💡 Recent Insights",
                ""
            ])
            for entry in recent_insights[:5]:
                meta = entry.metadata
                lines.append(f"- **[{meta.get('category', 'general').title()}]** {meta.get('insight', 'N/A')[:80]}")
        
        report = "\n".join(lines)
        
        # Save report
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to {output_path}")
        
        return report
    
    def learn_from_consensus(self, consensus_path: str = "./memories/consensus.md") -> Dict[str, Any]:
        """
        Extract learnings from the consensus file.
        
        Args:
            consensus_path: Path to consensus.md
            
        Returns:
            Summary of extracted learnings
        """
        consensus_file = Path(consensus_path)
        if not consensus_file.exists():
            logger.warning(f"Consensus file not found: {consensus_path}")
            return {"learnings": 0}
        
        with open(consensus_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        learnings = {
            "decisions": [],
            "mistakes": [],
            "successes": [],
            "insights": []
        }
        
        # Extract from "Key Decisions Made" section
        decisions_match = re.search(r'## Key Decisions Made\n(.+?)(?:\n##|\Z)', content, re.DOTALL)
        if decisions_match:
            decisions_text = decisions_match.group(1)
            for line in decisions_text.split('\n'):
                if line.strip().startswith('-') or line.strip().startswith('|'):
                    decision = re.sub(r'^[-|]\s*', '', line).strip()
                    if decision and not decision.startswith('Decision'):
                        learnings["decisions"].append({
                            "decision": decision,
                            "outcome": "pending"
                        })
        
        # Extract from "What We Did This Cycle" section
        actions_match = re.search(r'## What We Did This Cycle\n(.+?)(?:\n##|\Z)', content, re.DOTALL)
        if actions_match:
            actions_text = actions_match.group(1)
            
            # Look for successes (✅)
            for match in re.finditer(r'✅\s*(.+?)(?:\n|$)', actions_text):
                learnings["successes"].append({
                    "success": match.group(1).strip(),
                    "pattern": ""
                })
            
            # Look for failures (❌)
            for match in re.finditer(r'❌\s*(.+?)(?:\n|$)', actions_text):
                learnings["mistakes"].append({
                    "mistake": match.group(1).strip(),
                    "lesson": ""
                })
        
        # Store learnings
        stored_ids = self.store_learnings(learnings)
        
        return {
            "learnings": sum(len(v) for v in learnings.values()),
            "stored": {k: len(v) for k, v in stored_ids.items()}
        }


# Singleton instance
_engine_instance: Optional[LearningEngine] = None


def get_learning_engine(
    memory_store: MemoryStore = None,
    logs_path: str = None,
    reports_path: str = None
) -> LearningEngine:
    """Get or create the learning engine singleton"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = LearningEngine(
            memory_store,
            logs_path or os.environ.get('LOGS_PATH', './logs'),
            reports_path or os.environ.get('MEMORY_LEARNING_REPORTS_PATH', './memories/learning-reports')
        )
    return _engine_instance


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Learning Engine CLI")
    parser.add_argument("command", choices=["process", "report", "consensus"])
    parser.add_argument("--log", help="Cycle log file path")
    parser.add_argument("--activities", help="Activities.jsonl path")
    parser.add_argument("--period", choices=["weekly", "monthly"], default="weekly")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    engine = get_learning_engine()
    
    if args.command == "process":
        result = engine.process_cycle(args.log, args.activities)
        print(json.dumps(result, indent=2))
    
    elif args.command == "report":
        output = args.output or f"./memories/learning-reports/{args.period}/report-{datetime.now().strftime('%Y%m%d')}.md"
        report = engine.generate_learning_report(args.period, output)
        print(f"Report generated: {output}")
        print(report[:500] + "..." if len(report) > 500 else report)
    
    elif args.command == "consensus":
        result = engine.learn_from_consensus()
        print(json.dumps(result, indent=2))