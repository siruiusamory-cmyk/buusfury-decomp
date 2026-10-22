	CODE16
|sub_0805440C|
	LSL      r7, r1, #4
|unk_0805440E|
	INCBIN	baserom.gba_0x5440e_0x54412.extracted
	LSL      r7, r7, #0x1f
	LSL      r0, r0, #0
	LDRB     r0, [r6, #0x1f]
	LSL      r3, r2, #0
	LSL      r0, r0, #0x10
	BX       pc
	LSL      r0, r0, #0
