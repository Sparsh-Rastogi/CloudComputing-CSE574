"""Unit tests for CloudBurst Schedule Builder and Models."""
import unittest
import math
from src.cloudburst.model.vm import VMType, VMInstance, build_vm_pool, get_default_catalog
from src.cloudburst.model.workflow import Workflow, parse_dax_xml
from src.cloudburst.model.schedule import Schedule
from src.cloudburst.builder import (
    build_schedule,
    compare_schedules_deb,
    BOOT_DELAY,
    BILLING_PERIOD,
    BANDWIDTH,
)


class TestBuilder(unittest.TestCase):
    def test_hand_checked_tiny_dag(self):
        catalog = [
            VMType(0, "small", 1.0, 0.10, 50.0, 30.0),
            VMType(1, "medium", 2.0, 0.20, 90.0, 54.0),
        ]
        pool = [
            VMInstance(0, catalog[0], "s-0"),
            VMInstance(1, catalog[1], "m-0"),
        ]

        wf = Workflow(
            name="tiny",
            n=3,
            length=[100.0, 200.0, 50.0],
            parents=[[], [(0, 1.0e8)], [(1, 0.0)]],
            children=[[(1, 1.0e8)], [(2, 0.0)], []],
            order=[0, 1, 2],
        )

        mapping = [0, 1, 1]
        deadline = 500.0
        sched = build_schedule(wf, pool, mapping, deadline=deadline)

        self.assertTrue(math.isclose(sched.placements[0].start, 97.0, rel_tol=1e-5))
        self.assertTrue(math.isclose(sched.placements[0].finish, 197.0, rel_tol=1e-5))
        self.assertTrue(math.isclose(sched.placements[1].start, 198.0, rel_tol=1e-5))
        self.assertTrue(math.isclose(sched.placements[1].finish, 298.0, rel_tol=1e-5))
        self.assertTrue(math.isclose(sched.placements[2].start, 298.0, rel_tol=1e-5))
        self.assertTrue(math.isclose(sched.placements[2].finish, 323.0, rel_tol=1e-5))

        self.assertTrue(math.isclose(sched.makespan, 323.0, rel_tol=1e-5))
        self.assertTrue(sched.deadline_met)
        self.assertEqual(sched.violation, 0.0)

        self.assertTrue(math.isclose(sched.cost, 0.30, rel_tol=1e-5))
        self.assertTrue(math.isclose(sched.energy, 7910.0 + 16488.0, rel_tol=1e-5))

        expected_util = 225.0 / 419.0
        self.assertTrue(math.isclose(sched.utilization, expected_util, rel_tol=1e-5))

    def test_dax_parsing(self):
        wf = parse_dax_xml("workflows/Montage_50.xml")
        self.assertEqual(wf.n, 50)
        self.assertEqual(len(wf.order), 50)
        visited = set()
        for task_idx in wf.order:
            for p_idx, _ in wf.parents[task_idx]:
                self.assertIn(p_idx, visited, f"Parent {p_idx} not visited before {task_idx}")
            visited.add(task_idx)

    def test_deb_rules(self):
        sched_feas = Schedule(placements=[], makespan=100.0, cost=1.0, energy=100.0, utilization=0.5, deadline_met=True, violation=0.0)
        sched_infeas = Schedule(placements=[], makespan=150.0, cost=0.5, energy=50.0, utilization=0.5, deadline_met=False, violation=50.0)

        self.assertEqual(compare_schedules_deb(sched_feas, sched_infeas, 1.0, 0.5), -1)
        self.assertEqual(compare_schedules_deb(sched_infeas, sched_feas, 0.5, 1.0), 1)

        sched_feas2 = Schedule(placements=[], makespan=110.0, cost=0.8, energy=90.0, utilization=0.5, deadline_met=True, violation=0.0)
        self.assertEqual(compare_schedules_deb(sched_feas, sched_feas2, 1.0, 0.8), 1)
        self.assertEqual(compare_schedules_deb(sched_feas2, sched_feas, 0.8, 1.0), -1)

        sched_infeas2 = Schedule(placements=[], makespan=160.0, cost=0.2, energy=20.0, utilization=0.5, deadline_met=False, violation=60.0)
        self.assertEqual(compare_schedules_deb(sched_infeas, sched_infeas2, 0.5, 0.2), -1)


if __name__ == "__main__":
    unittest.main()

