	CODE16
|sub_0801E0A6|
	CMP      r0, #0
	BLE      |loc_0801E0AE|
	SUB      r0, #1
	STR      r0, [r4, #0x40]
|loc_0801E0AE|
	ADD      r0, sp, #8
	LDR      r1, [r4, #0x1c]
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	LDR      r0, [sp, #8]
	LDR      r1, [sp, #0x10]
	LDR      r2, [sp, #0x14]
	ADD      r1, r0, r1
	LDR      r0, [sp, #0xc]
	STR      r1, [sp]
	ADD      r0, r0, r2
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	ASR      r1, r1, #1
	STR      r0, [sp, #0x1c]
	LDR      r2, [sp, #0x1c]
	STR      r1, [sp]
	STR      r1, [sp, #0x18]
	LSL      r1, r1, #8
	STR      r0, [sp, #4]
	STR      r1, [r4, #0x20]
	LSL      r2, r2, #8
	STR      r2, [r4, #0x24]
	LDR      r0, [r4, #0x40]
	LDR      r1, [pc, #0x68]
	ASR      r0, r0, #3
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LSL      r0, r0, #2
	ADD      r0, r0, r1
	STR      r0, [r4, #0x18]
	ADD      r0, r4, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x475c
	LDR      r0, [r4, #0x1c]
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
	ADD      r0, r1, #0
	STR      r1, [sp, #0x14]
	LDR      r1, [r4, #0x1c]
	ADD      r1, #0xff
	ADD      r1, #0x91
	LDRB     r1, [r1, #0xd]
	LSR      r1, r1, #1
	ADD      r0, r0, r1
	ADD      r0, #1
	STR      r0, [r4, #4]
	ADD      sp, #0x20
	POP      {r4, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x40]
	LSL      r2, r1, #0x1f
	BPL      |sub_0801E12E|
	MOV      r0, #0
	POP      {r3, pc}
