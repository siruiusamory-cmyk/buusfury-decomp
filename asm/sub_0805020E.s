	CODE16
|sub_0805020E|
	LSL      r0, r0, #0xc
	LDR      r1, [pc, #0xc]
	MOV      r0, #1
	LDRB     r1, [r1]
	CMP      r1, #2
	BCC      |loc_0805021C|
	MOV      r0, #0
|loc_0805021C|
	BX       lr
	LSL      r0, r0, #0
	LDR      r2, [pc, #0x1b0]
	LSL      r0, r0, #0xc
	MOV      r0, #0
	BX       lr
|sub_08050228|
|unk_08050228|
		MOV r0, #1
		BX       lr
		MOV r0, #0
		BX       lr
		MOV r0, #1
		BX       lr
		MOV r0, #1
		BX       lr
		MOV r0, #0
		BX       lr
