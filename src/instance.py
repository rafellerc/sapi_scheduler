import numpy as np
from ortools.constraint_solver import pywrapcp
from random import randint


class ShapeError(Exception):
    pass


class ConsistencyError(Exception):
    pass


class Instance(object):
    """ An instance of the SAPI scheduling problem.
    """

    def __init__(self, n_p_units, n_days, n_tasks):
        """
        Args:
            n_p_units: (int) The number of p_units considered in any solution.
                The p_units will be indexed by the letter 'i'.
            n_days: (int) The number of days considered in the solution.
                The days will be indexed by the letter 'j'.
            n_tasks: (int) The number of tasks considered in each day. The
                current solution does not admit a variable number of tasks.
                The tasks will be indexed by the letter 'k'.

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
            solver: (ortools.constraint_solver.pywrapcp.Solver) The ortools
                constraint solver used to define the solution.
            shifts: (dictionary) The solution matrix for the given instance.
                It's implemented as a dictionary indexed by triples of (i,j,k),
                where a 1 represents that p_unit 'i' will be allocated in
                day 'j' for task 'k'.
            shifts_flat: (list) A flattened version of the solution.
        """
        self.solver = pywrapcp.Solver("instance_solver")
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
                    self.shifts[(i, j, k)] = self.solver.BoolVar(
                        'person{}_day{}_task{}'.format(i, j, k))

        self.shifts_flat = [self.shifts[(i, j, k)] for i in range(n_p_units)
                              for j in range(n_days) for k in range(n_tasks)]

    # This Section, though long is only concerned with getter and setter
    # methods for the class using the @property decorator######################
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

    def solve(self):
        """
        """
        # [Demand of people per task constraint]
        for j in range(self.n_days):
            for k in range(self.n_tasks):
                self.solver.Add(sum(self.shifts[(i, j, k)]*self.n_people[i] for i in range(self.n_p_units)) == self.people_per_task[j, k])

        # Create Decision Builder
        db = self.solver.Phase(self.shifts, self.solver.CHOOSE_FIRST_UNBOUND,
                          self.solver.ASSIGN_MIN_VALUE)
        # Create the solution collector.
        solution = self.solver.Assignment()
        solution.Add(self.shifts_flat)
        collector = self.solver.AllSolutionCollector(solution)

        self.solver.Solve(db, [collector])
        print("Solutions found:", collector.SolutionCount())
        print("Time:", solver.WallTime(), "ms")

                

if __name__ == '__main__':
    inst = Instance(10, 5, 4)
    Qjk = np.random.randint(1, high=4, size=[5, 4])
    QGjk = np.copy(Qjk)
    QCjk = np.copy(Qjk)
    # QGjk[2,3]=4
    # QGjk[4,3]=5
    # QGjk[1,0]=5

    inst.people_per_task = Qjk
    inst.women_per_task = QGjk
    inst.parents_per_task = QCjk

    inst.check_consistency()

# # NOTE The numpy random int generator works with open intervals of type [a, b[
# # while random.randint(a,b) works with [a, b]

# # Number of people
# n_people = 10
# n_days = 3
# n_tasks = 2

# # Number of people per task. its a matrix (n_days x n_tasks) where
# # each task has always the same amount of people on every day.
# people_per_task = np.random.randint(1, 5, size=n_days)
# people_per_task = people_per_task.reshape(-1,1).repeat(n_tasks, axis=1)

# # Vector is_parent(i) is 0 when person 'i' is not a parent and 1 when it is.
# # prob_parent is in [0,1] and is the probability of any person being a parent
# prob_parent = 0.5
# is_parent = (np.random.rand(n_people) < prob_parent).astype(int)

# # is_man(i) is 1 when person 'i' is a man and 0 when its a woman.
# prob_man = 0.5
# is_man = (np.random.rand(n_people) < prob_man).astype(int)

# # not_available is list of triples (i,j,k) each of which represent a
# # non-availalability of person "i" on day "j" for task "k".
# # prob_not_available is the probability any triple (i,j,k) is in this list
# # so we generate prob_not_available*n_days*n_people*n_tasks distinct random
# # triples.
# prob_not_available = 0.3
# not_available = []
# while len(not_available) < prob_not_available*n_days*n_people*n_tasks:
#     new_triple = (randint(0, n_people-1), randint(0, n_days-1), randint(0, n_tasks-1))
#     if new_triple not in not_available:
#         not_available.append(new_triple)

# # is_allocated is the opposite of not_available, where the triple (i,j,k)
# # indicates that person 'i' must work on day 'j' for task 'k'.
# prob_is_allocated = 0.2
# is_allocated = []
# while len(is_allocated) < prob_is_allocated*n_days*n_people*n_tasks:
#     new_triple = (randint(0, n_people-1), randint(0, n_days-1), randint(0, n_tasks-1))
#     if (new_triple not in not_available) and (new_triple not in is_allocated):
#         is_allocated.append(new_triple)


# solver = pywrapcp.Solver("instance_solver")

# # Definition of the solution
# # S = np.zeros([n_people, n_days, n_tasks])
# S = {}

# for i in range(n_people):
#     for j in range(n_days):
#         for k in range(n_tasks):
#             S[(i, j, k)] = solver.BoolVar('person{}_day{}_task{}'.format(i, j, k))

# S_flat = [S[(i,j,k)] for i in range(n_people) for j in range(n_days) for k in range(n_tasks)]

# # TODO Check dims

# print('people per task {}'.format(people_per_task))
# print('is parent {}'.format(is_parent))
# print('is man {}'.format(is_man))
# print('not available {}'.format(not_available))
# print('is_allocated {}'.format(is_allocated))
