import math
import random
from abc import ABC, abstractclassmethod, abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import Dict, List, Tuple

from lark import Lark, Transformer, Tree, Visitor
from lark.grammar import NonTerminal, Terminal
from lark.tree_matcher import TreeMatcher


class Compiler(ABC):
    @abstractmethod
    def compile(
        self,
        expression: Tree,
    ):
        raise NotImplementedError


class Grammar(object):
    def __init__(
        self,
        grammar_spec: str,
        start: str = None,
        sampling_weights: Dict[str, List[float]] = None,
        primitives: List[str] = None,
    ):
        self._grammar_spec = grammar_spec
        self._start_name = start
        self._sampling_weights = sampling_weights or {}
        self._primitives = set(primitives) if primitives else None

        self._lark_parser = Lark(
            grammar_spec,
            start=start,
            propagate_positions=True,
            parser="lalr",
            maybe_placeholders=False,
            lexer="contextual",
        )

        self._tree_matcher = TreeMatcher(self._lark_parser)

        self._initialize_sampler_constants()

        self._lark_parser_for_start = {
            k.value: Lark(
                grammar_spec,
                start=k.value,
                propagate_positions=True,
                parser="lalr",
                maybe_placeholders=False,
                lexer="contextual",
            )
            for k in self._nonterminals.keys()
        }

    def _initialize_sampler_constants(self):
        start = self.lark_parser.options.start
        terminals, rules, ignore_names = self.lark_parser.grammar.compile(start, ())
        ignore_names_set = set(ignore_names)

        names_to_symbols = {}
        for r in rules:
            t = r.origin
            names_to_symbols[t.name] = t

        terminal_map = {}
        for t in terminals:
            names_to_symbols[t.name] = Terminal(t.name)
            if t.name in ignore_names_set:
                continue
            s = t.pattern.value
            terminal_map[t.name] = s

        nonterminals = {}

        for rule in rules:
            nonterminals.setdefault(rule.origin.name, []).append(tuple(rule.expansion))

        allowed_rules = {*terminal_map, *nonterminals}
        while dict(nonterminals) != (
            nonterminals := {
                k: clean
                for k, v in nonterminals.items()
                if (clean := [x for x in v if all(r.name in allowed_rules for r in x)])
            }
        ):
            allowed_rules = {*terminal_map, *nonterminals}

        self._terminal_map = terminal_map
        self._rev_terminal_map = {v: k for k, v in terminal_map.items()}
        self._nonterminals = nonterminals
        self._names_to_symbols = names_to_symbols

        self._vocabulary = sorted(list(set(terminal_map.values())))

        def _compute_min_primitives(x, path=None):
            if path is None:
                path = []
            path_lookup = set(path)

            if x.name in path_lookup:
                return float("inf")

            if x.name in self._primitives:
                return 1

            if isinstance(x, Terminal):
                return 0

            productions = self._nonterminals.get(x.name, [])
            new_path = path + [x.name]

            sub_min_primitives = [
                sum(_compute_min_primitives(x_, new_path) for x_ in p)
                for p in productions
            ]

            rv = min(
                sub_min_primitives,
                default=float("inf"),
            )

            return rv

        all_terminals_and_nonterminals = set()
        for k, v in nonterminals.items():
            for p in v:
                for s in p:
                    all_terminals_and_nonterminals.add(s)

        self._min_primitives = {}
        for x in all_terminals_and_nonterminals:
            self._min_primitives[x] = _compute_min_primitives(x)

        self._min_primitives_choices = {}
        for x in all_terminals_and_nonterminals:
            if isinstance(x, Terminal):
                continue

            choices = self._nonterminals[x.name]
            self._min_primitives_choices[x] = [
                sum(self._min_primitives[y] for y in p) for p in choices
            ]

        self._start_symbol = self._names_to_symbols[self._start_name]

    @property
    def vocabulary(self):
        return self._vocabulary

    @property
    def vocabulary_map(self):
        return self._terminal_map

    @property
    def rev_vocabulary_map(self):
        return self._rev_terminal_map

    def parse(self, expression: str):
        return self.lark_parser.parse(expression)

    @property
    def lark_parser(self):
        return self._lark_parser

    @property
    def tree_matcher(self):
        return self._tree_matcher

    @property
    def start_symbol(self):
        return self._start_symbol

    @property
    def primitives(self):
        return self._primitives

    @property
    def names_to_symbols(self):
        return self._names_to_symbols

    @property
    def nonterminals(self):
        return self._nonterminals


class Environment(ABC):
    @abstractproperty
    def grammar(self) -> Grammar:
        raise NotImplementedError

    @abstractproperty
    def compiler(self) -> Compiler:
        raise NotImplementedError

    @property
    def observation_compiler(self) -> Compiler:
        return self.compiler

    @abstractclassmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractproperty
    def compiled_shape(self) -> Tuple[int, ...]:
        raise NotImplementedError


_grammar_spec = r"""
s: binop | circle | quad

// Number quantized 0 to 16.
number: "0" -> zero | "1" -> one | "2" -> two | "3" -> three | "4" -> four | "5" -> five | "6" -> six | "7" -> seven | "8" -> eight | "9" -> nine | "A" -> ten | "B" -> eleven | "C" -> twelve | "D" -> thirteen | "E" -> fourteen | "F" -> fifteen

// angles [0, 45, 90, 135, 180, 225, 270, 315]
angle: "G" -> zerodeg | "H" -> onedeg | "I" -> twodeg | "J" -> threedeg | "K" -> fourdeg | "L" -> fivedeg | "M" -> sixdeg | "N" -> sevendeg

// (Circle radius x y)
circle: "(" "Circle" " " number " " number " " number ")"

// (Quad x0 y0 x1 y1 x2 y2 x3 y3)
// quad: "(" "Quad" " " number " " number " " number " " number " " number " " number " " number " " number ")"

// (Quad x y w h angle)
quad: "(" "Quad" " " number " " number " " number " " number " " angle ")"

binop: "(" op " " s " " s ")"

op: "+" -> add | "-" -> subtract

%ignore /[\t\n\f\r]+/ 
"""


_CANVAS_WIDTH = 128
_CANVAS_HEIGHT = 128

_SCALE_X = _CANVAS_WIDTH / 32
_SCALE_Y = _CANVAS_HEIGHT / 32


class CSG2DAtoPath(Transformer):
    def __init__(
        self,
        visit_tokens: bool = True,
    ) -> None:
        super().__init__(visit_tokens)

    def quad(self, children):
        x, y, w, h, angle_degrees = children

        x *= 2
        y *= 2
        w *= 2
        h *= 2

        # Coordinates of the four corners of the quad.
        # (x, y) is the center of the quad.
        x0 = x - w / 2
        y0 = y - h / 2
        x1 = x + w / 2
        y1 = y - h / 2
        x2 = x + w / 2
        y2 = y + h / 2
        x3 = x - w / 2
        y3 = y + h / 2

        # Rotate the quad.
        angle = math.radians(angle_degrees)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        x0, y0 = (
            x + (x0 - x) * cos_angle - (y0 - y) * sin_angle,
            y + (x0 - x) * sin_angle + (y0 - y) * cos_angle,
        )
        x1, y1 = (
            x + (x1 - x) * cos_angle - (y1 - y) * sin_angle,
            y + (x1 - x) * sin_angle + (y1 - y) * cos_angle,
        )
        x2, y2 = (
            x + (x2 - x) * cos_angle - (y2 - y) * sin_angle,
            y + (x2 - x) * sin_angle + (y2 - y) * cos_angle,
        )
        x3, y3 = (
            x + (x3 - x) * cos_angle - (y3 - y) * sin_angle,
            y + (x3 - x) * sin_angle + (y3 - y) * cos_angle,
        )

        return f"quad {x0} {y0} {x1} {y1} {x2} {y2} {x3} {y3}"

    def circle(self, children):
        r, x, y = children
        r *= 2
        x *= 2
        y *= 2
        return f"circle {r} {x} {y}"

    def binop(self, children):
        op, left, right = children

        res = []

        if isinstance(left, list):
            res.extend(left)
        else:
            res.append(left)

        res.append(op)

        if isinstance(right, list):
            res.extend(right)
        else:
            res.append(right)

        return res

    def add(self, children):
        return "+"

    def subtract(self, children):
        return "-"

    def s(self, children):
        return children[0]

    def zero(self, _):
        return 0

    def one(self, _):
        return 1

    def two(self, _):
        return 2

    def three(self, _):
        return 3

    def four(self, _):
        return 4

    def five(self, _):
        return 5

    def six(self, _):
        return 6

    def seven(self, _):
        return 7

    def eight(self, _):
        return 8

    def nine(self, _):
        return 9

    def ten(self, _):
        return 10

    def eleven(self, _):
        return 11

    def twelve(self, _):
        return 12

    def thirteen(self, _):
        return 13

    def fourteen(self, _):
        return 14

    def fifteen(self, _):
        return 15

    def zerodeg(self, _):
        return 0

    def onedeg(self, _):
        return 45

    def twodeg(self, _):
        return 90

    def threedeg(self, _):
        return 135

    def fourdeg(self, _):
        return 180

    def fivedeg(self, _):
        return 225

    def sixdeg(self, _):
        return 270

    def sevendeg(self, _):
        return 315


class CSG2DACompiler(Compiler):
    def __init__(self) -> None:
        super().__init__()
        self._expression_to_path = CSG2DAtoPath()

    def _get_path(self, expression: Tree):
        paths_and_ops = self._expression_to_path.transform(expression)
        return paths_and_ops

    def compile(self, expression: Tree):
        return self._get_path(expression)


class CSG2DA(Environment):
    def __init__(self) -> None:
        super().__init__()

        self._grammar = Grammar(
            _grammar_spec,
            start="s",
            primitives=["circle", "quad"],
        )

        self._compiler = CSG2DACompiler()
        # self._observation_compiler = CSG2DASketchCompiler()
        # self._goal_checker = BinaryIOUGoalChecker()

    @property
    def grammar(self) -> Grammar:
        return self._grammar

    @property
    def compiler(self) -> Compiler:
        return self._compiler

    @property
    def observation_compiler(self) -> Compiler:
        return self._observation_compiler

    @property
    def compiled_shape(self) -> Tuple[int, ...]:
        return None

    @classmethod
    def name(self) -> str:
        return "csg2da"

    def goal_reached(self, compiledA, compiledB) -> bool:
        return self._goal_checker.goal_reached(compiledA, compiledB)


class GrammarSampler(ABC):
    def __init__(self, grammar: Grammar):
        self._grammar = grammar

    @property
    def grammar(self) -> Grammar:
        return self._grammar

    @abstractmethod
    def sample(self, start, **kwargs) -> str:
        raise NotImplementedError


class NaiveRandomSampler(GrammarSampler):
    def sample(self, start) -> str:
        def _sample_inner(current):
            if isinstance(current, Terminal):
                return self.grammar._terminal_map[current.name]

            choices = self.grammar._nonterminals[current.name]
            weights = self.grammar._sampling_weights.get(current.name)

            choice = random.choices(choices, weights=weights)[0]

            return "".join(self.sample(x) for x in choice)

        return _sample_inner(start)


@dataclass
class DerivationChoice:
    partial_expression: str
    unexpanded_start: int
    unexpanded_end: int
    expansion_choices: list
    expansion_index: int
    unexpanded_rule_name: str

    @property
    def pretty(self) -> str:
        rv = self.partial_expression + "\n"
        rv += " " * self.unexpanded_start + "^" * (
            self.unexpanded_end - self.unexpanded_start
        )
        rv += f" -> {self.expansion_choices[self.expansion_index]}"
        return rv


class ConstrainedRandomSampler(GrammarSampler):
    def sample(
        self,
        start,
        min_primitives=4,
        max_primitives=10,
        return_steps=False,
    ):
        num_primitives = random.randint(min_primitives, max_primitives)
        min_primitives = num_primitives
        max_primitives = num_primitives

        assert (
            min_primitives <= max_primitives
        ), "min_primitives must be <= max_primitives"

        tree = Tree(start, [])
        choice_history = []

        def tree_to_string(tree: Tree) -> str:
            if not tree.children:
                if isinstance(tree.data, Terminal):
                    return self.grammar._terminal_map[tree.data.name]
                return ""
            return "".join(tree_to_string(child) for child in tree.children)

        def tree_to_string_node_position(tree: Tree, search_node: Tree):
            def _f(tree: Tree, search_node: Tree, current_start=0) -> tuple[str, int]:
                found = -1

                if tree is search_node:
                    found = current_start

                if not tree.children:
                    if isinstance(tree.data, Terminal):
                        return self.grammar._terminal_map[tree.data.name], found
                    return f"<{tree.data.name}>", found

                current = current_start
                current_rv = ""
                for child in tree.children:
                    stringified, c_found = _f(child, search_node, current)
                    if c_found != -1:
                        found = c_found
                    current_rv += stringified
                    current += len(stringified)

                return current_rv, found

            rv, start = _f(tree, search_node)
            end = start + len(f"<{search_node.data.name}>")
            return rv, start, end

        def pick_expansion(nt, choose_fn=None):
            if return_steps:
                tree_string, start, end = tree_to_string_node_position(tree, nt)

            choices = self.grammar._nonterminals[nt.data.name]
            choice_costs = self.grammar._min_primitives_choices[nt.data]

            if choose_fn is None:
                selected_choices = choices
            else:
                chosen_cost = choose_fn(choice_costs)
                selected_choices = [
                    choice
                    for choice, cost in zip(choices, choice_costs)
                    if cost == chosen_cost
                ]

            chosen = random.choice(selected_choices)

            if return_steps:
                choice_history.append(
                    DerivationChoice(
                        partial_expression=tree_string,
                        unexpanded_start=start,
                        unexpanded_end=end,
                        expansion_choices=choices,
                        expansion_index=choices.index(chosen),
                        unexpanded_rule_name=nt.data.name,
                    )
                )

            return chosen

        def num_primitives_in_tree(tree):
            return sum(num_primitives_in_tree(child) for child in tree.children) + int(
                tree.data.name in self.grammar._primitives
            )

        def get_unexpanded(tree):
            if not len(tree.children):
                if isinstance(tree.data, NonTerminal):
                    return [tree]
                return []

            rv = []
            for child in tree.children:
                rv.extend(get_unexpanded(child))
            return rv

        current_primitives = 0
        unexpanded_min_primitives = self.grammar._min_primitives[start]
        queue = [tree]

        while queue:
            tree_potential = current_primitives + unexpanded_min_primitives

            if tree_potential < min_primitives:
                choice_fn = max
            elif tree_potential > min_primitives and tree_potential < max_primitives:
                choice_fn = None
            else:
                choice_fn = min

            current_unexpanded = random.choice(queue)

            expansion = pick_expansion(current_unexpanded, choice_fn)
            current_primitives += sum(
                item.name in self.grammar._primitives for item in expansion
            )
            unexpanded_min_primitives -= self.grammar._min_primitives[
                current_unexpanded.data
            ]
            unexpanded_min_primitives += sum(
                self.grammar._min_primitives[item] for item in expansion
            )
            current_unexpanded.children = [Tree(item, []) for item in expansion]
            queue.remove(current_unexpanded)
            queue.extend(
                [
                    child
                    for child in current_unexpanded.children
                    if isinstance(child.data, NonTerminal)
                ]
            )

        expression = tree_to_string(tree)

        if return_steps:
            return expression, choice_history

        return expression


@dataclass(frozen=True)
class Mutation(object):
    start: int
    end: int
    replacement: str
    edit_probs: List[Tuple[int, int, float]] = None

    def apply(self, expression: str) -> str:
        return expression[: self.start] + self.replacement + expression[self.end :]

    def reverse(self, expression: str) -> "Mutation":
        new_start = self.start
        new_end = self.start + len(self.replacement)
        return Mutation(new_start, new_end, expression[self.start : self.end])

    def pretty(self, expression: str) -> str:
        pointer = (
            " " * self.start
            + "^" * (self.end - self.start)
            + " --> "
            + self.replacement
        )
        return expression + "\n" + pointer

    def shift_other(self, other: "Mutation") -> "Mutation":
        """How should another mutation be shifted when this mutation is applied?"""

        if other.start < self.start:
            return other

        if other.start >= self.end:
            return Mutation(
                other.start + len(self.replacement) - (self.end - self.start),
                other.end + len(self.replacement) - (self.end - self.start),
                other.replacement,
            )

        raise ValueError("Mutations overlap!")


class AddParents(Visitor):
    def __default__(self, tree):
        for subtree in tree.children:
            if isinstance(subtree, Tree):
                subtree.parent = tree


class CountPrimitives(Visitor):
    def __init__(self, primitives) -> None:
        super().__init__()
        self._primitives = primitives

    def __default__(self, tree):
        self_count = tree.data in self._primitives
        count = sum(child.primitive_count for child in tree.children) + self_count
        tree.primitive_count = count


def nodes_with_max_primitives(tree: Tree, primitive_set, max_primitives):
    CountPrimitives(primitive_set).visit(tree)
    return [x for x in tree.iter_subtrees() if x.primitive_count <= max_primitives]


def random_mutation(
    expression: str,
    grammar: Grammar,
    sampler: ConstrainedRandomSampler,
    selection_max_primitives: int = 2,
    replacement_max_primitives: int = 2,
    max_attempts_difference: int = 100,
) -> Mutation:
    tree = grammar.parse(expression)
    AddParents().visit(tree)

    candidates = nodes_with_max_primitives(
        tree, grammar.primitives, selection_max_primitives
    )

    candidate_primitive_counts = [x.primitive_count for x in candidates]
    unique_primitive_counts = list(set(candidate_primitive_counts))
    candidate_primitive_count = random.choice(unique_primitive_counts)
    candidates_with_count = [
        x for x in candidates if x.primitive_count == candidate_primitive_count
    ]
    candidates = candidates_with_count

    while True:
        if not candidates:
            return None

        candidate = random.choice(candidates)

        if not hasattr(candidate, "parent"):
            # We have the root, sample a new expression.
            start = 0
            end = len(expression)
            sub_expression = expression[start:end]
            start_symbol = grammar.start_symbol
        else:
            parent = candidate.parent
            start = candidate.meta.start_pos
            end = candidate.meta.end_pos

            sub_expression = expression[start:end]
            self_child_index = parent.children.index(candidate)

            matched = grammar.tree_matcher.match_tree(parent, parent.data)
            rule_name = matched.children[self_child_index].data
            options = grammar.nonterminals[rule_name]

            if len(options) <= 1:
                candidates.remove(candidate)
                continue

            start_symbol = grammar.names_to_symbols[rule_name]

        attempts = 0
        while True:
            replacement_expression = sampler.sample(
                start_symbol,
                min_primitives=0,
                max_primitives=replacement_max_primitives,
            )
            attempts += 1

            if replacement_expression != sub_expression:
                break

            if attempts > max_attempts_difference:
                candidates.remove(candidate)
                break

        mutation = Mutation(start, end, replacement_expression)
        return mutation


env = CSG2DA()
sampler = ConstrainedRandomSampler(env.grammar)


def sample():
    expr = sampler.sample(env.grammar.start_symbol, 4, 4)
    return expr


def expression_to_ops(expr):
    rv = env.compiler.compile(env.grammar.parse(expr))

    if isinstance(rv, str):
        return [rv]
    return rv


def get_mutated(expr):
    m = random_mutation(expr, env.grammar, sampler)
    return m.apply(expr)


def parse_expression(expr):
    return env.grammar.parse(expr)
