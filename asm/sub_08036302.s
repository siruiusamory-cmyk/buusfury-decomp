	CODE16
|sub_08036302|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08036326|
	LDR      r1, [pc, #0x6c]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	MOV      r1, #1
	STR      r1, [r0, #0xc]
	MOV      r1, #0
	STR      r1, [r0, #0x10]
|loc_08036326|
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803634C|
	MOV      r1, #2
	STR      r1, [r0, #0xc]
	STR      r4, [r0, #4]
	MOV      r1, #0
	STR      r1, [r0, #0x10]
	LDR      r1, [pc, #0x40]
	STR      r1, [r0]
|loc_0803634C|
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08036370|
	MOV      r1, #1
	STR      r1, [r0, #0xc]
	STR      r4, [r0, #4]
	STR      r1, [r0, #0x10]
	LDR      r1, [pc, #0x20]
	STR      r1, [r0]
|loc_08036370|
	POP      {r4, pc}
|loc_08036372|
	DCW      0x0000
	DCW      0x1c34,0x0300,0x8098,0x086b,0xa734,0x0875,0x92a8,0x0831
	DCW      0x05c4,0x0000,0xb6e0
|loc_0803638A|
	LSR      r4, r0, #0x20
	SWI      0x84
	LSR      r4, r0, #0x20
	ADD      r5, sp, #0x260
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r3, #0
	CMP      r0, #0
	BNE      |loc_080363AA|
	MOV      r0, #0x1c
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080363C2|
|loc_080363AA|
	LDR      r1, [pc, #0x84]
	STMIA    r0!, {r1, r5}
	SUB      r0, #8
	STR      r4, [r0, #0x18]
	STR      r6, [r0, #0x14]
	MOV      r1, #0
	STR      r1, [r0, #0x10]
	LDR      r1, [pc, #0x78]
	LDR      r1, [r1, #4]
	SUB      r1, r1, r4
	SUB      r1, #1
	STR      r1, [r0, #0xc]
|loc_080363C2|
	POP      {r4, r5, r6, pc}
	LDR      r1, [pc, #0x70]
	MOV      r2, #0xf3
	LDR      r1, [r1]
	LDRH     r1, [r1, #4]
	AND      r1, r2
	LDR      r2, [pc, #0x64]
	CMP      r1, #0
	LDR      r2, [r2, #4]
	BEQ      |loc_080363E8|
	STR      r2, [r0, #0xc]
	LDR      r1, [r0, #0x10]
	ADD      r1, #1
	STR      r1, [r0, #0x10]
	LDR      r0, [r0, #0x14]
	CMP      r1, r0
	BLE      |loc_080363F6|
	MOV      r0, #1
	BX       lr
|loc_080363E8|
	LDR      r1, [r0, #0xc]
	SUB      r1, r2, r1
	LDR      r2, [r0, #0x18]
	CMP      r1, r2
	BLE      |loc_080363F6|
	MOV      r1, #0
	STR      r1, [r0, #0x10]
|loc_080363F6|
	MOV      r0, #0
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x14]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r5, r0, #0
	LDR      r6, [r4, #0xc]
	LDR      r4, [r4, #0x10]
	MOV      r0, #0x1c
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803642E|
	LDR      r1, [pc, #0x18]
	STMIA    r0!, {r1, r5}
	SUB      r0, #8
	STR      r4, [r0, #0x18]
	STR      r6, [r0, #0x14]
	MOV      r1, #0
	STR      r1, [r0, #0x10]
	LDR      r1, [pc, #0xc]
	LDR      r1, [r1, #4]
	SUB      r1, r1, r4
	SUB      r1, #1
	STR      r1, [r0, #0xc]
|loc_0803642E|
	POP      {r4, r5, r6, pc}
|sub_08036430|
|unk_08036430|
	INCBIN	baserom.gba_0x36430_0x36432.extracted
|sub_08036432|
	DCW      0x0804
	DCW      0x0f90
	DCW      0x0300
	DCW      0xa738
	DCW      0x0875
