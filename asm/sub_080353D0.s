	CODE16
|sub_080353D0|
	PUSH     {r3, lr}
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080353E0|
	LDR      r1, [pc, #0x1f0]
	STR      r1, [r0]
|loc_080353E0|
	POP      {r3, pc}
	PUSH     {r0, r1, r4, r5, r6, r7, lr}
	MOV      r0, #0xff
	ADD      r0, #0x81
	SUB      sp, #0x44
	STR      r0, [sp, #0x40]
	LDR      r0, [pc, #0x1d8]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	CMP      r1, #0
	BNE      |sub_080353FC|
	MOV      r0, #1
	ADD      sp, #0x4c
	POP      {r4, r5, r6, r7, pc}
