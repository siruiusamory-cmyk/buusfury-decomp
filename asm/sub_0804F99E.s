	CODE16
|sub_0804F99E|
	LSL      r0, r0, #0xc
	MOV      r0, #0
	BX       lr
	CMP      r1, #0xff
	BCC      |loc_0804F9AE|
	LDR      r0, [r0, #4]
	ADD      r0, #1
	BX       lr
|loc_0804F9AE|
	LDR      r0, [r0]
	LSL      r1, r1, #1
	LDRH     r1, [r0, r1]
	LSL      r1, r1, #1
	LDRH     r0, [r0, r1]
	ADD      r0, #1
	BX       lr
|sub_0804F9BC|
|unk_0804F9BC|
		MOV r0, #0
		BX       lr
		MOV r0, #0
		BX       lr
		MOV r0, #1
		BX       lr
		MOV r0, #1
		BX       lr
		MOV r0, #1
		BX       lr
		MOV r0, #0
		BX       lr
		MOV r0, #0
		BX       lr
