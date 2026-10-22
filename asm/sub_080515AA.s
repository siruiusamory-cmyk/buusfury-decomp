	CODE16
|sub_080515AA|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_080515C6|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080515C6|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080515D4|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080515D4|
	POP      {r3, r4, r5, pc}
|loc_080515D6|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x738c,0x0875,0xe454
|loc_080515E6|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_080515FE|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080515FE|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08051616|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051616|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_0805162E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805162E|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_08051646|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051646|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_0805165E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805165E|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_08051676|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051676|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |loc_08050D30|
	CMP      r5, #0
	BEQ      |loc_0805168E|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805168E|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_0805169E|
	BL       |GBARam_Free|
|loc_0805169E|
	POP      {r3, pc}
|sub_080516A0|
|unk_080516A0|
	INCBIN	baserom.gba_0x516a0_0x516a2.extracted
