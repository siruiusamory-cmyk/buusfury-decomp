	CODE16
|sub_08019D42|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	LDRB     r1, [r0, #0x15]
	LSL      r1, r1, #1
	ADD      r0, r1, r0
	ADD      r0, #0x2e
	LDRB     r5, [r0]
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08019D64|
	LDR      r1, [pc, #0x268]
	STR      r1, [r0]
	STR      r5, [r0, #0xc]
	MOV      r1, #0
	STR      r1, [r0, #4]
|loc_08019D64|
	ADD      r5, r0, #0
	MOV      r1, #0x12
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
	LDR      r1, [pc, #0x24c]
	PUSH     {r3, lr}
	LDRB     r1, [r1]
	CMP      r1, #0
	BEQ      |sub_08019D86|
	MOV      r0, #0
	POP      {r3, pc}
