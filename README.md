# Finite Field Calculator

A Python-based calculator for performing arithmetic in finite fields of the form GF(p^n), where p is prime and n is a positive integer. The calculator supports:
- Field selection with p ≤ 101 and n ≤ 12
- Addition and subtraction of field elements
- Multiplication and division of field elements
- Automatic handling of reduction by irreducible polynomials
- Interactive GUI interface

Field elements are represented as polynomials over F_p rather than as powers of a primitive element. This choice makes addition and subtraction operations straightforward, while making multiplication and division more complex. As such, the calculator's primary utility lies in computing products and multiplicative inverses in the field.

The project uses Tkinter for its graphical interface, with the focus being on the mathematical engine powering the calculations rather than the GUI implementation itself.

This project serves both as a practical tool for finite field computations and as a demonstration of:
- Object-oriented programming in Python
- Mathematical algorithm implementation
- GUI development using Tkinter
- Test-driven development practices

The implementation emphasizes mathematical correctness and clean code structure over computational efficiency, making it suitable for educational purposes and moderate-size calculations.


## Development Plan

This project is being developed in four distinct phases:

### Phase 1: Initial Implementation
Focus on creating working implementations of all core functionality. This includes the mathematical engine for finite field calculations, the GUI components for user interaction, and basic integration of all parts. The emphasis is on correctness rather than optimization or elegance.

### Phase 2: Comprehensive Testing
Development of extensive test suites for all components. This includes unit tests for individual classes and methods, integration tests for the complete system, and thorough testing of edge cases and error handling. The goal is to ensure mathematical correctness and robust behavior under all conditions.

### Phase 3: Code Refinement
Optimization and cleanup of the codebase while maintaining test compliance. This involves standardizing coding style, improving algorithm efficiency where possible, enhancing error handling, and refactoring for better readability and maintainability.

### Phase 4: Documentation
Creation of comprehensive documentation at all levels. This includes inline comments, function and class docstrings, mathematical background information, usage examples, and architectural documentation. The aim is to make the project accessible to future developers and users.

**Current Status: Halfway Through Phase 3 - Code Refinement (Back-end done, Front-end to be done)**


## Code Architecture

The project consists of seven Python modules organized in a three-tier structure:

calculator_main.py

├── GUI Components:

│   ├── field_selector_gui.py  ┐

│   ├── poly_entry_gui.py      ├── tkinter

│   └── result_display_gui.py  ┘

│
└── Mathematical Engine:

├── calculator_engine.py    ┐

                            ├── modular_polynomial.py
                            
└── irreducible_finder.py   ┘

The main module coordinates between the GUI components and mathematical engine. All GUI components are built using tkinter, while the mathematical components are built upon the core modular_polynomial module. 


## Module Descriptions

### GUI Components
- **field_selector_gui.py**: Creates a frame allowing users to select the field GF(p^n) by inputting p and n. Validates inputs, manages the field selection state, and displays the irreducible polynomial being used to construct the field.

- **poly_entry_gui.py**: Provides an interface for entering two polynomials and selecting an operation (addition, subtraction, multiplication, or division). Dynamically adjusts to the degree of the field polynomial modulus, providing the appropriate number of coefficient entry boxes.

- **result_display_gui.py**: Simple display frame that shows the result of field operations in standard polynomial notation.

### Mathematical Engine
- **modular_polynomial.py**: Core class implementing polynomial arithmetic modulo p. Handles basic operations (addition, subtraction, multiplication, division with remainder) and includes methods for polynomial evaluation and comparison.

- **calculator_engine.py**: Manages field arithmetic by combining modular polynomial operations with reduction by the field's irreducible polynomial. Implements the extended Euclidean algorithm for finding multiplicative inverses in the field.

- **irreducible_finder.py**: Generates irreducible polynomials of specified degree over F_p. Uses a combination of constructive methods and irreducibility testing to efficiently find appropriate field-defining polynomials.

### Main Controller
- **calculator_main.py**: Coordinates the GUI components and mathematical engine. Manages state between components, handles user input events, and ensures proper initialization and update of all calculator components.


## Mathematical Background

### Core Mathematical Concepts
The calculator relies heavily on the following fundamental concepts:

- [Polynomial Long Division](https://en.wikipedia.org/wiki/Polynomial_long_division): Used extensively for reduction modulo the field's irreducible polynomial.

- [Modular Exponentiation](https://en.wikipedia.org/wiki/Modular_exponentiation): Required for efficiently computing large powers required for checking if a polynomial is irreducible.

- [Extended Euclidean Algorithm](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm): Applied to polynomials to find multiplicative inverses in the field.

- [Euler's Theorem](https://en.wikipedia.org/wiki/Euler%27s_theorem): Used to find multiplicative inverses of elements in the base field F_p via the relation a^(-1) ≡ a^(p-2) (mod p).

### Supporting Mathematical Concepts
Additional mathematical ideas employed in the implementation:

- [Horner's Method](https://en.wikipedia.org/wiki/Horner%27s_method): An efficient algorithm for evaluating polynomials at specific values.

- [Primitive Elements](https://en.wikipedia.org/wiki/Primitive_element_(finite_field)): Primitive Elements of the base field F_p are used in the construction of irreducible polynomials.

- [Polynomial Irreducibility Tests](https://en.wikipedia.org/wiki/Irreducible_polynomial#Irreducibility_tests): Specifically, the root-based test for quadratic and cubic polynomials over finite fields.
  
