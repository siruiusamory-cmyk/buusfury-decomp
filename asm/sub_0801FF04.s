	CODE16
|sub_0801FF04|
	EXPORT |sub_0801FF04|
	PUSH     {r4, lr}
	LDR      r2, [r1]
	CMP      r2, #0
	BEQ      |sub_0801FF3A|
	MOV      r4, #0
	MOV      r0, #0xff
	ADD      r0, #0x15
	STR      r4, [r1]
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801FF32|
	LDR      r1, [pc, #0x20]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r4, [r1, #0xc]
	STR      r4, [r1, #8]
	STR      r4, [r1, #0x10]
	LDR      r1, [pc, #0x24]
	STR      r1, [r0]
|loc_0801FF32|
	BL       |inc_0x03d784_0x041118| + 0xcc
	MOV      r0, #0
	POP      {r4, pc}
