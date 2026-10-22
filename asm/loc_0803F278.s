	CODE16
|loc_0803F278|
	LDR      r0, [pc, #0x13c]
	PUSH     {r3, lr}
	MOV      r1, #1
	LSL      r1, r1, #0xa
	LDR      r0, [r0]
	BL       |loc_0803F3F4|
	LDR      r1, [pc, #0x140]
	MOV      r0, #0
	STRH     r0, [r1, #2]
	POP      {r3, pc}
