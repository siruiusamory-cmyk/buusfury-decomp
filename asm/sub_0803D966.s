	CODE16
|sub_0803D966|
	ADD      r3, r0, #0
	ADD      r0, r1, #0
	ADD      r1, r3, #0
	ADD      r1, #8
	PUSH     {r4, lr}
	LDR      r4, [r3]
	CMP      r2, #0
	BNE      |loc_0803D98C|
	CMP      r4, #0
	BEQ      |loc_0803D984|
	CMP      r4, #1
	BNE      |loc_0803D982|
	BL       |inc_0x049120_0x055620|
|loc_0803D982|
	POP      {r4, pc}
|loc_0803D984|
	LDR      r2, [r3, #4]
	BL       |inc_0x049120_0x055620| + 0x18
|loc_0803D98A|
	POP      {r4, pc}
|loc_0803D98C|
	CMP      r4, #0
	BEQ      |loc_0803D99A|
	CMP      r4, #1
	BNE      |loc_0803D98A|
	BL       |inc_0x049120_0x055620| + 0x88
	POP      {r4, pc}
|loc_0803D99A|
	LDR      r3, [r3, #4]
	BL       |inc_0x049120_0x055620| + 0x6c
	POP      {r4, pc}
	LSL      r0, r0, #0
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	LDRH     r0, [r0]
	LSL      r0, r0, #0x1b
	BPL      |sub_0803D9B4|
	MOV      r0, #3
	LSL      r0, r0, #0x19
	BX       lr
