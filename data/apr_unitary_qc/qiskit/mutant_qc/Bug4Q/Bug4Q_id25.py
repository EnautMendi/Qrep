from qiskit import QuantumCircuit
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
    circuit.ccx(0,1,2)
    circuit.barrier()
    circuit.measure(bit_lst,bit_lst)

    return circuit