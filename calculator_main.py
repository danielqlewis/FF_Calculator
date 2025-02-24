import tkinter as tk
from gui_coordinator import GuiCoordinator
from calculator_controller import CalculatorController

def main():
    root = tk.Tk()
    calculator_controller = CalculatorController()
    GuiCoordinator(root, calculator_controller)
    root.mainloop()


if __name__ == "__main__":
    main()