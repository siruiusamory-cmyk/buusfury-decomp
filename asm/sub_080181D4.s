	CODE16
|sub_080181D4|
	STR      r1, [r6]
	LDR      r0, [r4, #0x30]
	LDR      r1, [r4, #0x4c]
	ASR      r0, r0, #8
	SUB      r0, r1, r0
	STR      r0, [r4, #0x44]
	LDR      r1, [r4, #0x60]
	LDRB     r1, [r1, #1]
	SUB      r0, r0, r1
	STR      r0, [r4, #0x3c]
	LDMIA    r5!, {r1, r2, r3, r5}
	ADD      r0, sp, #0x1c
	STMIA    r0!, {r1, r2, r3, r5}
	LDR      r2, [sp, #0x1c]
	LDR      r1, [r4, #0x38]
	SUB      r0, #0x10
	CMP      r2, r1
	BLE      |loc_080181FA|
	STR      r1, [sp, #0x1c]
|loc_080181FA|
	LDR      r2, [sp, #0x20]
	LDR      r1, [r4, #0x3c]
	CMP      r2, r1
	BLE      |loc_08018204|
	STR      r1, [sp, #0x20]
|loc_08018204|
	LDR      r2, [sp, #0x24]
	LDR      r1, [r4, #0x40]
	CMP      r2, r1
	BGE      |loc_0801820E|
	STR      r1, [sp, #0x24]
|loc_0801820E|
	LDR      r2, [sp, #0x28]
	LDR      r1, [r4, #0x44]
	CMP      r2, r1
	BGE      |loc_08018218|
	STR      r1, [sp, #0x28]
|loc_08018218|
	ADD      r5, sp, #0x2c
	LDMIA    r0!, {r0, r1, r2, r3}
	STMIA    r5!, {r0, r1, r2, r3}
	MOV      r1, #0xff
	LDR      r0, [r4, #0x24]
	ADD      r1, #0xe1
	CMP      r0, r1
	BLE      |sub_08018236|
	LDR      r0, [pc, #0x50]
	LDR      r0, [r0, #4]
	LSL      r0, r0, #0x1d
	BPL      |sub_08018236|
	MOV      r0, #0
	ADD      sp, #0x44
	POP      {r4, r5, r6, r7, pc}
