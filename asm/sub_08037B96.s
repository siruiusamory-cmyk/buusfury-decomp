	CODE16
|sub_08037B96|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08037BB2|
	LDR      r1, [pc, #8]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08037BB2|
	POP      {r4, pc}
|sub_08037BB4|
|unk_08037BB4|
	INCBIN	baserom.gba_0x37bb4_0x37bb6.extracted
|sub_08037BB6|
	DCW      0x0300
	DCW      0xb0f8
	DCW      0x0804
