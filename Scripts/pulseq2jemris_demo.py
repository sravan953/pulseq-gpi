"""
This is starter code to export a Gradient Recalled Echo as a XML file that can be read in JEMRIS.
"""
from mr_gpi.pulseq2jemris.jseqtree import JSeqTree

fov = 220e-3
deltak = 1 / fov

j = JSeqTree()

rf1 = j.make_rf_pulse(
    {"Axis": "RF", "Duration": "0.1", "FlipAngle": "20", "InitialPhase": "C*(C+1)*50", "Observe": "C=C1.Counter"})
a1 = j.add_to_atomic(rf1)

d1 = j.make_delay({"Delay": "TE", "DelayType": "C2C", "Observe": "TE=P.TE", "StartSeq": "A1", "StopSeq": "A3"})

t1 = j.make_trap_grad_pulse({"Area": "-A/2", "Axis": "GX", "Observe": "A=P4.Area"})
t2 = j.make_trap_grad_pulse({"Area": "-KMY+C*DKY", "Axis": "GY", "Observe": "KMY=P.KMAXy, C=C1.Counter, DKY=P.DKy"})
a2 = j.add_to_atomic(t1, t2)

t3 = j.make_trap_grad_pulse(
    {"ADCs": "NX", "Axis": "GX", "FlatTopArea": "2*KMX", "FlatTopTime": "4", "Observe": "KMX=P.KMAXx, NX=P.Nx",
     "PhaseLock": "1"})
a3 = j.add_to_atomic(t3)

t4 = j.make_trap_grad_pulse({"Area": "1.5*A", "Axis": "GX", "Observe": "A=P4.Area"})
t5 = j.make_trap_grad_pulse({"Area": "-A", "Axis": "GY", "Observe": "A=P3.Area"})
a4 = j.add_to_atomic(t4, t5)

d2 = j.make_delay({"Delay": "TR", "DelayType": "B2E", "Name": "D2", "Observe": "TR=P.TR", "StartSeq": "A1"})

c1 = j.add_to_concat({"Observe": "NY=P.Ny", "Repetitions": "NY"}, a1, d1, a2, a3, a4, d2)
c2 = j.add_to_concat({}, c1)

j.make_seq_tree({"FOVx": "128", "FOVy": "128", "FOVz": "1", "Name": "P", "Nx": "32", "Ny": "32", "Nz": "1", "TE": "8",
                 "TR": "50"}, c2)
j.write_xml('gre_gpi_jemris')
