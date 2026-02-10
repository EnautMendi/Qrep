from qiskit import *

def Bug4Q_id39(indList):
    """
        Input: ind, type[list], the value of each qubit, from q{0} to q{n-1}
    """
    qc = QuantumCircuit(4, 4)

    # initialize
    for ind, val in enumerate(indList):
        if val == 1:
            qc.x(qc.qubits[ind]) 

    qc.cx(3, 1)
    qc.cx(1, 0)
    qc.cx(0, 1)
    qc.ccx(3, 2, 1)
    qc.cx(1, 2)
    qc.cx(3, 2)
    qc.measure(0, 0)
    qc.measure(1, 1)
    qc.measure(2, 2)
    qc.measure(3, 3)

    return qc