	CODE16
|sub_0803DB7C|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRH     r0, [r1]
	ADD      r7, r2, #0
	ADD      r5, r1, #0
	CMP      r0, #0
	SUB      sp, #0x1c
	BEQ      |loc_0803DC70|
	LDRH     r0, [r5]
	CMP      r0, #0x25
	BNE      |loc_0803DC72|
	MOV      r0, #0
	MOV      r1, #0x20
	STR      r1, [sp, #0x14]
	STR      r0, [sp, #0x18]
	ADD      r5, #2
	LDRH     r0, [r5]
	CMP      r0, #0x30
	BNE      |loc_0803DBA8|
	MOV      r1, #0x30
	STR      r1, [sp, #0x14]
	ADD      r5, #2
|loc_0803DBA8|
	LDRH     r0, [r5]
	SUB      r0, #0x30
	CMP      r0, #9
	BHI      |loc_0803DBCA|
|loc_0803DBB0|
	LDR      r0, [sp, #0x18]
	LDRH     r1, [r5]
	LSL      r3, r0, #2
	ADD      r0, r3, r0
	LSL      r0, r0, #1
	ADD      r0, r0, r1
	SUB      r0, #0x30
	STR      r0, [sp, #0x18]
	ADD      r5, #2
	LDRH     r0, [r5]
	SUB      r0, #0x30
	CMP      r0, #9
	BLS      |loc_0803DBB0|
|loc_0803DBCA|
	LDRH     r0, [r5]
	CMP      r0, #0
	BEQ      |loc_0803DBEA|
	CMP      r0, #0x53
	BEQ      |sub_0803DC02|
	CMP      r0, #0x64
	BEQ      |loc_0803DC1E|
	CMP      r0, #0x73
	BNE      |loc_0803DC80|
	LDR      r1, [r7]
	LDMIA    r1!, {r0}
	STR      r1, [r7]
	LDRH     r1, [r0]
	CMP      r1, #0
	BEQ      |loc_0803DC80|
	B        |loc_0803DBF2|
|loc_0803DBEA|
	MOV      r0, #0
	STRH     r0, [r4]
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
|loc_0803DBF2|
	LDRH     r1, [r0]
	ADD      r0, #2
	STRH     r1, [r4]
	LDRH     r1, [r0]
	ADD      r4, #2
	CMP      r1, #0
	BNE      |loc_0803DBF2|
	B        |loc_0803DC80|
