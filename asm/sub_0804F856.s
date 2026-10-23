	CODE16
|sub_0804F856|
	LSR      r7, r0, #0x20
	MOV      r1, #9
	LSL      r1, r1, #6
	ADD      r0, r0, r1
	BX       lr
	MOV      r1, #1
	LSL      r1, r1, #9
	ADD      r0, r0, r1
	LDR      r0, [r0, #0x28]
	BX       lr
	LSL      r0, r0, #0
	LDR      r0, [pc, #0]
	BX       lr
|sub_0804F870|
|unk_0804F870|
	INCBIN	baserom.gba_0x4f870_0x4f872.extracted
|dat_0804F872|
	DCW      0x0805
	DCW      0x22a3
	DCW      0x0092
	DCW      0x1882
