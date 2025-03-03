"""
Finite Field Calculator - Main Entry Point

This module serves as the entry point for the Finite Field Calculator application,
which allows users to perform arithmetic operations in finite fields of the form GF(p^n).

Author: Daniel Lewis
Version: 1.0 (March 2025)
GitHub: https://github.com/danielqlewis/FF_Calculator
"""

from gui_coordinator import GuiCoordinator
from calculator_controller import CalculatorController


def main():
    calculator_controller = CalculatorController()
    coordinator = GuiCoordinator(calculator_controller)
    coordinator.root.mainloop()


if __name__ == "__main__":
    main()
