	CODE16
|loc_08009744|
	PUSH     {r4, r5, lr}
	LDR      r2, [r1]
	ADD      r4, r1, #0
	LDR      r1, [r1, #4]
	SUB      sp, #8
	STR      r1, [sp, #4]
	ADD      r1, r2, #0
	STR      r2, [sp]
	MOV      r2, #0
	CMP      r1, #0
	BGE      |loc_0800975C|
	STR      r2, [sp]
|loc_0800975C|
	LDR      r1, [sp, #4]
	MOV      r5, sp
	CMP      r1, #0
	BGE      |loc_08009766|
	STR      r2, [sp, #4]
|loc_08009766|
	LDR      r1, [sp]
	ADD      r2, r0, #0
	ADD      r2, #0x80
	ASR      r3, r1, #0xa
	LDRH     r1, [r2, #0x1c]
	CMP      r3, r1
	BLE      |loc_08009778|
	LSL      r1, r1, #0xa
	STR      r1, [sp]
|loc_08009778|
	LDR      r1, [sp, #4]
	LDRH     r2, [r2, #0x1e]
	ASR      r1, r1, #0xa
	CMP      r1, r2
	BLE      |loc_08009786|
	LSL      r1, r2, #0xa
	STR      r1, [sp, #4]
|loc_08009786|
	ADD      r1, r5, #0
	BL       |sub_080094B8|
	LDR      r0, [sp]
	LDR      r1, [r4]
	CMP      r0, r1
	BNE      |sub_080097A2|
	LDR      r1, [sp, #4]
	LDR      r0, [r4, #4]
	CMP      r1, r0
	BNE      |sub_080097A2|
	MOV      r0, #1
	ADD      sp, #8
	POP      {r4, r5, pc}
