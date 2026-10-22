	CODE16
|sub_08051C96|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08051CB2|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08051CB2|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051CC0|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051CC0|
	POP      {r3, r4, r5, pc}
|loc_08051CC2|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x9680,0x0875,0xe454
|loc_08051CD2|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08051CEE|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08051CEE|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051CFC|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051CFC|
	POP      {r3, r4, r5, pc}
|loc_08051CFE|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xdd38,0x0871,0xe454
|loc_08051D0E|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r0, #0xff
	ADD      r0, #0x8d
	LDR      r0, [r0]
	ADD      r5, r1, #0
	CMP      r0, #0
	BEQ      |loc_08051D2C|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08051D2C|
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeadc
	CMP      r5, #0
	BEQ      |loc_08051D3E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051D3E|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08051D5A|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #0x18]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08051D5A|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051D68|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051D68|
	POP      {r3, r4, r5, pc}
|loc_08051D6A|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x4fbc,0x0805,0xe454
|loc_08051D7A|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0xc]
	ADD      r5, r1, #0
	CMP      r0, #0
	BEQ      |loc_08051D94|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_08051D94|
	LDR      r0, [pc, #0xc]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051DA2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051DA2|
	POP      {r3, r4, r5, pc}
|sub_08051DA4|
|unk_08051DA4|
	INCBIN	baserom.gba_0x51da4_0x51da6.extracted
