import json

import pandas as pd
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import hellinger_distance
from qulacs_core import QuantumState
from scipy.stats import chisquare

from qulacsQasm import convert_qiskit_to_qulacs


def getExecResults(qc, shots, filename, inputs):
    columns = ['file', 'shots', 'input', 'counts']
    results_df = pd.DataFrame(columns=columns)
    # initialized_circuits = dict()
    for input in inputs:
        qc_init = circuitinitialization(qc, input)
        counts = execute_circuit_qulacs(qc_init, shots)
        new_row = {'file': filename, 'shots': shots, 'input': input, 'counts': counts}
        new_df = pd.DataFrame.from_dict(new_row, orient='index').T
        results_df = pd.concat([results_df, new_df], ignore_index=True)

    return results_df

def get_counts_from_ints(int_list, num_bits):
    binary_dict = {}

    for number in int_list:
        # Convert integer to binary string, remove the '0b' prefix
        binary_str = str(bin(number)[2:])
        if len(binary_str) < num_bits:
            for x in range(num_bits-len(binary_str)):
                binary_str = '0' + binary_str

        # Update the dictionary with the count of the binary string
        if binary_str in binary_dict:
            binary_dict[binary_str] += 1
        else:
            binary_dict[binary_str] = 1

    return binary_dict

def execute_circuit_qulacs(qc, shots):
    seed = 42
    transpiled_qc = transpile(qc, basis_gates=["sx", "cx", "x", "rz"], num_processes=1)
    lacs = convert_qiskit_to_qulacs(transpiled_qc)
    state = QuantumState(transpiled_qc.num_qubits)
    state.set_zero_state()
    lacs.update_quantum_state(state)
    int_ocurrences = state.sampling(shots, seed)
    counts = get_counts_from_ints(int_ocurrences, transpiled_qc.num_qubits)

    return counts

def evaluateCircuit(qc, shots, filename, oracle_df, test_cases):

    results_df = getExecResults(qc, shots, filename, test_cases)
    test_cases_df = compareResults(oracle_df, results_df)
    test_cases_falling = test_cases_df['Killed'].sum()
    # distance = test_cases_df['Distance'].max()
    distance = test_cases_df['Distance'].mean()

    return test_cases_falling, distance

def getTestCaseDict(test_cases_df):
    result_dict = {}

    for index, row in test_cases_df.iterrows():
        test_case = row['Test_case']
        killed = row['Killed']
        distance = row['Distance']

        # Calculate the value based on the 'killed' condition
        value = (1 if killed else 0) + distance

        # Update the dictionary
        if test_case in result_dict:
            result_dict[test_case] += value
        else:
            result_dict[test_case] = value

    return result_dict


def all_test_execution(qc, shots, filename, oracle_df, all_inputs):

    results_df = getExecResults(qc, shots, filename, all_inputs)
    test_cases_df = compareResults(oracle_df, results_df)
    filtered_df = test_cases_df[test_cases_df['Killed'] == True]
    if len(filtered_df) > 0:
        score = filtered_df['Distance'].sum()
    else:
        score = 0
    test_case_dict = getTestCaseDict(test_cases_df)
    
    return score, test_case_dict

def compareOutputs(oracle_output, mutant_output):
    result = False

    oracle_output = str(oracle_output)
    oracle_output = oracle_output.replace("'", "\"")
    mutant_output = str(mutant_output)
    mutant_output = mutant_output.replace("'", "\"")

    expected = json.loads(oracle_output)
    observed = json.loads(mutant_output)

    sorted_expected = dict(sorted(expected.items()))
    sorted_observed = dict(sorted(observed.items()))


    if len(list(sorted_observed.values())) == len(list(sorted_expected.values())):
        if sorted_expected.keys() == sorted_observed.keys():
            results = chisquare(list(sorted_observed.values()), list(sorted_expected.values()))
            if results[1] < 0.01:
                result = True
        else:
            result = True
    else:
        result = True


    return result

def getHellinger(oracle_output, mutant_output):
    oracle_output = str(oracle_output)
    oracle_output = oracle_output.replace("'", "\"")
    mutant_output = str(mutant_output)
    mutant_output = mutant_output.replace("'", "\"")

    expected = json.loads(oracle_output)
    observed = json.loads(mutant_output)

    distance = hellinger_distance(expected, observed)

    return distance
def compareResults(oracle_df, mutant_df):
    inputs = mutant_df['input'].values
    test_cases = pd.DataFrame(columns=['Test_case', 'Killed', 'Distance'])
    for inp in inputs:
        oracle_ouput = oracle_df[oracle_df['input'] == str(inp)]
        mutant_output = mutant_df[mutant_df['input'] == str(inp)]
        killed = compareOutputs(oracle_ouput['counts'].values[0], mutant_output['counts'].values[0])
        distance = getHellinger(oracle_ouput['counts'].values[0], mutant_output['counts'].values[0])
        new_line = {'Test_case': inp, 'Killed': killed, 'Distance': distance}
        new_df = pd.DataFrame.from_dict(new_line, orient='index').T
        test_cases = pd.concat([test_cases, new_df], ignore_index=True)

    return test_cases

def circuitinitialization(qc, input_base):
    inp = input_base[1:-2]
    base = input_base[-2]
    initialization = QuantumCircuit(qc.num_qubits)
    x = 0
    for bit in inp:
        if bit == '1':
            initialization.x(x)
        x = x + 1

    qc = initialization.compose(qc)

    if base == 'x':
        for qubit in qc.qubits:
            qc.h(qubit)
    elif base == 'y':
        for qubit in qc.qubits:
            qc.sdg(qubit)
            qc.h(qubit)

    return qc
