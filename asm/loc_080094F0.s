	CODE16
|loc_080094F0|
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	LDMIA    r1!, {r4, r5}
	MOV      r1, #0
	CMP      r4, #0
	SUB      sp, #8
	BGE      |loc_08009500|
	ADD      r4, r1, #0
|loc_08009500|
	CMP      r5, #0
	BGE      |loc_08009506|
	ADD      r5, r1, #0
|loc_08009506|
	ADD      r2, r0, #0
	ADD      r2, #0x80
	LDRH     r1, [r2, #0x1c]
	CMP      r4, r1
	BLE      |loc_08009512|
	ADD      r4, r1, #0
|loc_08009512|
	LDRH     r1, [r2, #0x1e]
	CMP      r5, r1
	BLE      |loc_0800951A|
	ADD      r5, r1, #0
|loc_0800951A|
	LSL      r2, r4, #0xa
	STR      r2, [sp]
	LSL      r2, r5, #0xa
	STR      r2, [sp, #4]
	MOV      r1, sp
	BL       |sub_080094B8|
	LDR      r0, [r6]
	CMP      r4, r0
	BNE      |sub_0800953A|
	LDR      r0, [r6, #4]
	CMP      r5, r0
	BNE      |sub_0800953A|
	MOV      r0, #1
	ADD      sp, #8
	POP      {r4, r5, r6, pc}
