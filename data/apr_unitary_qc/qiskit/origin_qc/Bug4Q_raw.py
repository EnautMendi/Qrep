from qiskit import *
from math import pi
from qiskit.visualization import plot_bloch_multivector, plot_histogram
from qiskit.quantum_info.operators import Operator


def Bug4Q_id8(indList):
    circ = QuantumCircuit(3)
    
    # initialize
    for ind, val in enumerate(indList):
        if val == 1:
            circ.x(circ.qubits[ind]) 

    circ.crz(pi/2,2,0)
    circ.crz(pi/4,2,1)
    U = Operator(circ)

    qae = QuantumRegister(2,'qae')
    reg_b = QuantumRegister(2,'b')
    qc = QuantumCircuit(qae,reg_b)
    qc.append(U,[qae[0],reg_b[0],reg_b[1]])
    return qc 

def Bug4Q_id25(indList):
    bit = 3
    bit_lst = list(range(bit))
    circuit = QuantumCircuit(bit, bit)
    circuit.reset(0)
    circuit.reset(1)
    circuit.reset(2)

    # initialize
    for ind, val in enumerate(indList):
        if val == 1:
            circuit.x(circuit.qubits[ind]) 

    circuit.x(0)
    circuit.x(1)    
    circuit.ccx(2,1,0)
    circuit.barrier()

    return circuit

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
    circuit.x(1)
    circuit.cx(0,1)

    return circuit

def Bug4Q_id27(indList):
    """
        Input: ind, type[list], the value of each qubit, from q{0} to q{n-1}
    """

    def QFT(n, inverse=False):
        """This function returns a circuit implementing the (inverse) QFT."""

        circuit = QuantumCircuit(n, name='IQFT' if inverse else 'QFT')
    
        # here's your old code, building the inverse QFT
        for i in range(int(n/2)):
            # note that I removed the qin register, since registers are not 
            # really needed and you can just use the qubit indices 
            circuit.swap(i, n - 1 - i)
        for i in range(n):
            circuit.h(i)
            for j in range(i + 1, n, 1):
                circuit.cp(-pi / pow(2, j - i), j, i)
    
        # now we invert it to get the regular QFT
        if inverse:
            circuit = circuit.inverse()
        
        return circuit

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

    iqft = QFT(n, inverse=True)   
    circuit.compose(iqft, inplace=True) 

    return circuit

def Bug4Q_id39(indList):
    """
        Input: ind, type[list], the value of each qubit, from q{0} to q{n-1}
    """
    qc = QuantumCircuit(4, 4)
    for i in range(4):
        qc.h(i)
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

    return qc