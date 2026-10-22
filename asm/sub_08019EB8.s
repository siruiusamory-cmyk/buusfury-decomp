	CODE16
|sub_08019EB8|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	MOV      r1, #0xff
	ADD      r1, #0x2d
	BL       |inc_0x0158_0x143f2| + 0x13440
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08019EDA|
	LDR      r1, [pc, #0x108]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #4]
	STR      r1, [r0, #8]
	STR      r1, [r0, #0xc]
|loc_08019EDA|
	ADD      r5, r0, #0
	MOV      r1, #0x13
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
	LDR      r1, [pc, #0xd0]
	PUSH     {r3, lr}
	LDR      r1, [r1, #0x14]
	LDR      r1, [r1, #0xc]
	CMP      r1, #0
	BNE      |sub_08019EFE|
	MOV      r0, #0
	POP      {r3, pc}
