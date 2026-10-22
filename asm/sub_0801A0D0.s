	CODE16
|sub_0801A0D0|
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
	BEQ      |loc_0801A0F4|
	LDR      r1, [pc, #0x230]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #4]
	STR      r1, [r0, #8]
	STR      r5, [r0, #0xc]
|loc_0801A0F4|
	ADD      r5, r0, #0
	MOV      r1, #0x13
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
	LDR      r1, [pc, #0x204]
	PUSH     {r3, lr}
	LDR      r1, [r1, #0x14]
	LDR      r1, [r1, #0xc]
	CMP      r1, #0
	BNE      |sub_0801A118|
	MOV      r0, #0
	POP      {r3, pc}
