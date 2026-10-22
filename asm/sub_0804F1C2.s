	CODE16
|sub_0804F1C2|
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x18]
	MOV      r1, #0
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x953a
	ADD      r0, r4, #0
	BEQ      |loc_0804F1E2|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0804F1E2|
	POP      {r4, pc}
|sub_0804F1E4|
|unk_0804F1E4|
; cited by 0x0804F1C8 (a pc-relative load targets 0x0804F1E4)
		DCD     0x0877B134
		BX       lr
	INCBIN  baserom.gba_0x4f1ea_0x4f1ec.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f1ee_0x4f1f0.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f1f2_0x4f1f4.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f1f6_0x4f1f8.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f1fa_0x4f1fc.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f1fe_0x4f200.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f202_0x4f204.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f206_0x4f208.extracted
		BX       lr
	INCBIN  baserom.gba_0x4f20a_0x4f20c.extracted
		BX       lr
