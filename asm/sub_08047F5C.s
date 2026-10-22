	CODE16
|sub_08047F5C|
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r1, r0, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LDRB     r0, [r7, #0x1f]
	PUSH     {r3, r4, r5, lr}
	PUSH     {r0, r1, r2}
	SUB      sp, #0xc
	LDR      r4, [sp, #0x28]
	ADD      r5, sp, #4
	ADD      r1, r5, #0
	MOV      r0, #0
	ADD      r3, sp, #0x14
	ADD      r2, sp, #0xc
	STR      r4, [sp]
	BL       |loc_08047F84|
