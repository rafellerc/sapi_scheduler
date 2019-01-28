#! /usr/bin/env python
import unittest
from contextlib import contextmanager
import numpy as np
from numpy.random import randint

from src.instance import Instance, ShapeError


class InstanceTest(unittest.TestCase):
    """
    """

    def test_init(self):
        """
        Tests the initialization process
        """
        n_people = 100
        n_days = 7
        n_tasks = 5
        inst = Instance(n_people, n_days, n_tasks)
        # # Test if the solution attribute has the correct shape.
        # self.assertEqual(len(inst.solution), n_days*n_people*n_tasks)

        # Test if the instance accepts the correct shaped variables.
        Qjk = 2*randint(0, high=2, size=(n_days, n_tasks))
        Ci = randint(0, high=2, size=n_people)
        Gi = randint(0, high=2, size=n_people)
        Fijk = set([(randint(0, n_people), randint(0, n_days),
                     randint(0, n_tasks)) for i in range(15)])
        Rijk = set([(randint(0, n_people), randint(0, n_days),
                     randint(0, n_tasks)) for i in range(15)])
        Rijk = list(Rijk.difference(Fijk))
        Fijk = list(Fijk)
        
        inst.is_parent = Ci
        inst.is_man = Gi
        inst.is_allocated = Fijk
        inst.not_available = Rijk
        inst.people_per_task = Qjk

        # Test with the wrongly shaped variables (Should raise ShapeError)
        Qjk = 2*randint(0, high=2, size=(n_days+1, n_tasks+1))
        Ci = randint(0, high=2, size=n_people+1)
        Gi = randint(0, high=2, size=n_people+1)
        Fijk = set([(randint(0, n_people), randint(0, n_days))
                    for i in range(15)])
        Rijk = set([(randint(0, n_people), randint(0, n_days))
                    for i in range(15)])
        Rijk = list(Rijk.difference(Fijk))
        Fijk = list(Fijk)

        with self.assertRaises(ShapeError):
            inst.is_parent = Ci
        with self.assertRaises(ShapeError):
            inst.is_man = Gi
        with self.assertRaises(ShapeError):
            inst.is_allocated = Fijk
        with self.assertRaises(ShapeError):
            inst.not_available = Rijk
        with self.assertRaises(ShapeError):
            inst.people_per_task = Qjk

        

if __name__ == '__main__':
    unittest.main()