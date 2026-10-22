	CODE16
|sub_080074EC|
	PUSH     {r3, r4, r5, lr}
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	MOV      r5, #0x10
	CMP      r0, #0
	BEQ      |loc_08007504|
	LDR      r1, [pc, #0x6c]
	STR      r1, [r0]
	LSL      r1, r5, #4
	STR      r1, [r0, #4]
	STR      r5, [r0, #8]
|loc_08007504|
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r4, [pc, #0x60]
	LDR      r0, [r4, #4]
	BL       |loc_08011DB4|
	MOV      r0, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0x8b4a
	BL       |inc_0x03d784_0x041118| + 0x11c
	MOV      r1, #1
	LDR      r0, [r4]
	BL       |loc_0800938C|
	LDR      r0, [r4, #4]
	BL       |loc_08011E0E|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0800753C|
	LDR      r1, [pc, #0x3c]
	STR      r1, [r0]
	MOV      r1, #0
	STR      r1, [r0, #4]
	STR      r5, [r0, #8]
|loc_0800753C|
	BL       |inc_0x03d784_0x041118| + 0x11c
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08007554|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
