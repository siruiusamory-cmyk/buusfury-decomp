|sub_0804EF48|
	EXPORT |sub_0804EF48|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x18
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0804EF66|
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r4, [r0, #4]
	STR      r1, [r0, #0xc]
	LDR      r2, [pc, #8]
	STR      r1, [r0, #0x10]
	STR      r2, [r0]
	STR      r1, [r0, #0x14]
|loc_0804EF66|
	POP      {r4, pc}
|sub_0804EF68|
|unk_0804EF68|
	INCBIN	baserom.gba_0x4ef68_0x4ef6a.extracted
|sub_0804EF6A|
	DCW      0x0804
