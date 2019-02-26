from random import randint

import numpy as np
# NOTE: Must have python 3.6.1 or higher to use cp_models
from ortools.sat.python import cp_model
from tabulate import tabulate


class ShapeError(Exception):
    pass


class ConsistencyError(Exception):
    pass


class ContraintSatError(Exception):
    pass


class SolutionBuilder(cp_model.CpSolverSolutionCallback):
    """ Builds the solutions found by the solver.
    """

    def __init__(self, sol_list, shifts, n_p_units, n_days, n_tasks, max_sols):
        """
            sol_list: (list) The Instance object's list of solutions.
        """
        cp_model.CpSolverSolutionCallback.__init__(self)
        # This should be a reference to the object's list. Check if true.
        self._sol_list = sol_list
        self._shifts = shifts
        self._n_p_units = n_p_units
        self._n_days = n_days
        self._n_tasks = n_tasks
        self._solution_count = 0
        self._solution_limit = max_sols

    def on_solution_callback(self):
        self._solution_count += 1
        # print('Solution %i' % self._solution_count)
        solution = np.zeros([self._n_p_units, self._n_days, self._n_tasks])
        for i in range(self._n_p_units):
            for j in range(self._n_days):
                for k in range(self._n_tasks):
                    solution[i, j, k] = self.Value(self._shifts[(i, j, k)])
        self._sol_list.append(solution)
        if self._solution_count >= self._solution_limit:
            print('Stop search after %i solutions' % self._solution_limit)
            self.StopSearch()

    def solution_count(self):
        return self._solution_count


class Instance(object):
    """ An instance of the SAPI scheduling problem.
    """

    def __init__(self, n_p_units, n_days, n_tasks, max_time=100, max_sols=100):
        """
        Args:
            n_p_units: (int) The number of p_units considered in any solution.
                The p_units will be indexed by the letter 'i'.
            n_days: (int) The number of days considered in the solution.
                The days will be indexed by the letter 'j'.
            n_tasks: (int) The number of tasks considered in each day. The
                current solution does not admit a variable number of tasks.
                The tasks will be indexed by the letter 'k'.
            max_time: (int) The time limit imposed to the solver in seconds.
            max_sols: (int) The maximum number of solution to be stored.

        Attributes:
            people_per_task: (numpy.ndarray) The number of p_units per
                task on each day. It's a matrix (n_days x n_tasks).
            n_parents: (numpy.ndarray) An array where n_parents(i) is the
                number of parents on the p_unit 'i'.
            n_women: (numpy.ndarray) An array where n_women(i) is the number
                of women in the p_unit 'i'.
            reject: (list) A list of triples (i,j,k) each of which
                represent a rejection/non-availability of p_unit "i" on day 
                "j" for task "k".
            force: (list) The opposite of reject, that is, the triple (i,j,k)
                indicates that p_unit 'i' must work on day 'j' for task 'k'.
            model: (ortools.sat.python.cp_model.CpModel) The ortools
                constraint solver used to define the solution.
            shifts: (dictionary) The solution matrix for the given instance.
                It's implemented as a dictionary indexed by triples of (i,j,k),
                where a 1 represents that p_unit 'i' will be allocated in
                day 'j' for task 'k'.
        """
        self.model = cp_model.CpModel()
        self.max_sols = max_sols
        self.max_time = max_time
        self.shifts = {}

        # TODO set them as property, with a setter method that reinitializes
        # the 'solution' variable. Guarantee the consistency of the instance.
        self._n_p_units = n_p_units
        self._n_days = n_days
        self._n_tasks = n_tasks

        self._people_per_task = None
        self._parents_per_task = None
        self._women_per_task = None
        self._n_people = None
        self._n_parents = None
        self._n_women = None
        self._reject = []
        self._force = []

        for i in range(n_p_units):
            for j in range(n_days):
                for k in range(n_tasks):
                    self.shifts[(i, j, k)] = self.model.NewBoolVar(
                        'person{}_day{}_task{}'.format(i, j, k))

        # self.shifts_flat = [self.shifts[(i, j, k)] for i in range(n_p_units)
        #                       for j in range(n_days) for k in range(n_tasks)]

    # This Section, though long is only concerned with getter and setter
    # methods for the class using the @property decorator
    ###########################################################################
    ###########################################################################
    @property
    def n_p_units(self):
        return self._n_p_units

    @property
    def n_days(self):
        return self._n_days

    @property
    def n_tasks(self):
        return self._n_tasks

    @property
    def people_per_task(self):
        return self._people_per_task

    @people_per_task.setter
    def people_per_task(self, Qjk):
        # Check data type and shape consistency
        if type(Qjk) != np.ndarray:
            raise TypeError("Object must be numpy.ndarray")
        if Qjk.shape != (self._n_days, self._n_tasks):
            raise ShapeError("Wrong shape to people_per_task, correct "
                             "shape should be {}".format((self._n_days, self._n_tasks)))
        self._people_per_task = Qjk

    @property
    def parents_per_task(self):
        return self._parents_per_task

    @parents_per_task.setter
    def parents_per_task(self, QCjk):
        # Check data type and shape consistency
        if type(QCjk) != np.ndarray:
            raise TypeError("Object must be numpy.ndarray")
        if QCjk.shape != (self._n_days, self._n_tasks):
            raise ShapeError("Wrong shape to parents_per_task, correct "
                             "shape should be {}".format((self._n_days, self._n_tasks)))
        self._parents_per_task = QCjk

    @property
    def women_per_task(self):
        return self._women_per_task

    @women_per_task.setter
    def women_per_task(self, QGjk):
        # Check data type and shape consistency
        if type(QGjk) != np.ndarray:
            raise TypeError("Object must be numpy.ndarray")
        if QGjk.shape != (self._n_days, self._n_tasks):
            raise ShapeError("Wrong shape to women_per_task, correct "
                             "shape should be {}".format((self._n_days, self._n_tasks)))
        self._women_per_task = QGjk

    @property
    def n_people(self):
        return self._n_people

    @n_people.setter
    def n_people(self, Pi):
        # Check data type and shape consistency
        if type(Pi) != np.ndarray:
            raise TypeError("Object must be numpy.ndarray")
        if Pi.shape != (self._n_p_units, ):
            raise ShapeError("Wrong shape to n_people, correct shape "
                             "should be {}".format((self._n_p_units,)))
        self._n_people = Pi

    @property
    def n_parents(self):
        return self._n_parents

    @n_parents.setter
    def n_parents(self, Ci):
        # Check data type and shape consistency
        if type(Ci) != np.ndarray:
            raise TypeError("Object must be numpy.ndarray")
        if Ci.shape != (self._n_p_units, ):
            raise ShapeError("Wrong shape to n_parents, correct shape "
                             "should be {}".format((self._n_p_units,)))
        self._n_parents = Ci

    @property
    def n_women(self):
        return self._n_women

    @n_women.setter
    def n_women(self, Gi):
        # Check data type and shape consistency
        if type(Gi) != np.ndarray:
            raise TypeError("Object must be numpy.ndarray")
        if Gi.shape != (self._n_p_units, ):
            raise ShapeError("Wrong shape to n_women, correct shape "
                             "should be {}".format((self._n_p_units,)))
        self._n_women = Gi

    @property
    def reject(self):
        return self._reject

    @reject.setter
    def reject(self, Rijk):
        # Check data type and shape consistency
        for triple in Rijk:
            if type(triple) == tuple:
                if len(triple) != 3:
                    raise ShapeError("Tuples must have lenght 3")
            else:
                raise TypeError("Elements of reject must be tuples.")
        self._reject = Rijk

    @property
    def force(self):
        return self._force

    @force.setter
    def force(self, Fijk):
        # Check data type and shape consistency
        for triple in Fijk:
            if type(triple) == tuple:
                if len(triple) != 3:
                    raise ShapeError("Tuples must have lenght 3")
            else:
                raise TypeError("Elements of force must be tuples.")
        self._force = Fijk

    ###########################################################################
    ###########################################################################

    def check_consistency(self):
        # Check if the min number of women/parents per task is lesser than or
        # equal to the requested number of people
        gender_inconsist = np.argwhere(
            self.women_per_task > self.people_per_task)
        if len(gender_inconsist) > 0:
            raise ConsistencyError("The 'women_per_task' variable has greater"
                                   " values than the 'people_per_task' variable in the following"
                                   " days/tasks: {}".format(['day ' + str(day) + ' task ' + str(task)
                                                             for (day, task) in gender_inconsist]))

        parent_inconsist = np.argwhere(
            self.parents_per_task > self.people_per_task)
        if len(parent_inconsist) > 0:
            raise ConsistencyError("The 'parents_per_task' variable has greater"
                                   " values than the 'people_per_task' variable in the following"
                                   " days/tasks: {}".format(['day ' + str(day) + ' task ' + str(task)
                                                             for (day, task) in parent_inconsist]))

    def solve(self, relax=[], min_gap=4):
        """ Applies all the problem's constraints and applies the solver to
        the instance.
        Args:
            relax: (list) A list with integers indicating which constraints
                should be relaxed. To be used when no solution is found. The
                default relaxation is to remove the Constraint 7 "Max one
                allocation per 4 weeks", i.e. relax=[7]. To relax multiple
                contraints put them on the list, i.e. relax = [2, 3, 7]
            min_gap: (int) The minimun time between two allocations in
                constraint 7. Used for relaxing the problem.
        """
        self.solver = cp_model.CpSolver()
        self.solver.parameters.max_time_in_seconds = self.max_time
        self.solution_list = []

        # Before solving, check consistency
        print('Checking Instance Consistency...')
        self.check_consistency()

        print('Solving Instance...')
        # [Constraint 1: Demand of people per task]
        if 1 not in relax:
            for j in range(self.n_days):
                for k in range(self.n_tasks):
                    self.model.Add(sum(self.shifts[(i, j, k)] * self.n_people[i]
                                       for i in range(self.n_p_units)) ==
                                   self.people_per_task[j, k])
        # [Constraint 2: Min number of parents]
        if 2 not in relax:
            for j in range(self.n_days):
                for k in range(self.n_tasks):
                    self.model.Add(sum(self.shifts[(i, j, k)] * self.n_parents[i]
                                       for i in range(self.n_p_units)) >=
                                   self.parents_per_task[j, k])
        # [Constraint 3: Min number of women]
        if 3 not in relax:
            for j in range(self.n_days):
                for k in range(self.n_tasks):
                    self.model.Add(sum(self.shifts[(i, j, k)] * self.n_women[i]
                                       for i in range(self.n_p_units)) >=
                                   self.women_per_task[j, k])
        # [Constraint 4: One task per day]
        if 4 not in relax:
            for i in range(self.n_p_units):
                for j in range(self.n_days):
                    self.model.Add(sum(self.shifts[(i, j, k)]
                                       for k in range(self.n_tasks)) <= 1)

        # [Constraint 5: Force Variables]
        if 5 not in relax:
            for triple in self.force:
                self.model.Add(self.shifts[triple] == 1)

        # [Constraint 6: Reject Variables]
        if 6 not in relax:
            for triple in self.reject:
                self.model.Add(self.shifts[triple] == 0)

        # [Constraint 7: Max one allocation per 4 weeks]
        if 7 not in relax:
            for i in range(self.n_p_units):
                for j_0 in range(self.n_days - min_gap):
                    self.model.Add(sum(self.shifts[(i, j, k)] for j in range(
                        j_0, j_0 + min_gap) for k in range(self.n_tasks)) <= 1)

        self.solution_printer = SolutionBuilder(self.solution_list, self.shifts,
                                                self.n_p_units, self.n_days,
                                                self.n_tasks, self.max_sols)
        self.status = self.solver.SearchForAllSolutions(
            self.model, self.solution_printer)
        self.n_solutions = self.solution_printer.solution_count()
        print('Status = %s' % self.solver.StatusName(self.status))
        print('Number of solutions found: %i' %
              self.solution_printer.solution_count())


def print_solution(sol_matrix, names=None):
    """ Prints the solution to the terminal
    Args:
        sol_matrix: (numpy.array) The solution matrix
        names: (list) The list with the names of the people in order.
    """
    headers = ['day {}'.format(i + 1) for i in range(sol_matrix.shape[1])]
    headers.insert(0, ' ')
    if names is None:
        names = list(range(sol_matrix.shape[0]))
    contents = []
    for k in range(sol_matrix.shape[2]):
        row = ['task {}'.format(k + 1)]
        for j in range(sol_matrix.shape[1]):
            people = ''
            for i in range(sol_matrix.shape[0]):
                if sol_matrix[i, j, k] == 1:
                    people = people + str(names[i]) + ', '
            # Remove the last two strings (A space and a comma)
            if len(people) > 2:
                people = people[0:-2]
            row.append(people)
        contents.append(row)
    print(tabulate(contents, headers=headers, tablefmt="fancy_grid"))


if __name__ == '__main__':
    names = ['Pedro e Kim', 'Tania', 'Clarissa', 'Guilherme', 'Rafael',
             'Andressa', 'Carlinhos', 'Debora', 'Carol e Rafaela', 'Bruna']
    inst = Instance(10, 3, 2)
    # Define the p units.
    inst.n_people = np.array([2, 1, 1, 1, 1, 1, 1, 1, 2, 1])
    inst.n_women = np.array([1, 1, 1, 0, 0, 1, 0, 1, 2, 1])
    inst.n_parents = np.array([0, 1, 0, 0, 0, 0, 0, 1, 0, 0])
    # One baby task (4 people - 2 parents - 2 women) and one kids task
    # (2 people - 0 parents - 1 women)
    inst.people_per_task = np.array([[4, 2], [4, 2], [4, 2]])
    inst.women_per_task = np.array([[2, 1], [2, 1], [2, 1]])
    inst.parents_per_task = np.array([[2, 0], [2, 0], [2, 0]])
    # Force Pedro e Kim on the first day task 1, Debora on day 2 task 1, and
    # Rafael on day 3 task 2.
    inst.force = [(0, 0, 0), (7, 1, 0), (4, 2, 1)]
    # Reject Clarissa on day 1 task 2, Andressa on day 2 task 2, and Carlinhos
    # on day 3 task 1.
    inst.reject = [(2, 0, 1), (5, 1, 1), (6, 2, 0)]

    inst.solve()
    print_solution(inst.solution_list[50], names=names)
