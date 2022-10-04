# This script conducts integrity tests
# noinspection PyUnresolvedReferences
import pytest

# General Duties Imports
from os import getcwd

# Import Tests
from TestingModules.testing_utility_functions import load_pickle_from_file
from TestingModules.CleanUpTests import clean_up_test, pre_clean_test

# Burrow Preference
from TestingModules.TypeCheck import test_burrow_preference_config
from TestingModules.MachineCheck import test_run_burrow_preference_machine, test_burrow_preference_machine_vars
from TestingModules.DAQCheck import test_daq_burrow_preference, test_daq_burrow_preference_acquisition, \
    test_daq_burrow_preference_runtime

# Lick Training
from TestingModules.TypeCheck import test_lick_training_config
from TestingModules.DAQCheck import test_daq_lick, test_daq_lick_acquisition, test_daq_lick_runtime


# Delete existing test directory if exists
pre_clean_test("".join([getcwd(), "//TestingModules//Data"]))

# Burrow Preference
test_burrow_preference_config(load_pickle_from_file("".join([getcwd(), "\\TestingModules\\", "Test_Mouse_BPT.pkl"])))

test_run_burrow_preference_machine()

test_burrow_preference_machine_vars()

test_daq_burrow_preference()

test_daq_burrow_preference_acquisition()

test_daq_burrow_preference_runtime()

# Licking Training
test_lick_training_config(load_pickle_from_file("".join([getcwd(), "\\TestingModules\\", "Test_Mouse_LTC.pkl"])))

test_daq_lick()

test_daq_lick_acquisition()

test_daq_lick_runtime()

# Clean up? which doesn't work hence above
clean_up_test("".join([getcwd(), "//TestingModules//Data"]))
