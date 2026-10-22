	CODE16
|loc_0803B9A6|
	ADD      r7, r3, #0
	CMP      r3, r2
	STR      r3, [sp, #0x2c]
	STR      r2, [sp, #0x30]
	BLE      |sub_0803B9BE|
	LDR      r3, [sp, #0x34]
	MOV      r2, #3
	CMP      r3, #0
	BGT      |loc_0803B9BA|
	MOV      r2, #2
|loc_0803B9BA|
	STRB     r2, [r4, #0x10]
	B        |sub_0803B9CC|
