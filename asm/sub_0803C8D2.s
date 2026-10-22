	CODE16
|sub_0803C8D2|
	LSR      r7, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	LDMIA    r3!, {r4}
	LSR      r4, r0, #0x20
	LDRB     r0, [r2]
	MOV      r2, #0x29
	LSL      r2, r2, #4
	ADD      r1, r1, r2
	STRB     r0, [r1]
	MOV      r0, #1
	BX       lr
	LSL      r0, r0, #0
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
