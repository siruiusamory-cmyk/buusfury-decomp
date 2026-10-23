	CODE16
|sub_0804EC0C|
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [pc, #4]
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, pc}
|sub_0804EC18|
|unk_0804EC18|
; cited by 0x0804EC10 (a pc-relative load targets 0x0804EC18)
		DCD     0x03003234
		BX       lr
	INCBIN  baserom.gba_0x4ec1e_0x4ec20.extracted
		BX       lr
