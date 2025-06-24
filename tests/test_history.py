import pytest
from unittest.mock import Mock, patch
from app.calculation import Calculation
from app.history import LoggingObserver, AutoSaveObserver
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError

# Sample setup for mock calculation
calculation_mock = Mock(spec=Calculation)
calculation_mock.operation = "addition"
calculation_mock.operand1 = 5
calculation_mock.operand2 = 3
calculation_mock.result = 8

# Test cases for LoggingObserver

@patch('logging.info')
def test_logging_observer_logs_calculation(logging_info_mock):
    observer = LoggingObserver()
    observer.update(calculation_mock)
    logging_info_mock.assert_called_once_with(
        "Calculation performed: addition (5, 3) = 8"
    )

def test_logging_observer_no_calculation():
    observer = LoggingObserver()
    with pytest.raises(AttributeError):
        observer.update(None)  # Passing None should raise an exception as there's no calculation

# Test cases for AutoSaveObserver

def test_autosave_observer_triggers_save():
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = True
    observer = AutoSaveObserver(calculator_mock)
    
    observer.update(calculation_mock)
    calculator_mock.save_history.assert_called_once()

@patch('logging.info')
def test_autosave_observer_logs_autosave(logging_info_mock):
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = True
    observer = AutoSaveObserver(calculator_mock)
    
    observer.update(calculation_mock)
    logging_info_mock.assert_called_once_with("History auto-saved")

def test_autosave_observer_does_not_trigger_save_when_disabled():
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = False
    observer = AutoSaveObserver(calculator_mock)
    
    observer.update(calculation_mock)
    calculator_mock.save_history.assert_not_called()

# Additional negative test cases for AutoSaveObserver

def test_autosave_observer_invalid_calculator():
    with pytest.raises(TypeError):
        AutoSaveObserver(None)  # Passing None should raise a TypeError

def test_autosave_observer_no_calculation():
    calculator_mock = Mock(spec=Calculator)
    calculator_mock.config = Mock(spec=CalculatorConfig)
    calculator_mock.config.auto_save = True
    observer = AutoSaveObserver(calculator_mock)
    
    with pytest.raises(AttributeError):
        observer.update(None)  # Passing None should raise an exception


@patch('builtins.input', side_effect=['clear', 'exit'])  # simulate clear, then exit
@patch('builtins.print')
@patch.object(Calculator, 'clear_history', return_value=None)
@patch.object(Calculator, 'save_history', return_value=None)
def test_clear_command(mock_save, mock_clear, mock_print, mock_input):
    from app.calculator_repl import calculator_repl

    calculator_repl()

    mock_clear.assert_called_once()
    mock_print.assert_any_call("History cleared")

@patch('builtins.input', side_effect=['undo', 'exit'])
@patch('builtins.print')
@patch.object(Calculator, 'undo', return_value=True)
@patch.object(Calculator, 'save_history', return_value=None)
def test_undo_command_success(mock_save, mock_undo, mock_print, mock_input):
    from app.calculator_repl import calculator_repl
    calculator_repl()
    mock_undo.assert_called_once()
    mock_print.assert_any_call("Operation undone")

import pytest
from unittest.mock import patch
from app.calculator import Calculator

@patch('builtins.input', side_effect=['redo', 'exit'])
@patch('builtins.print')
@patch.object(Calculator, 'redo', return_value=True)
@patch.object(Calculator, 'save_history', return_value=None)
def test_redo_command_success(mock_save, mock_redo, mock_print, mock_input):
    from app.calculator_repl import calculator_repl
    calculator_repl()
    mock_redo.assert_called_once()
    mock_print.assert_any_call("Operation redone")

import pytest
from unittest.mock import patch
from app.calculator import Calculator

@patch('builtins.input', side_effect=['redo', 'exit'])
@patch('builtins.print')
@patch.object(Calculator, 'redo', return_value=False)
@patch.object(Calculator, 'save_history', return_value=None)
def test_redo_command_nothing_to_redo(mock_save, mock_redo, mock_print, mock_input):
    from app.calculator_repl import calculator_repl
    calculator_repl()
    mock_redo.assert_called_once()
    mock_print.assert_any_call("Nothing to redo")


import pytest
from unittest.mock import patch
from app.calculator import Calculator

@patch('builtins.input', side_effect=['undo', 'exit'])
@patch('builtins.print')
@patch.object(Calculator, 'undo', return_value=False)  # ← simulate no undo available
@patch.object(Calculator, 'save_history', return_value=None)
def test_undo_command_nothing_to_undo(mock_save, mock_undo, mock_print, mock_input):
    from app.calculator_repl import calculator_repl

    calculator_repl()

    mock_undo.assert_called_once()
    mock_print.assert_any_call("Nothing to undo")

@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
@patch.object(Calculator, 'save_history', return_value=None)
def test_save_command_success(mock_save, mock_print, mock_input):
    from app.calculator_repl import calculator_repl

    calculator_repl()

    mock_save.assert_called()
    mock_print.assert_any_call("History saved successfully")

@patch('builtins.input', side_effect=['save', 'exit'])
@patch('builtins.print')
@patch.object(Calculator, 'save_history', side_effect=RuntimeError("disk full"))
def test_save_command_error(mock_save, mock_print, mock_input):
    from app.calculator_repl import calculator_repl

    calculator_repl()

    mock_print.assert_any_call("Error saving history: disk full")


@patch('builtins.input', side_effect=['history', 'exit'])
@patch('builtins.print')
@patch.object(Calculator, 'show_history', return_value=[])
@patch.object(Calculator, 'save_history', return_value=None)
def test_history_command_empty(mock_save, mock_show, mock_print, mock_input):
    from app.calculator_repl import calculator_repl

    calculator_repl()

    mock_show.assert_called_once()
    mock_print.assert_any_call("No calculations in history")

@patch('builtins.input', side_effect=['history', 'exit'])
@patch('builtins.print')
@patch.object(Calculator, 'show_history', return_value=["5 + 5 = 10", "2 * 3 = 6"])
@patch.object(Calculator, 'save_history', return_value=None)
def test_history_command_non_empty(mock_save, mock_show, mock_print, mock_input):
    from app.calculator_repl import calculator_repl

    calculator_repl()

    mock_show.assert_called_once()
    mock_print.assert_any_call("\nCalculation History:")
    mock_print.assert_any_call("1. 5 + 5 = 10")
    mock_print.assert_any_call("2. 2 * 3 = 6")

@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
@patch('app.calculator_repl.Calculator')
def test_load_command_success(mock_calculator_class, mock_print, mock_input):
    from app.calculator_repl import calculator_repl

    mock_calc = Mock()
    mock_calc.load_history.return_value = None
    mock_calc.save_history.return_value = None
    mock_calc.add_observer.return_value = None
    mock_calculator_class.return_value = mock_calc

    calculator_repl()

    mock_calc.load_history.assert_called_once()
    mock_print.assert_any_call("History loaded successfully")


@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
@patch('app.calculator_repl.Calculator')
def test_load_command_failure(mock_calculator_class, mock_print, mock_input):
    from app.calculator_repl import calculator_repl

    mock_calc = Mock()
    mock_calc.load_history.side_effect = RuntimeError("file not found")
    mock_calc.save_history.return_value = None
    mock_calc.add_observer.return_value = None
    mock_calculator_class.return_value = mock_calc

    calculator_repl()

    mock_calc.load_history.assert_called_once()
    mock_print.assert_any_call("Error loading history: file not found")

@patch('builtins.input', side_effect=['add', 'cancel', 'exit'])
@patch('builtins.print')
def test_add_command_cancel_first_input(mock_print, mock_input):
    from app.calculator_repl import calculator_repl
    calculator_repl()

    mock_print.assert_any_call("Operation cancelled")

@patch('builtins.input', side_effect=['add', '5', 'cancel', 'exit'])
@patch('builtins.print')
def test_add_command_cancel_second_input(mock_print, mock_input):
    from app.calculator_repl import calculator_repl
    calculator_repl()

    mock_print.assert_any_call("Operation cancelled")


@patch('builtins.input', side_effect=['add', '1', '2', 'exit'])
@patch('builtins.print')
@patch('app.calculator_repl.Calculator')
@patch('app.calculator_repl.OperationFactory.create_operation')
def test_arithmetic_command_validation_error(mock_factory, mock_calc_class, mock_print, mock_input):
    from app.calculator_repl import calculator_repl

    # Set up mocks
    mock_calc = Mock()
    mock_calc.perform_operation.side_effect = ValidationError("invalid input")
    mock_calc.add_observer.return_value = None
    mock_calc.save_history.return_value = None
    mock_calc_class.return_value = mock_calc

    mock_operation = Mock()
    mock_factory.return_value = mock_operation

    calculator_repl()

    mock_print.assert_any_call("Error: invalid input")

@patch('builtins.input', side_effect=['add', '1', '2', 'exit'])
@patch('builtins.print')
@patch('app.calculator_repl.Calculator')
@patch('app.calculator_repl.OperationFactory.create_operation')
def test_arithmetic_command_unexpected_exception(mock_factory, mock_calc_class, mock_print, mock_input):
    from app.calculator_repl import calculator_repl

    mock_calc = Mock()
    mock_calc.perform_operation.side_effect = RuntimeError("crash")
    mock_calc.add_observer.return_value = None
    mock_calc.save_history.return_value = None
    mock_calc_class.return_value = mock_calc

    mock_operation = Mock()
    mock_factory.return_value = mock_operation

    calculator_repl()

    mock_print.assert_any_call("Unexpected error: crash")

# Unknown command
@patch('builtins.input', side_effect=['foobar', 'exit'])
@patch('builtins.print')
def test_unknown_command_prints_message(mock_print, mock_input):
    from app.calculator_repl import calculator_repl
    calculator_repl()
    mock_print.assert_any_call("Unknown command: 'foobar'. Type 'help' for available commands.")

# KeyboardInterrupt handling
@patch('builtins.input', side_effect=[KeyboardInterrupt, 'exit'])
@patch('builtins.print')
def test_keyboard_interrupt_handling(mock_print, mock_input):
    from app.calculator_repl import calculator_repl
    calculator_repl()
    mock_print.assert_any_call("\nOperation cancelled")

# EOFError handling
@patch('builtins.input', side_effect=[EOFError])
@patch('builtins.print')
def test_eof_error_handling(mock_print, mock_input):
    from app.calculator_repl import calculator_repl
    calculator_repl()
    mock_print.assert_any_call("\nInput terminated. Exiting...")

# General exception in loop
@patch('builtins.input', side_effect=[Exception("unexpected fail"), 'exit'])
@patch('builtins.print')
def test_general_exception_in_loop(mock_print, mock_input):
    from app.calculator_repl import calculator_repl
    calculator_repl()
    mock_print.assert_any_call("Error: unexpected fail")

# Fatal error during Calculator init
@patch('builtins.print')
@patch('app.calculator_repl.Calculator', side_effect=Exception("init crash"))
def test_fatal_error_on_startup(mock_calc, mock_print):
    from app.calculator_repl import calculator_repl
    with pytest.raises(Exception, match="init crash"):
        calculator_repl()
    mock_print.assert_any_call("Fatal error: init crash")

# Arithmetic input cancelled (first number)
@patch('builtins.input', side_effect=['add', 'cancel', 'exit'])
@patch('builtins.print')
def test_add_cancel_first_input(mock_print, mock_input):
    from app.calculator_repl import calculator_repl
    calculator_repl()
    mock_print.assert_any_call("Operation cancelled")

# Arithmetic input cancelled (second number)
@patch('builtins.input', side_effect=['add', '5', 'cancel', 'exit'])
@patch('builtins.print')
def test_add_cancel_second_input(mock_print, mock_input):
    from app.calculator_repl import calculator_repl
    calculator_repl()
    mock_print.assert_any_call("Operation cancelled")

# Arithmetic validation error
@patch('builtins.input', side_effect=['add', '1', '2', 'exit'])
@patch('builtins.print')
@patch('app.calculator_repl.Calculator')
@patch('app.calculator_repl.OperationFactory.create_operation')
def test_arithmetic_command_validation_error(mock_factory, mock_calc_class, mock_print, mock_input):
    from app.calculator_repl import calculator_repl
    mock_calc = Mock()
    mock_calc.perform_operation.side_effect = ValidationError("invalid input")
    mock_calc.add_observer.return_value = None
    mock_calc.save_history.return_value = None
    mock_calc_class.return_value = mock_calc
    mock_factory.return_value = Mock()
    calculator_repl()
    mock_print.assert_any_call("Error: invalid input")

# Arithmetic unexpected error
@patch('builtins.input', side_effect=['add', '1', '2', 'exit'])
@patch('builtins.print')
@patch('app.calculator_repl.Calculator')
@patch('app.calculator_repl.OperationFactory.create_operation')
def test_arithmetic_command_unexpected_exception(mock_factory, mock_calc_class, mock_print, mock_input):
    from app.calculator_repl import calculator_repl
    mock_calc = Mock()
    mock_calc.perform_operation.side_effect = RuntimeError("crash")
    mock_calc.add_observer.return_value = None
    mock_calc.save_history.return_value = None
    mock_calc_class.return_value = mock_calc
    mock_factory.return_value = Mock()
    calculator_repl()
    mock_print.assert_any_call("Unexpected error: crash")