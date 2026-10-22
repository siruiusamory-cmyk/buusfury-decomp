	CODE16
|sub_0802054A|
	LSL      r0, r0, #0x18
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0x18
	LSL      r1, r3, #9
	LSL      r0, r0, #0
	SUB      r3, r0, #6
	LSL      r0, r0, #0
	ADD      r0, r2, r4
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, lr}
	LDR      r4, [r1, #4]
	SUB      sp, #0x14
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0xa1
	LDMIA    r1!, {r2}
	LDR      r1, [r1]
	ASR      r2, r2, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #8]
	ADD      r1, r2, #0
	STR      r2, [sp, #4]
	LDR      r2, [sp, #8]
	STR      r1, [sp, #0xc]
	STR      r2, [sp, #0x10]
	LDR      r2, [r0, #8]
	ADD      r1, r0, #0
	STR      r2, [sp]
	ADD      r2, r0, #0
	ADD      r3, r0, #0
	ADD      r3, #0xc
	ADD      r2, #0x1c
	ADD      r1, #0x14
	ADD      r5, sp, #0xc
	ADD      r0, r5, #0
|loc_08020590|
	BL       |inc_0x153f2_0x1a3f2| + 0x3edc
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x3c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      sp, #0x14
	POP      {r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r2, [r1, #4]
	LDR      r5, [r0, #0xc]
	ADD      r2, #0xff
	ADD      r2, #0xa1
	LDR      r4, [r2]
	ADD      r4, r4, r5
	STR      r4, [r2]
	LDR      r4, [r2, #4]
	LDR      r3, [r0, #0x10]
	ADD      r3, r4, r3
	STR      r3, [r2, #4]
	LDR      r3, [r0, #0x1c]
	SUB      r3, #1
	STR      r3, [r0, #0x1c]
	BNE      |loc_080205DE|
	LDR      r3, [r0, #0x14]
	LDR      r4, [r0, #0x18]
	LSL      r3, r3, #8
	STMIA    r2!, {r3}
	LSL      r4, r4, #8
	STR      r4, [r2]
	MOV      r2, #1
	STR      r2, [r0, #0x20]
	LDR      r2, [r0]
	LDR      r3, [r2, #0x14]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_080205DE|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, lr}
	LDR      r0, [r1, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x40]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
	PUSH     {r4, lr}
	LDR      r0, [r1, #4]
	LDR      r1, [r0]
	ADD      r4, r0, #0
	LDR      r2, [r1, #0x40]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r4, pc}
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r1, #4]
	SUB      sp, #0x14
	ADD      r5, r0, #0
	ADD      r1, r5, #0
	ADD      r1, #0xff
	ADD      r1, #0xa1
	LDMIA    r1!, {r2}
	LDR      r1, [r1]
	ASR      r2, r2, #8
	ASR      r1, r1, #8
	STR      r1, [sp, #8]
	ADD      r1, r2, #0
	STR      r2, [sp, #4]
	LDR      r2, [sp, #8]
	STR      r1, [sp, #0xc]
	STR      r2, [sp, #0x10]
	LDR      r2, [r4, #8]
	ADD      r3, r4, #0
	STR      r2, [sp]
	ADD      r2, r4, #0
	ADD      r2, #0x1c
	ADD      r3, #0xc
	ADD      r1, r4, #0
	ADD      r1, #0x14
	ADD      r0, sp, #0xc
	BL       |inc_0x153f2_0x1a3f2| + 0x3edc
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x3c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4, #0xc]
	ADD      r2, r0, #0
	CMP      r0, #0
	BGE      |loc_08020660|
|unk_0802065E|
	INCBIN	baserom.gba_0x2065e_0x20660.extracted
