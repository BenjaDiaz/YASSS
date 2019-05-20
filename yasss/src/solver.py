import logging
import pycosat
from typing import List

logger = logging.getLogger(__name__)


class SudokuSolver:

    def _cell_to_literal(self, row: int, column: int, value: int):
        return 81 * (row - 1) + 9 * (column - 1) + value

    def _literal_to_value(self, row: int, column: int, literal: int):
        return literal - 81 * (row - 1) - 9 * (column - 1)

    def _build_individual_cell_clauses(self) -> List[List[int]]:
        """
        Generates individual cell clauses accepting exactly one value between 1 and 9 per cell.
        :return: List of clauses in CNF.
        """
        cnf = []
        for row in range(1, 10):
            for column in range(1, 10):
                individual_cell_clause = []
                for value in range(1, 10):
                    literal = self._cell_to_literal(row, column, value)
                    individual_cell_clause.append(literal)
                    for exclusion_value in range(value + 1, 10):
                        exclusion_literal = self._cell_to_literal(row, column, exclusion_value)
                        cnf.append([-literal, -exclusion_literal])
                cnf.append(individual_cell_clause)
        return cnf

    def _build_row_clauses(self) -> List[List[int]]:
        """
        Generates row clauses accepting exactly one value between 1 and 9 per row.
        :return: List of clauses in CNF.
        """
        cnf = []
        for row in range(1, 10):
            for value in range(1, 10):
                row_clause = []
                for column in range(1, 10):
                    literal = self._cell_to_literal(row, column, value)
                    row_clause.append(literal)
                    for exclusion_value in range(value + 1, 10):
                        exclusion_literal = self._cell_to_literal(row, column, exclusion_value)
                        cnf.append([-literal, -exclusion_literal])
                cnf.append(row_clause)
        return cnf

    def _build_column_clauses(self) -> List[List[int]]:
        """
        Generates column clauses accepting exactly one value between 1 and 9 per column.
        :return: List of clauses in CNF.
        """
        cnf = []
        for column in range(1, 10):
            for value in range(1, 10):
                column_clause = []
                for row in range(1, 10):
                    literal = self._cell_to_literal(row, column, value)
                    column_clause.append(literal)
                    for exclusion_value in range(value + 1, 10):
                        exclusion_literal = self._cell_to_literal(row, column, exclusion_value)
                        cnf.append([-literal, -exclusion_literal])
                cnf.append(column_clause)
        return cnf

    def _build_block_clauses(self) -> List[List[int]]:
        """
        Generates block clauses accepting exactly one value between 1 and 9 per 3x3 block.
        :return: List of clauses in CNF.
        """
        cnf = []
        for i in 0, 3, 6:
            for j in 0, 3, 6:
                for value in range(1, 10):
                    block_clause = []
                    for row in range(1, 4):
                        for column in range(1, 4):
                            literal = self._cell_to_literal(row + i, column + j, value)
                            block_clause.append(literal)
                    cnf.append(block_clause)
        return cnf

    def _build_used_cell_clauses(self, sudoku: List[List[int]]) -> List[List[int]]:
        """
        Generates clauses for each value already present on the sudoku board.
        :return: List of clauses in CNF.
        """
        cnf = []
        for row in range(1, 10):
            for column in range(1, 10):
                value = sudoku[row - 1][column - 1]
                if value:
                    literal = self._cell_to_literal(row, column, value)
                    cnf.append([literal])
        return cnf

    def _find_solution(self, cnf: List[List[int]]) -> List[List[int]]:
        """
        Finds solution using pycoSAT solver.
        :param cnf: List of clauses in CNF.
        :return: Solved sudoku board represented as a 2D matrix.
        """
        literals = []
        for literal in pycosat.solve(cnf):
            if literal > 0:
                literals.append(literal)
        solution = []
        for i in range(1, 10):
            solution.append([])
        for i, literal in enumerate(literals):
            row = (i // 9) + 1
            column = i - ((row - 1) * 9) + 1
            solution[row - 1].append(self._literal_to_value(row, column, literal))
        return solution

    def solve(self, sudoku: List[List[int]]) -> List[List[int]]:
        """
        Solves a sudoku using a SAT solver.
        :param sudoku: 2D matrix representing a sudoku board. 0's are empty spaces.
        :return: Solves matrix.
        """
        cnf = [*self._build_individual_cell_clauses(),
               *self._build_row_clauses(),
               *self._build_column_clauses(),
               *self._build_block_clauses(),
               *self._build_used_cell_clauses(sudoku)]

        solution = self._find_solution(cnf)

        logger.debug("Solved sudoku: %s" % solution)

        return solution
