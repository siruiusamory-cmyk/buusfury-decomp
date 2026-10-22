	CODE16
|loc_08040D1E|
	LDR      r0, [pc, #0x178]
	PUSH     {r4}
	MOV      r1, #0
	STRH     r1, [r0, #8]
	LDRH     r3, [r0]
	MOV      r4, #0x80
	MOV      r2, #1
	BIC      r3, r4
	MOV      r4, #0x40
	BIC      r3, r4
	STRH     r3, [r0]
	STRH     r2, [r0, #8]
	LDR      r2, [pc, #0x180]
	LDR      r3, [pc, #0x150]
	STRH     r2, [r3, #8]
	LDR      r2, [pc, #0x17c]
	LDR      r3, [pc, #0x160]
	STR      r2, [r3, #0xc]
	MOV      r2, #0xc0
	STRH     r2, [r0, #2]
	LDR      r0, [pc, #0x148]
	STRB     r1, [r0, #6]
	POP      {r4}
	BX       lr
