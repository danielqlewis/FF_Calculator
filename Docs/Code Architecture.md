# Finite Field Calculator - Code Architecture

## 1. Overall Architecture

- **Entry Point**: `calculator_main` 
  - Creates `CalculatorController` instance
  - Passes controller to `GuiCoordinator` constructor
  - `GuiCoordinator` stores controller as attribute

- **Data Flow**:
  - User input → GUI → Coordinator → Controller → Engine → Result
  - `GuiCoordinator` orchestrates GUI and delegates calculations

## 2. Back-End Architecture

- **Three-Layer Design**:
  1. `modular_polynomial`: Core polynomial operations in modular arithmetic
  2. `irreducible_finder`: Generates irreducible polynomials using algorithms from layer 1
  3. `calculator_engine`: 
     - Creates `FiniteFieldCalculator` with irreducible polynomial modulus
     - Handles GF(p^n) operations using modular arithmetic
     - Implements field-specific operations (esp. multiplicative inverse)

- **Dependencies**: 
  - `calculator_engine` → `irreducible_finder` → `modular_polynomial`

## 3. Front-End Architecture

### GUI Components

- **Field Selector** (`field_selector_gui`):
  - User specifies p, n for GF(p^n)
  - Toggle to activate/deactivate field
  - Displays irreducible modulus

- **Polynomial Entry** (`poly_entry_gui`):
  - Entry fields for polynomial coefficients
  - Radio buttons for operations (add, subtract, multiply, divide)
  - Dynamically adjusts to field size

- **Result Display** (`result_display_gui`):
  - Displays calculation outcomes

### Callback Architecture

- **Component Creation Pattern**:
  - Each GUI module exports `create_X_frame(parent, callbacks, tk_packet)`
  - Returns dictionary with frame widget and interface functions

- **Component Interface Dictionary Schema**:
  ```
  {
    'frame': ttk.Frame,              # The widget to display
    'function1': callable,           # Interface functions for external control
    'function2': callable,
    ...
  }
  ```

- **Callback Registration Flow**:
  ```
  GuiCoordinator → registers callbacks with components:
    field_selector ← on_field_select, on_field_deselect
    poly_entry ← on_calculation_requested
  ```

- **Interface Functions for GuiCoordinator**:
  ```
  field_selector:
    deactivate_and_show_loading()
    update_modulus_display(modulus_text)
    reset_to_initial_state()
    
  poly_entry:
    set_active(active)
    update_field_size(num_terms)
    
  result_display:
    update_result(new_text)
    clear_result()
  ```

## 4. Event Flow Examples

### Field Selection Event:
1. User toggles checkbox in field_selector
2. Checkbox command calls `toggle_field()`
3. `toggle_field()` calls coordinator's `on_field_select(p, n)`
4. Coordinator validates, shows loading, calls controller's `initialize_field_async()`
5. Async calculation completes, controller calls continuation function
6. Coordinator updates UI via component interface functions

### Calculation Event:
1. User enters polynomials, selects operation, clicks "Calculate"
2. Click triggers `perform_calculation()` in poly_entry
3. Function calls coordinator's `on_calculation_requested(poly1, poly2, op)`
4. Coordinator delegates to controller's `perform_calculation()`
5. Controller processes and returns result
6. Coordinator updates result display with `update_result()`

## 5. Asynchronous Processing

- Field initialization uses asynchronous processing to prevent UI freezing
- UI updates scheduled on main thread via `root.after(0, lambda: func())` pattern
- Loading indicators provide user feedback during computation
