	CODE16
|sub_08050DD8|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x1c]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r5, #0
	BEQ      |loc_08050DF8|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050DF8|
	POP      {r3, r4, r5, pc}
|sub_08050DFA|
|unk_08050DFA|
	INCBIN	baserom.gba_0x50dfa_0x50dfe.extracted
|sub_08050DFE|
	DCW      0x0804
