	CODE16
|sub_0800FA80|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	BL       |loc_0800E97E|
	LDR      r2, [pc, #0x25c]
	LDR      r1, [r5]
	MOV      r0, #0xa3
	LSL      r0, r0, #2
	ADD      r1, r1, r2
	ADD      r0, r4, r0
	LDR      r2, [r0]
	ASR      r1, r1, #0xa
	LSL      r1, r1, #0xa
	ADD      r1, r2, r1
	STR      r1, [r0]
	MOV      r1, #1
	LSL      r1, r1, #9
	ADD      r1, r4, r1
	LDR      r1, [r1, #0x24]
	LDR      r1, [r1, #4]
	LDR      r2, [r0]
	LSL      r1, r1, #0xa
	CMP      r2, r1
	BLE      |loc_0800FAB4|
	STR      r1, [r0]
|loc_0800FAB4|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0x228]
	LSL      r1, r1, #2
	ADD      r2, #0xc
	PUSH     {r3, lr}
	LDR      r1, [r2, r1]
	BL       |loc_0800ED18|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r3, [pc, #0x214]
	LSL      r2, r1, #2
	ADD      r3, #0xc
	LDR      r2, [r3, r2]
	LDR      r3, [r0, #0x14]
	CMP      r3, r2
	BNE      |sub_0800FAE2|
	BL       |loc_0800EEB0|
	CMP      r0, #0
	BEQ      |sub_0800FAE2|
	MOV      r0, #1
	POP      {r3, pc}
