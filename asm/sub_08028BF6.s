	CODE16
|sub_08028BF6|
|unk_08028BF6|
; cited by 0x080289FA (a pc-relative load targets 0x08028BFC)
		MOV r0, #0
		BX       lr
	INCBIN  baserom.gba_0x28bfa_0x28c02.extracted
|sub_08028C02|
|unk_08028C02|
	INCBIN  baserom.gba_0x28c02_0x28c04.extracted
		PUSH {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #4
	BNE      |sub_08028C22|
	MOV      r0, #0x44
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08028C22|
	ADD      r0, r4, #0
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
