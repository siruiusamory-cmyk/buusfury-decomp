	CODE16
|sub_0801FD54|
	LDR      r0, [r4, #0x20]
	ADD      r0, #1
	STR      r0, [r4, #0x20]
|loc_0801FD5A|
	STR      r7, [r4, #0x10]
	MOV      r0, #0
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	MOV      r6, #0
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r2, #1
	BEQ      |sub_0801FE2C|
	CMP      r5, #7
	BNE      |loc_0801FE54|
	MOV      r0, #0xff
	ADD      r0, #0x1d
	BL       |GBARam_Malloc|
	LDR      r7, [pc, #0x1c4]
	CMP      r0, #0
	BEQ      |loc_0801FD9A|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r6, [r0, #4]
	STR      r7, [r0]
	STR      r6, [r1, #0xc]
	STR      r6, [r1, #8]
	MOV      r2, #0xff
	ADD      r2, #0x15
	STR      r6, [r1, #0x10]
	STRB     r6, [r2, r0]
	LDR      r2, [pc, #0x1b0]
	STR      r2, [r0]
	STR      r4, [r1, #0x18]
|loc_0801FD9A|
	BL       |inc_0x03d784_0x041118| + 0x11c
	CMP      r0, #2
	BNE      |loc_0801FE5E|
	MOV      r0, #0xff
	ADD      r0, #0x21
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801FDC4|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	STR      r6, [r0, #4]
	STR      r7, [r0]
	ADD      r1, #1
	STR      r6, [r1, #0xc]
	STR      r6, [r1, #8]
	LDR      r2, [pc, #0x18c]
	STR      r6, [r1, #0x10]
	STR      r2, [r0]
	STR      r4, [r1, #0x14]
|loc_0801FDC4|
	BL       |inc_0x03d784_0x041118| + 0x11c
	CMP      r0, #2
	BNE      |loc_0801FE5E|
	ADD      r0, r4, #0
	BL       |loc_0801F556|
	MOV      r1, #7
	MOV      r0, #0
	BL       |inc_0x049120_0x055620| + 0x71dc
	BL       |inc_0x03d784_0x041118| + 0x29dc
	MOV      r0, #0xff
	ADD      r0, #0x19
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801FE00|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	STR      r6, [r0, #4]
	STR      r7, [r0]
	ADD      r1, #1
	STR      r6, [r1, #0xc]
	STR      r6, [r1, #8]
	LDR      r2, [pc, #0x154]
	STR      r6, [r1, #0x10]
	STR      r2, [r0]
	STR      r6, [r1, #0x14]
|loc_0801FE00|
	BL       |inc_0x03d784_0x041118| + 0x11c
	MOV      r0, #0xff
	ADD      r0, #0x15
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801FE24|
	ADD      r1, r0, #0
	ADD      r1, #0xff
	STR      r6, [r0, #4]
	STR      r7, [r0]
	ADD      r1, #1
	STR      r6, [r1, #0xc]
	STR      r6, [r1, #8]
	STR      r6, [r1, #0x10]
	LDR      r1, [pc, #0x130]
	STR      r1, [r0]
|loc_0801FE24|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
