	CODE16
|sub_08039078|
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803908C|
	LDR      r1, [pc, #0x10]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0803908C|
	POP      {r4, pc}
|loc_0803908E|
	DCW      0x0000
	DCW      0x1bb0,0x0300,0xffff
|loc_08039096|
	LDRB     r7, [r7, #0x1f]
	BCS      |loc_08038FEC|
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, lr}
	SUB      sp, #0x34
	STR      r1, [sp, #0x20]
	LDRB     r0, [r1, #0x10]
	ADD      r3, sp, #0
	ADD      r4, r1, #0
	STRB     r0, [r3, #0x14]
	LDR      r0, [pc, #0x74]
	MOV      r5, sp
	STR      r0, [sp, #0x1c]
	MOV      r0, #1
	LSL      r0, r0, #0xc
	STR      r0, [sp, #0x18]
	ADD      r0, sp, #4
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	MOV      r0, #0xff
	ADD      r0, #0xd1
	LDR      r0, [r0, r4]
	ADD      r3, sp, #0
	STRB     r0, [r3]
	STR      r4, [sp, #0x30]
	LDR      r4, [pc, #0x58]
	ADD      r2, r5, #0
	MOV      r1, #0
	LDR      r0, [r4, #4]
	BL       |inc_0x0158_0x143f2| + 0x11ab4
	CMP      r0, #0
	BEQ      |sub_080390FE|
	LDR      r4, [r4]
	MOV      r0, #2
	BL       |inc_0x03d784_0x041118| + 0x2348
	ADD      r0, #0x30
	LSL      r3, r0, #1
	ADD      r0, r3, r0
	LDR      r1, [pc, #0x40]
	LSL      r0, r0, #2
	ADD      r1, r0, r1
	LDR      r0, [pc, #0x3c]
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r4, r0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #1
	ADD      sp, #0x34
	POP      {r4, r5, pc}
