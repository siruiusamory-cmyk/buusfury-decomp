	CODE16
|loc_08050544|
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_08050556|
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08050562|
|loc_08050556|
	LDR      r1, [pc, #0xc]
	MOV      r2, #0
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	STR      r2, [r0, #8]
	STR      r2, [r0, #0xc]
|loc_08050562|
	POP      {r4, pc}
|sub_08050564|
|unk_08050564|
	INCBIN	baserom.gba_0x50564_0x50566.extracted
