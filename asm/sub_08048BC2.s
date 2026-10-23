	CODE16
|sub_08048BC2|
	LSR      r4, r0, #0x20
	ADD      r2, #0x48
	LSL      r0, r0, #0xc
	POP      {r3, r4, r5, pc}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048BD4|
|unk_08048BD4|
	INCBIN	baserom.gba_0x48bd4_0x48bd6.extracted
	CODE16
|dat_08048BD6|
	DCW      0x0300
|unk_08048BD8|
	INCBIN	baserom.gba_0x48bd8_0x48bda.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048BE4|
|unk_08048BE4|
	INCBIN	baserom.gba_0x48be4_0x48be6.extracted

