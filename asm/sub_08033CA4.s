	CODE16
|sub_08033CA4|
	STR      r4, [sp, #0x30]
	LDRB     r0, [r4, #0x10]
	ADD      r3, sp, #0x20
	ADD      r2, sp, #0x10
	STRB     r0, [r3, #4]
	LDR      r0, [pc, #0xb8]
	STR      r0, [sp, #0x2c]
	MOV      r0, #1
	LSL      r0, r0, #0xa
	B        |sub_08033CBA|
