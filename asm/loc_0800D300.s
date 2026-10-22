	CODE16
|loc_0800D300|
|unk_0800D300|
		NEG r0, r0
	MOV      r3, #0x2c
	LDR      r1, [pc, #0x220]
	MUL      r0, r3
	ADD      r0, r0, r1
	ADD      r0, #4
	BX       lr
