	CODE16
|sub_08025204|
	MOV      r3, #1
	LSL      r3, r3, #0xc
	ADD      r3, sp
	LDR      r1, [r3, #0x78]
	LDR      r0, [r1, #0x3c]
	LDR      r2, [r4, #0x10]
	MOV      r1, #1
	CMP      r2, #2
	BGT      |loc_08025218|
	MOV      r1, #0
|loc_08025218|
	STR      r1, [r0, #0x20]
	LDR      r0, [r4]
	LDR      r1, [r6]
	LDR      r2, [r4, #0x10]
	SUB      r1, #4
	CMP      r1, r2
	BLE      |sub_0802522A|
	MOV      r1, #1
	B        |loc_0802522C|
