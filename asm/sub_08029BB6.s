	CODE16
|sub_08029BB6|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08029BD2|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08029BD2|
	POP      {r4, pc}
|sub_08029BD4|
|unk_08029BD4|
	INCBIN	baserom.gba_0x29bd4_0x29bd6.extracted
|sub_08029BD6|
	DCW      0x0300
	DCW      0x1b50
	DCW      0x0300
|unk_08029BDC|
	INCBIN	baserom.gba_0x29bdc_0x29bde.extracted
	DCW      0x0804
