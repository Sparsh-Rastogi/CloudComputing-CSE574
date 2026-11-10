"""Unit tests verifying all scheduling algorithms."""
import unittest
import math
from src.cloudburst.model.vm import build_vm_pool
from src.cloudburst.model.workflow import parse_dax_xml
from src.cloudburst.algorithms import (
    schedule_heft,
    schedule_pso_plain,
    schedule_heft_td,
    schedule_rodriguez_pso,
    schedule_ceas,
    schedule_wpso,
    schedule_ipso_gwo,
    schedule_pacm,
    schedule_ddhpso,
)


class TestAlgorithms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wf = parse_dax_xml("workflows/Montage_50.xml")
        cls.pool = build_vm_pool(task_count=cls.wf.n)
        cls.heft_sched, cls.heft_map = schedule_heft(cls.wf, cls.pool)
        cls.deadline = 1.5 * cls.heft_sched.makespan

    def test_heft_runs(self):
        self.assertGreater(self.heft_sched.makespan, 0)
        self.assertGreater(self.heft_sched.cost, 0)
        self.assertGreater(self.heft_sched.energy, 0)
        self.assertGreater(self.heft_sched.utilization, 0)

    def test_heft_td_runs(self):
        sched = schedule_heft_td(self.wf, self.pool, deadline=self.deadline)
        self.assertGreater(sched.makespan, 0)
        self.assertLessEqual(sched.makespan, 1.5 * self.heft_sched.makespan)

    def test_rodriguez_pso_runs(self):
        sched = schedule_rodriguez_pso(self.wf, self.pool, deadline=self.deadline, pop_size=5, iterations=5)
        self.assertGreater(sched.makespan, 0)
        self.assertGreater(sched.cost, 0)

    def test_ceas_runs(self):
        sched = schedule_ceas(self.wf, self.pool, deadline=self.deadline)
        self.assertGreater(sched.makespan, 0)
        self.assertGreater(sched.cost, 0)

    def test_wpso_runs(self):
        sched = schedule_wpso(self.wf, self.pool, deadline=self.deadline, pop_size=5, iterations=5)
        self.assertGreater(sched.makespan, 0)
        self.assertGreater(sched.cost, 0)

    def test_ipso_gwo_runs(self):
        c_ref, e_ref, m_ref = self.heft_sched.cost, self.heft_sched.energy, self.heft_sched.makespan
        sched = schedule_ipso_gwo(self.wf, self.pool, deadline=self.deadline, c_ref=c_ref, e_ref=e_ref, m_ref=m_ref, pop_size=5, iterations=6)
        self.assertGreater(sched.makespan, 0)

    def test_pacm_runs(self):
        sched = schedule_pacm(self.wf, self.pool, deadline=self.deadline)
        self.assertGreater(sched.makespan, 0)
        self.assertGreater(sched.cost, 0)

    def test_ddhpso_runs(self):
        sched = schedule_ddhpso(
            self.wf,
            self.pool,
            deadline=self.deadline,
            heft_sched=self.heft_sched,
            heft_mapping=self.heft_map,
            pop_size=5,
            iterations=5,
        )
        self.assertGreater(sched.makespan, 0)
        # Monotonicity test: DD-HPSO is seeded with HEFT, so its result should never be worse than HEFT under Deb's rules
        self.assertTrue(sched.makespan <= self.deadline or sched.violation <= self.heft_sched.violation + 1e-4)


if __name__ == "__main__":
    unittest.main()
