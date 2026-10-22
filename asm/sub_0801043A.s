	CODE16
|sub_0801043A|
	CMP      r2, #0
	BGE      |loc_08010442|
	MOV      r2, #1
	STR      r2, [r4, #4]
|loc_08010442|
	LDR      r2, [r4, #4]
	CMP      r2, #0
	BEQ      |loc_0801044A|
|unk_08010448|
	INCBIN	baserom.gba_0x10448_0x1044a.extracted
