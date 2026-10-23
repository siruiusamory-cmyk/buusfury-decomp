	CODE16
|sub_0805227C|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_08052292|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052292|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_080522AA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080522AA|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_080522C2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080522C2|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_080522DA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080522DA|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_080522F2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080522F2|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_0805230A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805230A|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_08052322|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052322|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_0805233A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805233A|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_08052352|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052352|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_0805236E|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_0805236E|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_0805237C|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805237C|
	POP      {r3, r4, r5, pc}
|loc_0805237E|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x1700,0x0807,0xe454
|loc_0805238E|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_080523AA|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080523AA|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080523B8|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080523B8|
	POP      {r3, r4, r5, pc}
|loc_080523BA|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x9ec4,0x086f,0xe454
|loc_080523CA|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	MOV      r1, #0
	ADD      r4, r0, #0
	ADD      r0, #0x68
	BL       |inc_0x03d784_0x041118| + 0x1e08
	MOV      r1, #0
	ADD      r0, r4, #0
	ADD      r0, #0x34
	BL       |inc_0x03d784_0x041118| + 0x1e08
	LDR      r0, [pc, #0x20]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_080523F8|
	LDR      r0, [pc, #0x1c]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080523F8|
	LDR      r0, [pc, #0x18]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052406|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052406|
	POP      {r3, r4, r5, pc}
|loc_08052408|
	DCW      0x9680
	DCW      0x0804,0xffff,0x0000,0xea54,0x0874,0xe454
|loc_08052416|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08052432|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08052432|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08052440|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052440|
	POP      {r3, r4, r5, pc}
|loc_08052442|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xdd38,0x0871,0xe454
|loc_08052452|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_0805246A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805246A|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08052482|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08052482|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_0805249A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805249A|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_080524B2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080524B2|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |dat_08034280| + 0x14
	CMP      r5, #0
	BEQ      |loc_080524CA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080524CA|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |Object_InstallHandlerTable1|
	CMP      r5, #0
	BEQ      |loc_080524E2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080524E2|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_080524F2|
	BL       |GBARam_Free|
|loc_080524F2|
	POP      {r3, pc}
|sub_080524F4|
|unk_080524F4|
	INCBIN	baserom.gba_0x524f4_0x524f6.extracted
|sub_080524F6|
	DCW      0x0804
