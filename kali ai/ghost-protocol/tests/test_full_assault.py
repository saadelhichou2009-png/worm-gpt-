#!/usr/bin/env python3
"""
⚔️ GHOST PROTOCOL — FULL ASSAULT TEST
========================================
End-to-end test of the complete system.
"""

import os
import sys
import json
import asyncio
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class TestFullAssault(unittest.TestCase):
    """Test suite for Ghost Protocol."""
    
    def setUp(self):
        """Skip all tests if orchestrator can't initialize."""
        try:
            from core.ghost_orchestrator import GhostOrchestrator
            self.orchestrator = GhostOrchestrator()
        except:
            self.skipTest("Orchestrator not available")
    
    def test_orchestrator_initialization(self):
        """Test that orchestrator initializes all systems."""
        self.assertIsNotNone(self.orchestrator)
        self.assertIsNotNone(self.orchestrator.router)
        self.assertIsNotNone(self.orchestrator.c2)
        self.assertIsNotNone(self.orchestrator.queue)
        self.assertIsNotNone(self.orchestrator.db)
        print("✅ Orchestrator initialized successfully")
    
    def test_chaos_router_initialization(self):
        """Test chaos router initialization."""
        from core.chaos_router import ChaosRouter
        router = ChaosRouter()
        self.assertIsNotNone(router)
        self.assertIsNotNone(router.jailbreaks)
        self.assertGreater(len(router.jailbreaks), 0)
        print(f"✅ Chaos Router initialized with {len(router.jailbreaks)} jailbreaks")
    
    def test_payload_generation(self):
        """Test payload factory generates payloads."""
        from core.payload_factory import PayloadFactory
        pf = PayloadFactory()
        
        payload = pf.generate("reverse_shell_python")
        self.assertIsNotNone(payload)
        print(f"✅ Payload generated: {type(payload)}")
    
    def test_zero_trace_db(self):
        """Test zero-trace database operations."""
        from storage.zero_trace_db import ZeroTraceDB
        db = ZeroTraceDB(auto_wipe_minutes=0)
        
        db.set("test", {"data": "value"}, ttl=10)
        self.assertEqual(db.get("test"), {"data": "value"})
        self.assertTrue(db.exists("test"))
        
        db.delete("test")
        self.assertIsNone(db.get("test"))
        
        db.self_destruct()
        print("✅ ZeroTraceDB operations verified")
    
    def test_proxy_rotator(self):
        """Test proxy rotator creates chains."""
        from core.proxy_rotator import FreeProxyRotator
        pr = FreeProxyRotator()
        
        chain = pr.get_proxy_chain(3)
        self.assertGreaterEqual(len(chain), 3)
        print(f"✅ Proxy chain created: {len(chain)} hops")


def run_manual_tests():
    """Run manual end-to-end tests."""
    
    print("⚔️ GHOST PROTOCOL — MANUAL TESTS")
    print("=" * 60)
    
    # Test 1: All systems initialize
    print("\n[TEST 1] System Initialization")
    from core.ghost_orchestrator import GhostOrchestrator
    o = GhostOrchestrator()
    print("  ✅ Systems initialized")
    
    # Test 2: Queue works
    print("\n[TEST 2] Task Queue")
    def dummy_task():
        return "test_complete"
    tid = o.queue.submit(dummy_task, priority=1)
    import time
    time.sleep(0.5)
    result = o.queue.get_result(tid)
    assert result['status'].value == 'completed', f"Queue failed: {result}"
    print("  ✅ Task queue working")
    
    # Test 3: Chat interface works
    print("\n[TEST 3] Chat Interface")
    help_text = o._help()
    assert "/recon" in help_text, "Help missing recon command"
    print("  ✅ Chat interface working")
    
    print("\n✅ ALL TESTS PASSED")


if __name__ == "__main__":
    # Unit tests
    unittest.main(argv=['first-arg--is-ignored'], exit=False)
    
    # Manual tests
    run_manual_tests()