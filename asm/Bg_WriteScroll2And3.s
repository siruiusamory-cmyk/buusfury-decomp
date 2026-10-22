	CODE16
|Bg_WriteScroll2And3|
	MOV      r1, #1
	LSL      r1, r1, #0xf
	ADD      r0, r0, r1
	LDR      r1, [r0, #0x2c]
	LDR      r3, [pc, #0xc8]
	LDR      r2, [r0, #0x30]
	STRH     r1, [r3]
	STRH     r2, [r3, #2]
	LDR      r1, [r0, #0x2c]
	LDR      r0, [r0, #0x30]
	STRH     r1, [r3, #4]
	STRH     r0, [r3, #6]
	BX       lr
	LDR      r3, [pc, #0xb8]
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r3]
	LDRH     r1, [r1, #2]
	LSL      r1, r1, #0x1a
	LSR      r2, r1, #0x1f
	MOV      r1, #1
	LSL      r1, r1, #0xf
	ADD      r1, r0, r1
	CMP      r2, #0
	BEQ      |loc_08025D6A|
	LDR      r2, [r1, #0x2c]
	LDR      r4, [r1, #0xc]
	CMP      r2, r4
	BLE      |loc_08025D6A|
	SUB      r2, #1
	STR      r2, [r1, #0x2c]
|loc_08025D6A|
	LDR      r2, [r3]
	LDRH     r2, [r2, #2]
	LSL      r2, r2, #0x1b
	LSR      r2, r2, #0x1f
	BEQ      |loc_08025D80|
	LDR      r2, [r1, #0x2c]
	LDR      r4, [r1, #0x14]
	CMP      r2, r4
	BGE      |loc_08025D80|
	ADD      r2, #1
	STR      r2, [r1, #0x2c]
|loc_08025D80|
	LDR      r2, [r3]
	LDRH     r2, [r2, #2]
	LSL      r2, r2, #0x19
	LSR      r2, r2, #0x1f
	BEQ      |loc_08025D96|
	LDR      r2, [r1, #0x30]
	LDR      r4, [r1, #0x10]
	CMP      r2, r4
	BLE      |loc_08025D96|
	SUB      r2, #1
	STR      r2, [r1, #0x30]
|loc_08025D96|
	LDR      r2, [r3]
	ADD      r4, r3, #0
	LDRH     r2, [r2, #2]
	LSL      r2, r2, #0x18
	LSR      r2, r2, #0x1f
	BEQ      |loc_08025DAE|
	LDR      r2, [r1, #0x30]
	LDR      r3, [r1, #0x18]
	CMP      r2, r3
	BGE      |loc_08025DAE|
	ADD      r2, #1
	STR      r2, [r1, #0x30]
|loc_08025DAE|
	LDR      r2, [pc, #0x58]
	MOV      r5, #1
	ADD      r2, r0, r2
	LDR      r3, [r2]
	ADD      r3, #0xf0
	STR      r3, [r2, #8]
	LDR      r3, [r2, #4]
	ADD      r3, #0xa0
	STR      r3, [r2, #0xc]
	LDR      r3, [r4]
	ADD      r2, r5, #0
	LDRH     r3, [r3, #2]
	LSL      r3, r3, #0x18
	LSR      r6, r3, #0x1c
	BNE      |loc_08025DCE|
	MOV      r2, #0
|loc_08025DCE|
	LDR      r6, [r1, #0x3c]
	CMP      r2, r6
	BEQ      |loc_08025DDC|
	LSR      r2, r3, #0x1c
	BNE      |loc_08025DDA|
	MOV      r5, #0
|loc_08025DDA|
	STR      r5, [r1, #0x3c]
|loc_08025DDC|
	LDR      r1, [r4]
	LDRH     r1, [r1, #4]
	LSL      r1, r1, #0x1f
	BEQ      |loc_08025DEE|
	LDR      r1, [r0]
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_08025DEE|
	POP      {r4, r5, r6, pc}
|sub_08025DF0|
|unk_08025DF0|
	INCBIN	baserom.gba_0x25df0_0x25df2.extracted
