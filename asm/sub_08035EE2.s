	CODE16
|sub_08035EE2|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08035EFE|
	LDR      r1, [pc, #8]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08035EFE|
	POP      {r4, pc}
|sub_08035F00|
|unk_08035F00|
	INCBIN	baserom.gba_0x35f00_0x35f02.extracted
|sub_08035F02|
	DCW      0x0875
|unk_08035F04|
	INCBIN	baserom.gba_0x35f04_0x35f06.extracted
	DCW      0x0804
