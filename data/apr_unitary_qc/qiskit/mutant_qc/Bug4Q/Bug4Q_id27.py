from math import  pi,pow
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit

def Bug4Q_id27(indList):
    """
        Input: ind, type[list], the value of each qubit, from q{0} to q{n-1}
    """

    def IQFT(circuit, qin, n):
        for i in range (int(n/2)):
            circuit.swap(qin[i], qin[n -1 -i])
        for i in range (n):
            circuit.h(qin[i])
            for j in range (i +1, n, 1):
                circuit.cp(-pi/ pow(2, j-i), qin[j], qin[i])        # 原本是cu1，替换成cp

    n = 3
    qin = QuantumRegister(n)
    cr = ClassicalRegister(n)
    circuit = QuantumCircuit(qin, cr, name="Inverse_Quantum_Fourier_Transform")

    # initialize
    for ind, val in enumerate(indList):
        if val == 1:
            circuit.x(circuit.qubits[ind]) 

    circuit.h(qin)
    circuit.z(qin[2])
    circuit.s(qin[1])
    circuit.z(qin[0])
    circuit.t(qin[0])

    IQFT(circuit, qin, n)
    circuit.measure (qin, cr)

    return circuit