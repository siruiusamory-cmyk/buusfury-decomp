	CODE16
|sub_0804E9E8|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0804E9FC|
	LDR      r1, [pc, #0xc]
	STR      r1, [r0]
|loc_0804E9FC|
	ADD      r1, r0, #0
	STR      r0, [r4, #4]
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	POP      {r3, r4, r5, pc}
|sub_0804EA08|
|unk_0804EA08|
	INCBIN	baserom.gba_0x4ea08_0x4ea0a.extracted
