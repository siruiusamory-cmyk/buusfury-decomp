	CODE16
|sub_0803BCF4|
	LDR      r1, [sp, #0x18]
|unk_0803BCF6|
	INCBIN	baserom.gba_0x3bcf6_0x3bcf8.extracted
	CMP      r1, r0
	BGE      |sub_0803BD02|
	MOV      r0, #1
	ADD      sp, #0x1c
	POP      {r4, r5, pc}
