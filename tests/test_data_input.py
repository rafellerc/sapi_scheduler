#! /usr/bin/env python
import unittest
from contextlib import contextmanager
from datetime import datetime
import os.path as osp

import numpy as np

from src.data_input import read_ficha_servo, read_demanda, read_solution_sheet, get_problem_info


class DataInputTest(unittest.TestCase):
    """
    """

    def test_ficha_servo(self):
        """
        Tests the reading of the ficha servo type file
        """
        dirname = osp.dirname(__file__)
        ficha_servo_path = osp.join(dirname, 'Example_Ficha_Servo.xlsx')

        tasks, people = read_ficha_servo(ficha_servo_path)

        # The test sheet should have 65 people on it
        self.assertEqual(len(people), 65)
        # The test sheet should have 9 tasks.
        self.assertEqual(len(tasks), 9)

        # Check that the only task answers are 'Não Aceito', 'Aceito'
        # and 'Gosto'.
        for id_, person in people.items():
            for answ in person.task_answ.values():
                self.assertTrue(answ in ['Não Aceito', 'Aceito', 'Gosto'])
            for task in person.task_answ.keys():
                self.assertTrue(task in tasks)
        # Check that all genders are 'F' or 'M'
        for id_, person in people.items():
            self.assertTrue(person.gender in ['F', 'M'])

    def test_demanda(self):
        """
        """
        dirname = osp.dirname(__file__)
        ficha_servo_path = osp.join(dirname, 'Example_Ficha_Servo.xlsx')
        demanda_path = osp.join(dirname, 'Example_Demanda.xlsx')

        tasks_ficha, people = read_ficha_servo(ficha_servo_path)

        tasks_demanda, people_demand, women_demand, parents_demand = read_demanda(
            demanda_path)

        # Check that the tasks are the same for both files.
        self.assertTrue(len(tasks_demanda) == len(tasks_ficha))
        for task in tasks_demanda:
            self.assertTrue(task in tasks_ficha)

    def test_solution_sheet(self):
        """
        """
        dirname = osp.dirname(__file__)
        sol_sheet_path = osp.join(dirname, 'Example_Indisponibilidade.xlsx')
        # Pay close attention to the date formatting
        days_expected = ['03/02/2019', '10/02/2019',
                         '17/02/2019', '24/02/2019']
        tasks = ['BercCM', 'BercEBD', 'BercCV', 'MatCM',
                 'MatEBD', 'MatCV', 'JardEBD', 'JuvEBD', 'indisp',
                 'not_allocated']

        days, sheet_info = read_solution_sheet(sol_sheet_path)
        # Assert that the function reads the dates correctly
        self.assertTrue(days == days_expected)
        for triple in sheet_info:
            # Assert that all the days info is contained in the days list
            self.assertTrue(triple[1] in days)
            # Assert that all info belongs to one of the tasks, is 'indisp' or
            # 'not_allocated'.
            self.assertTrue(triple[2] in tasks)

    def test_get_problem_info(self):
        """
        """
        dirname = osp.dirname(__file__)
        ficha_servo_path = osp.join(dirname, 'Example_Ficha_Servo.xlsx')
        sol_sheet_path = osp.join(dirname, 'Example_Indisponibilidade.xlsx')
        demanda_path = osp.join(dirname, 'Example_Demanda.xlsx')

        problem_info = get_problem_info(
            ficha_servo_path, demanda_path, sol_sheet_path)

        self.assertTrue(problem_info.n_p_units == 65)
        self.assertTrue(problem_info.n_days == 4)
        self.assertTrue(len(problem_info.tasks) == 9)

        expected_tasks = ['BercCM', 'BercEBD', 'BercCV', 'MatCM',
                          'MatEBD', 'MatCV', 'JardEBD', 'JuvEBD', 'MusEBD']
        self.assertTrue(sorted(problem_info.tasks) == sorted(expected_tasks))
        self.assertTrue(len(problem_info.names) == 65)
        # Check two random names
        self.assertTrue('Carol Cruz' in problem_info.names and
                        'Vanessa Andrade' in problem_info.names)
        n_women = np.array([1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0,
                            1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1,
                            0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1,
                            1, 1, 1, 1, 1, 0, 1, 0])
        n_parents = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1,
                              1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                              1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                              1, 1, 1, 1, 1, 0, 0, 0])
        self.assertTrue((problem_info.n_women == n_women).all())
        self.assertTrue((problem_info.n_parents == n_parents).all())

        # Check some random preferences (Péricles Pereira: 22,
        # and Gabriela Seabra Gomes Mustafá: 25), given that they have no
        # unavailabilities the only force and reject triples come from the
        # 'ficha servo'.
        reject_Pericles = []
        reject_Gabi = []
        for reject in problem_info.reject:
            if reject[0] == 22:
                reject_Pericles.append(reject)
            if reject[0] == 26:
                reject_Gabi.append(reject)
        expected_reject_Pericles = [(22, j, k) for j in range(
            problem_info.n_days) for k in [0, 2, 3, 5, 8]]
        expected_reject_Gabi = [(26, j, k) for j in range(
            problem_info.n_days) for k in [1, 4, 6, 7, 8]]

        self.assertTrue(sorted(expected_reject_Pericles)
                        == sorted(reject_Pericles))
        self.assertTrue(sorted(expected_reject_Gabi) == sorted(reject_Gabi))

        # Also there should be no forced allocations for either
        for force in problem_info.force:
            self.assertTrue(force[0] != 22 and force[0] != 26)

        # There should be forced allocations for Carol Martins:29,
        # Ana Rafaela:20, Bruna Oliveira:37 and Rafael:53.
        expected_force = [(29, 0, 0), (20, 0, 0), (37, 0, 7), (53, 0, 7)]
        self.assertTrue(sorted(expected_force) == sorted(problem_info.force))


if __name__ == '__main__':
    unittest.main()
