	CODE16
|sub_08009ADA|
	LSR      r7, r0, #0x20
	LSL      r1, r6, #0x1d
	LSR      r5, r0, #0x20
	ADD      r0, r4, r6
	LSL      r0, r0, #0xc
	LSL      r1, r4, #0xa
	LSR      r5, r0, #0x20
	LSL      r5, r5, #0xa
	LSR      r5, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x224]
	STR      r0, [r4]
	LDR      r0, [r1, #0xc]
	LDR      r2, [r1, #8]
	STR      r0, [r4, #8]
	STR      r2, [r4, #4]
	LDR      r0, [r1, #4]
	BL       |inc_0x046118_0x049114| + 0x988
	STR      r0, [r4, #0xc]
	ADD      r0, r4, #0
	POP      {r4, pc}
	MOV      r3, #0
	STRH     r3, [r0]
	STRH     r2, [r0, #2]
	STR      r1, [r0, #4]
	BX       lr
