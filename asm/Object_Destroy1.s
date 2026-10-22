	CODE16
|Object_Destroy1|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x5c]
	ADD      r7, r1, #0
	STR      r0, [r5]
	ADD      r0, #0x30
	STR      r0, [r5, #0xc]
	LDR      r4, [r5, #0x24]
	LDR      r6, [pc, #0x40]
	ADD      r4, #2
	BMI      |loc_0800B2E6|
|loc_0800B2D4|
	LSL      r0, r4, #1
	ADD      r0, r0, r5
	ADD      r0, #0x60
	LDRH     r1, [r0, #0x18]
	LDR      r0, [r6, #4]
	BL       |loc_0801142A|
	SUB      r4, #1
	BPL      |loc_0800B2D4|
|loc_0800B2E6|
	LDR      r0, [r5, #0x48]
	CMP      r0, #0
	BEQ      |loc_0800B2F4|
	ADD      r1, r0, #0
	LDR      r0, [r6, #4]
	BL       |loc_08011944|
|loc_0800B2F4|
	MOV      r1, #0
	ADD      r0, r5, #0
	ADD      r0, #0x80
	BL       |inc_0x03d784_0x041118| + 0x1e08
	LDR      r0, [pc, #0x18]
	CMP      r7, #0
	STR      r0, [r5]
	BEQ      |loc_0800B30C|
	ADD      r0, r5, #0
	BL       |GBARam_Free|
|loc_0800B30C|
	POP      {r3, r4, r5, r6, r7, pc}
|loc_0800B30E|
	DCW      0x0000
	DCW      0x1720,0x0807,0xb0a9,0x0800,0xe454
|loc_0800B31A|
	LSR      r4, r0, #0x20
	STR      r6, [sp, #0x2d0]
	LSR      r4, r0, #0x20
	LDR      r7, [sp, #0x180]
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
|unk_0800B328|
	INCBIN	baserom.gba_0xb328_0xb32a.extracted
	LSR      r0, r0, #0x20
