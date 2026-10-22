	CODE16
|sub_08048DB2|
	LSL      r0, r0, #0xc
|loc_08048DB4|
	SUB      sp, #0x1a0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048DC0|
|unk_08048DC0|
	INCBIN	baserom.gba_0x48dc0_0x48dc2.extracted
