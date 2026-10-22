	CODE16
|sub_08037474|
|unk_08037474|
; cited by 0x08037274 (a pc-relative load targets 0x08037478)
		MOV r0, #0
		BX       lr
	INCBIN  baserom.gba_0x37478_0x3747e.extracted
|sub_0803747E|
|unk_0803747E|
	INCBIN  baserom.gba_0x3747e_0x37480.extracted
		PUSH {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r6, r3, #0
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_0803749C|
	MOV      r0, #0x70
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_0803749C|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
