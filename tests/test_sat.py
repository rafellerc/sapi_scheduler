#! /usr/bin/env python
import unittest
from contextlib import contextmanager
import numpy as np
from numpy.random import randint

from src.instance import Instance, print_solution


class SatisfiabilityTest(unittest.TestCase):
    """
    """

    def test_sat(self):
        """
        Tests
        """
        names = ['Pedro e Kim', 'Tania', 'Clarissa', 'Guilherme', 'Rafael',
                 'Andressa', 'Carlinhos', 'Debora', 'Carol e Rafaela', 'Bruna',
                 'Manu', 'Erika Mesq.', 'Alane', 'Carol e Leo', 'Larissa',
                 'Lucas Mendes', 'Marcus', 'Pericles', 'Sayro', 'Luciana',
                 'Aline Palm.', 'Belinha', 'Eliane', 'Aline Wiez.', 'Ranuzia',
                 'Grazi', 'Socorro']
        inst = Instance(27, 6, 2)
        # Define the p units.
        inst.n_people = np.array(
            [2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        inst.n_women = np.array(
            [1, 1, 1, 0, 0, 1, 0, 1, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1])
        inst.n_parents = np.array(
            [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1])
        # One baby task (4 people - 2 parents - 2 women) and one kids task
        # (2 people - 0 parents - 1 women)
        inst.people_per_task = np.array(
            [[3, 2], [3, 2], [3, 2], [3, 2], [3, 2], [3, 2]])
        inst.women_per_task = np.array(
            [[2, 1], [2, 1], [2, 1], [2, 1], [2, 1], [2, 1]])
        inst.parents_per_task = np.array(
            [[1, 0], [1, 0], [1, 0], [1, 0], [1, 0], [1, 0]])

        inst.force = [(7, 1, 0)]
        inst.reject = [(2, 0, 1), (5, 1, 1)]

        inst.solve()

        solution = inst.solution_list[0]

        # [Constraint 1: Demand of people per task]
        for j in range(inst.n_days):
            for k in range(inst.n_tasks):
                self.assertTrue(np.dot(solution[:, j, k], inst.n_people) ==
                                inst.people_per_task[j, k])

        # [Constraint 2: Min number of parents]
        for j in range(inst.n_days):
            for k in range(inst.n_tasks):
                self.assertTrue(np.dot(solution[:, j, k], inst.n_parents) ==
                                inst.parents_per_task[j, k])

        # [Constraint 3: Min number of women]
        for j in range(inst.n_days):
            for k in range(inst.n_tasks):
                self.assertTrue(np.dot(solution[:, j, k], inst.n_women) ==
                                inst.women_per_task[j, k])

        # [Constraint 4: One task per day]
        for i in range(inst.n_p_units):
            for j in range(inst.n_days):
                self.assertTrue(np.sum(solution[i, j, :]) <= 1)

        # [Constraint 5: Force Variables]
        for triple in inst.force:
            self.assertTrue(solution[triple] == 1)

        # [Constraint 6: Reject Variables]
        for triple in inst.reject:
            self.assertTrue(solution[triple] == 0)

        # [Constraint 7: Max one allocation per 4 weeks]
        for i in range(inst.n_p_units):
            for j in range(inst.n_days - 4):
                self.assertTrue(np.sum(solution[i, j:(j + 4), :]) <= 1)


if __name__ == '__main__':
    unittest.main()
