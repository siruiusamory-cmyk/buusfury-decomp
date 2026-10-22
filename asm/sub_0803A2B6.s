	CODE16
|sub_0803A2B6|
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803A2C6|
	LDR      r1, [pc, #0xcc]
	STR      r1, [r0]
|loc_0803A2C6|
	POP      {r3, pc}
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r3, #0x38
	STRB     r3, [r1, #8]
	STRB     r2, [r1, #0x11]
	STR      r2, [r0, #4]
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	CMP      r0, #0
	BEQ      |loc_0803A2F6|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r0, [pc, #0x88]
	LDR      r1, [r4, #4]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_0803A2F6|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
	POP      {r4, pc}
