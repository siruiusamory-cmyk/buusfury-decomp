	CODE16
|sub_0803F24C|
	PUSH     {r3, lr}
	MOV      r1, #1
	LSL      r1, r1, #0xa
	LDR      r0, [r0]
	BL       |loc_0803F3F4|
	LDR      r1, [pc, #0x16c]
	MOV      r0, #0
	STRH     r0, [r1, #2]
	SUB      r1, #0x40
	STRH     r0, [r1, #6]
	STRH     r0, [r1, #0x12]
	LDR      r1, [pc, #0x134]
	STRH     r0, [r1, #4]
	POP      {r3, pc}
