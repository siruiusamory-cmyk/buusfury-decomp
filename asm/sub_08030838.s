	CODE16
|sub_08030838|
	CMP      r0, #0x50
	BNE      |loc_08030840|
	MOV      r2, #2
	STRB     r2, [r1, #0x11]
|loc_08030840|
	ADD      r0, #8
	LSL      r0, r0, #0x19
	LSR      r0, r0, #0x19
	STRH     r0, [r1, #0x12]
	POP      {r4}
	BX       lr
|sub_0803084C|
|unk_0803084C|
	INCBIN	baserom.gba_0x3084c_0x30850.extracted
