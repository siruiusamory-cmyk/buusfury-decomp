	CODE16
|sub_0803B772|
	LDR      r3, [sp, #0x3c]
	LDR      r0, [sp, #0x40]
	ASR      r3, r3, #8
	LSL      r5, r3, #1
	ADD      r6, r5, #0
	ASR      r2, r0, #8
	ADD      r0, r2, #1
	SUB      r5, r5, r2
	SUB      r2, r3, r2
	LSL      r2, r2, #1
	STR      r2, [sp, #0x2c]
	MOV      r2, #0
	STR      r2, [sp, #0x24]
	MOV      r2, #0xff
	ADD      r2, #1
	STR      r2, [sp, #0x1c]
	STR      r2, [sp, #0x28]
	STR      r2, [sp, #0x20]
	STR      r6, [sp, #0x30]
	MOV      r3, #0xff
	LDR      r2, [sp, #0x44]
	LDR      r6, [sp, #0x54]
	MVN      r3, r3
	CMP      r2, r6
	BLE      |loc_0803B7AC|
	LDR      r2, [sp, #0x24]
	STR      r3, [sp, #0x1c]
|unk_0803B7A8|
	INCBIN	baserom.gba_0x3b7a8_0x3b7aa.extracted
	STR      r2, [sp, #0x24]
|loc_0803B7AC|
	LDR      r2, [sp, #0x48]
	LDR      r6, [sp, #0x58]
	CMP      r2, r6
	BLE      |loc_0803B7BC|
	LDR      r2, [sp, #0x28]
	STR      r3, [sp, #0x20]
|unk_0803B7B8|
	INCBIN	baserom.gba_0x3b7b8_0x3b7ba.extracted
	STR      r2, [sp, #0x28]
|loc_0803B7BC|
	CMP      r0, r1
	BGE      |loc_0803B7C2|
	SUB      r1, r0, #1
|loc_0803B7C2|
	SUB      r6, r1, #1
	CMP      r6, #0
	BLE      |loc_0803B8B0|
	CMP      r5, #0
	BGE      |sub_0803B824|
	LDR      r0, [sp, #0x30]
	LDR      r1, [sp, #0x24]
	ADD      r5, r5, r0
	LDR      r0, [sp, #0x34]
	ADD      r0, r0, r1
	STR      r0, [sp, #0x34]
	LDR      r0, [sp, #0x38]
	LDR      r1, [sp, #0x28]
	ADD      r0, r0, r1
	STR      r0, [sp, #0x38]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x54]
	ADD      r2, r2, r1
	ADD      r1, sp, #0x34
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |loc_0803B8CA|
	LDR      r0, [sp, #0x34]
	LDR      r1, [sp, #0x24]
	STR      r6, [sp, #0x10]
	SUB      r0, r0, r1
	STR      r0, [sp, #0x34]
	LDR      r0, [sp, #0x38]
	LDR      r1, [sp, #0x28]
	ADD      r3, sp, #0x34
	SUB      r0, r0, r1
	STR      r0, [sp, #0x38]
	ADD      r1, sp, #0x54
	LDMIA    r1!, {r0, r1}
	STR      r0, [sp, #8]
	STR      r1, [sp, #0xc]
	ADD      r1, sp, #0x24
	LDMIA    r1!, {r0, r1}
	STR      r0, [sp]
	STR      r1, [sp, #4]
	ADD      r1, r4, #0
	ADD      r0, r7, #0
	LDMIA    r3!, {r2, r3}
	BL       |sub_0803B4FC|
	ADD      sp, #0x5c
	POP      {r4, r5, r6, r7, pc}
