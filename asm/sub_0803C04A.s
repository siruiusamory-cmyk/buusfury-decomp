	CODE16
|sub_0803C04A|
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [pc, #0x54]
	LDR      r2, [pc, #0x58]
	LDR      r1, [r1]
	ADD      r0, #0xff
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDMIA    r1!, {r2}
	ADD      r0, #0xa1
	STMIA    r0!, {r2}
	LDR      r1, [r1]
	STR      r1, [r0]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #0x24
	STRB     r0, [r4, #8]
	POP      {r4, pc}
	PUSH     {r3, lr}
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803C08A|
	LDR      r1, [pc, #0x2c]
	STR      r1, [r0]
|loc_0803C08A|
	POP      {r3, pc}
	LDR      r0, [pc, #0x28]
	LDR      r0, [r0]
	LDR      r2, [r0, #0x58]
	ADD      r2, #0x4c
	LDR      r2, [r2, #0x54]
	LDR      r0, [r0, #0x50]
	CMP      r2, r0
	BNE      |sub_0803C0A4|
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	MOV      r0, #1
	BX       lr
