	CODE16
|Battle_ComputeDamage|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	ADD      r4, r1, #0
	ADD      r1, #8
	LDMIA    r1!, {r0, r1}
	SUB      sp, #0x34
	STR      r1, [sp, #0x24]
	ADD      r2, r6, #0
	ADD      r2, #0xff
	LDRB     r1, [r0]
	LDR      r5, [r0, #4]
	ADD      r2, #0xa1
	STR      r2, [sp, #0x30]
	ADD      r2, #0x10
	STR      r2, [sp, #0x2c]
	LDR      r2, [r4, #0xc]
	ADD      r2, #0xff
	ADD      r2, #0xa1
	CMP      r1, #0
	BNE      |loc_0800EA44|
	STR      r2, [sp, #0x28]
	LDRH     r7, [r2, #0x10]
	LDRB     r0, [r0, #1]
	CMP      r0, #3
	BNE      |sub_0800EA10|
	MOV      r0, #0
	STR      r0, [r4, #0x10]
	B        |sub_0800EA2C|
