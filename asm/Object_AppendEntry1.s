	CODE16
|Object_AppendEntry1|
	ADD      r0, #0xe4
	LDR      r2, [r0]
	CMP      r2, #0xfa
	BEQ      |loc_08004466|
	ADD      r2, #1
	LDR      r3, [r0]
	STR      r2, [r0]
	LSL      r2, r3, #2
	ADD      r0, r2, r0
	MOV      r2, #0
	ORR      r1, r2
	LSL      r1, r1, #4
	ADD      r0, #4
	LSR      r1, r1, #4
	STR      r1, [r0]
|loc_08004466|
	BX       lr
