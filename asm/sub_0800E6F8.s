	CODE16
|sub_0800E6F8|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x4c]
	LDR      r3, [pc, #0x50]
	ADD      r5, r1, #0
	STR      r0, [r4]
|loc_0800E704|
	LDR      r1, [r3]
	MOV      r0, #0
	CMP      r1, #0
	BLE      |loc_0800E71C|
|loc_0800E70C|
	LSL      r2, r0, #2
	ADD      r2, r2, r3
	LDR      r2, [r2, #4]
	CMP      r2, r4
	BEQ      |loc_0800E720|
	ADD      r0, #1
	CMP      r1, r0
	BGT      |loc_0800E70C|
|loc_0800E71C|
	MOV      r0, #0
	MVN      r0, r0
|loc_0800E720|
	SUB      r1, #1
	STR      r1, [r3]
	SUB      r1, r1, r0
	BEQ      |loc_0800E738|
	LSL      r0, r0, #2
	ADD      r0, r0, r3
	LSL      r2, r1, #2
	ADD      r1, r0, #0
	ADD      r1, #8
	ADD      r0, #4
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0800E738|
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |sub_0800E85E|
	CMP      r5, #0
	BEQ      |loc_0800E74A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0800E74A|
	POP      {r4, r5, r6, pc}
|sub_0800E74C|
|unk_0800E74C|
	INCBIN	baserom.gba_0xe74c_0xe74e.extracted
