	CODE16
|sub_0804EE84|
	MOV      r0, #0
	MOV      r1, #1
	SUB      r0, r1, r0
	BX       lr
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	LDR      r1, [pc, #0xc]
	MOV      r0, #1
	LDRB     r1, [r1]
	CMP      r1, #1
	BEQ      |loc_0804EE9C|
	MOV      r0, #0
|loc_0804EE9C|
	BX       lr
	LSL      r0, r0, #0
	ADD      r2, #0xe4
	LSL      r0, r0, #0xc
	MOV      r0, #0
	BX       lr
|sub_0804EEA8|
|unk_0804EEA8|
		MOV r0, #0
		BX       lr
