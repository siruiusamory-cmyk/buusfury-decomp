	CODE16
|State_CopyBlock1|
	PUSH     {r4, r5, lr}
	LDR      r1, [r0, #4]
	MOV      r4, #0
	CMP      r1, #0
	SUB      sp, #0xdc
	BEQ      |loc_080091C6|
	LDR      r4, [r1, #0x34]
|loc_080091C6|
	LDR      r5, [pc, #0x38]
	CMP      r4, #0
	LDMIA    r5!, {r1, r2, r3}
	STMIA    r0!, {r1, r2, r3}
	LDMIA    r5!, {r2, r3}
	STMIA    r0!, {r2, r3}
	BEQ      |loc_080091E4|
	MOV      r0, #0
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x48]
	MOV      r2, #0
	ADD      r1, r4, #0
	ADD      r0, sp, #4
	BL       |loc_08004038|
|loc_080091E4|
	LDR      r4, [pc, #0x14]
	LDR      r0, [r4, #0xc]
	BL       |loc_08009A2A|
	LDR      r0, [r4, #0x14]
	BL       |loc_08011E0E|
	LDR      r0, [r4, #0x20]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4d00
	ADD      sp, #0xdc
	POP      {r4, r5, pc}
|sub_080091FC|
|unk_080091FC|
	INCBIN	baserom.gba_0x91fc_0x91fe.extracted
|sub_080091FE|
	DCW      0x0807
	DCW      0x1968
	DCW      0x0300
