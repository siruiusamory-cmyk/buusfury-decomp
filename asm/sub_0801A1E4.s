	CODE16
|sub_0801A1E4|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	MOV      r1, #0xa0
	BL       |inc_0x0158_0x143f2| + 0x13440
	MOV      r0, #0x18
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801A202|
	LDR      r1, [pc, #0x134]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r1, [r0, #4]
|loc_0801A202|
	ADD      r5, r0, #0
	MOV      r1, #0x13
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
	LDR      r1, [pc, #0xf8]
	PUSH     {r3, lr}
	LDR      r1, [r1, #0x14]
	LDR      r1, [r1, #0xc]
	CMP      r1, #0
	BNE      |sub_0801A226|
	MOV      r0, #0
	POP      {r3, pc}
