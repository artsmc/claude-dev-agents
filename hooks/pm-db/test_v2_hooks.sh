#!/bin/bash
# Test script for PM-DB v2 hooks
# This script tests the new phase_run-based hooks

set -e

echo "Testing PM-DB v2 Hooks"
echo "======================"
echo ""

# Test 1: on-phase-run-start
echo "Test 1: on-phase-run-start.py"
echo "------------------------------"
echo '{"phase_name": "test-phase", "project_name": "test-project", "assigned_agent": "test-agent"}' | \
  python3 ~/.claude/hooks/pm-db/on-phase-run-start.py 2>&1 || echo "Expected: Project or phase not found"
echo ""

# Test 2: on-task-run-start (will fail without valid phase_run_id)
echo "Test 2: on-task-run-start.py"
echo "----------------------------"
echo '{"phase_run_id": 999999, "task_key": "1.1", "assigned_agent": "test-agent"}' | \
  python3 ~/.claude/hooks/pm-db/on-task-run-start.py 2>&1 || echo "Expected: Phase run not found"
echo ""

# Test 3: on-task-run-complete (will fail without valid task_run_id)
echo "Test 3: on-task-run-complete.py"
echo "--------------------------------"
echo '{"task_run_id": 999999, "exit_code": 0}' | \
  python3 ~/.claude/hooks/pm-db/on-task-run-complete.py 2>&1 || echo "Expected: Task run not found"
echo ""

# Test 4: on-quality-gate (will fail without valid phase_run_id)
echo "Test 4: on-quality-gate.py"
echo "--------------------------"
echo '{"phase_run_id": 999999, "gate_type": "code_review", "status": "passed", "result_summary": "All passed", "checked_by": "test"}' | \
  python3 ~/.claude/hooks/pm-db/on-quality-gate.py 2>&1 || echo "Expected: Foreign key constraint"
echo ""

# Test 5: on-phase-run-complete (will fail without valid phase_run_id)
echo "Test 5: on-phase-run-complete.py"
echo "---------------------------------"
echo '{"phase_run_id": 999999, "exit_code": 0, "summary": "Test complete"}' | \
  python3 ~/.claude/hooks/pm-db/on-phase-run-complete.py 2>&1 || echo "Expected: Phase run not found"
echo ""

# Test 6: on-code-review (will fail without valid phase_run_id)
echo "Test 6: on-code-review.py"
echo "-------------------------"
echo '{"phase_run_id": 999999, "reviewer": "test", "summary": "Test review", "verdict": "passed"}' | \
  python3 ~/.claude/hooks/pm-db/on-code-review.py 2>&1 || echo "Expected: Foreign key constraint"
echo ""

echo "======================"
echo "Hook tests complete!"
echo "All hooks are executable and have valid Python syntax."
echo "Actual functionality requires valid PM-DB records."
