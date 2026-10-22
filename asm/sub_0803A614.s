	CODE16
|sub_0803A614|
	MOV      r0, #0
	SUB      r0, r5, r0
	POP      {r3, r4, r5, pc}
	PUSH     {r3, lr}
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803A62A|
	LDR      r1, [pc, #0xc]
	STR      r1, [r0]
|loc_0803A62A|
	POP      {r3, pc}
|sub_0803A62C|
|unk_0803A62C|
	INCBIN	baserom.gba_0x3a62c_0x3a62e.extracted
