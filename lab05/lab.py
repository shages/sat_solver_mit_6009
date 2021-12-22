#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
from typing import TypeVar

sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

from itertools import product, combinations
import math
from collections import defaultdict
import satrs

Literal = tuple[str, bool]
Clause = list[Literal]
Formula = list[Clause]


def simplify_formula(formula: Formula, assignment: Literal) -> Formula:
    """Simplify a formula for a given variable assignment"""
    var, val = assignment
    reduced = []
    for clause in formula:
        # clauses with a single assertion which contradicts this assertion
        # lead to an unsatisfiable formula
        if len(clause) == 1 and clause[0][0] == var and clause[0][1] != val:
            raise Exception("Formula could not be simplified")

        # clauses with this assertion reduce to true and can be removed
        # from the formula
        if assignment in clause:
            continue

        # remaining clauses can exclude the asserted variable, as the other
        # variables in the clause may yet be satisfiable
        reduced.append([l for l in clause if l[0] != var])

    return reduced


def check_contradict(f: Formula):
    """Check if there is a contradiction between clauses"""
    marks = {}
    for clause in f:
        if len(clause) != 1:
            continue
        var, val = clause[0]
        if var in marks:
            if marks[var] != val:
                raise Exception(f"contradition on {var}")
        else:
            marks[var] = val


def form_len(f: Formula) -> int:
    """Sum of clauses in formula"""
    return len(f)


def form_size(f: Formula) -> int:
    """Sum of literals in formula"""
    return sum(len(c) for c in f)


def form_vars(f: Formula) -> set[str]:
    """Set of variables in formula"""
    return set(var for clause in f for var, _ in clause)


def _satisfying_assignment(formula: list[list[tuple[str, bool]]]):
    try:
        check_contradict(formula)
    except Exception:
        return None

    variables = form_vars(formula)
    if len(variables) == 0:
        return {}

    # check for obvious simplification
    for clause in formula:
        if len(clause) == 1:
            try:
                new_formula = simplify_formula(formula, clause[0])
                result = _satisfying_assignment(new_formula)
                if result is not None:
                    missing_vars = (
                        variables - form_vars(new_formula) - set(clause[0][0])
                    )
                    return {
                        **result,
                        **{k: False for k in missing_vars},
                        clause[0][0]: clause[0][1],
                    }
                return None
            except Exception:
                return None

    # pick arbitrary variable to assign, in this case the first
    # variable of the first literal of the first clause
    for lit in product([formula[0][0][0]], [True, False]):
        try:
            new_formula = simplify_formula(formula, lit)
        except Exception:
            continue

        result = _satisfying_assignment(new_formula)
        if result is not None:
            missing_vars = variables - form_vars(new_formula) - set(lit[0])
            return {
                **result,
                **{k: False for k in missing_vars},
                lit[0]: lit[1],
            }
    return None


def opt_clauses_by_len(formula: Formula) -> Formula:
    """Prioritize short clauses first to simplify quicker"""
    return list(sorted(formula, key=lambda clause: len(clause)))


def opt_clauses_by_impact(formula: Formula) -> Formula:
    """Prioritize variables which affect more clauses"""
    counts = defaultdict(int)
    for clause in formula:
        for var, val in clause:
            counts[var] += 1
    return list(
        sorted(
            formula,
            key=lambda clause: math.prod([counts[v] for v, _ in clause]),
            reverse=True,
        ),
    )


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
    # ensure type is list[list[tuple]]
    trans = [[(a, b) for a, b in c] for c in formula]
    # return _satisfying_assignment(trans)
    return satrs.sat(trans)


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

    students = student_preferences.keys()
    rooms = room_capacities.keys()
    rules = []

    # 1 - students assigned to prefs only

    # simple assertions
    for student, prefs in student_preferences.items():
        rules.append([(f"{student}_{pref}", True) for pref in prefs])

    # 2 - each student assigned to exactly one room

    # alice_b or alice_k or alice_p
    # = (not alice_b or not_alice_c) and (not alice_k or not alice_c) and (not alice_k or not alice_b)
    for student in students:
        for room_combs in combinations(rooms, 2):
            rules.append([(f"{student}_{room}", False) for room in room_combs])

    # 3 - room capacity

    # 2 people: (alice_k and bob_k) or (alice_k and charles_k) or (alice_k and dana_k) or (bob_k and charles_k) or (bob_k and dana_k) or (charles_k and dana_k)
    # 1 person: (not alice_k or not bob_k) and (not alice_k or not charles_k) ...
    for room, capacity in room_capacities.items():
        if capacity >= len(students):
            continue
        for student_comb in combinations(students, capacity + 1):
            rules.append([(f"{student}_{room}", False) for student in student_comb])

    return rules


if __name__ == "__main__":
    import doctest

    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
