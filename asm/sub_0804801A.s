	CODE16
|sub_0804801A|
|unk_0804801A|
; cited by 0x08047FF6 (a pc-relative load targets 0x08048030)
		LDR r0, [pc, #0x18]
		ADD r0, pc
		CMP r2, r0
		BEQ      |loc_0804802A|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |Thunk_JumpRegister1|
|loc_0804802A|
		MOV r0, #0
		DCW     0xE7F2
	INCBIN  baserom.gba_0x4802e_0x48034.extracted
		DCD     0xF7FB7FDD
