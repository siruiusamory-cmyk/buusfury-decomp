	CODE16
|sub_08006E3C|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r0, [pc, #0x1a0]
	LDR      r0, [r0, #0x14]
	BL       |sub_08011A1E|
	LDR      r0, [pc, #0x19c]
	LDR      r1, [r0]
	LDR      r0, [pc, #0x194]
	LDR      r0, [r0, #0x10]
	BL       |loc_080126D4|
	LDR      r0, [pc, #0x18c]
	LDR      r0, [r0, #0xc]
	BL       |loc_0800425C|
	LDR      r0, [pc, #0x184]
	LDR      r1, [pc, #0x180]
	LDR      r0, [r0, #8]
	MOV      r5, #0x10
	ADD      r0, #0x80
	LDR      r2, [r0, #0x10]
	LDR      r0, [pc, #0x180]
	LDR      r1, [r1, #4]
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x17c]
	CMP      r2, #0
	BNE      |sub_08006EE8|
	LDR      r6, [pc, #0x16c]
	LDR      r2, [r6]
	LDRH     r2, [r2, #4]
	LSL      r2, r2, #0x1d
	LSR      r2, r2, #0x1f
	BEQ      |sub_08006EE8|
	MOV      r7, #0
	ADD      r3, r7, #0
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08006E9C|
	LSL      r1, r5, #4
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x158]
	STR      r5, [r0, #8]
	STR      r1, [r0]
|loc_08006E9C|
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r0, [r6, #0x14]
	BL       |Object_Construct8|
	LDR      r0, [pc, #0x14c]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_08006EBA|
	ADD      r0, r4, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0x92fe
	LDR      r0, [pc, #0x140]
	STR      r0, [r4]
|loc_08006EBA|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r0, [r6, #0x14]
	BL       |loc_08011E0E|
	MOV      r1, #1
	LDR      r0, [r6, #8]
	BL       |loc_0800938C|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08006EE0|
	LDR      r1, [pc, #0x120]
	STMIA    r0!, {r1, r7}
	SUB      r0, #8
	STR      r5, [r0, #8]
|loc_08006EE0|
	BL       |inc_0x03d784_0x041118| + 0x11c
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
