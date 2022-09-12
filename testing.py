# This script conducts integrity tests
import pytest

# General Duties Imports
from os import getcwd

# Import Tests
from testing_utility_functions import load_pickle_from_file
from TypeCheck import test_burrow_preference_config
from CleanUpTests import clean_up_test, pre_clean_test

# Delete existing test directory if exists
pre_clean_test(getcwd())

test_burrow_preference_config(load_pickle_from_file("".join([getcwd(), "\\", "Test_Mouse.pkl"])))

# Clean up? which doesn't work hence above
clean_up_test(getcwd())
