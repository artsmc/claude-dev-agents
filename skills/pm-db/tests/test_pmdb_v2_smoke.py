#!/usr/bin/env python3
"""
Smoke test for PM-DB v2 migration - verifies basic functionality works.
"""

import sys
from pathlib import Path

# Add lib to path
lib_path = Path(__file__).parent.parent.parent.parent / "lib"
sys.path.insert(0, str(lib_path))

from project_database import ProjectDatabase


def test_smoke():
    """Basic smoke test - create project, phase, plan, and task."""

    print("🧪 PM-DB v2 Smoke Test")
    print("=" * 60)

    db = ProjectDatabase()

    try:
        # Clean up any existing test project
        print("\n0. Cleaning up existing test data...")
        existing = db.get_project_by_name("test-project")
        if existing:
            db.conn.execute("DELETE FROM projects WHERE id = ?", (existing['id'],))
            db.conn.commit()
            print("   ✅ Existing test project removed")

        # Create project
        print("\n1. Creating project...")
        project_id = db.create_project(
            "test-project",
            "Test project for PM-DB v2",
            "/tmp/test-project"
        )
        print(f"   ✅ Project created: ID={project_id}")

        # Create phase
        print("\n2. Creating phase...")
        phase_id = db.create_phase(
            project_id=project_id,
            name="feature-auth",
            phase_type="feature",
            job_queue_rel_path="job-queue/feature-auth",
            planning_rel_path="planning",
            description="Authentication feature"
        )
        print(f"   ✅ Phase created: ID={phase_id}")

        # Create phase plan
        print("\n3. Creating phase plan...")
        plan_id = db.create_phase_plan(
            phase_id=phase_id,
            planning_approach="Implement JWT-based authentication"
        )
        print(f"   ✅ Phase plan created: ID={plan_id}")

        # Add plan documents
        print("\n4. Adding plan documents...")
        frd_id = db.add_plan_document(
            plan_id=plan_id,
            doc_type="frd",
            doc_name="FRD",
            content="# Functional Requirements\n\nUser authentication with JWT tokens."
        )
        print(f"   ✅ FRD added: ID={frd_id}")

        # Create task
        print("\n5. Creating task...")
        task_id = db.create_task(
            plan_id=plan_id,
            task_key="1.0",
            name="Setup JWT library",
            description="Install and configure JWT library",
            execution_order=1,
            wave=1,
            priority="high",
            difficulty="medium",
            sub_phase="1"
        )
        print(f"   ✅ Task created: ID={task_id}")

        # Approve plan
        print("\n6. Approving phase plan...")
        db.approve_phase_plan(plan_id, "tech-lead")
        print(f"   ✅ Phase plan approved")

        # Create phase run
        print("\n7. Creating phase run...")
        run_id = db.create_phase_run(
            phase_id=phase_id,
            plan_id=plan_id,
            assigned_agent="backend-agent"
        )
        print(f"   ✅ Phase run created: ID={run_id}")

        # Start phase run
        print("\n8. Starting phase run...")
        db.start_phase_run(run_id)
        print(f"   ✅ Phase run started")

        # Create task run
        print("\n9. Creating task run...")
        task_run_id = db.create_task_run(
            phase_run_id=run_id,
            task_id=task_id,
            assigned_agent="backend-agent"
        )
        print(f"   ✅ Task run created: ID={task_run_id}")

        # Complete task run
        print("\n10. Completing task run...")
        db.complete_task_run(task_run_id, 0)
        print(f"    ✅ Task run completed")

        # Add quality gate
        print("\n11. Adding quality gate...")
        gate_id = db.add_quality_gate(
            phase_run_id=run_id,
            gate_type="code_review",
            status="passed",
            result_summary="All checks passed",
            checked_by="reviewer-agent"
        )
        print(f"    ✅ Quality gate added: ID={gate_id}")

        # Complete phase run
        print("\n12. Completing phase run...")
        db.complete_phase_run(run_id, 0, "Phase completed successfully")
        print(f"    ✅ Phase run completed")

        # Get metrics
        print("\n13. Calculating phase metrics...")
        metrics = db.get_phase_metrics(phase_id)
        print(f"    ✅ Metrics calculated:")
        print(f"       - Total runs: {metrics['total_runs']}")
        print(f"       - Successful runs: {metrics['successful_runs']}")
        print(f"       - Total tasks: {metrics['total_tasks']}")

        # Generate dashboard
        print("\n14. Generating phase dashboard...")
        dashboard = db.generate_phase_dashboard(phase_id)
        print(f"    ✅ Dashboard generated:")
        print(f"       - Phase status: {dashboard['phase']['status']}")
        print(f"       - Recent runs: {len(dashboard['recent_runs'])}")

        print("\n" + "=" * 60)
        print("✅ All smoke tests passed!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Smoke test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = test_smoke()
    sys.exit(0 if success else 1)
