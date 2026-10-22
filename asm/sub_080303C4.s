	CODE16
|sub_080303C4|
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x7c]
	LDR      r1, [r0, #4]
	ADD      r4, r0, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	LDR      r1, [r4, #8]
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x64]
	LDR      r1, [r0, #8]
	ADD      r4, r0, #0
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	LDR      r1, [r4, #4]
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117ec
	ADD      r0, r4, #0
	BEQ      |loc_08030402|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08030402|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #8]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r4, #4]
	LDR      r0, [r0, #0x2c]
	CMP      r0, #0
	BEQ      |sub_0803043A|
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
|loc_08030424|
	BEQ      |loc_0803042E|
	LDR      r1, [pc, #0x20]
	STR      r1, [r0]
	MOV      r1, #0x1e
	STR      r1, [r0, #4]
|loc_0803042E|
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r0, [r4, #4]
	LDR      r0, [r0, #0x1c]
	ADD      r0, #1
	POP      {r4, pc}
