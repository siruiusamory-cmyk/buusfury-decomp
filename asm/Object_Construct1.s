	CODE16
|Object_Construct1|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	SUB      sp, #4
	ADD      r7, sp, #0x28
	LDMIA    r7!, {r4, r5, r6, r7}
	CMP      r0, #0
	BNE      |loc_0801413A|
	MOV      r0, #0x20
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08014152|
|loc_0801413A|
	LDR      r1, [sp, #8]
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x40]
	STR      r1, [r0]
	LDR      r1, [sp, #0xc]
	STR      r1, [r0, #8]
	LDR      r1, [sp, #0x10]
	STR      r1, [r0, #0xc]
	STR      r4, [r0, #0x14]
	STRB     r6, [r0, #0x18]
	STR      r5, [r0, #0x10]
	STR      r7, [r0, #0x1c]
|loc_08014152|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	ADD      r2, r0, #0
	ADD      r0, r1, #0
	PUSH     {r4, lr}
	LDR      r1, [r2, #0x10]
	STRB     r1, [r0, #3]
	MOV      r1, #1
	STRB     r1, [r0, #2]
	LDR      r1, [pc, #0x1c]
	STR      r1, [r0, #0x20]
	LDR      r3, [r2, #8]
	LDR      r4, [r2, #0xc]
	STR      r3, [r0, #4]
	STR      r4, [r0, #8]
	LDRB     r1, [r2, #0x18]
	STRB     r1, [r0]
	LDR      r1, [r2, #0x1c]
	STR      r1, [r0, #0xc]
	LDR      r1, [r2, #0x14]
	BL       |inc_0x03d784_0x041118| + 0x356
	POP      {r4, pc}
|sub_08014180|
|unk_08014180|
	INCBIN	baserom.gba_0x14180_0x14182.extracted
|sub_08014182|
	DCW      0x0804
	DCW      0xf5a5
	DCW      0x0803
