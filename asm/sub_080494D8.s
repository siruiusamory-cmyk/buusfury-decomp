	CODE16
|sub_080494D8|
	STRB     r1, [r7, #0x15]
	LSL      r0, r0, #0
	POP      {r0, r4, r6, pc}
|sub_080494DE|
|unk_080494DE|
; cited by 0x080495F4 (a pc-relative load targets 0x0804962C)
	INCBIN	baserom.gba_0x494de_0x49b44.extracted
