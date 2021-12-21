#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
from typing import TypeVar

sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

from itertools import product

Literal = tuple[str, bool]
Clause = list[Literal]
Formula = list[Clause]


def simplify_formula(formula: Formula, lit: Literal) -> Formula:
    print("simplifying")
    print(lit)
    print(formula)
    var, val = lit
    reduced = [
        [l for l in c if l[0] != var or len(c) == 1] for c in formula if lit not in c
    ]
    if any(var == v for c in reduced for v, _ in c):
        raise Exception("Formula could not be simplified")
    return reduced


def satisfying_assignment(formula: list[list[tuple[str, bool]]]):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    variables = form_vars(formula)
    print(f"Solving formula with len={form_len(formula)}, size={form_size(formula)}")

    # initial simplification step
    init_result = {}
    while True:
        for clause in formula:
            if len(clause) == 1:
                init_result[clause[0][0]] = clause[0][1]
                try:
                    formula = simplify_formula(formula, clause[0])
                    break
                except Exception:
                    print("Could not simplify formula with known literal")
                    return None
        else:
            break

    print(f"Reduced formula to len={form_len(formula)}, size={form_size(formula)}")
    reduced_variables = form_vars(formula)
    if len(reduced_variables) == 0:
        return init_result

    for var in reduced_variables:
        for val in [True, False]:
            lit = (var, val)
            print(f"Trying '{lit}'")
            try:
                new_formula = simplify_formula(formula, (var, val))
            except Exception:
                print("Could not simplify formula")
                continue

            result = satisfying_assignment(new_formula)
            # print(f"Trying '{lit}' with reduced f size: {form_size(new_formula)}")
            # print(new_formula)
            # remaining_vars = form_vars(new_formula)
            # remaining_list = list(remaining_vars)
            # result = None if len(new_formula) else {}
            # for vals in product(*[[True, False] for _ in remaining_list]):
            #     print(f"vals={vals}")
            #     lits = [(var, val) for var, val in zip(remaining_list, vals)]
            #     print(f"lits={lits}")
            #     if all(any(lit in c for lit in lits) for c in new_formula):
            #         result = [lit] + lits
            if result:
                print(f"Found result for lit={lit}")
                print(result)
                # result_dict = dict(result)
                # print(result_dict)
                missing_vars = reduced_variables - result.keys()
                print(missing_vars)
                return {
                    **init_result,
                    **result,
                    **{k: False for k in missing_vars},
                }
    return None


def form_len(f: Formula) -> int:
    return len(f)


def form_size(f: Formula) -> int:
    return sum(len(c) for c in f)


def form_vars(f: Formula) -> set[str]:
    return set(var for clause in f for var, _ in clause)


def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    raise NotImplementedError


if __name__ == "__main__":
    import doctest

    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
