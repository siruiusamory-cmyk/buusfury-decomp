	CODE16
|loc_0803C60C|
	STR      r0, [sp, #4]
	ADD      r0, r1, #0
	STR      r1, [sp]
	LDR      r1, [sp, #4]
	STR      r0, [sp, #0x10]
	ADD      r3, sp, #0x10
	STR      r1, [sp, #0x14]
	LDMIA    r3!, {r1, r3}
	ADD      r2, sp, #0x10
	ADD      r0, r2, #4
	CMP      r1, r3
	BLE      |loc_0803C626|
	ADD      r0, r2, #0
|loc_0803C626|
	LDR      r0, [r0]
	ADD      r2, r4, #0
	ASR      r0, r0, #1
	ADD      r0, #1
	ADD      r2, #8
	STR      r0, [r4, #0x18]
	STR      r2, [sp]
	ADD      r3, r5, #0
	MOV      r0, #0
	LDRB     r2, [r5, #0x10]
	ADD      r1, sp, #0x18
	BL       |sub_0802e444|
	ADD      r1, r0, #0
	STR      r0, [r4, #0x10]
	LDR      r0, [r6]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      sp, #0x20
	POP      {r4, r5, r6, pc}
