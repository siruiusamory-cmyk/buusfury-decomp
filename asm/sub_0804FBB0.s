	CODE16
|sub_0804FBB0|
	ADD      r1, r0, #0
	LDR      r1, [r1, #0xc]
	MOV      r0, #1
	CMP      r1, #0
	BEQ      |loc_0804FBBC|
	MOV      r0, #0
|loc_0804FBBC|
	BX       lr
	LSL      r0, r0, #0
	LDR      r0, [r0, #0xc]
	BX       lr
|sub_0804FBC4|
|unk_0804FBC4|
		LDR r0, [r0, #0x2c]
		BX       lr
		LDR r0, [r0, #0xc]
		BX       lr
		LDR r0, [r0, #0x14]
		BX       lr
		MOV r0, #0
		BX       lr
		MOV r0, #1
		BX       lr
		MOV r0, #1
		BX       lr
		MOV r0, #1
		BX       lr
