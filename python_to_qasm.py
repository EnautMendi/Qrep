import importlib.util
import os

from qiskit import QuantumCircuit
from qiskit.qasm2 import dumps
from apr_unitary_qc.qiskit.origin_qc.Bug4Q.Bug4Q_id27_origin import Bug4Q_id27

if __name__ == "__main__":
    circuit = Bug4Q_id27([0,0,0])
    print(circuit)
    qasm_code = dumps(circuit)
    print(qasm_code)
    # Save QASM code to a file
    # Ensure the output directory exists
    output_directory = f'apr_unitary_qc/qasm/mutant_qc/Bug4Q'
    os.makedirs(output_directory, exist_ok=True)
    file_path = output_directory + '/Bug4Q_id27_origin.qasm'

    with open(file_path, "a") as qasm_file:
        qasm_file.write(qasm_code)
