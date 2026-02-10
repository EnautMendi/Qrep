import argparse
import math
import os
import time

import pandas as pd
from qiskit import QuantumCircuit
import multiprocessing as mp

from circuitExecution import all_test_execution
from patchGeneration import getPositionGate, deleteGate, gen_possible_patches, apply_instruction_random, \
    gen_possible_patches_delete


def updateArchive(instruction, score, max_solutions, patch_archive):
    # Modify the shared DataFrame
    patch_archive_df = pd.DataFrame(patch_archive['data'])
    if max_solutions == 'All':
        max_solutions = len(patch_archive_df) + 1
    if len(patch_archive_df) < max_solutions:
        new_row = pd.DataFrame.from_dict(instruction, orient='index').T
        patch_archive_df = pd.concat([patch_archive_df, new_row], ignore_index=True)
    else:
        if score < patch_archive_df['Score'].iloc[-1]:
            new_row = pd.DataFrame.from_dict(instruction, orient='index').T
            patch_archive_df = patch_archive_df.drop(patch_archive_df.index[-1])
            patch_archive_df = pd.concat([patch_archive_df, new_row], ignore_index=True)
    patch_archive_df = patch_archive_df.sort_values(by='Score', ascending=True, ignore_index=True)
    patch_archive['data'] = patch_archive_df.to_dict(orient='list')


def apply_patches(index, row, faulty_qc, firstScore, max_solutions, shots, filename, oracle_df, lock, patch_archive, finish, gates, num_evaluations, test_cases_dict, possible_patches):
    score, params, evaluations = apply_instruction_random(faulty_qc, row, shots, oracle_df, filename, test_cases_dict)
    difference = firstScore - score
    with lock:
        gates_df = pd.DataFrame(gates['data'])
        gate_index = gates_df.index[gates_df['Position'] == row['Position']].item()
        if gates_df.loc[gate_index, 'Suspiciousness'] == 0.0:
            gates_df.at[gate_index, 'Suspiciousness'] = difference
        else:
            gates_df.at[gate_index, 'Suspiciousness'] = max(gates_df.loc[gate_index, 'Suspiciousness'], difference)
        gates['data'] = gates_df.to_dict(orient='list')
    with lock:
        num_evaluations.value = num_evaluations.value + evaluations
        instruction = {'Operator': row['Operator'], 'Position': row['Position'], 'Gate': row['Gate'],
                       'New_gate': row['New_gate'], 'New_params': params, 'New_qubits': row['New_qubits'],
                       'Score': score, 'Evaluation': num_evaluations.value, 'Timestamp': time.time()}
        updateArchive(instruction, score, max_solutions, patch_archive)
        possible_patches_df = pd.DataFrame(possible_patches['data'])
        possible_patches_df.at[index, 'Executed'] = 'Yes'
        possible_patches['data'] = possible_patches_df.to_dict(orient='list')

    if score == 0:
        # position = row['Position']
        # gate = row['Gate']
        # print(f'SOLUTION FOUND BY DELETING GATE {gate} IN POSITION {position}!')
        # Modify the shared boolean
        finish.set()
    return score

def init_pool_processes(lock, patch_archive, finish, gates, num_evaluations, possible_patches):
    #Initialize each process with a global variable lock.
    global shared_lock
    global shared_patch_archive
    global shared_finish
    global shared_gates
    global shared_evaluations
    global shared_possible_patches
    shared_lock = lock
    shared_patch_archive = patch_archive
    shared_finish = finish
    shared_gates = gates
    shared_evaluations = num_evaluations
    shared_possible_patches = possible_patches


def process_task(task):
    step_name, index, row, faulty_qc, firstScore, max_solutions, shots, filename, oracle_df, test_cases_dict = task

    score = apply_patches(index, row, faulty_qc, firstScore, max_solutions, shots, filename, oracle_df, shared_lock, shared_patch_archive, shared_finish, shared_gates, shared_evaluations, test_cases_dict, shared_possible_patches)

    return score
def execute_step(step_name, faulty_qc, firstScore, max_solutions, shots, filename, oracle_df, gates, patch_archive, finish, num_evaluations, step_time_limit, test_cases_dict, possible_patches=None):
    lock = mp.Lock()
    step_start_time = time.time()
    num_processes = 15
    with mp.Pool(initializer=init_pool_processes, initargs=(lock, patch_archive, finish, gates, num_evaluations, possible_patches), processes=num_processes) as pool:

        possible_patches_df = pd.DataFrame(possible_patches['data'])
        tasks = [(step_name, index, row, faulty_qc, firstScore, max_solutions, shots, filename, oracle_df, test_cases_dict) for index, row in possible_patches_df.iterrows()]
        result = pool.map_async(process_task, tasks)

        print("Waiting for tasks to complete...")
        result.wait(timeout=step_time_limit)  # Blocking call, waits until all tasks are done

        # Retrieve the results
        if result.ready():  # Ensure tasks are complete
            results = result.get()
            print(f"All tasks completed with results: {results}")
            # Close and join the pool
            pool.close()  # No more tasks can be submitted
            pool.join()  # Wait for all worker processes to finish
            # print("Pool has been closed and joined.")
        else:
            # Close and join the pool
            pool.terminate()  # No more tasks can be submitted
            pool.join()  # Wait for all worker processes to finish
            # print("Pool has been closed and joined.")

    step_end_time = time.time()
    used_time = step_end_time - step_start_time
    # print(f'Step used time: {used_time}')
    gates_df = pd.DataFrame(gates['data'])
    gates_df = gates_df.sort_values(by='Suspiciousness', ascending=False, ignore_index=True)
    gates['data'] = gates_df.to_dict(orient='list')
    return used_time

# Function to monitor the elapsed time and stop processes
def monitor_time_and_terminate(limit, event, proces_name):
    start_time = time.time()
    while not event.is_set():
        elapsed_time = time.time() - start_time
        if elapsed_time >= limit:
            str_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            print(f"\nTime limit of {limit}s reached at {str_time} in {proces_name}, terminating all processes...")
            event.set()
            break
        time.sleep(0.1)  # Sleep briefly to avoid busy-waiting

def getFaultyQc(faulty_file_path):
    qc = QuantumCircuit.from_qasm_file(faulty_file_path)
    new_qc = QuantumCircuit(qc.num_qubits)
    for instruction in qc.data:
        if (instruction[0].name != 'measure') and (instruction[0].name != 'barrier'):
            new_qc.append(instruction)

    return new_qc

def start_random(oracle_file_path, faulty_file_path, max_solutions, time_limit, run, path_char):
    supported_gates = ["x", "h", "t", "s", "z", "y", "sx", "sdg", "tdg", "p", "rx", "ry", "rz", "r", "swap", "cx", "cy", "cz", "ch", "csx", "crx", "cry", "crz", "rzz", "rxx", "ryy", "rzx", "cp"]

    splited_path = faulty_file_path.split(path_char)
    filename = splited_path[-1]
    folder = splited_path[-2]

    faulty_qc = getFaultyQc(faulty_file_path)
    gates_df = getPositionGate(faulty_qc)


    shots = 2 ** faulty_qc.num_qubits * 2
    if shots < 1024:
        shots = 1024

    oracle_df = pd.read_csv(oracle_file_path)
    all_inputs = oracle_df['input'].tolist()

    first_time = time.time()
    firstScore, test_cases_dict = all_test_execution(faulty_qc, shots, filename, oracle_df, all_inputs)

    first_execution = time.time() - first_time
    if first_execution*2 > time_limit:
        print('ERROR: The maximum time limit introduced is smaller than the time needed to execute the circuit once for all the test cases.')
        print(f'UPDATE: Time limit was updated to {first_execution + time_limit} to be able to be executed.')
        time_limit = first_execution + time_limit

    possible_patches_df = gen_possible_patches(faulty_qc, supported_gates, gates_df)
    possible_patches_df = pd.concat([possible_patches_df, gen_possible_patches_delete(gates_df)], ignore_index=True)
    sorted_patches = possible_patches_df.sample(frac=1).reset_index(drop=True)

    # Manager to create shared object
    manager = mp.Manager()
    num_evaluations = manager.Value(int, 0)
    patch_archive_df = pd.DataFrame(
        columns=['Operator', 'Position', 'Gate', 'New_gate', 'New_params', 'New_qubits', 'Score'])
    patch_archive = manager.dict({'data': patch_archive_df.to_dict(orient='list')})
    gates = manager.dict({'data': gates_df.to_dict(orient='list')})
    possible_patches = manager.dict({'data': sorted_patches.to_dict(orient='list')})

    # Create a shared event (Listener)
    finish = mp.Event()

    start_time = time.time()

    # Start the monitor process
    monitor_process_general = mp.Process(target=monitor_time_and_terminate, args=(time_limit, finish, 'Main'))
    monitor_process_general.start()

    if firstScore > 0:
        # print(gates_df)
        possible_patches_df = pd.DataFrame(possible_patches['data'])
        print(f'Patches to try: {len(possible_patches_df)}')
        if not finish.is_set() and len(possible_patches_df) > 0:
            execute_step('Add&Replace', faulty_qc, firstScore, max_solutions, shots, filename, oracle_df, gates, patch_archive, finish, num_evaluations, time_limit, test_cases_dict, possible_patches)

    else:
        instruction = {'Operator': 'Equivalent', 'Position': None, 'Gate': None, 'New_gate': None,
                       'New_params': None, 'New_qubits': None, 'Score': firstScore}
        updateArchive(instruction, firstScore, max_solutions, patch_archive)
        #print(f'PROCESS INTERRUPTED: The faulty program introduced passed all test cases, so the program is considered as non faulty!')
    finish.set()
    monitor_process_general.join()
    end_time = time.time()
    exec_time = end_time - start_time

    os.makedirs(f'./results_random_run{run}/{folder}', exist_ok=True)
    results_name = filename.replace('.qasm', f'_random.csv')

    gates_df = pd.DataFrame(gates['data'])
    gates_df.to_csv(f'./results_random_run{run}/{folder}/gates_{results_name}', index=False)

    patch_archive_df = pd.DataFrame(patch_archive['data'])
    patch_archive_df['Total_exec_time'] = exec_time
    patch_archive_df['Total_evaluations'] = num_evaluations.value
    patch_archive_df['First_score'] = firstScore
    if firstScore > 0:
        patch_archive_df['Overall_improvement'] = patch_archive_df['First_score'] - patch_archive_df['Score']
        patch_archive_df['Overall_improvement_percent'] = patch_archive_df['Overall_improvement']/patch_archive_df['First_score'] * 100
    else:
        patch_archive_df['Overall_improvement'] = 0
        patch_archive_df['Overall_improvement_percent'] = 0

    patch_archive_df.to_csv(f'./results_random_run{run}/{folder}/solutions_{results_name}', index=False)

    # print('___________________________________BEST SOLUTIONS: _________________________________________')
    # print(patch_archive_df)
    # print(f'Execution time {exec_time}s')
