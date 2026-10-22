	CODE16
|loc_0800C454|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_0800C46E|
	MOV      r0, #0x34
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_0800C46E|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_0800C46E|
	MOV      r3, #0x40
	ADD      r0, r4, #0
	LDR      r2, [pc, #0x128]
	LDR      r1, [pc, #0x128]
	BL       |loc_08011874|
	LDR      r0, [pc, #0x128]
	STR      r0, [r4]
	LDR      r1, [r5]
	LDR      r3, [r5, #4]
	SUB      r1, #4
	LSL      r1, r1, #8
	SUB      r3, #4
	LSL      r3, r3, #8
	STR      r1, [r4, #0x1c]
	ADD      r0, r4, #0
	ADD      r0, #0x1c
	STR      r3, [r4, #0x20]
	LDR      r0, [r6]
	STR      r0, [r4, #0x24]
	LDR      r0, [r6, #4]
	STR      r0, [r4, #0x28]
	MOV      r0, #0x20
	STR      r0, [r4, #0x18]
	MOV      r0, #0x38
	STRB     r0, [r4, #8]
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0, #0x18]
	SUB      r1, #1
	STR      r1, [r0, #0x18]
	BNE      |sub_0800C4BE|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0xe8]
	SUB      r0, #8
	LDR      r0, [r0]
	BL       |loc_08011944|
	POP      {r3, pc}
