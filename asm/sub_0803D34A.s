	CODE16
|sub_0803D34A|
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803D35E|
	LDR      r1, [pc, #0x14]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0803D35E|
	POP      {r4, pc}
|sub_0803D360|
|unk_0803D360|
	INCBIN	baserom.gba_0x3d360_0x3d362.extracted
