	CODE16
|sub_08020FE6|
|unk_08020FE6|
		LDR r1, [r2, #0x30]
		CMP r1, r0
		BNE      |loc_08020FF0|
		MOV r0, #0
		DCW     0xE7F8
|loc_08020FF0|
		LDRB r1, [r2, #0x14]
		LDR r3, [r0, #0x3c]
		MOV r4, #1
		EOR r3, r4
		CMP r1, r3
		BEQ      |loc_08021000|
		MOV r0, #0
		DCW     0xE7F0
|loc_08021000|
		LDR r1, [r0, #0x38]
		LDR r3, [r0, #0x30]
		LDR r4, [r0, #0x34]
		MUL r3, r1
		MUL r4, r1
		ADD r1, r3, #0
		STR r3, [sp, #8]
		ADD r3, r4, #0
		STR r4, [sp, #0xc]
		LDR r4, [r0, #0x20]
		LDR r0, [r0, #0x24]
		ADD r1, r4, r1
		ADD r0, r0, r3
		STR r0, [sp, #0xc]
		ADD r0, r1, #0
		STR r1, [sp, #8]
		LDR r1, [sp, #0xc]
		ADD r3, r0, #0
		ADD r4, r1, #0
		ADD r1, #0xc
		SUB r4, #0xc
		SUB r3, #0xc
		ADD r0, #0xc
		STR r0, [sp, #8]
		STR r1, [sp, #0xc]
		MOV r1, sp
		ADD r0, r2, #4
		STR r3, [sp]
		STR r4, [sp, #4]
		BL       |inc_0x049120_0x055620| + 0xa1a0
		CMP r0, #0
		BEQ      |loc_08021046|
		MOV r0, #1
		DCW     0xE7CD
|loc_08021046|
		MOV r0, #0
		DCW     0xE7CB
|loc_0802104A|
|unk_0802104A|
		MOV r0, #0
		DCW     0xE7C9
|loc_0802104E|
|unk_0802104E|
; cited by 0x08020DBE (a pc-relative load targets 0x08021054)
		MOV r0, #0
		DCW     0xE7C7
	INCBIN  baserom.gba_0x21052_0x2105a.extracted
|sub_0802105A|
|unk_0802105A|
	INCBIN  baserom.gba_0x2105a_0x2105c.extracted
		CMP r1, #3
	BLT      |sub_08021064|
	MOV      r0, #1
	BX       lr
