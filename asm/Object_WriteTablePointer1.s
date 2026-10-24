	CODE16
|Object_WriteTablePointer1|
	LSL      r3, r1, #3
	SUB      r1, r3, r1
	LDR      r2, [pc, #0x2c8]
	LSL      r1, r1, #2
	ADD      r1, r1, r2
	MOV      r2, #1
	LSL      r2, r2, #9
	ADD      r0, r0, r2
	STR      r1, [r0, #0x24]
	BX       lr
