	CODE16
|sub_0804E50A|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
|sub_0804E51E|
|unk_0804E51E|
	INCBIN  baserom.gba_0x4e51e_0x4e520.extracted
		BX       lr
	INCBIN  baserom.gba_0x4e522_0x4e524.extracted
		BX       lr
