	CODE16
|loc_080097EA|
	PUSH     {lr}
	LDMIA    r1!, {r3}
	SUB      sp, #0x10
	ASR      r3, r3, #8
	STR      r3, [sp]
	LDR      r1, [r1]
	ASR      r1, r1, #8
	STR      r1, [sp, #4]
	LDRB     r1, [r2]
	LDRB     r2, [r2, #1]
	ADD      r1, r3, r1
	STR      r1, [sp, #8]
	LDR      r1, [sp, #4]
	ADD      r1, r1, r2
	STR      r1, [sp, #0xc]
	ADD      r0, #0x80
	LDR      r1, [r0, #0x28]
	MOV      r0, sp
	BL       |loc_08009324|
	ADD      sp, #0x10
	POP      {pc}
