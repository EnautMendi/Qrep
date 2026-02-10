from qiskit import *

def Bug4Q_id26(indList):
    """
        Input: ind, type[list], the value of each qubit, from q{0} to q{n-1}
    """
    circuit = QuantumCircuit(2)

    # initialize
    for ind, val in enumerate(indList):
        if val == 1:
            circuit.x(circuit.qubits[ind]) 

    circuit.h(0)
    circuit.h(1)
    circuit.cx(0,1)
    circuit.measure_all()

    return circuit