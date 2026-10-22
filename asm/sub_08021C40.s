	CODE16
|sub_08021C40|
	PUSH     {r3, r4, r5, lr}
	MOV      r5, #0
	STR      r5, [r0, #0x2c]
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x26c]
	MOV      r1, #0xb4
	STR      r1, [r0, #4]
	MOV      r1, #0x3c
	STR      r1, [r4, #0x30]
	STR      r5, [r4, #0x18]
	STR      r5, [r0, #0xc]
	STR      r5, [r4, #0x20]
	STR      r5, [r0, #0x10]
	STR      r5, [r4, #0x28]
	MOV      r0, #0
	BL       |sub_0802e732|
	ADD      r1, r0, #0
	STR      r0, [r4, #0x1c]
	LDR      r0, [pc, #0x24c]
	LDR      r0, [r0, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r0, #0
	STR      r5, [r4, #0x24]
	BL       |loc_08021BF8|
	BL       |inc_0x03d784_0x041118| + 0x29dc
	POP      {r3, r4, r5, pc}
	PUSH     {r3, lr}
	CMP      r0, #0
	BEQ      |loc_08021C8E|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08021C8E|
	BL       |inc_0x03d784_0x041118| + 0x29fe
	LDR      r1, [pc, #0x220]
	MOV      r0, #0
	LDR      r2, [r1, #0x10]
	STRH     r0, [r2, #2]
	LDR      r2, [r1, #0x10]
	STRH     r0, [r2, #4]
	LDR      r2, [r1, #0x10]
	STRH     r0, [r2, #6]
	LDR      r2, [r1, #0x10]
	ADD      r2, #0xff
	ADD      r2, #0x81
	STRH     r0, [r2, #0xc]
	LDR      r2, [r1, #0x14]
	STRH     r0, [r2, #2]
	LDR      r2, [r1, #0x14]
	STRH     r0, [r2, #4]
	LDR      r2, [r1, #0x14]
	STRH     r0, [r2, #6]
	LDR      r1, [r1, #0x14]
	ADD      r1, #0xff
	ADD      r1, #0x81
	STRH     r0, [r1, #0xc]
	POP      {r3, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x1f4]
	ADD      r4, r0, #0
	LDR      r0, [r7, #0xc]
	CMP      r0, #0
	BEQ      |sub_08021CD0|
	MOV      r0, #0xff
	POP      {r3, r4, r5, r6, r7, pc}
