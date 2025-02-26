import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from gui_coordinator import GuiCoordinator
from calculator_controller import CalculatorController


def main():
    root = tk.Tk()
    calculator_controller = CalculatorController()
    GuiCoordinator(root, calculator_controller, [tk, ttk, messagebox])
    root.mainloop()


if __name__ == "__main__":
    main()