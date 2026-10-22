	CODE16
|sub_08009704|
	ADD      r3, r1, #0
	MOV      r1, #0xff
	ADD      r1, #1
	LSL      r1, r3
	LSL      r2, r2, #0x1e
	CMP      r2, #0
	LDRH     r2, [r0, #4]
	BGE      |loc_0800971A|
	ORR      r1, r2
	STRH     r1, [r0, #4]
	B        |loc_0800971E|
|loc_0800971A|
	BIC      r2, r1
	STRH     r2, [r0, #4]
|loc_0800971E|
	LDRH     r0, [r0, #4]
	LDR      r1, [pc, #0x1d8]
	STRH     r0, [r1, #0x10]
	POP      {r4, r5}
	BX       lr
