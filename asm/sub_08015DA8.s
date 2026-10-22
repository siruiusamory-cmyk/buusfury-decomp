	CODE16
|sub_08015DA8|
	PUSH     {r4, lr}
	LDR      r1, [r0, #0x1c]
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x64f6
	LDR      r0, [r4, #4]
	LDR      r1, [r4, #0x20]
	BL       |inc_0x0158_0x143f2| + 0x64f6
	POP      {r4, pc}
	PUSH     {r4, r5, r6, r7}
	MOV      r7, #1
	MOV      r1, #0xff
	ADD      r1, #0x11
	SUB      sp, #0x10
	STR      r7, [r1, r0]
	LDR      r5, [r0, #0x4c]
	SUB      r6, r7, #5
	ADD      r4, r0, #0
	ADD      r4, #0x4c
	ADD      r2, r6, #0
	MOV      r1, #0
	CMP      r5, #0
	BLE      |loc_08015DEE|
|loc_08015DDA|
	LSL      r3, r1, #1
	ADD      r3, r3, r1
	LSL      r3, r3, #2
	ADD      r3, r3, r4
	LDR      r3, [r3, #0xc]
	ADD      r1, #1
	ADD      r2, r3, r2
	ADD      r2, #0xa
	CMP      r5, r1
	BGT      |loc_08015DDA|
|loc_08015DEE|
	LDR      r1, [r0, #0x2c]
	LDR      r3, [r0, #0x24]
	SUB      r1, r1, r3
	CMP      r1, r2
	LDR      r1, [r0, #0x1c]
	BLT      |sub_08015E16|
	MOV      r2, #0
	STR      r2, [r1, #0x10]
	STR      r2, [r1, #8]
	LDR      r1, [r0, #0x20]
	STR      r2, [r1, #0x10]
	STR      r2, [r1, #8]
	STR      r2, [r0, #0x34]
	LDR      r1, [r0, #0x4c]
	STR      r1, [r0, #0x38]
	LDR      r1, [r0, #0x24]
	STR      r1, [r0, #0x48]
	ADD      sp, #0x10
	POP      {r4, r5, r6, r7}
	BX       lr
