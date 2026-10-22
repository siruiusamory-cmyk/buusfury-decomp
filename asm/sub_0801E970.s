	CODE16
|sub_0801E970|
	LDR      r0, [pc, #0x74]
	PUSH     {r3, r4, r5, lr}
	SUB      r0, #0x24
	LDR      r1, [r0]
	LDRH     r1, [r1, #4]
	LSL      r1, r1, #0x1e
	LSR      r1, r1, #0x1f
	BEQ      |loc_0801E9BC|
	LDR      r0, [r0, #4]
	MOV      r4, #0
	LDR      r5, [pc, #0x6c]
	ADD      r3, r4, #0
	MOV      r2, #0x40
	ADD      r0, r0, r5
	LDR      r1, [pc, #0x68]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	BL       |inc_0x03d784_0x041118| + 0x2a3e
	MOV      r0, #0xff
	ADD      r0, #0x21
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801E9B8|
	LDR      r1, [pc, #0x4c]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	ADD      r1, r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r4, [r1, #0xc]
	STR      r4, [r1, #8]
	STR      r4, [r1, #0x10]
	LDR      r1, [pc, #0x4c]
	STR      r1, [r0]
|loc_0801E9B8|
	BL       |inc_0x03d784_0x041118| + 0xcc
|loc_0801E9BC|
	MOV      r0, #0
	POP      {r3, r4, r5, pc}
	PUSH     {r3, lr}
	BL       |inc_0x03d784_0x041118| + 0x2a3e
	BL       |inc_0x03d784_0x041118| + 0x2954
	LDR      r0, [pc, #0x1c]
	SUB      r0, #0x24
	LDR      r0, [r0, #0x10]
	BL       |inc_0x0158_0x143f2| + 0x9528
	MOV      r1, #0
	LDR      r0, [pc, #0x30]
	BL       |inc_0x0158_0x143f2| + 0x12430
	POP      {r3, pc}
|sub_0801E9DE|
|unk_0801E9DE|
	INCBIN	baserom.gba_0x1e9de_0x1e9e2.extracted
