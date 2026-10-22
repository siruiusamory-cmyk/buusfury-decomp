	CODE16
|Bios_Diff16Unfilter|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	ADD      r0, #0x1c
	MOV      r3, #0
	LDRSH    r0, [r0, r3]
	LDR      r3, [pc, #0x60]
	LDR      r1, [pc, #0x60]
	MUL      r0, r3
	ADD      r0, r0, r1
	ASR      r1, r0, #0x10
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0x13440
	LDRB     r0, [r4, #0x15]
	LSL      r0, r0, #1
	ADD      r0, r0, r4
	ADD      r0, #0x2e
	LDRB     r4, [r0]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08019FAC|
	LDR      r1, [pc, #0x44]
	STR      r1, [r0]
	MOV      r1, #0
	STRB     r1, [r0, #4]
	STR      r4, [r0, #8]
|loc_08019FAC|
	ADD      r4, r0, #0
	MOV      r1, #3
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
|loc_08019FC0|
	DCW      0xda98
	DCW      0x0871,0xde7c,0x0804,0x3284,0x0300,0xd05c,0x0804,0xe244
	DCW      0x0804,0xdf18,0x0804,0xd9b0,0x0804,0xe2d8,0x0804,0x0ccd
	DCW      0x0000,0xffff
|loc_08019FE6|
	LSL      r0, r0, #0
	BGT      |sub_0801A014|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x320]
	PUSH     {r3, lr}
	LDR      r1, [r1, #0x14]
	LDR      r1, [r1, #0xc]
	CMP      r1, #0
	BNE      |sub_08019FFC|
	MOV      r0, #0
	POP      {r3, pc}
