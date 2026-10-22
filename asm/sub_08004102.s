	CODE16
|sub_08004102|
	PUSH     {r4, r5}
	LDR      r5, [pc, #0x50]
	LDR      r1, [r5]
	CMP      r1, #0
	BEQ      |loc_08004152|
	MOV      r3, #0
	MOV      r2, #0
	CMP      r1, #0
	BLE      |loc_08004142|
|loc_08004114|
	LSL      r1, r2, #2
	ADD      r1, r1, r5
	LDR      r1, [r1, #4]
	LDR      r4, [r1, #0x58]
	CMP      r4, r0
	BNE      |loc_0800413A|
	CMP      r3, #0
	BNE      |loc_08004138|
	LDR      r3, [r0]
	STR      r3, [r1, #0x5c]
	LDR      r3, [r0, #4]
	STR      r3, [r1, #0x60]
	LDR      r3, [r0, #8]
	STR      r3, [r1, #0x64]
	LDR      r3, [r0, #0xc]
	STR      r3, [r1, #0x68]
	ADD      r3, r1, #0
	ADD      r3, #0x5c
|loc_08004138|
	STR      r3, [r1, #0x58]
|loc_0800413A|
	LDR      r1, [r5]
	ADD      r2, #1
	CMP      r1, r2
	BGT      |loc_08004114|
|loc_08004142|
	LDR      r0, [r5]
	LDR      r1, [pc, #0x10]
	LSL      r0, r0, #2
	ADD      r0, r0, r5
	LDR      r0, [r0]
	SUB      r1, #4
	LDR      r0, [r0, #0x58]
	STR      r0, [r1]
|loc_08004152|
	POP      {r4, r5}
	BX       lr
|sub_08004156|
|unk_08004156|
; cited by 0x0800403A (a pc-relative load targets 0x08004158)
	INCBIN	baserom.gba_0x4156_0x4212.extracted
