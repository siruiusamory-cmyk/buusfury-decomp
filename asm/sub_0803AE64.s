	CODE16
|sub_0803AE64|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803AE80|
	LDR      r1, [pc, #0x24]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0803AE80|
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803AE9E|
	LDR      r1, [pc, #8]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0803AE9E|
	POP      {r4, pc}
|sub_0803AEA0|
|unk_0803AEA0|
	INCBIN	baserom.gba_0x3aea0_0x3aea2.extracted
|sub_0803AEA2|
	DCW      0x0804
	DCW      0xd674
	DCW      0x0804
