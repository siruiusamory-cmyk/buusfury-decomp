	CODE16
|sub_0804FEBE|
	LSL      r0, r0, #0
	MOV      r0, #1
	BX       lr
	MOV      r2, #1
	LDR      r1, [r1, #0x14]
	LDR      r3, [pc, #0xc]
	ADD      r0, r2, #0
	CMP      r1, r3
	BEQ      |loc_0804FED2|
	MOV      r0, #0
|loc_0804FED2|
	SUB      r0, r2, r0
	BX       lr
|sub_0804FED6|
|unk_0804FED6|
; cited by 0x0804FEC8 (a pc-relative load targets 0x0804FED8)
	INCBIN  baserom.gba_0x4fed6_0x4fedc.extracted
		LDR r0, [r1, #0x58]
		ADD r0, #0x4c
		LDR r0, [r0, #0x54]
		LDR r1, [r1, #0x50]
		CMP r0, r1
		BNE      |sub_0804FEEC|
		MOV r0, #1
		B        |inc_0x049120_0x055620| + 0x6dce
