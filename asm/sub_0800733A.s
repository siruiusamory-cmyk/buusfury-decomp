	CODE16
|sub_0800733A|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x78]
	ADD      r5, r1, #0
	STR      r0, [r4]
	ADD      r0, r4, #0
	ADD      r0, #0x14
	BL       |sub_08004102|
	LDR      r0, [pc, #0x6c]
	STR      r0, [r4]
	LDR      r0, [r4, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r5, #0
	BEQ      |loc_08007366|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08007366|
	POP      {r3, r4, r5, pc}
	PUSH     {lr}
	LDR      r1, [r0, #0x10]
	SUB      sp, #0xdc
	CMP      r1, #0
	BEQ      |loc_08007382|
	ADD      r2, r0, #0
	ADD      r2, #0x14
	MOV      r0, #0
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x48]
	ADD      r0, sp, #4
	BL       |loc_08004038|
|loc_08007382|
	ADD      sp, #0xdc
	POP      {pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08007398|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, pc}
