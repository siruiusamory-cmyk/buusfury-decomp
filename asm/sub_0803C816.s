	CODE16
|sub_0803C816|
	LSR      r7, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	STRH     r0, [r3, #4]
	LSR      r3, r5, #1
	BCS      |loc_0803C79C|
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, lr}
	LDR      r0, [r1, #0x58]
	ADD      r4, r1, #0
	MOV      r1, #1
	LSL      r1, r1, #9
	ADD      r1, r4, r1
	SUB      sp, #0x24
	STR      r0, [r1]
	MOV      r0, #0xff
	ADD      r0, #0x23
	BL       |inc_0x0158_0x143f2|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeca0
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	LDR      r5, [pc, #0x74]
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x115a4
	MOV      r1, #1
	LSL      r1, r1, #0xa
	CMP      r0, r1
	BLT      |loc_0803C8B6|
	ADD      r1, r4, #0
	ADD      r0, sp, #0xc
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	LDR      r0, [sp, #0xc]
	LDR      r2, [sp, #0x14]
	LDR      r3, [sp, #0x18]
	ADD      r2, r0, r2
	STR      r2, [sp, #4]
	ASR      r2, r2, #1
	LDR      r0, [sp, #0x10]
	STR      r2, [sp, #4]
	ADD      r0, r0, r3
	STR      r0, [sp, #8]
	ASR      r0, r0, #1
	STR      r2, [sp, #0x1c]
	MOV      r2, #0x37
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x20]
	MOV      r0, #0
	ADD      r1, sp, #0x1c
	BL       |inc_0x153f2_0x1a3f2| + 0x413a
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	MOV      r1, #0x45
	LDR      r2, [pc, #0x30]
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDR      r4, [pc, #0x2c]
	LDR      r0, [r5]
	MOV      r2, #0x40
	MOV      r3, #0
	ADD      r0, r0, r4
	BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_0803C8B6|
	ADD      sp, #0x24
	POP      {r4, r5, pc}
|sub_0803C8BA|
|unk_0803C8BA|
		MOV r0, #1
		BX       lr
