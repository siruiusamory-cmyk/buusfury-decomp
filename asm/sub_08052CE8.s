	CODE16
|sub_08052CE8|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0xc]
	ADD      r5, r1, #0
	CMP      r0, #0
	BEQ      |loc_08052D00|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08052D00|
	LDR      r0, [pc, #0xc]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052D0E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052D0E|
	POP      {r3, r4, r5, pc}
|sub_08052D10|
|unk_08052D10|
	INCBIN	baserom.gba_0x52d10_0x52d12.extracted
|sub_08052D12|
	DCW      0x0804
