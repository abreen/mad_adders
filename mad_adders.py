# mad_adders.py
# Exploring the power of genetic algorithms

from random import choice, uniform

def list_to_int(x):
    return sum([10**i * x[i] for i in range(len(x))])

def list_sum(a, b):
    return list_to_int(a) + list_to_int(b)


# We will ultimately be evaluating the performance of a particular
# addition algorithm by testing candidates with input and seeing
# how close they end up to the right answer. We'll need a function
# to generate two random numbers that should be added, as well as
# the correct answer. We will represent the numbers as lists of
# one-digit numbers, to encourage handling addition one digit
# at a time.
def generate_problem(min_size, max_size):
    """Generates a triple (a, b, c) where a and b are lists of
    integers between min_size and max_size (exclusive) long, and
    c is the sum of a and b if they are interpreted as lists whose
    leftmost element is the least significant digit. The digits
    in each list will never create a carry out of a column.
    """
    size = choice(range(min_size, max_size))

    a = [choice(range(10)) for _ in range(size)]
    b = [choice(range(10)) % (10 - a[i]) for i in range(size)]

    return a, b, list_sum(a, b)


# We'll write a function that helps us visualize a given
# addition problem.
def print_problem(a, b):
    a_str = ''.join(map(str, a))[::-1]
    b_str = ''.join(map(str, b))[::-1]
    print(a_str + ' + ' + b_str + ' = ?')


# Just as in real life, we'll represent an algorithm as a
# list of steps. However, we'll stick to iterative algorithms
# (not recursion). We'll also restrict ourselves to a finite
# set of kinds of steps. We'll give each candidate algorithm
# a choice of different binary operations (e.g., addition and
# multiplication of one-digit numbers) and restrict them to a
# looping style.

def add(x, y):
    return x + y

def mult(x, y):
    return x * y

def div(x, y):
    return x / y

def exp(x, y):
    return x ** y

def rand_in_len(seq):
    return choice(range(len(seq)))

def zero(seq):
    return 0

def append(prev, new):
    return prev + [new]

def prepend(prev, new):
    return [new] + prev

def replace(prev, new):
    return [new]

def insert_rand(prev, new):
    i = choice(range(len(prev) + 1))
    return prev[:i] + [new] + prev[i:]


BINARY_OPERATIONS = [add, mult, div, exp]
ACCUMULATORS = [append, prepend, replace, insert_rand]
CHOOSERS = [len, rand_in_len, zero]

# We'll define the loop structure that any candidate must follow.
def loop(x, y, op, acc, chooser):
    z = []
    for i in range(chooser(x)):
        z = acc(z, op(x[i], y[i]))

    return z


# We'll devise a way to randomly generate candidate algorithms.
# This will serve as our "seed" population of algorithms.
def generate_candidate():
    op = choice(BINARY_OPERATIONS)

    # Our "accumulator" will be a binary function that will be
    # used to combine the accumulated previous results with
    # a new result.
    acc = choice(ACCUMULATORS)

    # Chooses when to stop iteration.
    chooser = choice(CHOOSERS)

    return op, acc, chooser


# We'll also give ourselves a way to visualize a candidate
# addition algorithm using Python-like syntax.
def algorithm_name(op, acc, chooser):
    op_s, acc_s, chooser_s = op.__name__, acc.__name__, chooser.__name__
    return "add_{}".format(op_s[0] + acc_s[0] + chooser_s[0])

def print_algorithm(op, acc, chooser):
    op_s, acc_s, chooser_s = op.__name__, acc.__name__, chooser.__name__

    s = "def {}(x, y):\n".format(algorithm_name(op, acc, chooser))
    s += "    z = []\n"
    s += "    for i in range({}(x)):\n".format(chooser_s)
    s += "        z = {}(z, {}(x[i], y[i]))\n".format(acc_s, op_s)
    s += "    return z"
    print(s)


# At the end of each round, we'll need to do some artificial selection.
# We need an evaluation function of each candidate algorithm.
# We'll say that an algorithm is better than the other candidates if,
# when every candidate is tested on the same addition problems, it produces
# a final answer that is closest to the actual answer. Note: if an
# algorithm produces a serious error while it's executing (e.g., division
# by zero), we'll rate it very poorly (by adding a large number
# to its final score).
def candidate_score(algorithm, problems):
    op, acc, chooser = algorithm
    alg_name = algorithm_name(*algorithm)
    score = 0

    for a, b, answer in problems:
        #print_problem(a, b)
        #print("correct answer:", answer)

        try:
            alg_ans = loop(a, b, op, acc, chooser)

            if any(map(lambda x: x > 9, alg_ans)):
                #print("(at least one digit was > 9)")
                raise ValueError()

            alg_ans_val = list_to_int(alg_ans)
            #print("algorithm produced:", alg_ans_val)

            score += abs(alg_ans_val - answer)
        except:
            score += 999

    print("{} score: {}".format(alg_name, score))
    return score / len(problems)


# We'll use Python's sorted() function to produce a list of candidates
# that are sorted from best to worst. Then, after each round, we'll take
# the top-performing algorithms.
def sort_candidates(all_candidates, problems):
    def score(candidate):
        return candidate_score(candidate, problems)

    return sorted(all_candidates, key=score)


# Finally, we need a way to generate a new (larger) population of
# algorithms from a (smaller) set of more fit algorithms. This function will
# return a list of new algorithms that are produced genetically from the
# input algorithms.
def repopulate(candidates):
    children = set(candidates)

    for c1 in candidates:
        for c2 in candidates:
            if c1 == c2:
                continue

            # for each trait, we'll either take one parent trait
            # or we'll "mutate" and choose any other trait at random;
            # "mutations" will be rarer, however
            if uniform(0, 1) > 0.25:
                op = choice([c1[0], c2[0]])
            else:
                op = choice([x for x in BINARY_OPERATIONS \
                             if x not in [c1[0], c2[0]]])

            if uniform(0, 1) > 0.25:
                acc = choice([c1[1], c2[1]])
            else:
                acc = choice([x for x in ACCUMULATORS \
                             if x not in [c1[1], c2[1]]])

            if uniform(0, 1) > 0.25:
                chooser = choice([c1[2], c2[2]])
            else:
                chooser = choice([x for x in CHOOSERS \
                             if x not in [c1[2], c2[2]]])

            children.add((op, acc, chooser))

    return children


# We'll start by randomly generating "seed" candidates.
num_candidates = int(input('How many "seed" candidates? '))

candidates = {generate_candidate() for _ in range(num_candidates)}

num_rounds = int(input("How many rounds? "))
num_problems = int(input("How many problems per round? "))

for r in range(num_rounds):
    print("=== ROUND {} ===".format(r))

    problems = [generate_problem(2, 3) for _ in range(num_problems)]
    best = sort_candidates(candidates, problems)[:5]

    print("---")
    print("top candidates:")
    for c in best:
        print(algorithm_name(*c))

    print("---")
    print("best algorithm so far:")
    print_algorithm(*best[0])

    # Lastly, we generate new candidate algorithms by genetically
    # combining the strongest algorithms.
    candidates = repopulate(best)
