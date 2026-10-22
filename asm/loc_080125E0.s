	CODE16
|loc_080125E0|
	MOV      r0, #0xff
	ADD      r0, #0xc5
	BX       lr
	LSL      r0, r0, #0
	ADD      r0, r1, #0
	ADD      r1, r2, #0
	PUSH     {r3, lr}
	LDR      r2, [r0]
	LDR      r3, [r2, #4]
	ADD      r3, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08012618|
	LDR      r1, [pc, #0x2e8]
	STR      r1, [r0]
	LDR      r1, [r4, #0xc]
	STR      r1, [r0, #4]
	LDR      r1, [r4, #8]
	LDR      r2, [r4, #4]
	STR      r1, [r0, #0xc]
	STR      r2, [r0, #8]
|loc_08012618|
	STR      r0, [r4, #0xc]
	LDR      r0, [pc, #0x2dc]
	STRH     r0, [r4, #4]
	STRH     r0, [r4, #6]
	MVN      r0, r0
	STRH     r0, [r4, #8]
	STRH     r0, [r4, #0xa]
	POP      {r4, pc}
