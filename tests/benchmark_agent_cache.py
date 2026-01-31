"""
Performance benchmarks for Agent Context Caching System.

Tests cache lookup, hash calculation, queries under load.
Targets from TR.md FR-18:
- Cache lookup: < 50ms p95
- Hash calculation: < 100ms for 1MB file
- Agent metrics query: < 500ms
- Checklist progress query: < 100ms

Zero external dependencies - uses only Python standard library.
"""

import time
import tempfile
import os
from pathlib import Path
import sys
import statistics

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.project_database import ProjectDatabase


def setup_database():
    """Create temp database with schema applied."""
    temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
    temp_db.close()
    db = ProjectDatabase(temp_db.name)

    # Setup schema
    db.conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    db.conn.execute("""
        CREATE TABLE IF NOT EXISTS phase_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phase_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    """)
    db.conn.execute("""
        CREATE TABLE IF NOT EXISTS task_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phase_run_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    """)
    db.conn.commit()

    migration_path = Path(__file__).parent.parent / 'migrations' / '006_agent_context_cache.sql'
    with open(migration_path, 'r') as f:
        db.conn.executescript(f.read())
    db.conn.commit()

    return db, temp_db.name


def benchmark_hash_calculation():
    """Benchmark hash calculation for 1MB file (target: < 100ms)."""
    print("\n=== Benchmark: Hash Calculation (1MB file) ===")
    print("Target: < 100ms")

    db, db_path = setup_database()

    # Create 1MB content
    content = "A" * (1024 * 1024)  # 1MB

    # Warm-up
    db.calculate_file_hash(content)

    # Benchmark
    times = []
    for i in range(100):
        start = time.time()
        db.calculate_file_hash(content)
        end = time.time()
        times.append((end - start) * 1000)  # Convert to ms

    db.close()
    os.unlink(db_path)

    avg_time = statistics.mean(times)
    p95_time = sorted(times)[int(len(times) * 0.95)]
    p99_time = sorted(times)[int(len(times) * 0.99)]

    print(f"  Avg: {avg_time:.2f}ms")
    print(f"  P95: {p95_time:.2f}ms")
    print(f"  P99: {p99_time:.2f}ms")
    print(f"  Status: {'✅ PASS' if p95_time < 100 else '❌ FAIL'}")

    return p95_time < 100


def benchmark_cache_lookup():
    """Benchmark cache lookup (target: < 50ms p95)."""
    print("\n=== Benchmark: Cache Lookup ===")
    print("Target: < 50ms p95")

    db, db_path = setup_database()

    # Setup: Cache 1000 files
    print("  Setting up 1000 cached files...")
    for i in range(1000):
        content = f"# File {i}\n\n" + ("Content " * 100)
        db.cache_file(f'docs/file_{i}.md', content)

    # Warm-up
    db.get_cached_file('docs/file_500.md')

    # Benchmark random lookups
    times = []
    import random
    for i in range(1000):
        file_idx = random.randint(0, 999)
        start = time.time()
        db.get_cached_file(f'docs/file_{file_idx}.md')
        end = time.time()
        times.append((end - start) * 1000)  # Convert to ms

    db.close()
    os.unlink(db_path)

    avg_time = statistics.mean(times)
    p95_time = sorted(times)[int(len(times) * 0.95)]
    p99_time = sorted(times)[int(len(times) * 0.99)]

    print(f"  Avg: {avg_time:.2f}ms")
    print(f"  P95: {p95_time:.2f}ms")
    print(f"  P99: {p99_time:.2f}ms")
    print(f"  Status: {'✅ PASS' if p95_time < 50 else '❌ FAIL'}")

    return p95_time < 50


def benchmark_checklist_progress_query():
    """Benchmark checklist progress query (target: < 100ms)."""
    print("\n=== Benchmark: Checklist Progress Query ===")
    print("Target: < 100ms")

    db, db_path = setup_database()

    # Setup: Create checklist with 100 items
    inv_id = db.create_agent_invocation('test-agent', 'testing')
    checklist_id = db.create_checklist(inv_id, 'Large Checklist', 100)

    items = [
        {'item_order': i, 'description': f'Task {i}', 'priority': 'medium'}
        for i in range(1, 101)
    ]
    item_ids = db.create_checklist_items(checklist_id, items)

    # Complete half the items
    for item_id in item_ids[:50]:
        db.update_checklist_item(item_id, 'completed')

    # Warm-up
    db.get_checklist_progress(checklist_id)

    # Benchmark
    times = []
    for i in range(100):
        start = time.time()
        db.get_checklist_progress(checklist_id)
        end = time.time()
        times.append((end - start) * 1000)  # Convert to ms

    db.close()
    os.unlink(db_path)

    avg_time = statistics.mean(times)
    p95_time = sorted(times)[int(len(times) * 0.95)]
    p99_time = sorted(times)[int(len(times) * 0.99)]

    print(f"  Avg: {avg_time:.2f}ms")
    print(f"  P95: {p95_time:.2f}ms")
    print(f"  P99: {p99_time:.2f}ms")
    print(f"  Status: {'✅ PASS' if p95_time < 100 else '❌ FAIL'}")

    return p95_time < 100


def benchmark_agent_metrics_query():
    """Benchmark agent metrics query (target: < 500ms)."""
    print("\n=== Benchmark: Agent Metrics Query ===")
    print("Target: < 500ms")

    db, db_path = setup_database()

    # Setup: Create 1000 invocations with file reads
    print("  Setting up 1000 agent invocations with file reads...")
    for i in range(1000):
        inv_id = db.create_agent_invocation('test-agent', 'testing')

        # Log 5 file reads per invocation
        for j in range(5):
            cache_status = 'hit' if j % 2 == 0 else 'miss'
            db.log_file_read(inv_id, f'file_{j}.md', cache_status, 1024)

        db.complete_agent_invocation(inv_id, 'completed')

    # Warm-up
    db.get_agent_metrics('test-agent')

    # Benchmark
    times = []
    for i in range(50):
        start = time.time()
        db.get_agent_metrics('test-agent')
        end = time.time()
        times.append((end - start) * 1000)  # Convert to ms

    db.close()
    os.unlink(db_path)

    avg_time = statistics.mean(times)
    p95_time = sorted(times)[int(len(times) * 0.95)]
    p99_time = sorted(times)[int(len(times) * 0.99)]

    print(f"  Avg: {avg_time:.2f}ms")
    print(f"  P95: {p95_time:.2f}ms")
    print(f"  P99: {p99_time:.2f}ms")
    print(f"  Status: {'✅ PASS' if p95_time < 500 else '❌ FAIL'}")

    return p95_time < 500


def benchmark_large_cache():
    """Benchmark operations with 10,000 cached files."""
    print("\n=== Benchmark: Large Cache (10,000 files) ===")
    print("Testing performance with large cache size")

    db, db_path = setup_database()

    # Setup: Cache 10,000 files
    print("  Caching 10,000 files (this may take a minute)...")
    start_setup = time.time()
    for i in range(10000):
        if i % 1000 == 0:
            print(f"    Cached {i} files...")
        content = f"# File {i}\n\nContent for file {i}"
        db.cache_file(f'docs/file_{i}.md', content)
    end_setup = time.time()
    print(f"  Setup completed in {end_setup - start_setup:.2f}s")

    # Benchmark lookups
    print("  Benchmarking random lookups...")
    times = []
    import random
    for i in range(100):
        file_idx = random.randint(0, 9999)
        start = time.time()
        db.get_cached_file(f'docs/file_{file_idx}.md')
        end = time.time()
        times.append((end - start) * 1000)

    db.close()
    os.unlink(db_path)

    avg_time = statistics.mean(times)
    p95_time = sorted(times)[int(len(times) * 0.95)]

    print(f"  Avg lookup time: {avg_time:.2f}ms")
    print(f"  P95 lookup time: {p95_time:.2f}ms")
    print(f"  Status: {'✅ PASS' if p95_time < 100 else '⚠ DEGRADED' if p95_time < 200 else '❌ FAIL'}")

    return p95_time < 200  # Allow 2x degradation for large cache


def main():
    """Run all benchmarks."""
    print("=" * 70)
    print("Agent Context Caching System - Performance Benchmarks")
    print("=" * 70)

    results = {}

    results['hash_calculation'] = benchmark_hash_calculation()
    results['cache_lookup'] = benchmark_cache_lookup()
    results['checklist_progress'] = benchmark_checklist_progress_query()
    results['agent_metrics'] = benchmark_agent_metrics_query()
    results['large_cache'] = benchmark_large_cache()

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for r in results.values() if r)

    for name, passed_result in results.items():
        status = "✅ PASS" if passed_result else "❌ FAIL"
        print(f"  {name:25s}: {status}")

    print(f"\nTotal: {passed}/{total} benchmarks passed")

    if passed == total:
        print("\n🎉 All performance targets met!")
        return 0
    else:
        print(f"\n⚠ {total - passed} benchmark(s) failed")
        return 1


if __name__ == '__main__':
    exit(main())
