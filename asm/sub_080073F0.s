	CODE16
|sub_080073F0|
	PUSH     {r4, lr}
	MOV      r2, #0x85
	LSL      r2, r2, #2
	SUB      sp, #0x30
	ADD      r2, r1, r2
	STR      r2, [sp]
	ADD      r2, r0, #0
	ADD      r2, #0x10
	LDR      r1, [r0, #0x14]
	ADD      r4, sp, #4
	ADD      r0, r4, #0
	LDR      r3, [pc, #0x54]
	BL       |loc_0801246E|
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800741C|
	LDR      r1, [pc, #0x48]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0800741C|
	BL       |inc_0x03d784_0x041118| + 0x11c
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |sub_080124D2|
	ADD      sp, #0x30
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	MOV      r0, #0x18
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0800743E|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
