	CODE16
|sub_0803C55E|
	MOV      r0, #2
	STR      r0, [r4, #0x14]
	STRH     r7, [r5, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r5, #8]
	LDR      r0, [r4, #0x14]
	LSL      r0, r0, #1
	ADD      r0, #1
	STRB     r0, [r5, #0x11]
	STR      r7, [r4, #0x10]
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r5, [r1, #4]
	ADD      r4, r0, #0
	LDRH     r0, [r5, #0x12]
	SUB      sp, #0x20
	LDR      r6, [pc, #0xf0]
	ADD      r0, #1
	STRH     r0, [r5, #0x12]
	LDR      r1, [r4, #0x10]
	CMP      r1, #0
	BEQ      |loc_0803C59E|
	LDR      r0, [r4, #0x18]
	SUB      r0, #1
	STR      r0, [r4, #0x18]
	BNE      |loc_0803C59E|
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	MOV      r0, #0
	STR      r0, [r4, #0x10]
|loc_0803C59E|
	LDRH     r0, [r5, #0x12]
	CMP      r0, #8
	BNE      |sub_0803C64E|
	LDR      r0, [r4, #0x14]
	LSL      r0, r0, #1
	ADD      r0, #2
	STRB     r0, [r5, #0x11]
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r0, #0xa1
	LDMIA    r0!, {r1}
	LDR      r0, [r0]
	ASR      r1, r1, #8
	ASR      r0, r0, #8
	STR      r0, [sp, #0xc]
	ADD      r0, r1, #0
	STR      r1, [sp, #8]
	LDR      r1, [sp, #0xc]
	STR      r0, [sp, #0x10]
	STR      r1, [sp, #0x14]
	LDR      r1, [pc, #0xac]
	LDR      r0, [r4, #0x14]
	ADD      r1, #4
	LSL      r0, r0, #3
	ADD      r0, r0, r1
	LDR      r1, [sp, #0x10]
	LDR      r2, [r0]
	ADD      r1, r1, r2
	LDR      r2, [sp, #0x14]
	LDR      r0, [r0, #4]
	STR      r1, [sp, #8]
	ADD      r0, r2, r0
	STR      r0, [sp, #0xc]
	ADD      r0, r1, #0
	LDR      r1, [sp, #0xc]
	STR      r0, [sp, #0x18]
	STR      r1, [sp, #0x1c]
	LDR      r0, [r4, #8]
	LDR      r1, [sp, #0x18]
	SUB      r0, r0, r1
	LDR      r1, [r4, #0xc]
	LDR      r2, [sp, #0x1c]
	STR      r0, [sp]
	SUB      r1, r1, r2
	STR      r1, [sp, #4]
	STR      r1, [sp, #0xc]
	ADD      r1, r0, #0
	CMP      r0, #0
	STR      r0, [sp, #8]
	BGE      |loc_0803C604|
|unk_0803C602|
	INCBIN	baserom.gba_0x3c602_0x3c604.extracted
