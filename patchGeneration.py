import itertools

import numpy
import numpy as np
import pandas as pd
from qiskit.circuit import Instruction, CircuitInstruction
import logging
from scipy.optimize import minimize, Bounds

from circuitExecution import all_test_execution

logging.disable()

class GateGroup:
    def __init__(self, num_params, num_qubits, gates):
        self.num_params = num_params
        self.num_qubits = num_qubits
        self.gates = gates


def getPositionGate(qc):
    column_names = ['Position', 'Gate', 'Params', 'Qubits', 'Suspiciousness', 'KickedOut']
    df = pd.DataFrame(columns=column_names)
    x = 0
    for instruction in qc.data:
        if (instruction[0].name != 'measure') and (instruction[0].name != 'barrier'):
            new_line = {'Position': x, 'Gate': instruction[0].name, 'Params': instruction[0].params, 'Qubits': instruction.qubits, 'Suspiciousness': 0.0, 'KickedOut': 'No'}
            new_df = pd.DataFrame.from_dict(new_line, orient='index').T
            df = pd.concat([df, new_df], ignore_index=True)
            x = x + 1
    for qubit in qc.qubits:
        new_line = {'Position': x, 'Gate': None, 'Params': [],
                    'Qubits': (qubit,), 'Suspiciousness': 0.0, 'KickedOut': 'No'}
        new_df = pd.DataFrame.from_dict(new_line, orient='index').T
        df = pd.concat([df, new_df], ignore_index=True)
        x = x + 1
    return df


def gen_possible_patches(faulty_qc, supported_gates, gates_df):
    possible_patches_df = pd.DataFrame(columns=['Operator', 'Position', 'New_gate', 'New_params', 'New_qubits', 'Executed'])
    # shift_amount = int(position) % len(supported_gates)
    # supported_gates = supported_gates[shift_amount:] + supported_gates[:shift_amount]
    for new_gate in supported_gates:
        similargates, num_params, num_qubits = getSimilarGates(new_gate)
        qubits_combinations = list(itertools.permutations(faulty_qc.qubits, num_qubits))
        for new_qubits in qubits_combinations:
            # possible_params = [[], ]
            # if num_params > 0:
                # possible_params = list(itertools.permutations([0, np.pi, np.pi / 2, np.pi / 4, -np.pi / 2, -np.pi / 4], num_params))  #SIMPLE VALUES
                # possible_params = list(itertools.permutations([-np.pi, -3 * np.pi / 4, -np.pi / 2, -np.pi / 4, 0, np.pi / 4, np.pi / 2, 3 * np.pi / 4, np.pi], num_params))  # 2pi in steps of pi/4
                #possible_params = list(itertools.permutations([-np.pi, -7 * np.pi / 8, -6 * np.pi / 8, -5 * np.pi / 8, -4 * np.pi / 8, -3 * np.pi / 8, -2 * np.pi / 8, -np.pi / 8, 0, np.pi / 8, 2 * np.pi / 8, 3 * np.pi / 8, 4 * np.pi / 8, 5 * np.pi / 8, 6 * np.pi / 8, 7 * np.pi / 8, np.pi], num_params))  # 2pi in steps of pi/8
                # possible_params = list(itertools.permutations([-np.pi, -15 * np.pi / 16, -14 * np.pi / 16, -13 * np.pi / 16, -12 * np.pi / 16, -11 * np.pi / 16, -10 * np.pi / 16, -9 * np.pi / 16, -8 * np.pi / 16, -7 * np.pi / 16, -6 * np.pi / 16, -5 * np.pi / 16, -4 * np.pi / 16, -3 * np.pi / 16, -2 * np.pi / 16, -np.pi / 16, 0, np.pi / 16, 2 * np.pi / 16, 3 * np.pi / 16, 4 * np.pi / 16, 5 * np.pi / 16, 6 * np.pi / 16, 7 * np.pi / 16, 8 * np.pi / 16, 9 * np.pi / 16, 10 * np.pi / 16, 11 * np.pi / 16, 12 * np.pi / 16, 13 * np.pi / 16, 14 * np.pi / 16, 15 * np.pi / 16, np.pi], num_params))  # 2pi in steps of pi/16
                #possible_params = list(itertools.permutations([-np.pi, -31 * np.pi / 32, -30 * np.pi / 32, -29 * np.pi / 32, -28 * np.pi / 32,-27 * np.pi / 32, -26 * np.pi / 32, -25 * np.pi / 32, -24 * np.pi / 32, -23 * np.pi / 32, -22 * np.pi / 32, -21 * np.pi / 32, -20 * np.pi / 32, -19 * np.pi / 32, -18 * np.pi / 32, -17 * np.pi / 32, -16 * np.pi / 32, -15 * np.pi / 32, -14 * np.pi / 32, -13 * np.pi / 32, -12 * np.pi / 32, -11 * np.pi / 32, -10 * np.pi / 32, -9 * np.pi / 32, -8 * np.pi / 32, -7 * np.pi / 32, -6 * np.pi / 32, -5 * np.pi / 32, -4 * np.pi / 32, -3 * np.pi / 32, -2 * np.pi / 32, -np.pi / 32, 0, np.pi / 32, 2 * np.pi / 32, 3 * np.pi / 32, 4 * np.pi / 32, 5 * np.pi / 32, 6 * np.pi / 32, 7 * np.pi / 32, 8 * np.pi / 32, 9 * np.pi / 32, 10 * np.pi / 32, 11 * np.pi / 32, 12 * np.pi / 32, 13 * np.pi / 32, 14 * np.pi / 32, 15 * np.pi / 32, 16 * np.pi / 32, 17 * np.pi / 32, 18 * np.pi / 32, 19 * np.pi / 32, 20 * np.pi / 32, 21 * np.pi / 32, 22 * np.pi / 32, 23 * np.pi / 32, 24 * np.pi / 32, 25 * np.pi / 32, 26 * np.pi / 32, 27 * np.pi / 32, 28 * np.pi / 32, 29 * np.pi / 32, 30 * np.pi / 32, 31 * np.pi / 32, np.pi], num_params))  # 2pi in steps of pi/32
            # for new_params in possible_params:
            for index, row in gates_df.iterrows():
                position = row['Position']
                new_instruction = {'Operator': 'Add', 'Position': position, 'Gate': row['Gate'], 'New_gate': new_gate,
                               'New_params': [], 'New_qubits': new_qubits, 'Executed': 'No'}
                new_df = pd.DataFrame.from_dict(new_instruction, orient='index').T
                possible_patches_df = pd.concat([possible_patches_df, new_df], ignore_index=True)

                new_instruction = {'Operator': 'Replace', 'Position': position, 'Gate': row['Gate'], 'New_gate': new_gate,
                               'New_params': [], 'New_qubits': new_qubits, 'Executed': 'No'}
                new_df = pd.DataFrame.from_dict(new_instruction, orient='index').T
                possible_patches_df = pd.concat([possible_patches_df, new_df], ignore_index=True)

    return possible_patches_df

def gen_possible_patches_delete(gates_df):
    possible_patches_df = pd.DataFrame(columns=['Operator', 'Position', 'New_gate', 'New_params', 'New_qubits', 'Executed'])
    for index, row in gates_df.iterrows():
        position = row['Position']
        new_instruction = {'Operator': 'Delete', 'Position': position, 'Gate': row['Gate'], 'New_gate': None,
                       'New_params': [], 'New_qubits': None, 'Executed': 'No'}
        new_df = pd.DataFrame.from_dict(new_instruction, orient='index').T
        possible_patches_df = pd.concat([possible_patches_df, new_df], ignore_index=True)

    return possible_patches_df


def sort_by_group_based_on_group_number(possible_patches_df):
    sorted_patches_df = pd.DataFrame(columns=possible_patches_df.columns)  # New empty DataFrame to hold sorted rows
    grouped = possible_patches_df.groupby('New_gate', group_keys=False)  # Group by 'New_gate'

    group_keys = list(grouped.groups.keys())  # List of unique group keys (gates)

    while not possible_patches_df.empty:
        remaining_group_keys = []  # Track non-empty groups

        for group_idx, gate in enumerate(group_keys):
            if gate not in grouped.groups:  # Skip if the group is empty
                continue

            group = grouped.get_group(gate)  # Get the current group

            # Pick the row based on group index (group_idx) if possible, otherwise pick the first row
            if len(group) > group_idx:  # Ensure the group has enough rows to pick based on index
                selected_row = group.iloc[group_idx]  # Pick the row corresponding to the group's index
            else:
                selected_row = group.iloc[0]  # Default to picking the first row if group has fewer rows

            # Add the selected row to the sorted DataFrame
            sorted_patches_df = pd.concat([sorted_patches_df, pd.DataFrame([selected_row])], ignore_index=True)
            # Remove the selected row from the original DataFrame
            possible_patches_df = possible_patches_df.drop(selected_row.name).reset_index(drop=True)
            # Update the groups after row removal
            grouped = possible_patches_df.groupby('New_gate', group_keys=False)

            # Keep track of non-empty groups
            if not group.empty:
                remaining_group_keys.append(gate)

        # Update group keys to only include those with remaining rows
        group_keys = remaining_group_keys

    return sorted_patches_df


def getSimilarGates(gate):
    num_params = 0
    num_qubits = 0
    similarGates = []
    # ['cu', 'dcx']

    SingleQubit = GateGroup(0, 1, ["x", "h", "t", "s", "z", "y", "id", "sx", "sdg", "tdg"])
    SingleQubit_1param = GateGroup(1, 1, ["p", "rx", "ry", "rz"])
    SingleQubit_2param = GateGroup(2, 1, ["r"])
    SingleQubit_3param = GateGroup(3, 1, ["u"])
    DoubleQubit = GateGroup(0, 2, ["swap", "cx", "cy", "cz", "ch", "csx"])
    DoubleQubit_1param = GateGroup(1, 2, ["crx", "cry", "crz", "rzz", "rxx", "ryy", "rzx", "cp"])
    MultiQubit = GateGroup(0, 3, ["ccx", "cswap"])

    groups = [SingleQubit, SingleQubit_1param, SingleQubit_2param, SingleQubit_3param, DoubleQubit, DoubleQubit_1param, MultiQubit]

    #GET SIMILAR GATES BASED ONLY IN QUBITS
    # Find the number of qubits for the given gate
    for group in groups:
        if gate in group.gates:
            num_qubits = group.num_qubits
            num_params = group.num_params
            break

    # Collect all gates with the same number of qubits
    for group in groups:
        if group.num_qubits == num_qubits:
            similarGates.extend(group.gates)

    # Remove the input gate from the list (if desired)
    if num_params == 0:
        if gate in similarGates:
            similarGates.remove(gate)

    # GET SIMILAR GATES BASED ON QUBITS AND PARAMS
    # for group in groups:
    #     if gate in group.gates:
    #         similarGates = [item for item in group.gates if item != gate]
    #         num_params = group.num_params
    #         num_qubits = group.num_qubits

    return similarGates, num_params, num_qubits

def apply_instruction_random(faulty_qc, row, shots, oracle_df, filename, test_cases_dict):
    operator = row['Operator']
    similarGates, num_params, num_qubits = getSimilarGates(row['New_gate'])
    if operator == 'Delete':
        new_qc = deleteGate(faulty_qc, row['Position'])
        all_inputs = oracle_df['input'].tolist()
        score, tests_results_dict = all_test_execution(new_qc, shots, filename, oracle_df, all_inputs)
        evaluations = 1
        params = []
    else:
        if num_params > 0:
            score, params, evaluations = param_optimization_random(faulty_qc, row, num_params, shots, oracle_df, filename, test_cases_dict)
        else:
            if operator == 'Add':
                new_qc = addGate(faulty_qc, row['Position'], row['New_gate'], row['New_qubits'], row['New_params'])
                all_inputs = oracle_df['input'].tolist()
                score, tests_results_dict = all_test_execution(new_qc, shots, filename, oracle_df, all_inputs)
                evaluations = 1
                params = []
            elif operator == 'Replace':
                new_qc = replaceGate(faulty_qc, row['Position'], row['New_gate'], row['New_qubits'], row['New_params'])
                all_inputs = oracle_df['input'].tolist()
                score, tests_results_dict = all_test_execution(new_qc, shots, filename, oracle_df, all_inputs)
                evaluations = 1
                params = []

    return score, params, evaluations

def apply_instruction(faulty_qc, row, shots, oracle_df, filename, test_cases_dict):
    operator = row['Operator']
    similarGates, num_params, num_qubits = getSimilarGates(row['New_gate'])
    if num_params > 0:
        score, params, evaluations = param_optimization(faulty_qc, row, num_params, shots, oracle_df, filename, test_cases_dict)
    else:
        if operator == 'Add':
            new_qc = addGate(faulty_qc, row['Position'], row['New_gate'], row['New_qubits'], row['New_params'])
            all_inputs = oracle_df['input'].tolist()
            score, tests_results_dict = all_test_execution(new_qc, shots, filename, oracle_df, all_inputs)
            # score = prioritized_tc_exec(new_qc, shots, filename, oracle_df, test_cases_dict, 1)
            evaluations = 1
            params = []
        elif operator == 'Replace':
            new_qc = replaceGate(faulty_qc, row['Position'], row['New_gate'], row['New_qubits'], row['New_params'])
            all_inputs = oracle_df['input'].tolist()
            score, tests_results_dict = all_test_execution(new_qc, shots, filename, oracle_df, all_inputs)
            # score = prioritized_tc_exec(new_qc, shots, filename, oracle_df, test_cases_dict, 1)
            evaluations = 1
            params = []

    return score, params, evaluations

def deleteGate(qc, position):
    new_qc = qc.copy_empty_like()

    for x, gate in enumerate(qc.data):
        if x != position:
            new_qc.append(gate)

    return new_qc

def replaceGate(qc, position, new_name, new_qubits, new_params):
    new_qc = qc.copy_empty_like()

    for x, gate in enumerate(qc.data):
        if x == position:
            new_gate = CircuitInstruction(operation=Instruction(name=new_name, num_qubits=len(new_qubits), num_clbits=0, params=new_params), qubits=new_qubits)
            new_qc.append(new_gate)
        else:
            new_qc.append(gate)

    return new_qc

def replaceParams(qc, position, new_params):
    new_qc = qc.copy_empty_like()

    for x, gate in enumerate(qc.data):
        if x == position:
            new_gate = CircuitInstruction(
                operation=Instruction(name=gate.operation.name, num_qubits=len(gate.qubits), num_clbits=0,
                                      params=new_params), qubits=gate.qubits)
            new_qc.append(new_gate)
        else:
            new_qc.append(gate)

    return new_qc

def addGate(qc, position, new_name, new_qubits, new_params):
    new_qc = qc.copy_empty_like()

    x = 0
    for gate in qc.data:
        if x == position:
            new_gate = CircuitInstruction(operation=Instruction(name=new_name, num_qubits=len(new_qubits), num_clbits=0, params=new_params), qubits=new_qubits)
            new_qc.append(new_gate)
        new_qc.append(gate)
        x = x + 1

    if x < position:
        for qubit in qc.qubits:
            if x == position:
                new_gate = CircuitInstruction(operation=Instruction(name=new_name, num_qubits=len(new_qubits), num_clbits=0, params=new_params), qubits=new_qubits)
                new_qc.append(new_gate)
            x = x + 1

    return new_qc

def getNewQubitsCombinations(new_gate, origin_qubit, all_qubits):
    similargates, num_params, num_qubits = getSimilarGates(new_gate)
    new_qubits_combinations = []
    if num_qubits == 1:
        new_qubits_combinations.append((origin_qubit[-1],))
    elif num_qubits == 2:
        for qubit in all_qubits:
            if qubit != origin_qubit[-1]:
                new_qubits_combinations.append((qubit, origin_qubit[-1]))

    return new_qubits_combinations

def evaluate_guess(variables, faulty_qc, row, shots, oracle_df, filename, test_cases_dict):
    # new_qc = insertUgate(faulty_qc, row['Position'], list(variables))
    if row['Operator'] == 'Add':
        new_qc = addGate(faulty_qc, row['Position'], row['New_gate'], row['New_qubits'], variables)
    elif row['Operator'] == 'Replace':
        new_qc = replaceGate(faulty_qc, row['Position'], row['New_gate'], row['New_qubits'], variables)
    else:
        print(f'ERROR: Operator not supported!!!!!!!!!!!!')
        new_qc = faulty_qc.copy_empty_like()

    # if faulty_qc.num_qubits > 4:
    #     num_tc = faulty_qc.num_qubits**2
    # else:
    #     num_tc = (2**faulty_qc.num_qubits) * 3

    all_inputs = oracle_df['input'].tolist()
    score, tests_results_dict = all_test_execution(new_qc, shots, filename, oracle_df, all_inputs)
    # score = prioritized_tc_exec(new_qc, shots, filename, oracle_df, test_cases_dict, num_tc)

    return score

def param_optimization(faulty_qc, row, num_params, shots, oracle_df, filename, test_cases_dict):
    params = []
    for x in range(num_params):
        params.append(np.random.uniform(-np.pi, np.pi))

    initial_guess = numpy.array(params)

    bounds = Bounds(lb=-np.pi, ub=np.pi)
    optimize_result = minimize(fun=evaluate_guess, x0=initial_guess, args=(faulty_qc, row, shots, oracle_df, filename, test_cases_dict), method='COBYLA', bounds=bounds, options={'maxiter': 1000*num_params})
    score = optimize_result.fun
    params = optimize_result.x
    evaluations = optimize_result.nfev

    return score, params, evaluations

def param_optimization_random(faulty_qc, row, num_params, shots, oracle_df, filename, test_cases_dict):
    best_score = 1000000000
    best_evaluation = 1000*num_params
    best_params = []

    for x in range(1000*num_params):
        params = []
        for p in range(num_params):
            params.append(np.random.uniform(-np.pi, np.pi))

        current_score = evaluate_guess(params, faulty_qc, row, shots, oracle_df, filename, test_cases_dict)
        if current_score < best_score:
            best_score = current_score
            best_params = params
            if best_score == 0:
                best_evaluation = x
                return best_score, best_params, best_evaluation

        best_evaluation = x

    return best_score, best_params, best_evaluation
