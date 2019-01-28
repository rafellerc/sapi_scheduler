import numpy as np
from ortools.constraint_solver import pywrapcp
from random import randint


class ShapeError(Exception):
    pass


class Instance(object):
    """ An instance of the SAPI scheduling problem.
    """

    def __init__(self, n_people, n_days, n_tasks):
        """
        Args:
            n_people: (int) The number of people considered in any solution.
                The people will be indexed by the letter 'i'.
            n_days: (int) The number of days considered in the solution.
                The days will be indexed by the letter 'j'.
            n_tasks: (int) The number of tasks considered in each day. The
                current solution does not admit a variable number of tasks.
                The tasks will be indexed by the letter 'k'. 

        Attributes:
            people_per_task: (numpy.ndarray) The number of people per
                task on each day. It's a matrix (n_days x n_tasks).
            is_parent: (numpy.ndarray) An array where is_parent(i) is 0 when
                person 'i' is not a parent and 1 when it is a parent.  
            is_man: (numpy.ndarray) An array where is_man(i) is 0 when
                person 'i' is not a woman and 1 when it is a man.
            not_available: (list) A list of triples (i,j,k) each of which
                represent a non-availalability of person "i" on day "j" for 
                task "k".
            is_allocated: (list) The opposite of not_available, that is,  
                the triple (i,j,k) indicates that person 'i' must work on day
                 'j' for task 'k'.
            solver: (ortools.constraint_solver.pywrapcp.Solver) The ortools
                constraint solver used to define the solution.
            solution: (dictionary) The solution matrix for the given instance.
                It's implemented as a dictionary indexed by triples of (i,j,k),
                where a 1 represents that person 'i' will be allocated in 
                day 'j' for task 'k'.
            solution_flat: (list) A flattened version of the solution.
        """
        self.solver = pywrapcp.Solver("instance_solver")
        self.solution = {}

        # TODO set them as property, with a setter method that reinitializes 
        # the 'solution' variable. Guarantee the consistency of the instance. 
        self._n_people = n_people
        self._n_days = n_days
        self._n_tasks = n_tasks

        self._people_per_task = None
        self._is_parent = None
        self._is_man = None
        self._not_available = []
        self._is_allocated = []

        for i in range(n_people):
            for j in range(n_days):
                for k in range(n_tasks):
                    self.solution[(i, j, k)] = self.solver.BoolVar( \
                                'person{}_day{}_task{}'.format(i, j, k))

        self.solution_flat = [self.solution[(i,j,k)] for i in range(n_people) \
                              for j in range(n_days) for k in range(n_tasks)]        


    # This Section, though long is only concerned with getter and setter 
    # methods for the class using the @property decorator 
    @property
    def n_people(self):
        return self._n_people
    
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
        # Check consistency
        if type(Qjk) != np.ndarray:
            raise TypeError("Object must be numpy.ndarray")
        if Qjk.shape != (self._n_days, self._n_tasks):
            raise ShapeError("Wrong shape to people_per_task, correct \
                  shape should be {}".format((self._n_days, self._n_tasks)))
        self._people_per_task = Qjk

    @property
    def is_parent(self):
        return self._is_parent

    @is_parent.setter
    def is_parent(self, Ci):
        # Check consistency
        if type(Ci) != np.ndarray:
            raise TypeError("Object must be numpy.ndarray")
        if Ci.shape != (self._n_people, ):
            raise ShapeError("Wrong shape to is_parent, correct shape \
                  should be {}".format((self._n_people,)))
        self._is_parent = Ci

    @property
    def is_man(self):
        return self._is_man

    @is_man.setter
    def is_man(self, Gi):
        # Check consistency
        if type(Gi) != np.ndarray:
            raise TypeError("Object must be numpy.ndarray")
        if Gi.shape != (self._n_people, ):
            raise ShapeError("Wrong shape to is_man, correct shape \
                  should be {}".format((self._n_people,)))
        self._is_man = Gi

    @property
    def not_available(self):
        return self._not_available

    @not_available.setter
    def not_available(self, Rijk):
        # Check consistency
        for triple in Rijk:
            if type(triple) == tuple:
                if len(triple) != 3:
                    raise ShapeError("Tuples must have lenght 3")
            else:
                raise TypeError("Elements of not_available must be tuples.")
        self._not_available = Rijk

    @property
    def is_allocated(self):
        return self._is_allocated

    @is_allocated.setter
    def is_allocated(self, Fijk):
        # Check consistency
        for triple in Fijk:
            if type(triple) == tuple:
                if len(triple) != 3:
                    raise ShapeError("Tuples must have lenght 3")
            else:
                raise TypeError("Elements of is_allocated must be tuples.")
        self._is_allocated = Fijk

if __name__ == '__main__':
    inst = Instance(10,5,4)
    Qjk = np.random.random([5,5])
    inst.people_per_task = Qjk

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