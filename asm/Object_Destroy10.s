	CODE16
|Object_Destroy10|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1b8]
	ADD      r5, r1, #0
	STR      r0, [r4]
	ADD      r0, r4, #0
	ADD      r0, #0xff
	ADD      r0, #0xc1
	BL       |inc_0x0158_0x143f2| + 0x3faa
	MOV      r0, #0xff
	ADD      r0, #0xb1
	LDR      r0, [r0, r4]
	CMP      r0, #0
	BEQ      |loc_08017CB8|
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_08017CB8|
	MOV      r0, #0xff
	ADD      r0, #0x8d
	LDR      r0, [r0, r4]
	CMP      r0, #0
	BEQ      |loc_08017CCE|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08017CCE|
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeadc
	CMP      r5, #0
	BEQ      |loc_08017CE0|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08017CE0|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	CMP      r1, #3
	SUB      sp, #0x3c
	BNE      |loc_08017D9A|
	ADD      r6, r4, #0
	ADD      r6, #0xff
	ADD      r6, #0xc1
	LDR      r0, [r6, #0x10]
	ADD      r7, r2, #0
	ADD      r5, r2, #0
	CMP      r0, #0
	BEQ      |sub_08017D96|
	ADD      r1, r4, #0
	ADD      r0, sp, #0x2c
	BL       |inc_0x0158_0x143f2| + 0xfca2
	LDR      r0, [sp, #0x2c]
	LDR      r1, [r5, #8]
	CMP      r0, r1
	BGE      |sub_08017D96|
	LDR      r0, [r5]
	LDR      r1, [sp, #0x34]
	CMP      r0, r1
	BGE      |sub_08017D96|
	LDR      r0, [sp, #0x30]
	LDR      r1, [r5, #0xc]
	CMP      r0, r1
	BGE      |sub_08017D96|
	LDR      r0, [r5, #4]
	LDR      r1, [sp, #0x38]
	CMP      r0, r1
	BGE      |sub_08017D96|
	LDR      r0, [r7, #0x10]
	MOV      r2, #1
	LDRB     r1, [r0, #0x10]
	ADD      r0, #0xff
	ADD      r0, #0xa1
	EOR      r1, r2
	STRB     r1, [r4, #0x10]
	ADD      r1, r4, #0
	ADD      r1, #0xff
	ADD      r1, #0x81
	LDR      r2, [r0]
	LDR      r3, [r1, #0x20]
	LDR      r0, [r0, #4]
	LDR      r1, [r1, #0x24]
	SUB      r2, r2, r3
	SUB      r0, r0, r1
	STR      r0, [sp, #0x38]
	STR      r2, [sp, #0x34]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r2, r4, #0
	ADD      r2, #0xff
	ADD      r2, #0xbd
	STR      r6, [sp]
	ADD      r5, sp, #8
	ADD      r0, r5, #0
	LDR      r1, [r6, #0x10]
	ADD      r3, sp, #0x34
	BL       |inc_0x0158_0x143f2| + 0x12316
	LDR      r6, [pc, #0xec]
	MOV      r0, #8
	STR      r4, [r6]
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08017D7E|
	LDR      r1, [pc, #0xe0]
	STMIA    r0!, {r1, r5}
	SUB      r0, #8
|loc_08017D7E|
	BL       |inc_0x03d784_0x041118| + 0x11c
	MOV      r0, #0
	STR      r0, [r6]
	MOV      r4, #1
	MOV      r1, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0x1237a
	ADD      r0, r4, #0
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
