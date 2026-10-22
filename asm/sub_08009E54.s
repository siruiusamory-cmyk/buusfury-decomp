	CODE16
|sub_08009E54|
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0x44
	ADD      r7, sp, #0x28
	ADD      r5, r0, #0
	ADD      r4, r1, #0
	ADD      r0, r7, #0
	BL       |sub_0800FDFA|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0xa1
	ADD      r2, r5, #4
	STR      r2, [sp, #0x3c]
	STR      r1, [sp, #0x40]
	LDR      r0, [r1]
	LDR      r3, [r5, #4]
	ADD      r2, #4
	ADD      r0, r0, r3
	STR      r0, [r1]
	STR      r2, [sp, #0x38]
	LDR      r0, [r1, #4]
	LDR      r2, [r2]
	ADD      r6, sp, #0x18
	ADD      r0, r0, r2
	STR      r0, [r1, #4]
	ADD      r1, r4, #0
	ADD      r0, r6, #0
	BL       |sub_0800FDFA|
	LDR      r0, [pc, #0x184]
	STR      r6, [sp, #0x14]
	LDR      r1, [r0]
	CMP      r1, #0
	BEQ      |sub_08009F06|
	ADD      r0, sp, #4
	BL       |sub_0800FDFA|
	LDR      r2, [sp, #0xc]
	LDR      r3, [sp, #0x10]
	LDR      r0, [sp, #4]
	LDR      r1, [sp, #8]
	ADD      r2, #7
	ADD      r3, #7
	LSR      r3, r3, #3
	LSR      r2, r2, #3
	LDR      r6, [sp, #0x30]
	LSR      r0, r0, #3
	LSR      r1, r1, #3
	LSL      r1, r1, #3
	LSL      r0, r0, #3
	LSL      r2, r2, #3
	LSL      r3, r3, #3
	CMP      r0, r6
	BGE      |loc_08009ED2|
	LDR      r6, [sp, #0x28]
	CMP      r6, r2
	BGE      |loc_08009ED2|
	LDR      r6, [sp, #0x34]
	CMP      r1, r6
	BGE      |loc_08009ED2|
	LDR      r6, [sp, #0x2c]
	CMP      r6, r3
	BLT      |loc_08009EEA|
|loc_08009ED2|
	LDR      r6, [sp, #0x20]
	CMP      r0, r6
	BGE      |sub_08009F06|
	LDR      r0, [sp, #0x18]
	CMP      r0, r2
	BGE      |sub_08009F06|
	LDR      r0, [sp, #0x24]
	CMP      r1, r0
	BGE      |sub_08009F06|
	LDR      r0, [sp, #0x1c]
	CMP      r0, r3
	BGE      |sub_08009F06|
|loc_08009EEA|
	LDR      r1, [sp, #0x40]
	LDR      r2, [sp, #0x3c]
	LDR      r0, [r1]
	LDR      r2, [r2]
	SUB      r0, r0, r2
	STR      r0, [r1]
	LDR      r2, [sp, #0x38]
	LDR      r0, [r1, #4]
	LDR      r2, [r2]
	SUB      r0, r0, r2
	STR      r0, [r1, #4]
	MOV      r0, #0
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
