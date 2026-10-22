	CODE16
|sub_080232FA|
	ADD      r3, r6, #0
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r7, #4]
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x24]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |sub_0802333E|
	MOV      r0, #0xff
	ADD      r0, #0x3d
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08023336|
	LDR      r1, [pc, #0x194]
	STMIA    r0!, {r1, r6}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r6, [r1, #0xc]
	STR      r6, [r1, #8]
	STR      r6, [r1, #0x10]
	LDR      r1, [pc, #0x188]
	STR      r1, [r0]
|loc_08023336|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #1
	POP      {r3, r4, r5, r6, r7, pc}
