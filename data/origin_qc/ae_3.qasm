// Benchmark was created by MQT Bench on 2024-03-17
// For more information about MQT Bench, please visit https://www.cda.cit.tum.de/mqtbench/
// MQT Bench version: 1.1.0
// Qiskit version: 1.0.2

OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg meas[3];
u(pi/2,0,-pi) q[0];
u(pi/2,0,-pi) q[1];
u(0.9272952180016122,0,0) q[2];
cx q[0],q[2];
u(-0.9272952180016122,0,0) q[2];
cx q[0],q[2];
u(0.9272952180016122,0,0) q[2];
cx q[1],q[2];
u(-1.8545904360032244,0,0) q[2];
cx q[1],q[2];
h q[1];
cp(-pi/2) q[0],q[1];
h q[0];
u(1.8545904360032244,0,0) q[2];
barrier q[0],q[1],q[2];
measure q[0] -> meas[0];
measure q[1] -> meas[1];
measure q[2] -> meas[2];