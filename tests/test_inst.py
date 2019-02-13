#! /usr/bin/env python
import unittest
from contextlib import contextmanager
import numpy as np
from numpy.random import randint

from src.instance import Instance, ShapeError, ConsistencyError


class InstanceTest(unittest.TestCase):
    """
    """

    def test_init(self):
        """
        Tests the initialization process
        """
        n_p_units = 100
        n_days = 7
        n_tasks = 5
        inst = Instance(n_p_units, n_days, n_tasks)
        # # Test if the solution attribute has the correct shape.
        # self.assertEqual(len(inst.solution), n_days*n_p_units*n_tasks)

        # Test if the instance accepts the correct shaped variables.
        Qjk = 2 * randint(0, high=2, size=(n_days, n_tasks))
        QCjk = Qjk
        QGjk = Qjk
        Ci = randint(0, high=2, size=n_p_units)
        Gi = randint(0, high=2, size=n_p_units)
        Fijk = set([(randint(0, n_p_units), randint(0, n_days),
                     randint(0, n_tasks)) for i in range(15)])
        Rijk = set([(randint(0, n_p_units), randint(0, n_days),
                     randint(0, n_tasks)) for i in range(15)])
        Rijk = list(Rijk.difference(Fijk))
        Fijk = list(Fijk)

        inst.n_parents = Ci
        inst.n_women = Gi
        inst.force = Fijk
        inst.reject = Rijk
        inst.people_per_task = Qjk
        inst.parents_per_task = np.copy(QCjk)
        inst.women_per_task = np.copy(QGjk)

        # Check the pre-decision consistency.
        inst.check_consistency()

        # Check parent data inconsistency (QCjk > Qjk for some jk)
        with self.assertRaises(ConsistencyError):
            QCjk = inst.parents_per_task
            QCjk[0, 0] = QCjk[0, 0] + 1
            inst.parents_per_task = QCjk
            inst.check_consistency()

        # Get back to consistent state
        inst.parents_per_task = np.copy(inst.people_per_task)

        # Check gender data inconsistency (QGjk > Qjk for some jk)
        with self.assertRaises(ConsistencyError):
            QGjk = inst.women_per_task
            QGjk[0, 0] = QGjk[0, 0] + 1
            inst.women_per_task = QGjk
            inst.check_consistency()

        # Get back to consistent state
        inst.parents_per_task = np.copy(inst.people_per_task)

        # Test with the wrongly shaped variables (Should raise ShapeError)
        Qjk = 2 * randint(0, high=2, size=(n_days + 1, n_tasks + 1))
        QCjk = np.copy(Qjk)
        QGjk = np.copy(Qjk)

        Ci = randint(0, high=2, size=n_p_units + 1)
        Gi = randint(0, high=2, size=n_p_units + 1)
        Fijk = set([(randint(0, n_p_units), randint(0, n_days))
                    for i in range(15)])
        Rijk = set([(randint(0, n_p_units), randint(0, n_days))
                    for i in range(15)])
        Rijk = list(Rijk.difference(Fijk))
        Fijk = list(Fijk)

        with self.assertRaises(ShapeError):
            inst.n_parents = Ci
        with self.assertRaises(ShapeError):
            inst.n_women = Gi
        with self.assertRaises(ShapeError):
            inst.force = Fijk
        with self.assertRaises(ShapeError):
            inst.reject = Rijk
        with self.assertRaises(ShapeError):
            inst.people_per_task = Qjk
        with self.assertRaises(ShapeError):
            inst.parents_per_task = QCjk
        with self.assertRaises(ShapeError):
            inst.women_per_task = QGjk


if __name__ == '__main__':
    unittest.main()
