	CODE16
|sub_0804FCCA|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, pc}
|sub_0804FCDA|
|unk_0804FCDA|
	INCBIN  baserom.gba_0x4fcda_0x4fcdc.extracted
		BX       lr
	INCBIN  baserom.gba_0x4fcde_0x4fce0.extracted
		BX       lr
