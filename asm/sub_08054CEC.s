	CODE16
|sub_08054CEC|
	SUB      r3, #0x80
	LSL      r3, r0, #9
	ASR      r1, r0, #4
	LSL      r0, r6, #6
	ASR      r1, r0, #2
	STR      r0, [r4, r6]
	SUB      r3, #0x40
	CMP      r3, r0
|unk_08054CFC|
	INCBIN	baserom.gba_0x54cfc_0x54d00.extracted
	BX       pc
	LSL      r0, r0, #0
