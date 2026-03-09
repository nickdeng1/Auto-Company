"""
Unit Tests for Auto Company Memory System

Tests for:
- vector_store.py
- memory_retriever.py
- learning_engine.py
"""

import os
import sys
import json
import tempfile
import shutil
import unittest
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Use direct imports without relative imports
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

vector_store = load_module('vector_store', Path(__file__).parent.parent / 'vector_store.py')
memory_retriever = load_module('memory_retriever', Path(__file__).parent.parent / 'memory_retriever.py')
learning_engine = load_module('learning_engine', Path(__file__).parent.parent / 'learning_engine.py')

MemoryStore = vector_store.MemoryStore
get_memory_store = vector_store.get_memory_store
MemoryRetriever = memory_retriever.MemoryRetriever
get_retriever = memory_retriever.get_retriever
LearningEngine = learning_engine.LearningEngine
get_learning_engine = learning_engine.get_learning_engine


class TestMemoryStore(unittest.TestCase):
    """Tests for MemoryStore class"""
    
    def setUp(self):
        """Create temporary directory for tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.store = MemoryStore(self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_store_decision(self):
        """Test storing a decision"""
        memory_id = self.store.store_decision(
            decision="Launch EmailGuard as SaaS",
            outcome="success",
            reasoning="Market validation passed",
            agents_involved=["ceo-bezos", "cfo-campbell"],
            revenue_impact=500,
            project="emailguard",
            cycle=1
        )
        
        self.assertIsNotNone(memory_id)
        self.assertEqual(len(memory_id), 12)
        
        # Verify file was created
        decision_file = Path(self.temp_dir) / "decisions" / f"{memory_id}.json"
        self.assertTrue(decision_file.exists())
        
        # Verify content
        with open(decision_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['metadata']['decision'], "Launch EmailGuard as SaaS")
        self.assertEqual(data['metadata']['outcome'], "success")
    
    def test_store_mistake(self):
        """Test storing a mistake"""
        memory_id = self.store.store_mistake(
            mistake="Deployed without testing",
            lesson="Always run tests before deployment",
            prevention="Add pre-deploy test gate",
            cost=100,
            project="image-api",
            cycle=2
        )
        
        self.assertIsNotNone(memory_id)
        
        # Verify file was created
        mistake_file = Path(self.temp_dir) / "mistakes" / f"{memory_id}.json"
        self.assertTrue(mistake_file.exists())
    
    def test_store_success(self):
        """Test storing a success"""
        memory_id = self.store.store_success(
            success="First paying customer in 48 hours",
            pattern="Quick MVP + direct outreach",
            key_factors=["speed", "personal contact"],
            revenue_impact=100,
            project="emailguard",
            cycle=3
        )
        
        self.assertIsNotNone(memory_id)
        
        # Verify file was created
        success_file = Path(self.temp_dir) / "successes" / f"{memory_id}.json"
        self.assertTrue(success_file.exists())
    
    def test_store_insight(self):
        """Test storing an insight"""
        memory_id = self.store.store_insight(
            insight="Email validation market is $500M TAM",
            category="market",
            source="competitor analysis",
            confidence=0.8,
            project="emailguard",
            cycle=1
        )
        
        self.assertIsNotNone(memory_id)
        
        # Verify file was created
        insight_file = Path(self.temp_dir) / "insights" / f"{memory_id}.json"
        self.assertTrue(insight_file.exists())
    
    def test_query_similar(self):
        """Test querying similar memories"""
        # Store some memories
        self.store.store_decision(
            decision="Use FastAPI for backend",
            outcome="success",
            project="image-api",
            cycle=1
        )
        self.store.store_mistake(
            mistake="Forgot to add rate limiting",
            lesson="Always add rate limiting to public APIs",
            project="image-api",
            cycle=2
        )
        
        # Query for API-related memories
        results = self.store.query_similar("API backend", n_results=5)
        
        self.assertIsInstance(results, list)
        # In file mode, keyword matching should find results
        # Results depend on whether content matches
    
    def test_get_stats(self):
        """Test getting memory statistics"""
        # Store some memories
        self.store.store_decision("Test decision", project="test")
        self.store.store_mistake("Test mistake", "Test lesson", project="test")
        self.store.store_success("Test success", "Test pattern", project="test")
        self.store.store_insight("Test insight", "market", project="test")
        
        stats = self.store.get_stats()
        
        self.assertEqual(stats['decisions'], 1)
        self.assertEqual(stats['mistakes'], 1)
        self.assertEqual(stats['successes'], 1)
        self.assertEqual(stats['insights'], 1)
        self.assertEqual(stats['total'], 4)
    
    def test_export_all(self):
        """Test exporting all memories"""
        self.store.store_decision("Decision 1", project="test")
        self.store.store_mistake("Mistake 1", "Lesson 1", project="test")
        
        export = self.store.export_all()
        
        self.assertIn('decisions', export)
        self.assertIn('mistakes', export)
        self.assertEqual(len(export['decisions']), 1)
        self.assertEqual(len(export['mistakes']), 1)


class TestMemoryRetriever(unittest.TestCase):
    """Tests for MemoryRetriever class"""
    
    def setUp(self):
        """Create temporary directory and store"""
        self.temp_dir = tempfile.mkdtemp()
        self.store = MemoryStore(self.temp_dir)
        self.retriever = MemoryRetriever(self.store)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_build_concise_context(self):
        """Test building concise context"""
        # Store some memories
        self.store.store_mistake(
            mistake="Deployed on Friday",
            lesson="Never deploy on Friday",
            project="test"
        )
        self.store.store_success(
            success="Quick launch",
            pattern="Ship fast, iterate",
            project="test"
        )
        
        context = self.retriever.build_concise_context("deploy launch")
        
        # Should return a string (may be empty if no keyword match)
        self.assertIsInstance(context, str)
    
    def test_build_enhanced_prompt(self):
        """Test building enhanced prompt"""
        # Store some memories
        self.store.store_decision(
            decision="Use PostgreSQL for database",
            outcome="success",
            project="test"
        )
        
        prompt = self.retriever.build_enhanced_prompt(
            agent="cto-vogels",
            task="Choose database for new project",
            project="test"
        )
        
        self.assertIn("Historical Context", prompt)
    
    def test_get_project_memories(self):
        """Test getting project-specific memories"""
        # Store memories for different projects
        self.store.store_decision("Decision A", project="project-a")
        self.store.store_decision("Decision B", project="project-b")
        self.store.store_mistake("Mistake A", "Lesson", project="project-a")
        
        memories = self.retriever.get_project_memories("project-a")
        
        self.assertEqual(len(memories['decisions']), 1)
        self.assertEqual(len(memories['mistakes']), 1)
        self.assertEqual(memories['decisions'][0]['metadata']['project'], 'project-a')


class TestLearningEngine(unittest.TestCase):
    """Tests for LearningEngine class"""
    
    def setUp(self):
        """Create temporary directories"""
        self.temp_dir = tempfile.mkdtemp()
        self.logs_dir = Path(self.temp_dir) / "logs"
        self.reports_dir = Path(self.temp_dir) / "reports"
        self.logs_dir.mkdir()
        self.reports_dir.mkdir()
        
        self.store = MemoryStore(str(Path(self.temp_dir) / "vector-db"))
        self.engine = LearningEngine(
            self.store,
            str(self.logs_dir),
            str(self.reports_dir)
        )
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_learn_from_activities(self):
        """Test learning from activities"""
        activities = [
            {
                "ts": "2026-03-09T12:00:00Z",
                "cycle": 1,
                "agent": "ceo-bezos",
                "role": "CEO",
                "action": "decision",
                "input": "Product direction",
                "output": "Launch EmailGuard as SaaS",
                "file": "projects/emailguard/docs/decision.md"
            },
            {
                "ts": "2026-03-09T12:05:00Z",
                "cycle": 1,
                "agent": "devops-hightower",
                "role": "DevOps",
                "action": "deploy",
                "input": "Deploy to production",
                "output": "Deployment failed: missing token",
                "file": ""
            },
            {
                "ts": "2026-03-09T12:10:00Z",
                "cycle": 1,
                "agent": "qa-bach",
                "role": "QA",
                "action": "build",
                "input": "Run tests",
                "output": "All tests passed successfully",
                "file": "tests/"
            }
        ]
        
        learnings = self.engine.learn_from_activities(activities)
        
        # Should extract decision
        self.assertEqual(len(learnings['decisions']), 1)
        self.assertEqual(learnings['decisions'][0]['decision'], "Launch EmailGuard as SaaS")
        
        # Should extract mistake (failed deployment)
        self.assertEqual(len(learnings['mistakes']), 1)
        
        # Should extract success (tests passed)
        self.assertEqual(len(learnings['successes']), 1)
    
    def test_store_learnings(self):
        """Test storing extracted learnings"""
        learnings = {
            "decisions": [{"decision": "Test decision", "outcome": "pending"}],
            "mistakes": [{"mistake": "Test mistake", "lesson": "Test lesson"}],
            "successes": [{"success": "Test success", "pattern": "Test pattern"}],
            "insights": [{"insight": "Test insight", "category": "test"}]
        }
        
        stored_ids = self.engine.store_learnings(learnings)
        
        self.assertEqual(len(stored_ids['decisions']), 1)
        self.assertEqual(len(stored_ids['mistakes']), 1)
        self.assertEqual(len(stored_ids['successes']), 1)
        self.assertEqual(len(stored_ids['insights']), 1)
    
    def test_generate_learning_report(self):
        """Test generating learning report"""
        # Store some memories
        self.store.store_decision("Decision 1", outcome="success", project="test")
        self.store.store_mistake("Mistake 1", "Lesson 1", project="test")
        
        report = self.engine.generate_learning_report("weekly")
        
        self.assertIn("Learning Report", report)
        self.assertIn("Memory Statistics", report)
    
    def test_learn_from_consensus(self):
        """Test learning from consensus file"""
        # Create a test consensus file
        consensus_content = """# Auto Company Consensus

## What We Did This Cycle
- ✅ Deployed Image API successfully
- ❌ Failed to configure CI/CD

## Key Decisions Made
- Launch EmailGuard as $10/month SaaS
- Use FastAPI for all new projects
"""
        consensus_path = Path(self.temp_dir) / "consensus.md"
        with open(consensus_path, 'w') as f:
            f.write(consensus_content)
        
        result = self.engine.learn_from_consensus(str(consensus_path))
        
        self.assertIn('learnings', result)
        self.assertGreater(result['learnings'], 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete memory system"""
    
    def setUp(self):
        """Create temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.store = MemoryStore(str(Path(self.temp_dir) / "vector-db"))
        self.retriever = MemoryRetriever(self.store)
        self.engine = LearningEngine(
            self.store,
            str(Path(self.temp_dir) / "logs"),
            str(Path(self.temp_dir) / "reports")
        )
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_workflow(self):
        """Test complete workflow: store, retrieve, learn"""
        # 1. Store some initial memories
        self.store.store_decision(
            decision="Use ChromaDB for vector storage",
            outcome="success",
            reasoning="Better semantic search",
            agents_involved=["cto-vogels"],
            project="auto-company",
            cycle=1
        )
        
        self.store.store_mistake(
            mistake="Forgot to add error handling",
            lesson="Always add try-except blocks",
            prevention="Code review checklist",
            project="image-api",
            cycle=2
        )
        
        # 2. Retrieve relevant context
        context = self.retriever.build_concise_context("storage error handling")
        
        # 3. Learn from activities
        activities = [
            {
                "ts": "2026-03-09T12:00:00Z",
                "cycle": 3,
                "agent": "fullstack-dhh",
                "action": "build",
                "output": "Feature implemented successfully",
                "file": "projects/test/app.py"
            }
        ]
        
        learnings = self.engine.learn_from_activities(activities)
        self.engine.store_learnings(learnings)
        
        # 4. Verify stats
        stats = self.store.get_stats()
        self.assertGreater(stats['total'], 0)
        
        # 5. Generate report
        report = self.engine.generate_learning_report("weekly")
        self.assertIn("Learning Report", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)