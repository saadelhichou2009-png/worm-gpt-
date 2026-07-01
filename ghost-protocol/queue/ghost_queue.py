#!/usr/bin/env python3
"""
⚔️ GHOST PROTOCOL — GHOST TASK QUEUE
========================================
Multi-worker async task queue with priority and timeout.

This replaces paid services like Trigger.dev ($25/month).
50 workers execute tasks in parallel.
Tasks have priorities and automatic retry.
"""

import os
import queue
import time
import uuid
import threading
import logging
from typing import Any, Callable, Dict, Optional, List
from enum import Enum

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger("GhostQueue")

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RETRYING = "retrying"

class PrioritizedTask:
    """Wrapper for a task with priority."""
    
    def __init__(self, task_id: str, fn: Callable, args: tuple,
                 kwargs: dict, priority: int, timeout: int,
                 retries: int = 3):
        self.task_id = task_id
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.priority = priority
        self.timeout = timeout
        self.retries = retries
        self.max_retries = retries
        self.created_at = time.time()
    
    def __lt__(self, other):
        return self.priority < other.priority

class GhostTaskQueue:
    """
    Multi-worker task queue with priority scheduling.
    
    Architecture:
        Submit Task → Priority Queue → 50 Workers → Results
                      (sorted by       (parallel
                       priority)        execution)
    
    Features:
    - Up to 50 concurrent workers
    - Priority-based scheduling (0=highest, 10=lowest)
    - Automatic retry on failure (3 attempts)
    - Timeout per task (configurable)
    - Callbacks on completion
    """
    
    def __init__(self, max_workers: int = 50):
        self.task_queue = queue.PriorityQueue()
        self.results: Dict[str, Dict] = {}
        self.results_lock = threading.Lock()
        self.workers = []
        self.max_workers = max_workers
        self.running = True
        
        # Avvia worker pool
        for i in range(max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                daemon=True,
                name=f"Worker-{i}"
            )
            worker.start()
            self.workers.append(worker)
    
    def submit(self, fn: Callable, *args, priority: int = 5,
               timeout: int = 300, task_id: Optional[str] = None,
               **kwargs) -> str:
        """
        Submit a task for execution.
        
        Args:
            fn: Function to execute
            *args: Arguments to pass to function
            priority: 0 (highest) to 10 (lowest)
            timeout: Max execution time in seconds
            task_id: Optional custom ID
        
        Returns:
            task_id: ID to retrieve result later
        """
        tid = task_id or str(uuid.uuid4())[:8]
        
        task = PrioritizedTask(
            task_id=tid,
            fn=fn,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout
        )
        
        with self.results_lock:
            self.results[tid] = {
                "status": TaskStatus.PENDING,
                "result": None,
                "error": None,
                "started_at": None,
                "completed_at": None,
                "attempts": 0
            }
        
        self.task_queue.put((priority, task))
        
        return tid
    
    def _worker_loop(self):
        """Worker thread: pulls tasks from queue and executes them."""
        while self.running:
            try:
                _, task = self.task_queue.get(timeout=1)
            except queue.Empty:
                continue
            
            self._execute_task(task)
            self.task_queue.task_done()
    
    def _execute_task(self, task: PrioritizedTask):
        """Execute a single task with retry logic."""
        
        with self.results_lock:
            result = self.results[task.task_id]
            result["status"] = TaskStatus.RUNNING
            result["started_at"] = time.time()
            result["attempts"] += 1
        
        try:
            # Execute with timeout
            output = []
            error = []
            
            def target():
                try:
                    res = task.fn(*task.args, **task.kwargs)
                    output.append(res)
                except Exception as e:
                    error.append(e)
            
            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            thread.join(timeout=task.timeout)
            
            if thread.is_alive():
                # Timeout
                with self.results_lock:
                    self.results[task.task_id].update({
                        "status": TaskStatus.TIMEOUT,
                        "error": f"Timeout after {task.timeout}s"
                    })
                
                # Retry se possibile
                if task.retries > 0:
                    task.retries -= 1
                    self.task_queue.put((task.priority, task))
                return
            
            if error:
                raise error[0]
            
            # Success
            with self.results_lock:
                self.results[task.task_id].update({
                    "status": TaskStatus.COMPLETED,
                    "result": output[0] if output else None,
                    "completed_at": time.time()
                })
                
        except Exception as e:
            with self.results_lock:
                self.results[task.task_id].update({
                    "status": TaskStatus.FAILED,
                    "error": str(e),
                    "completed_at": time.time()
                })
            
            # Retry
            if task.retries > 0:
                task.retries -= 1
                self.task_queue.put((task.priority, task))
    
    def get_result(self, task_id: str, block: bool = False,
                   timeout: Optional[int] = None) -> Optional[Dict]:
        """
        Get task result.
        
        Args:
            task_id: ID from submit()
            block: Wait for completion
            timeout: Max wait time
        
        Returns:
            Result dict with status, result, error
        """
        
        with self.results_lock:
            result = self.results.get(task_id)
        
        if not result:
            return None
        
        if not block:
            return result
        
        # Wait for completion
        start = time.time()
        while result["status"] in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            time.sleep(0.1)
            
            with self.results_lock:
                result = self.results[task_id]
            
            if timeout and (time.time() - start) > timeout:
                return result
        
        return result
    
    def wait_all(self, timeout: Optional[int] = None):
        """Wait for all tasks to complete."""
        self.task_queue.join()
    
    def cancel(self, task_id: str) -> bool:
        """Cancel a pending task."""
        # Cannot easily remove from PriorityQueue
        # Mark as cancelled in results instead
        with self.results_lock:
            if task_id in self.results:
                self.results[task_id]["status"] = TaskStatus.FAILED
                self.results[task_id]["error"] = "Cancelled"
                return True
        return False
    
    def stats(self) -> Dict:
        """Get queue statistics."""
        with self.results_lock:
            statuses = {}
            for r in self.results.values():
                s = r["status"].value
                statuses[s] = statuses.get(s, 0) + 1
            
            return {
                "pending": self.task_queue.qsize(),
                "total_processed": len(self.results),
                "by_status": statuses
            }
    
    def shutdown(self):
        """Shutdown all workers."""
        self.running = False
        for w in self.workers:
            w.join(timeout=2)


if __name__ == "__main__":
    import time
    
    q = GhostTaskQueue(max_workers=10)
    
    def test_task(n):
        time.sleep(1)
        return f"Task {n} completed"
    
    print("Submitting 20 tasks...")
    ids = []
    for i in range(20):
        tid = q.submit(test_task, i, priority=i % 3)
        ids.append(tid)
    
    q.wait_all()
    
    for tid in ids:
        result = q.get_result(tid)
        print(f"  {tid}: {result['status'].value} - {result.get('result','')}")