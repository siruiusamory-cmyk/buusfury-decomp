	CODE16
|sub_08039C14|
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0x3c
	ADD      r0, sp, #0x24
	ADD      r4, r1, #0
	ADD      r1, r0, #0
	MOV      r2, #8
	ADD      r1, #0x18
	LDR      r3, [pc, #0x15c]
	BL       |inc_0x046118_0x049114| + 0xedc
	LDR      r0, [pc, #0x158]
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0xa1
	STR      r0, [sp, #0x14]
	STR      r0, [sp, #0x18]
	LDR      r2, [r1]
	LDR      r5, [r1, #4]
	ADD      r3, r2, r0
	STR      r3, [sp, #0xc]
	STR      r3, [sp, #0x1c]
	STR      r3, [sp, #0x24]
	ADD      r5, r5, r0
	MOV      r3, #3
	LSL      r3, r3, #0xc
	STR      r3, [sp, #0x14]
	STR      r5, [sp, #0x10]
	STR      r5, [sp, #0x20]
	STR      r5, [sp, #0x28]
	STR      r0, [sp, #0x18]
	LDR      r5, [r1]
	ADD      r2, r1, #4
	ADD      r3, r5, r3
	LDR      r5, [r2]
	STR      r3, [sp, #0xc]
	ADD      r0, r5, r0
	STR      r0, [sp, #0x10]
	ADD      r0, r3, #0
	LDR      r3, [sp, #0x10]
	STR      r0, [sp, #0x1c]
	STR      r0, [sp, #0x2c]
	STR      r3, [sp, #0x20]
	STR      r3, [sp, #0x30]
	LDR      r3, [pc, #0x11c]
	MOV      r0, #1
	LSL      r0, r0, #0xc
	STR      r0, [sp, #0x14]
	STR      r3, [sp, #0x18]
	LDR      r1, [r1]
	ADD      r7, sp, #4
	ADD      r0, r1, r0
	LDR      r1, [r2]
	STR      r0, [sp, #0xc]
	ADD      r1, r1, r3
	STR      r1, [sp, #0x10]
	STR      r1, [sp, #0x20]
	STR      r1, [sp, #0x38]
	STR      r0, [sp, #0x1c]
	STR      r0, [sp, #0x34]
	MOV      r2, #0x20
	ADD      r0, r7, #0
	LDR      r1, [pc, #0xfc]
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r0, [sp, #0x24]
	ADD      r3, sp, #0
	ASR      r0, r0, #8
	STRH     r0, [r3, #0x10]
	LDR      r0, [sp, #0x28]
	LDR      r1, [pc, #0xf0]
	ASR      r0, r0, #8
	STRH     r0, [r3, #0x12]
	LDR      r0, [sp, #0xc]
	MOV      r6, #0
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #2
	MVN      r6, r6
	ADD      r3, r6, #0
	ADD      r2, r0, r1
	ADD      r1, r7, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r5, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0xc8]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [pc, #0xc0]
	MOV      r2, #0x20
	ADD      r1, #0x20
	ADD      r0, r7, #0
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r0, [sp, #0x2c]
	ADD      r3, sp, #0
	ASR      r0, r0, #8
	STRH     r0, [r3, #0x10]
	LDR      r0, [sp, #0x30]
	LDR      r1, [pc, #0xac]
	ASR      r0, r0, #8
	STRH     r0, [r3, #0x12]
	LDR      r0, [sp, #0xc]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r2, r0, r1
	ADD      r3, r6, #0
	ADD      r1, r7, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r6, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x8c]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [pc, #0x80]
	MOV      r2, #0x20
	ADD      r1, #0x40
	ADD      r0, r7, #0
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r0, [sp, #0x34]
	ADD      r3, sp, #0
	ASR      r0, r0, #8
	STRH     r0, [r3, #0x10]
	LDR      r0, [sp, #0x38]
	LDR      r1, [pc, #0x70]
	ASR      r0, r0, #8
	STRH     r0, [r3, #0x12]
	LDR      r0, [sp, #0xc]
	LSL      r3, r0, #3
	SUB      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r2, r0, r1
	MOV      r3, #0
	MVN      r3, r3
	ADD      r1, r7, #0
	MOV      r0, #0
	BL       |inc_0x0158_0x143f2| + 0xf534
	ADD      r7, r0, #0
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x4c]
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDRB     r1, [r7, #8]
	ADD      r2, r7, #0
	ADD      r2, #0xff
	ADD      r1, #0xff
	STRB     r1, [r7, #8]
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r1, r6, #0
	ADD      r2, #0xc1
	STR      r4, [r2, #0x34]
	ADD      r1, #0xff
	ADD      r0, #0xc1
	STR      r4, [r0, #0x34]
	ADD      r1, #0xc1
	STR      r4, [r1, #0x34]
	ADD      r4, #0xff
	ADD      r4, #0xc1
	STR      r7, [r4, #0x30]
	STR      r5, [r2, #0x38]
	ADD      r0, #0x38
	STMIA    r0!, {r6, r7}
	STR      r5, [r1, #0x3c]
	ADD      sp, #0x3c
	MOV      r0, #1
	POP      {r4, r5, r6, r7, pc}
|sub_08039D7A|
|unk_08039D7A|
; cited by 0x08039C22 (a pc-relative load targets 0x08039D80)
	INCBIN	baserom.gba_0x39d7a_0x39d8e.extracted
|sub_08039D8E|
	DCW      0x0877
	DCW      0x1274
	DCW      0x0871
	DCW      0x32c4
	DCW      0x0300
