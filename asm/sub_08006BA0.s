	CODE16
|sub_08006BA0|
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0x28]
	ADD      r5, r0, #0
	LDR      r0, [r4]
	BL       |loc_08011AA0|
	LDR      r0, [r4, #4]
	LDR      r0, [r0]
	CMP      r0, #0
	BNE      |loc_08006BBE|
	MOV      r2, #0
	MOV      r1, #0xc
	LDR      r0, [r4]
	BL       |loc_08011C0C|
|loc_08006BBE|
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x2c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	POP      {r3, r4, r5, pc}
|sub_08006BCC|
|unk_08006BCC|
	INCBIN	baserom.gba_0x6bcc_0x6bce.extracted
|sub_08006BCE|
	DCW      0x0807
