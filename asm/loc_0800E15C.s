	CODE16
|loc_0800E15C|
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	SUB      sp, #0x80
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r1, [r0, #8]
	CMP      r1, #0
	BLE      |loc_0800E17A|
	SUB      r1, #1
	STR      r1, [r0, #8]
|loc_0800E17A|
	ADD      r1, r0, #0
	ADD      r1, #0x16
	MOV      r3, #0
	LDRSH    r1, [r1, r3]
	CMP      r1, #0
	BEQ      |loc_0800E1AA|
	LDR      r0, [r0, #8]
	CMP      r0, #0
	BNE      |loc_0800E1AA|
	LDR      r1, [r4]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r0, r4, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #2]
	ADD      r2, sp, #0x70
	LDR      r1, [pc, #0x1fc]
	LSR      r0, r0, #8
	STR      r0, [sp, #0x70]
	ADD      r0, sp, #4
	BL       |loc_08004098|
|loc_0800E1AA|
	ADD      sp, #0x80
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r4, r0, #0
	BL       |loc_08013C66|
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	BL       |sub_0800E074|
	POP      {r3, r4, r5, pc}
