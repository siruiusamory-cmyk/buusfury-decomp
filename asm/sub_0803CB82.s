	CODE16
|sub_0803CB82|
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x19c]
	SUB      sp, #0x10
	ADD      r4, r1, #0
	LDR      r0, [r0]
	MOV      r1, #0
	LDR      r2, [pc, #0x198]
	STR      r1, [sp, #8]
	CMP      r4, #0
	STR      r0, [sp, #0xc]
	STR      r2, [sp, #4]
	BEQ      |loc_0803CBA0|
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x8d
|loc_0803CBA0|
	ADD      r0, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	MOV      r1, #4
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x17c]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [pc, #0x178]
	STR      r0, [sp, #4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_0803CBCC|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0803CBCC|
	ADD      sp, #0x10
	POP      {r4, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r0, [r1, #0x58]
	ADD      r4, r1, #0
	LDR      r0, [r0, #0x64]
	LDR      r1, [r1, #0x50]
	SUB      sp, #0x6c
	CMP      r0, r1
	BEQ      |sub_0803CBE6|
	MOV      r0, #1
	ADD      sp, #0x6c
	POP      {r4, r5, r6, r7, pc}
