from gui_coordinator import GuiCoordinator
from calculator_controller import CalculatorController


def main():
    calculator_controller = CalculatorController()
    coordinator = GuiCoordinator(calculator_controller)
    coordinator.root.mainloop()


if __name__ == "__main__":
    main()
