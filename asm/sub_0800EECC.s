	CODE16
|sub_0800EECC|
	PUSH     {r4, r5}
	STR      r1, [r0, #0x38]
	LDR      r2, [r0, #0x3c]
	CMP      r2, #0
	BEQ      |sub_0800EEFE|
	CMP      r1, #0
	BEQ      |sub_0800EEFA|
	ADD      r2, r0, #0
	ADD      r2, #0x74
	STR      r2, [r0, #0x34]
	MOV      r2, #0
	MOV      r4, #0xff
	ADD      r4, #1
|loc_0800EEE6|
	LDR      r3, [r0, #0x3c]
	ADD      r5, r0, r2
	LDRB     r3, [r3, r2]
	ADD      r5, #0x70
	ADD      r2, #1
	LDRB     r3, [r1, r3]
	CMP      r2, r4
	STRB     r3, [r5, #4]
	BLT      |loc_0800EEE6|
	B        |loc_0800EF00|
