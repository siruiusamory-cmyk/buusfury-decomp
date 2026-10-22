	CODE16
|loc_08013E06|
	LDR      r1, [r0, #4]
	CMP      r1, #0
	BEQ      |loc_08013E1E|
	MOV      r2, #0x62
	LDRH     r2, [r2, r0]
	LSL      r2, r2, #8
	LSR      r2, r2, #0xe
	SUB      r1, r1, r2
	STR      r1, [r0, #4]
	BPL      |loc_08013E1E|
	MOV      r1, #0
	STR      r1, [r0, #4]
|loc_08013E1E|
	BX       lr
|sub_08013E20|
|unk_08013E20|
	INCBIN	baserom.gba_0x13e20_0x13e22.extracted
