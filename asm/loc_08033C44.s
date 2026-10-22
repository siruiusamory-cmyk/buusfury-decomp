	CODE16
|loc_08033C44|
	MOV      r7, #0
	CMP      r1, r2
	BLE      |loc_08033C76|
	STR      r3, [sp, #0x18]
	LDR      r1, [sp, #0x58]
	ADD      r1, #3
	STR      r1, [sp, #0x20]
	CMP      r0, #0
	BLE      |sub_08033C66|
	MOV      r0, #3
	STRB     r0, [r4, #0x10]
	LDR      r0, [sp, #0x44]
	STR      r0, [sp, #0x14]
	LDR      r0, [sp, #0x54]
	ADD      r0, #3
	STR      r0, [sp, #0x1c]
	B        |sub_08033CA4|
