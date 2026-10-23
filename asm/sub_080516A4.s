	CODE16
|sub_080516A4|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_080516BA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080516BA|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080516CA|
	BL       |GBARam_Free|
|loc_080516CA|
	POP      {r3, pc}
|sub_080516CC|
|unk_080516CC|
	INCBIN	baserom.gba_0x516cc_0x516ce.extracted
|sub_080516CE|
	DCW      0x0804
