	CODE16
|sub_0802114C|
|unk_0802114C|
; cited by 0x0802111E (a pc-relative load targets 0x08021168)
		MOV r0, #8
		DCW     0xF01C
		DCW     0xFA33
		CMP r0, #0
		BEQ      |loc_0802115C|
		LDR r1, [pc, #0x18]
		STMIA r0!, {r1, r5}
		SUB r0, #8
|loc_0802115C|
		ADD r1, r0, #0
		LDR r0, [r4]
		BL       |loc_08021094|
		DCW     0xE7F1
	INCBIN  baserom.gba_0x21166_0x2116e.extracted
