	EXPORT |sub_08042118|
|sub_08042118|
|unk_08042118|
; cited by 0x08041DE0 (a pc-relative load targets 0x08042184)
	INCBIN  baserom.gba_0x42118_0x4212c.extracted
		MOV r6, #0x3f
		CMP r0, #0xf0
		LDR r5, [pc, #0x11c]
		BEQ      |loc_08042170|
		CMP r0, #0xf1
		BEQ      |loc_08042178|
		CMP r0, #0xf2
		BEQ      |loc_08042180|
		CMP r0, #0xff
		BNE      |loc_080420E6|
		STRB r6, [r1]
		STRB r4, [r5]
		STRB r3, [r2]
		B        |loc_080420E6|
		STRB r3, [r2]
		B        |loc_080420E6|
		ORR r7, r6
		ADD r0, r7, #0
		STRB r0, [r2, #1]
		B        |loc_080420E6|
		LDRB r0, [r4, #1]
		CMP r0, #0
		BNE      |loc_0804215E|
		STRB r5, [r1]
		B        |loc_080420E6|
|loc_0804215E|
		MOV r0, #0x22
		STRB r0, [r1]
		B        |loc_080420E6|
		STRB r3, [r2, #1]
		B        |loc_080420E6|
|unk_08042168|
	INCBIN  baserom.gba_0x42168_0x42170.extracted
|loc_08042170|
		STRB r6, [r1]
		STRB r3, [r5]
		STRB r3, [r2]
		B        |loc_080420E6|
|loc_08042178|
		STRB r6, [r1]
		STRB r3, [r5]
		STRB r3, [r2]
		B        |loc_080420E6|
|loc_08042180|
		STRB r6, [r1]
		STRB r3, [r5]
		STRB r3, [r2]
		B        |loc_080420E6|
	CODE16
	EXPORT |sub_08042188|
	EXPORT |sub_08042220|
	EXPORT |loc_0804222A|
	EXPORT |sub_0804222C|
	EXPORT |loc_08042230|
	EXPORT |loc_08042238|
	EXPORT |sub_0804223C|
	EXPORT |sub_0804223E|
	EXPORT |loc_0804225C|
	EXPORT |loc_0804228C|
	EXPORT |loc_0804229C|
	EXPORT |sub_080422C6|
	EXPORT |sub_080422CA|
	EXPORT |loc_080422CE|
	EXPORT |loc_080422E6|
	EXPORT |loc_08042304|
	EXPORT |loc_0804230E|
	EXPORT |loc_08042318|
	EXPORT |loc_08042330|
	EXPORT |loc_0804233A|
	EXPORT |loc_0804234E|
	EXPORT |loc_08042366|
	EXPORT |loc_08042370|
	EXPORT |loc_08042372|
	EXPORT |loc_080423AA|
	EXPORT |loc_080423C4|
	EXPORT |sub_080423D4|
	EXPORT |sub_080423E8|
	EXPORT |loc_080423F6|
	EXPORT |loc_080423FE|
	EXPORT |loc_08042414|
	EXPORT |loc_0804242C|
	EXPORT |loc_0804244C|
	EXPORT |loc_08042458|
	EXPORT |loc_08042482|
	EXPORT |loc_080424A2|
	EXPORT |loc_080424AE|
	EXPORT |loc_080424FC|
	EXPORT |sub_080424FE|
	EXPORT |loc_08042500|
	EXPORT |loc_0804251E|
	EXPORT |loc_08042592|
	EXPORT |sub_080425B0|
	EXPORT |sub_080425B2|
	EXPORT |loc_0804269C|
	EXPORT |sub_08042880|
	EXPORT |loc_08042898|
	EXPORT |loc_080428D0|
	EXPORT |loc_080428E0|
	EXPORT |sub_08042904|
	EXPORT |loc_080429A4|
	EXPORT |loc_080429C4|
	EXPORT |loc_080429C6|
	EXPORT |loc_080429C8|
	EXPORT |sub_08042A4E|
	EXPORT |loc_08042A74|
	EXPORT |loc_08042A7A|
	EXPORT |loc_08042A8E|
	EXPORT |loc_08042AA4|
	EXPORT |loc_08042AAA|
	EXPORT |sub_08042AB8|
	EXPORT |sub_08042ADA|
	EXPORT |loc_08042AF6|
	EXPORT |loc_08042B32|
	EXPORT |loc_08042B56|
	EXPORT |sub_08042B68|
	EXPORT |sub_08042BF8|
	EXPORT |loc_08042C0E|
	EXPORT |loc_08042C1E|
	EXPORT |sub_08042C36|
	EXPORT |sub_08042C40|
	EXPORT |loc_08042C54|
	EXPORT |loc_08042C5C|
	EXPORT |sub_08042C6C|
	EXPORT |sub_08042C80|
	EXPORT |loc_08042C94|
	EXPORT |loc_08042CB2|
	EXPORT |loc_08042CC0|
	EXPORT |loc_08042CDA|
	EXPORT |loc_08042CE4|
	EXPORT |loc_08042CFE|
	EXPORT |sub_08042D00|
	EXPORT |sub_08042D72|
	EXPORT |loc_08042D9A|
	EXPORT |loc_08042DB2|
	EXPORT |loc_08042DC2|
	EXPORT |loc_08042DE6|
	EXPORT |loc_08042DF6|
	EXPORT |loc_08042E00|
	EXPORT |loc_08042E0A|
	EXPORT |loc_08042E1A|
	EXPORT |loc_08042E32|
	EXPORT |loc_08042E3C|
	EXPORT |loc_08042E3E|
	EXPORT |loc_08042E50|
	EXPORT |loc_08042E52|
	EXPORT |loc_08042E90|
	EXPORT |loc_08042EB6|
	EXPORT |loc_08042EC8|
	EXPORT |loc_08042EEA|
	EXPORT |loc_08042F20|
	EXPORT |loc_08042F2A|
	EXPORT |sub_08042F4C|
	EXPORT |loc_08042FC0|
	EXPORT |sub_08042FC2|
	EXPORT |loc_08042FD6|
	EXPORT |loc_08042FF2|
	EXPORT |loc_08042FFE|
	EXPORT |loc_0804301C|
	EXPORT |loc_08043038|
	EXPORT |loc_0804304C|
	EXPORT |loc_0804306C|
	EXPORT |sub_0804306E|
	EXPORT |sub_08043098|
	EXPORT |loc_080430B8|
	EXPORT |loc_080430BA|
	EXPORT |loc_080430E0|
	EXPORT |sub_080430E2|
	EXPORT |sub_080430E8|
	EXPORT |sub_08043114|
|sub_08042188|
	MOV      r1, #4
	STRB     r1, [r0, #4]
	MOV      r1, #0x20
	STRB     r1, [r0, #5]
	MOV      r2, #1
	STRH     r2, [r0, #6]
	MOV      r1, #0
	STRB     r1, [r0, #8]
	LDR      r1, [pc, #0xb8]
	STRH     r1, [r0, #0xa]
	LDR      r1, [pc, #0xb8]
	STR      r1, [r0, #0xc]
	ADR      r1, |loc_0804225C|
	STR      r1, [r0, #0x10]
	STRB     r2, [r0, #0x15]
	MOV      r1, #0xf0
	STRH     r1, [r0, #0x16]
	STRH     r1, [r0, #0x18]
	BX       lr
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x90]
	MOV      r5, #0
	STRB     r5, [r0, #1]
	STRB     r5, [r0, #2]
	STRB     r5, [r0, #3]
	STRB     r5, [r0, #4]
	STRB     r5, [r0, #5]
	STRB     r5, [r0]
	MOV      r2, #0x40
	MOV      r1, #0
	LDR      r0, [pc, #0xa0]
	BL       |inc_0x049120_0x055620| + 0x48
	MOV      r0, #4
	STRB     r0, [r4, #4]
	MOV      r0, #0x20
	STRB     r0, [r4, #5]
	MOV      r6, #1
	STRH     r6, [r4, #6]
	LDR      r0, [pc, #0x78]
	STRB     r5, [r4, #8]
	STRH     r0, [r4, #0xa]
	LDR      r0, [pc, #0x78]
	LDR      r1, [pc, #0x88]
	STR      r0, [r4, #0xc]
	ADR      r0, |loc_0804225C|
	STR      r0, [r4, #0x10]
	STRB     r6, [r4, #0x15]
	MOV      r0, #0xf0
	STRH     r0, [r4, #0x16]
	STRH     r0, [r4, #0x18]
	LDR      r0, [pc, #0x7c]
	BL       |loc_08042AAA|
	MOV      r0, #0x83
	LDR      r1, [pc, #0x78]
	LSL      r0, r0, #8
	STRH     r0, [r1, #8]
	LDR      r0, [pc, #0x48]
	STRB     r6, [r0]
	POP      {r4, r5, r6, pc}
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x3c]
	LDRB     r1, [r4, #6]
	CMP      r1, #0
	BEQ      |sub_08042220|
	CMP      r1, #1
	BEQ      |loc_0804222A|
	CMP      r1, #2
	BEQ      |loc_08042230|
	CMP      r1, #3
	BNE      |loc_08042238|
	BL       |loc_0804196a| + 0x6c
	POP      {r4, pc}
|sub_08042220|
|unk_08042220|
		BL       |inc_0x042118_0x049114| + 0x96
		MOV r0, #1
		STRB r0, [r4, #6]
		B        |loc_08042238|
|loc_0804222A|
|unk_0804222A|
	INCBIN	baserom.gba_0x4222a_0x4222c.extracted
|sub_0804222C|
|unk_0804222C|
	INCBIN	baserom.gba_0x4222c_0x42230.extracted
|loc_08042230|
	BL       |loc_08041c9a| + 0x4a
	MOV      r0, #3
	STRB     r0, [r4, #6]
|loc_08042238|
	MOV      r0, #1
	POP      {r4, pc}
|sub_0804223C|
|unk_0804223C|
	INCBIN	baserom.gba_0x4223c_0x4223e.extracted
|sub_0804223E|
	LSL      r0, r0, #0
	LDR      r4, [pc, #0x320]
	LSL      r0, r0, #0xc
	LDR      r3, [pc, #0x3a0]
	LSL      r0, r0, #0xc
	STRH     r0, [r3, r0]
	LSL      r0, r0, #0xc
	STRH     r4, [r3, r1]
	LSL      r0, r0, #0xc
	STRH     r1, [r3, r0]
	LSL      r0, r0, #0xc
	LDRB     r1, [r7, #0x1f]
	LSL      r0, r0, #0
	STRB     r0, [r1, #0x1c]
	LSR      r3, r7, #1
|loc_0804225C|
	STR      r3, [r2, r1]
|unk_0804225E|
	INCBIN	baserom.gba_0x4225e_0x42260.extracted
	CMP      r0, sb
	STRB     r4, [r2, r1]
	LSL      r1, r1, #1
	LSL      r0, r0, #0
	STRH     r2, [r3, r0]
	LSL      r0, r0, #0xc
	MOV      r0, #0xb1
	LSR      r4, r0, #0x20
	MOV      r0, #0xb9
	LSR      r4, r0, #0x20
	LSL      r0, r0, #4
	LSL      r0, r0, #0x10
	PUSH     {r4, lr}
	BL       |inc_0x042118_0x049114| + 0x18d6
	LDR      r2, [pc, #0x3dc]
	ADD      r4, r0, #0
	CMP      r0, r2
	LDR      r1, [pc, #0x3d8]
	BNE      |loc_0804228C|
	MOV      r0, #1
	STRB     r0, [r1, #8]
|loc_0804228C|
	LDRB     r0, [r1, #4]
	MOV      r2, #0
	CMP      r0, #0x17
	BEQ      |loc_0804229C|
	CMP      r0, #1
	BEQ      |loc_0804229C|
	STRB     r2, [r1, #5]
	STRB     r2, [r1, #4]
|loc_0804229C|
	STRB     r2, [r1, #7]
	STRB     r2, [r1, #0xd]
	STRB     r2, [r1, #1]
	STRB     r2, [r1]
	MOV      r0, #0xff
	STRB     r0, [r1, #6]
	BL       |sub_08043368|
	ADD      r0, r4, #0
	POP      {r4, pc}
	LDR      r1, [pc, #0x3b0]
	PUSH     {r7, lr}
	LDR      r1, [r1]
	LDR      r2, [pc, #0x3a8]
	LDRB     r1, [r1]
	CMP      r1, #0
	BNE      |sub_080422CA|
	LDRB     r0, [r2, #2]
	CMP      r0, #1
	BNE      |sub_080422C6|
	B        |loc_080422CE|
|sub_080422C6|
|unk_080422C6|
		MOV r0, #0
		B        |loc_080422CE|
|sub_080422CA|
	MOV      r1, #0
	STRB     r1, [r2, #3]
|loc_080422CE|
	BL       |inc_0x042118_0x049114| + 0x2d98
	POP      {r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x38c]
	ADD      r4, r0, #0
	LDR      r0, [r6]
	LDR      r7, [pc, #0x388]
	LDRB     r0, [r0, #4]
	CMP      r0, #0
	BEQ      |loc_0804230E|
	MOV      r5, #0
|loc_080422E6|
	LSL      r0, r5, #2
	LDR      r0, [r7, r0]
	LDRH     r1, [r0]
	LSL      r1, r1, #0x10
	BPL      |loc_08042304|
	LDRB     r0, [r0, #0x1a]
	ADD      r1, r0, #0
	AND      r1, r4
	BEQ      |loc_08042304|
	BIC      r0, r4
	ADD      r2, r0, #0
	ADD      r1, r5, #0
	MOV      r0, #0x20
	BL       |inc_0x042118_0x049114| + 0x28f4
|loc_08042304|
	ADD      r5, #1
	LSL      r5, r5, #0x18
	LSR      r5, r5, #0x18
	CMP      r5, #4
	BCC      |loc_080422E6|
|loc_0804230E|
	LDR      r0, [r6]
	LDRB     r0, [r0, #5]
	CMP      r0, #0
	BEQ      |loc_0804233A|
	MOV      r5, #0
|loc_08042318|
	LSL      r0, r5, #2
	LDR      r0, [r7, r0]
	LDRH     r1, [r0, #0x34]
	LSL      r1, r1, #0x10
	BPL      |loc_08042330|
	ADD      r0, #0x40
	LDRB     r0, [r0, #0xe]
	AND      r0, r4
	BEQ      |loc_08042330|
	ADD      r0, r5, #0
	BL       |inc_0x042118_0x049114| + 0x29dc
|loc_08042330|
	ADD      r5, #1
	LSL      r5, r5, #0x18
	LSR      r5, r5, #0x18
	CMP      r5, #4
	BCC      |loc_08042318|
|loc_0804233A|
	LDR      r1, [r6]
	LDRB     r0, [r1, #6]
	CMP      r0, #0
	BEQ      |loc_08042370|
	BIC      r0, r4
	STRB     r0, [r1, #6]
	LDR      r3, [pc, #0x314]
	MOV      r0, #0
	LDR      r5, [pc, #0x320]
	ADD      r3, #0x23
|loc_0804234E|
	LSL      r1, r0, #2
	LDR      r1, [r5, r1]
	LDRH     r2, [r1]
	CMP      r2, r3
	BNE      |loc_08042366|
	LDRB     r2, [r1, #3]
	AND      r2, r4
	BEQ      |loc_08042366|
	ADD      r1, #3
	LDRB     r2, [r1]
	BIC      r2, r4
	STRB     r2, [r1]
|loc_08042366|
	ADD      r0, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	CMP      r0, #4
	BCC      |loc_0804234E|
|loc_08042370|
	POP      {r3, r4, r5, r6, r7, pc}
|loc_08042372|
	PUSH     {r1, r2, r3, r4, r5, r6, r7, lr}
	MOV      r3, sp
	ADD      r2, sp, #4
	ADD      r1, sp, #8
	MOV      r5, #0
	BL       |inc_0x042118_0x049114| + 0x2076
	ADD      r3, sp, #0
	LDR      r6, [pc, #0x2dc]
	LDRB     r0, [r3, #8]
	ADD      r4, r6, #0
	ADD      r4, #0x30
	MOV      r7, #1
	CMP      r0, #0
	BEQ      |loc_080423FE|
	LDRB     r0, [r3, #8]
	STRH     r0, [r6, #0x14]
	LDRB     r0, [r3, #4]
	STRH     r0, [r6, #0x16]
	LDRB     r0, [r6, #9]
	CMP      r0, #0
	BEQ      |sub_080423E8|
	STRB     r7, [r6, #0xa]
	LDRB     r0, [r6, #6]
	LDRB     r1, [r3, #4]
	ORR      r0, r1
	BEQ      |sub_080423D4|
	MOV      r0, #0
|loc_080423AA|
	ADD      r3, sp, #0
	LDRB     r2, [r3, #8]
	ADD      r1, r7, #0
	LSL      r1, r0
	AND      r2, r1
	BEQ      |loc_080423C4|
	LDRB     r2, [r4]
	ORR      r1, r2
	STRB     r1, [r4]
	LDRH     r1, [r6, #0x32]
	LSL      r2, r0, #1
	ADD      r2, r2, r6
	STRH     r1, [r2, #0x34]
|loc_080423C4|
	ADD      r0, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	CMP      r0, #4
	BCC      |loc_080423AA|
	MOV      r1, #1
	MOV      r0, #0x31
	B        |loc_080423F6|
|sub_080423D4|
|unk_080423D4|
		MOV r2, #0
		STRB r2, [r6, #0xa]
		ADD r3, sp, #0
		LDRB r0, [r3, #8]
		BL       |inc_0x042118_0x049114| + 0x1264
		MOV r5, #1
		MOV r1, #1
		MOV r0, #0x33
		B        |loc_080423F6|
|sub_080423E8|
	ADD      r3, sp, #0
	LDRB     r0, [r3, #8]
	BL       |inc_0x042118_0x049114| + 0x1264
	MOV      r5, #1
	MOV      r1, #2
	MOV      r0, #0x30
|loc_080423F6|
	BL       |loc_0804333c|
	BL       |sub_08043368|
|loc_080423FE|
	LDR      r0, [pc, #0x264]
	LDR      r0, [r0]
	LDRB     r0, [r0]
	CMP      r0, #1
	BNE      |loc_080424AE|
	ADD      r3, sp, #0
	LDRB     r0, [r3]
	CMP      r0, #0
	BEQ      |loc_0804244C|
	MOV      r0, #0
	MOV      r2, #0
|loc_08042414|
	LDRB     r3, [r4]
	ADD      r1, r7, #0
	LSL      r1, r0
	AND      r3, r1
	BEQ      |loc_0804242C|
	ADD      r3, sp, #0
	LDRB     r3, [r3]
	AND      r1, r3
	BEQ      |loc_0804242C|
	LSL      r1, r0, #1
	ADD      r1, r1, r6
	STRH     r2, [r1, #0x34]
|loc_0804242C|
	ADD      r0, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	CMP      r0, #4
	BCC      |loc_08042414|
	ADD      r3, sp, #0
	LDRB     r1, [r3]
	LDRB     r0, [r4]
	BIC      r0, r1
	STRB     r0, [r4]
	LDRB     r0, [r3]
	MOV      r1, #1
	STRH     r0, [r6, #0x14]
	MOV      r0, #0x32
	BL       |loc_0804333c|
|loc_0804244C|
	LDRB     r0, [r4]
	CMP      r0, #0
	BEQ      |loc_080424A2|
	MOV      r6, #0
	LDR      r7, [pc, #0x208]
	MOV      r0, #0
|loc_08042458|
	LDRB     r2, [r4]
	MOV      r1, #1
	LSL      r1, r0
	AND      r2, r1
	BEQ      |loc_08042482|
	LSL      r2, r0, #1
	ADD      r3, r2, r7
	LDRH     r2, [r3, #0x34]
	CMP      r2, #0
	BEQ      |loc_08042482|
	SUB      r2, #1
	LSL      r2, r2, #0x10
	LSR      r2, r2, #0x10
	STRH     r2, [r3, #0x34]
	BNE      |loc_08042482|
	LDRB     r2, [r4]
	BIC      r2, r1
	ORR      r1, r6
	LSL      r6, r1, #0x18
	LSR      r6, r6, #0x18
	STRB     r2, [r4]
|loc_08042482|
	ADD      r0, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	CMP      r0, #4
	BCC      |loc_08042458|
	CMP      r6, #0
	BEQ      |loc_080424A2|
	ADD      r0, r6, #0
	BL       |inc_0x042118_0x049114| + 0x1264
	MOV      r5, #1
	MOV      r1, #1
	MOV      r0, #0x33
	STRH     r6, [r7, #0x14]
	BL       |loc_0804333c|
|loc_080424A2|
	LDRB     r0, [r4]
	LDR      r6, [pc, #0x1b8]
	CMP      r0, #0
	BNE      |loc_080424AE|
	MOV      r2, #0
	STRB     r2, [r6, #0xa]
|loc_080424AE|
	ADD      r0, r5, #0
	POP      {r1, r2, r3, r4, r5, r6, r7, pc}
|unk_080424B2|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r5, [pc, #0x1a8]
	ADD      r4, r1, #0
	LDR      r1, [pc, #0x1a4]
	ADD      r6, r0, #0
	LDRB     r0, [r5, #0xe]
	ADD      r1, #0x30
	SUB      sp, #0x24
	STR      r1, [sp, #0x20]
	CMP      r0, #0
	BEQ      |loc_08042592|
	MOV      r7, #0
	STRB     r7, [r5, #0xe]
	ADD      r0, r5, #0
	LDR      r1, [pc, #0x194]
	LDRB     r0, [r0, #5]
	LDR      r7, [r1]
	CMP      r6, #0x1f
	MOV      ip, r7
	BEQ      |sub_080425B2|
	BGT      |loc_0804251E|
	ADD      r1, r5, #0
	LDRH     r2, [r1, #0x1a]
	ADD      r7, r6, #0
	SUB      r7, #0x10
	SUB      r3, r2, #1
	LSL      r3, r3, #0x10
	LSR      r3, r3, #0x10
	STR      r3, [sp, #0x1c]
	LDRB     r1, [r1, #7]
	CMP      r7, #0xf
	BCS      |loc_080424FC|
	ADD      r3, pc, #0xC
	ADD      r3, r3, r7
	LDRH     r3, [r3, r7]
	LSL      r3, r3, #1
	ADD      pc, r3
|loc_080424FC|
	B        |sub_080425B0|
|sub_080424FE|
|unk_080424FE|
	INCBIN	baserom.gba_0x424fe_0x42500.extracted
|loc_08042500|
|unk_08042500|
	INCBIN	baserom.gba_0x42500_0x4251e.extracted
|loc_0804251E|
|unk_0804251E|
; cited by 0x08042240 (a pc-relative load targets 0x08042564)
		MOV r7, #0x13
		CMP r6, #0x32
		BEQ      |inc_0x042118_0x049114| + 0x4d8
		BGT      |loc_08042550|
		LDR r1, [pc, #0x138]
		ADD r1, #0x10
		CMP r6, #0x20
		BEQ      |inc_0x042118_0x049114| + 0x4ec
		CMP r6, #0x21
		BEQ      |inc_0x042118_0x049114| + 0x4ee
		CMP r6, #0x27
		BNE      |sub_080425B0|
		CMP r4, #0
		BNE      |sub_080425B0|
		CMP r0, #0x16
		BNE      |inc_0x042118_0x049114| + 0x4f0
		LDRB r0, [r5, #0x11]
		MOV r7, #1
		STRB r0, [r5, #4]
		LDRB r0, [r5, #0x12]
		STRB r0, [r5, #5]
		STRB r7, [r5, #2]
		MOV r1, #0
		MOV r0, #0x41
		B        |inc_0x042118_0x049114| + 0x75e
|loc_08042550|
		CMP r6, #0x33
		BEQ      |inc_0x042118_0x049114| + 0x520
		CMP r6, #0x34
		BEQ      |inc_0x042118_0x049114| + 0x522
		CMP r6, #0x3d
		BNE      |sub_080425B0|
		CMP r4, #0
		BNE      |sub_080425B0|
		MOV r7, #0
		STRB r7, [r5, #5]
		MOV r1, #0
		MOV r0, #0x42
		STRB r7, [r5, #4]
		B        |inc_0x042118_0x049114| + 0x75e
	INCBIN  baserom.gba_0x4256c_0x42592.extracted
|loc_08042592|
|unk_08042592|
		B        |sub_08042880|
	INCBIN  baserom.gba_0x42594_0x425b0.extracted
|sub_080425B0|
	B        |loc_0804269C|
|sub_080425B2|
|unk_080425B2|
; cited by 0x08042244 (a pc-relative load targets 0x080425E8)
		B        |inc_0x042118_0x049114| + 0x5ac
	INCBIN  baserom.gba_0x425b4_0x425f0.extracted
		B        |inc_0x042118_0x049114| + 0x638
	INCBIN  baserom.gba_0x425f2_0x42604.extracted
		B        |inc_0x042118_0x049114| + 0x5b8
		B        |inc_0x042118_0x049114| + 0x5e4
		B        |inc_0x042118_0x049114| + 0x6fa
	INCBIN  baserom.gba_0x4260a_0x42638.extracted
		B        |inc_0x042118_0x049114| + 0x66c
		B        |inc_0x042118_0x049114| + 0x6a6
	INCBIN  baserom.gba_0x4263c_0x4269c.extracted
|loc_0804269C|
|unk_0804269C|
		B        |loc_08042782|
	INCBIN  baserom.gba_0x4269e_0x426c4.extracted
		CMP r4, #0
		BNE      |loc_08042782|
		MOV r0, #0xd
		STRB r0, [r5, #5]
		STRB r0, [r5, #4]
		B        |loc_08042782|
|unk_080426D0|
		MOV r7, #0xe
		CMP r4, #0
		BNE      |loc_080426EA|
		ADD r0, sp, #8
		BL       |inc_0x042118_0x049114| + 0x1ea4
		CMP r0, #0
		BNE      |loc_080426EA|
		ADD r3, sp, #0
		LDRB r0, [r3, #8]
		CMP r0, #0
		BNE      |loc_080426EA|
		STRB r7, [r5, #4]
|loc_080426EA|
		LDRH r0, [r5, #0x1a]
		CMP r0, #0
		BEQ      |loc_08042782|
		SUB r0, #1
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		STRH r0, [r5, #0x1a]
		BNE      |loc_08042782|
		B        |loc_080427BA|
		CMP r4, #0
		BNE      |loc_08042782|
		ADD r0, sp, #8
		BL       |inc_0x042118_0x049114| + 0x1ea4
		CMP r0, #0
		BNE      |loc_08042782|
		ADD r3, sp, #0
		LDRB r0, [r3, #8]
		CMP r0, #0
		BNE      |loc_08042722|
		STRB r7, [r5, #4]
		MOV r0, #0xf
		STRB r0, [r5, #5]
		MOV r0, #0x22
		STRH r0, [r5, #0x1e]
		LDRB r0, [r5, #0x10]
		STRH r0, [r5, #0x14]
		B        |loc_08042740|
|loc_08042722|
		MOV r7, #0
		STRB r7, [r5, #5]
		STRB r7, [r5, #4]
		MOV r0, #0x23
		STRH r0, [r5, #0x1e]
		ADD r3, sp, #0
		LDRB r0, [r3, #8]
		STRH r0, [r5, #0x14]
		LDRB r0, [r5, #7]
		CMP r0, #0
		BEQ      |loc_08042740|
		MOV r0, #3
		STRB r0, [r5, #7]
		MOV r0, #9
		STRB r0, [r5, #4]
|loc_08042740|
		LDRH r0, [r5, #0x1e]
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		MOV r1, #1
		BL       |loc_0804333c|
		MOV r7, #0
		B        |loc_0804280E|
		CMP r4, #0
		BNE      |loc_08042782|
		MOV r0, ip
		LDRB r0, [r0, #3]
		MOV r7, #0
		ADD r3, r5, #0
		STRH r0, [r5, #0x14]
		MOV r0, #0x11
		STRB r0, [r5, #5]
		STRB r0, [r5, #4]
		STRB r7, [r5, #0x10]
		MOV r7, #1
|loc_08042768|
		MOV r0, ip
		LDRB r1, [r0, #3]
		LDRB r0, [r3, #0x10]
		ADD r2, r7, #0
		LSL r2, r0
		AND r1, r2
		BNE      |loc_08042782|
		ADD r0, #1
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		STRB r0, [r3, #0x10]
		CMP r0, #4
		BLO      |loc_08042768|
|loc_08042782|
		B        |loc_0804287A|
		MOV r7, #0x12
		CMP r4, #0
		BNE      |loc_080427A4|
		ADD r0, sp, #8
		BL       |inc_0x042118_0x049114| + 0x24f6
		CMP r0, #0
		BNE      |loc_080427A4|
		ADD r3, sp, #0
		LDRB r0, [r3, #8]
		CMP r0, #0
		BEQ      |loc_080427A2|
		LDRB r0, [r3, #8]
		CMP r0, #1
		BNE      |loc_080427A4|
|loc_080427A2|
		STRB r7, [r5, #4]
|loc_080427A4|
		LDRB r0, [r5, #0x10]
		LSL r0, r0, #1
		ADD r0, r0, r5
		LDRH r1, [r0, #0x34]
		CMP r1, #0
		BEQ      |loc_0804287A|
		SUB r1, #1
		LSL r1, r1, #0x10
		LSR r1, r1, #0x10
		STRH r1, [r0, #0x34]
		BNE      |loc_0804287A|
|loc_080427BA|
		STRB r7, [r5, #4]
		B        |loc_0804287A|
		CMP r4, #0
		BNE      |loc_0804287A|
		ADD r0, sp, #8
		BL       |inc_0x042118_0x049114| + 0x24f6
		CMP r0, #0
		BNE      |loc_0804287A|
		ADD r3, sp, #0
		LDRB r0, [r3, #8]
		CMP r0, #0
		BNE      |loc_080427DE|
		STRB r7, [r5, #4]
		MOV r0, #0x16
		STRB r0, [r5, #5]
		MOV r0, #0x32
		B        |loc_080427F0|
|loc_080427DE|
		MOV r7, #0
		STRB r7, [r5, #5]
		LDR r0, [pc, #0x3c8]
		STRB r7, [r5, #4]
		LDR r0, [r0]
		LDRB r0, [r0, #3]
		BL       |inc_0x042118_0x049114| + 0x1264
		MOV r0, #0x33
|loc_080427F0|
		STRH r0, [r5, #0x1e]
		LDRB r0, [r5, #0x10]
		MOV r7, #0
		LSL r0, r0, #1
		ADD r0, r0, r5
		STRH r7, [r0, #0x34]
		LDR r0, [sp, #0x20]
		STRB r7, [r0]
		STRB r7, [r5, #0xa]
		LDRH r0, [r5, #0x1e]
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		MOV r1, #1
		BL       |loc_0804333c|
|loc_0804280E|
		STRH r7, [r5, #0x1e]
		B        |loc_0804287A|
		CMP r0, #0xf
		BNE      |loc_0804287A|
		STRB r0, [r5, #4]
		MOV r7, #1
		STRB r7, [r5, #2]
		MOV r1, #0
		MOV r0, #0x41
		BL       |loc_0804333c|
		ADD r1, r5, #0
		LDRB r0, [r5, #0x10]
		ADD r1, #0x20
		LDRB r2, [r1, #4]
		LSL r7, r0
		ORR r2, r7
		STRB r2, [r1, #4]
		LDRH r1, [r5, #0x26]
		LSL r0, r0, #1
		ADD r0, r0, r5
		STRH r1, [r0, #0x28]
		LDRB r1, [r5, #0x10]
		MOV r0, #4
		BL       |loc_080446a8|
		LDRB r0, [r5, #0x10]
		MOV r1, #0xe
		BL       |inc_0x042118_0x049114| + 0x28ce
		ADD r3, sp, #0
		STRB r0, [r3, #8]
		LDRB r0, [r3, #8]
		CMP r0, #0
		BEQ      |loc_0804287A|
		MOV r7, #0
		STRB r7, [r5, #5]
		STRB r7, [r5, #4]
		BL       |sub_08043368|
		LDR r0, [pc, #0x34c]
		LDR r0, [r0]
		LDRB r1, [r0, #2]
		LDRB r0, [r0, #3]
		ORR r0, r1
		BL       |inc_0x042118_0x049114| + 0x1264
		ADD r3, sp, #0
		LDRB r0, [r3, #8]
		MOV r1, #1
		STRH r0, [r5, #0x14]
		MOV r0, #0x25
		BL       |loc_0804333c|
|loc_0804287A|
		MOV r7, #1
		STRB r7, [r5, #0xe]
		B        |loc_080428D0|
|sub_08042880|
	CMP      r4, #3
	BNE      |loc_080428D0|
	LDR      r5, [pc, #0x328]
	LDRB     r0, [r5, #0xf]
	CMP      r0, #0
	BEQ      |loc_080428D0|
	CMP      r6, #0x24
	BEQ      |loc_08042898|
	CMP      r6, #0x26
	BEQ      |loc_08042898|
	CMP      r6, #0x27
	BNE      |loc_080428D0|
|loc_08042898|
	BL       |inc_0x042118_0x049114| + 0x179a
	BL       |loc_0804389e|
	ADD      r0, sp, #8
	BL       |inc_0x042118_0x049114| + 0x17ac
	ADD      r3, sp, #0
	LDRB     r0, [r3, #8]
	CMP      r0, #0
	BNE      |loc_080428D0|
	LDR      r5, [pc, #0x2fc]
	LDR      r0, [r5]
	LDRB     r0, [r0]
	CMP      r0, #0
	BNE      |loc_080428D0|
	BL       |loc_08043800|
	LDR      r1, [r5]
	ADD      r0, #4
	LDRB     r1, [r1, #2]
	MOV      r7, #1
	STRB     r1, [r0]
	STRB     r7, [r0, #1]
	MOV      r0, #0x29
	BL       |loc_08042372|
	MOV      r4, #0
|loc_080428D0|
	CMP      r6, #0x10
	BEQ      |loc_080428E0|
	CMP      r6, #0x26
	BEQ      |loc_080429A4|
	CMP      r6, #0x30
	BEQ      |sub_08042904|
	CMP      r6, #0x3d
	BNE      |loc_080429C4|
|loc_080428E0|
	CMP      r4, #0
	BNE      |loc_080429C6|
	LDR      r5, [pc, #0x2c8]
	MOV      r7, #0xff
	STRB     r4, [r5, #0xd]
	STRB     r4, [r5, #1]
	STRB     r4, [r5]
	STRB     r7, [r5, #6]
	BL       |sub_08043368|
	CMP      r6, #0x3d
	BNE      |loc_080429C8|
	ADD      r3, sp, #0
	STRH     r4, [r3, #4]
	SWI      0xb
	STRB     r7, [r5, #6]
	ADD      sp, #0x24
	POP      {r4, r5, r6, r7, pc}
|sub_08042904|
|unk_08042904|
; cited by 0x08042660 (a pc-relative load targets 0x08042984)
		CMP r4, #0
		BNE      |inc_0x042118_0x049114| + 0x8c6
		BL       |loc_08043800|
		LDRB r0, [r0, #8]
		LDR r5, [pc, #0x2a0]
		STRH r0, [r5, #0x14]
		BL       |inc_0x042118_0x049114| + 0x1bc
		LDR r0, [sp, #0x20]
		LDRB r0, [r0]
		CMP r0, #0
		BEQ      |loc_08042950|
		LDRH r1, [r5, #0x14]
		MOV r7, #1
		BIC r0, r1
		LDR r1, [sp, #0x20]
		STRB r0, [r1]
		MOV r0, #0
		MOV r1, #0
|loc_0804292C|
		LDRH r2, [r5, #0x14]
		ADD r3, r7, #0
		LSL r3, r0
		AND r2, r3
		BEQ      |loc_0804293C|
		LSL r2, r0, #1
		ADD r2, r2, r5
		STRH r1, [r2, #0x34]
|loc_0804293C|
		ADD r0, #1
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		CMP r0, #4
		BLO      |loc_0804292C|
		LDRB r0, [r5, #6]
		CMP r0, #0
		BNE      |loc_08042950|
		STRB r1, [r5, #5]
		STRB r1, [r5, #4]
|loc_08042950|
		LDRB r0, [r5]
		LDRH r1, [r5, #0x14]
		ADD r3, sp, #0
		MOV ip, r0
		AND r0, r1
		STRB r0, [r3, #8]
		MOV r0, #0
		MOV r7, #1
|loc_08042960|
		ADD r3, sp, #0
		LDRB r3, [r3, #8]
		ADD r2, r7, #0
		LSL r2, r0
		AND r2, r3
		BEQ      |loc_08042976|
		LDRB r2, [r5, #1]
		CMP r2, #0
		BEQ      |loc_08042976|
		ADD r2, #0xff
		STRB r2, [r5, #1]
|loc_08042976|
		ADD r0, #1
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		CMP r0, #4
		BLO      |loc_08042960|
		MOV r0, ip
		BIC r0, r1
		STRB r0, [r5]
		LDRB r0, [r5, #7]
		CMP r0, #0
		BEQ      |inc_0x042118_0x049114| + 0x89e
		LDR r1, [pc, #0x21c]
		LDR r1, [r1]
		LDRB r1, [r1]
		CMP r1, #0xff
		BNE      |inc_0x042118_0x049114| + 0x8ba
		CMP r0, #8
		BNE      |inc_0x042118_0x049114| + 0x88e
		LDRH r0, [r5, #0x1c]
		STRH r0, [r5, #0x1a]
		MOV r0, #6
		STRB r0, [r5, #7]
		B        |inc_0x042118_0x049114| + 0x89c
|loc_080429A4|
|unk_080429A4|
		B        |inc_0x042118_0x049114| + 0x8c8
		LDRB r0, [r5, #4]
		CMP r0, #6
		BEQ      |loc_080429D2|
		CMP r0, #7
		BEQ      |loc_080429D2|
		STRB r7, [r5, #7]
		MOV r0, #5
		STRB r0, [r5, #4]
		LDR r0, [pc, #0x1f4]
		LDR r0, [r0]
		LDRB r0, [r0]
		CMP r0, #0xff
		BNE      |loc_080429D2|
		LDRB r0, [r5, #4]
		B        |inc_0x042118_0x049114| + 0x8b2
|loc_080429C4|
|unk_080429C4|
		B        |inc_0x042118_0x049114| + 0x8de
|loc_080429C6|
|unk_080429C6|
		B        |inc_0x042118_0x049114| + 0x8e2
|loc_080429C8|
|unk_080429C8|
		B        |loc_08042A3C|
		CMP r0, #0
		BNE      |loc_080429D2|
		MOV r7, #0xff
		STRB r7, [r5, #6]
|loc_080429D2|
		LDRB r0, [r5, #0xe]
		CMP r0, #0
		BNE      |loc_080429F6|
		MOV r1, #1
		MOV r0, #0x40
		B        |loc_080429F2|
		B        |inc_0x042118_0x049114| + 0x906
		BL       |inc_0x042118_0x049114| + 0x127a
		LDR r0, [pc, #0x1c4]
		LDR r0, [r0]
		LDRB r0, [r0]
		CMP r0, #0xff
		BEQ      |loc_080429F6|
		MOV r1, #0
		MOV r0, #0x50
|loc_080429F2|
		BL       |loc_0804333c|
|loc_080429F6|
		CMP r4, #0
		BEQ      |loc_08042A3C|
		CMP r6, #0x1c
		BNE      |inc_0x042118_0x049114| + 0x906
		LDR r5, [pc, #0x1b0]
		LDRB r0, [r5, #7]
		CMP r0, #4
		BNE      |inc_0x042118_0x049114| + 0x906
		LDR r0, [pc, #0x1a4]
		MOV r7, #1
		LDR r0, [r0]
		MOV r1, #0xf
		STRB r7, [r0]
		STRB r1, [r0, #2]
		MOV r0, #0xf
		BL       |inc_0x042118_0x049114| + 0x1264
		BL       |loc_0804389e|
|loc_08042A1C|
		B        |inc_0x042118_0x049114| + 0x7e8
		LDR r5, [pc, #0x190]
		STRH r6, [r5, #0x14]
		STRH r4, [r5, #0x16]
		LDRB r0, [r5, #0xe]
		CMP r0, #0
		BEQ      |loc_08042A30|
		MOV r0, #0
		STRB r0, [r5, #5]
		STRB r0, [r5, #4]
|loc_08042A30|
		MOV r1, #2
		MOV r0, #0xf0
		BL       |loc_0804333c|
		BL       |sub_08043368|
|loc_08042A3C|
		CMP r6, #0xff
		BNE      |loc_08042A1C|
		MOV r1, #0
		MOV r0, #0xf2
		BL       |loc_0804333c|
		BL       |sub_08043368|
		B        |inc_0x042118_0x049114| + 0x7e8
|sub_08042A4E|
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x15c]
	MOV      r7, #0
	ADD      r5, r0, #0
	LDRB     r4, [r6, #0xe]
	STRB     r7, [r6, #0xe]
	MOV      r0, #1
	STRB     r0, [r6, #0xf]
	LDR      r0, [pc, #0x14c]
	LDR      r0, [r0]
	LDRB     r0, [r0]
	CMP      r0, #0
	BNE      |loc_08042A7A|
	ADD      r0, r5, #0
	BL       |loc_08042372|
	LDRB     r0, [r6, #2]
	CMP      r0, #1
	BEQ      |loc_08042A8E|
|loc_08042A74|
	BL       |sub_08043368|
	B        |loc_08042AA4|
|loc_08042A7A|
	MOV      r0, sp
	BL       |inc_0x042118_0x049114| + 0x16f4
	CMP      r0, #0
	BNE      |loc_08042A8E|
	LDRB     r0, [r6, #3]
	ADD      r3, sp, #0
	LDRB     r1, [r3]
	ORR      r0, r1
	STRB     r0, [r6, #3]
|loc_08042A8E|
	LDR      r1, [r6, #0x44]
	CMP      r1, #0
	BEQ      |loc_08042AA4|
	ADD      r0, r5, #0
	BL       |inc_0x046118_0x049114| + 0x98a
	BL       |loc_0804389e|
	LDRB     r0, [r6, #2]
	CMP      r0, #2
	BEQ      |loc_08042A74|
|loc_08042AA4|
	STRB     r7, [r6, #0xf]
	STRB     r4, [r6, #0xe]
	POP      {r3, r4, r5, r6, r7, pc}
|loc_08042AAA|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08042AB8|
	MOV      r0, #4
	POP      {r3, r4, r5, pc}
|sub_08042AB8|
|unk_08042AB8|
		MOV r0, #0
		ADD r3, sp, #0
		STRH r0, [r3]
		SWI 0xb
		MOV r1, #0xff
		LDR r0, [pc, #0xec]
		STRB r1, [r0, #6]
		ADD r0, #0x40
		STMIA r0!, {r4, r5}
		LDR r0, [pc, #0xe8]
		BL       |inc_0x042118_0x049114| + 0x1748
		LDR r0, [pc, #0xe4]
		BL       |inc_0x042118_0x049114| + 0x1772
		MOV r0, #0
		B        |inc_0x042118_0x049114| + 0x99e
|sub_08042ADA|
	LDR      r3, [pc, #0xd4]
	MOV      r2, #0
	STRB     r2, [r3, #5]
	STRB     r2, [r3, #4]
	MOV      r0, #0xff
	STRB     r0, [r3, #6]
	STRB     r2, [r3, #7]
	STRB     r2, [r3, #0x10]
	STRB     r2, [r3, #0xc]
	MOV      r0, #0x24
	STRB     r2, [r0, r3]
	MOV      r0, #0x30
	STRB     r2, [r0, r3]
	MOV      r0, #0
|loc_08042AF6|
	LSL      r1, r0, #1
	ADD      r1, r1, r3
	ADD      r0, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	STRH     r2, [r1, #0x28]
	STRH     r2, [r1, #0x34]
	CMP      r0, #4
	BCC      |loc_08042AF6|
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |sub_08042ADA|
	LDR      r0, [pc, #0x9c]
	MOV      r2, #1
	STRB     r2, [r0, #4]
	MOV      r1, #2
	STRB     r1, [r0, #5]
	STR      r4, [r0, #0x3c]
	LDRB     r1, [r4, #0x11]
	STRB     r1, [r0, #9]
	LDRH     r1, [r4, #0x12]
	STRH     r1, [r0, #0x32]
	LDRH     r1, [r4, #0x14]
	STRH     r1, [r0, #0x18]
	LDRB     r1, [r4, #0x10]
	CMP      r1, #0
	BEQ      |loc_08042B32|
	STRB     r2, [r0, #0xb]
|loc_08042B32|
	POP      {r4, pc}
	LDR      r1, [pc, #0x78]
	MOV      r0, #0x15
	STRB     r0, [r1, #4]
	BX       lr
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	LDR      r5, [pc, #0x70]
	ADD      r4, r0, #0
	LDRB     r0, [r5, #4]
	ADD      r7, r1, #0
	ADD      r6, r3, #0
	CMP      r0, #0
	SUB      sp, #4
	BEQ      |sub_08042B68|
	CMP      r0, #8
	BNE      |loc_08042B56|
	CMP      r4, #1
	BEQ      |sub_08042B68|
|loc_08042B56|
	MOV      r0, #1
	STRH     r0, [r5, #0x14]
	MOV      r1, #1
	MOV      r0, #0xf3
	BL       |loc_0804333c|
	MOV      r0, #1
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
|sub_08042B68|
|unk_08042B68|
; cited by 0x080427E2 (a pc-relative load targets 0x08042BAC)
		BL       |loc_0804400c|
		CMP r0, #0
		BNE      |loc_08042B80|
		MOV r0, #2
		STRH r0, [r5, #0x14]
		MOV r1, #1
		MOV r0, #0xf3
		BL       |loc_0804333c|
		MOV r0, #2
		B        |inc_0x042118_0x049114| + 0xa4c
|loc_08042B80|
		ADD r1, r6, #0
		LDR r3, [pc, #0x38]
		MOV r0, #0
|loc_08042B86|
		LDRH r2, [r1]
		ADD r1, #2
		CMP r2, r3
		BEQ      |loc_08042B98|
		ADD r0, #1
		LSL r0, r0, #0x18
		LSR r0, r0, #0x18
		CMP r0, #0x10
		BLO      |loc_08042B86|
|loc_08042B98|
		CMP r0, #0x10
		BNE      |loc_08042BC0|
		MOV r0, #4
		STRH r0, [r5, #0x14]
		MOV r1, #1
		MOV r0, #0xf3
		BL       |loc_0804333c|
		MOV r0, #4
		B        |inc_0x042118_0x049114| + 0xa4c
		DCD     0x0300525C
		DCD     0x03004CC8
		DCD     0x08042A4F
		DCD     0x080424B3
		DCD     0x0000FFFF
|loc_08042BC0|
		CMP r4, #1
		BLS      |loc_08042BCE|
		MOV r0, #1
		MOV r4, #1
		MOV r7, #0
		STRB r0, [r5, #7]
		B        |loc_08042BD6|
|loc_08042BCE|
		MOV r0, #0
		STRB r0, [r5, #7]
		CMP r4, #0
		BEQ      |loc_08042BDC|
|loc_08042BD6|
		MOV r0, #5
		STRB r0, [r5, #4]
		B        |loc_08042BEA|
|loc_08042BDC|
		MOV r0, #9
		STRB r0, [r5, #4]
		LDRB r0, [r5, #0xb]
		CMP r0, #0
		BEQ      |loc_08042BEA|
		MOV r0, #2
		STRB r0, [r5, #0xb]
|loc_08042BEA|
		STRB r4, [r5, #6]
		STRH r7, [r5, #0x1a]
		LDR r0, [sp, #0xc]
		STRH r0, [r5, #0x26]
		STR r6, [r5, #0x20]
		MOV r0, #0
		B        |inc_0x042118_0x049114| + 0xa4c
|sub_08042BF8|
	PUSH     {r4, r5, r6, lr}
	LDR      r5, [pc, #0x3b0]
	ADD      r4, r0, #0
	LDRB     r0, [r5, #4]
	ADD      r6, r1, #0
	CMP      r0, #0
	BEQ      |loc_08042C1E|
	CMP      r0, #9
	BCC      |loc_08042C0E|
	CMP      r0, #0xb
	BLS      |loc_08042C1E|
|loc_08042C0E|
	MOV      r0, #1
	STRH     r0, [r5, #0x14]
	MOV      r1, #1
	MOV      r0, #0xf3
	BL       |loc_0804333c|
	MOV      r0, #1
	POP      {r4, r5, r6, pc}
|loc_08042C1E|
	BL       |loc_0804400c|
	CMP      r0, #0
	BNE      |sub_08042C36|
	MOV      r0, #2
	STRH     r0, [r5, #0x14]
	MOV      r1, #1
	MOV      r0, #0xf3
	BL       |loc_0804333c|
	MOV      r0, #2
	POP      {r4, r5, r6, pc}
|sub_08042C36|
|unk_08042C36|
		LDR r1, [pc, #0x378]
		MOV r0, #0
		LDR r3, [r1]
		LDRB r1, [r3, #8]
		B        |inc_0x042118_0x049114| + 0xb38
|sub_08042C40|
	LSL      r2, r0, #5
	ADD      r2, r2, r3
	LDRH     r2, [r2, #0x14]
	CMP      r2, r4
	BEQ      |loc_08042C54|
	ADD      r0, #1
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x18
	CMP      r1, r0
	BHI      |sub_08042C40|
|loc_08042C54|
	CMP      r1, #0
	BEQ      |loc_08042C5C|
	CMP      r1, r0
	BNE      |sub_08042C6C|
|loc_08042C5C|
	MOV      r0, #3
	STRH     r0, [r5, #0x14]
	MOV      r1, #1
	MOV      r0, #0xf3
	BL       |loc_0804333c|
	MOV      r0, #3
	POP      {r4, r5, r6, pc}
|sub_08042C6C|
|unk_08042C6C|
		LDRB r0, [r5, #4]
		MOV r1, #0xc
		CMP r0, #0
		BEQ      |loc_08042C78|
		CMP r0, #9
		BNE      |sub_08042C80|
|loc_08042C78|
		STRB r1, [r5, #4]
		MOV r0, #0xd
		STRB r0, [r5, #5]
		B        |inc_0x042118_0x049114| + 0xb6e
|sub_08042C80|
	MOV      r0, #0xb
	STRB     r0, [r5, #4]
	STRB     r1, [r5, #5]
	STRH     r4, [r5, #0x1e]
	STRH     r6, [r5, #0x1a]
	LDRB     r0, [r5, #7]
	CMP      r0, #0
	BEQ      |loc_08042C94|
	MOV      r0, #7
	STRB     r0, [r5, #7]
|loc_08042C94|
	MOV      r0, #0
	POP      {r4, r5, r6, pc}
	PUSH     {r4, r5, r7, lr}
	LDR      r5, [pc, #0x310]
	ADD      r1, r5, #0
	ADD      r1, #0x30
	LDRB     r2, [r1]
	ADD      r3, r2, #0
	AND      r3, r0
	BEQ      |loc_08042CE4|
	BIC      r2, r0
	STRB     r2, [r1]
	MOV      r1, #0
	MOV      r3, #1
	MOV      r4, #0
|loc_08042CB2|
	ADD      r2, r3, #0
	LSL      r2, r1
	AND      r2, r0
	BEQ      |loc_08042CC0|
	LSL      r2, r1, #1
	ADD      r2, r2, r5
	STRH     r4, [r2, #0x34]
|loc_08042CC0|
	ADD      r1, #1
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	CMP      r1, #4
	BCC      |loc_08042CB2|
	LDR      r1, [pc, #0x2e4]
	LDR      r1, [r1]
	LDRB     r4, [r1, #3]
	AND      r4, r0
	BEQ      |loc_08042CDA|
	ADD      r0, r4, #0
	BL       |inc_0x042118_0x049114| + 0x1264
|loc_08042CDA|
	ADD      r1, r4, #0
	MOV      r0, #0x33
	STRH     r4, [r5, #0x14]
	BL       |loc_0804333c|
|loc_08042CE4|
	POP      {r4, r5, r7, pc}
	PUSH     {r4, r5, r7, lr}
	LDR      r4, [pc, #0x2c0]
	ADD      r2, r0, #0
	MOV      r1, #0
	MOV      r0, #0
	CMP      r2, #0
	STRB     r1, [r4, #7]
	BEQ      |sub_08042D00|
	BL       |sub_08042ADA|
	MOV      r0, #0x17
	STRB     r0, [r4, #4]
|loc_08042CFE|
	POP      {r4, r5, r7, pc}
|sub_08042D00|
|unk_08042D00|
		LDRB r5, [r4, #4]
		MOV r2, #8
		SUB r5, #5
		CMP r5, #0xe
		BHS      |sub_08042D72|
		ADR      r3, |loc_08042D14|
		LDRB r3, [r3, r5]
		LSL r3, r3, #1
		ADD pc, r3
		LSL r0, r0, #0
|loc_08042D14|
		LSR r7, r0, #0xc
		ADD r2, #0xb
		ASR r7, r1, #0xc
		ASR r3, r2, #0x1c
		SUB r3, r3, r4
		ADD r2, r6, #4
		CMP r4, #0x2c
		STRB r2, [r4, #4]
		STRB r1, [r4, #5]
		MOV r0, #0x13
		B        |inc_0x042118_0x049114| + 0xc60
	INCBIN  baserom.gba_0x42d2a_0x42d72.extracted
|sub_08042D72|
	STRB     r1, [r4, #5]
	STRB     r1, [r4, #4]
	MOV      r0, #0x43
	LDRB     r1, [r4, #4]
	CMP      r1, #0
	BNE      |loc_08042CFE|
	BL       |loc_0804333c|
	POP      {r4, r5, r7, pc}
	PUSH     {r7, lr}
	BL       |sub_080440e0|
	CMP      r0, #0
	BEQ      |loc_08042D9A|
	MOV      r1, #0
	MOV      r0, #0xf1
	BL       |loc_0804333c|
	BL       |sub_08043368|
|loc_08042D9A|
	POP      {r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r6, [pc, #0x20c]
	LDRH     r0, [r6, #0x18]
	CMP      r0, #0
	BEQ      |loc_08042E3C|
	LDR      r0, [pc, #0x208]
	LDR      r0, [r0]
	LDRB     r0, [r0, #4]
	CMP      r0, #0
	BEQ      |loc_08042E0A|
	MOV      r6, #0
|loc_08042DB2|
	LDR      r3, [pc, #0x200]
	LSL      r7, r6, #2
	LDR      r0, [r3, r7]
	LDRH     r0, [r0]
	LSL      r0, r0, #0x10
	BPL      |loc_08042E00|
	MOV      r5, #0
	MOV      r4, #0
|loc_08042DC2|
	LDR      r3, [pc, #0x1f0]
	MOV      r1, #1
	LDR      r0, [r3, r7]
	LSL      r1, r4
	LDRB     r0, [r0, #0x1a]
	ADD      r2, r0, #0
	AND      r2, r1
	BEQ      |loc_08042DE6|
	LSL      r2, r4, #2
	LDR      r2, [r3, r2]
	LDR      r3, [pc, #0x1d4]
	LDRH     r2, [r2, #2]
	LDRH     r3, [r3, #0x18]
	CMP      r2, r3
	BLS      |loc_08042DE6|
	ORR      r1, r5
	LSL      r5, r1, #0x18
	LSR      r5, r5, #0x18
|loc_08042DE6|
	CMP      r5, #0
	BEQ      |loc_08042DF6|
	EOR      r0, r5
	ADD      r2, r0, #0
	ADD      r1, r6, #0
	MOV      r0, #0x20
	BL       |inc_0x042118_0x049114| + 0x28f4
|loc_08042DF6|
	ADD      r4, #1
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x18
	CMP      r4, #4
	BCC      |loc_08042DC2|
|loc_08042E00|
	ADD      r6, #1
	LSL      r6, r6, #0x18
	LSR      r6, r6, #0x18
	CMP      r6, #4
	BCC      |loc_08042DB2|
|loc_08042E0A|
	LDR      r0, [pc, #0x1a4]
	LDR      r0, [r0]
	LDRB     r0, [r0, #5]
	CMP      r0, #0
	BEQ      |loc_08042E3C|
	LDR      r5, [pc, #0x19c]
	LDR      r6, [pc, #0x194]
	MOV      r4, #0
|loc_08042E1A|
	LSL      r0, r4, #2
	LDR      r0, [r5, r0]
	LDRH     r1, [r0, #0x34]
	LSL      r1, r1, #0x10
	BPL      |loc_08042E32|
	LDRH     r0, [r0, #0x36]
	LDRH     r1, [r6, #0x18]
	CMP      r0, r1
	BLS      |loc_08042E32|
	ADD      r0, r4, #0
	BL       |inc_0x042118_0x049114| + 0x29dc
|loc_08042E32|
	ADD      r4, #1
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x18
	CMP      r4, #4
	BCC      |loc_08042E1A|
|loc_08042E3C|
	POP      {r3, r4, r5, r6, r7, pc}
|loc_08042E3E|
	LDR      r1, [pc, #0x16c]
	PUSH     {r7, lr}
	LDRB     r0, [r1, #2]
	CMP      r0, #0
	BNE      |loc_08042E52|
	MOV      r1, #0
	MOV      r0, #0x45
	BL       |loc_0804333c|
|loc_08042E50|
	POP      {r7, pc}
|loc_08042E52|
	LDRB     r0, [r1, #2]
	CMP      r0, #1
	BNE      |loc_08042E50|
	MOV      r0, #2
	STRB     r0, [r1, #2]
	POP      {r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r7, [pc, #0x154]
	LDRH     r6, [r7, #8]
	MOV      r5, #0
	STRH     r5, [r7, #8]
	LDR      r4, [pc, #0x140]
	LDRB     r0, [r4, #4]
	CMP      r0, #0xf
	BNE      |loc_08042EB6|
	LDRB     r0, [r4, #0x10]
	LSL      r0, r0, #1
	ADD      r0, r0, r4
	LDRH     r1, [r0, #0x28]
	SUB      r1, #1
	LSL      r1, r1, #0x10
	LSR      r1, r1, #0x10
	STRH     r1, [r0, #0x28]
	BEQ      |loc_08042E90|
	LDRB     r0, [r4, #0x10]
	LDR      r1, [pc, #0x12c]
	LSL      r0, r0, #2
	LDR      r0, [r1, r0]
	LDRH     r0, [r0]
	CMP      r0, #0x27
	BNE      |loc_08042EB6|
|loc_08042E90|
	BL       |loc_08042E3E|
	MOV      r0, #0x18
	STRB     r0, [r4, #4]
	LDRB     r1, [r4, #0x10]
	MOV      r0, #4
	BL       |loc_080446a8|
	LDRB     r0, [r4, #0x10]
	ADD      r1, r4, #0
	ADD      r1, #0x20
	MOV      r3, #1
	LDRB     r2, [r1, #4]
	LSL      r3, r0
	BIC      r2, r3
	LSL      r0, r0, #1
	ADD      r0, r0, r4
	STRB     r2, [r1, #4]
	STRH     r5, [r0, #0x28]
|loc_08042EB6|
	STRH     r6, [r7, #8]
	LDRB     r0, [r4, #4]
	CMP      r0, #0x18
	BNE      |loc_08042EEA|
	LDRB     r0, [r4, #2]
	CMP      r0, #1
	BNE      |loc_08042EC8|
	BL       |loc_08042E3E|
|loc_08042EC8|
	LDRB     r0, [r4, #2]
	CMP      r0, #0
	BNE      |loc_08042EEA|
	STRB     r5, [r4, #5]
	LDR      r0, [pc, #0xdc]
	STRB     r5, [r4, #4]
	LDR      r0, [r0]
	LDRB     r1, [r0, #2]
	LDRB     r0, [r0, #3]
	ORR      r0, r1
	BL       |inc_0x042118_0x049114| + 0x1264
	MOV      r1, #1
	MOV      r0, #0x25
	STRH     r5, [r4, #0x14]
	BL       |loc_0804333c|
|loc_08042EEA|
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r1, r2, r3, r4, r5, r6, r7, lr}
	LDR      r5, [pc, #0xbc]
	LDRB     r0, [r5, #4]
	CMP      r0, #5
	BCC      |loc_08042FC0|
	CMP      r0, #8
	BHI      |loc_08042FC0|
	LDR      r6, [pc, #0xb4]
	LDRB     r2, [r5, #0xc]
	LDR      r1, [r6]
	LDRB     r0, [r1, #2]
	LDRB     r1, [r1, #7]
	EOR      r2, r0
	AND      r2, r0
	BIC      r2, r1
	STR      r2, [sp, #8]
	STRB     r0, [r5, #0xc]
	LDR      r2, [sp, #8]
	CMP      r2, #0
	BEQ      |loc_08042F20|
	LDR      r0, [sp, #8]
	MOV      r1, #1
	STRH     r0, [r5, #0x14]
	MOV      r0, #0x10
	BL       |loc_0804333c|
|loc_08042F20|
	MOV      r0, #0
	LDR      r7, [pc, #0x88]
	MOV      r4, #0
	ADD      r7, #0x20
	STR      r0, [sp, #4]
|loc_08042F2A|
	MOV      r0, #1
	LSL      r0, r4
	LSL      r6, r0, #0x18
	LDR      r0, [sp, #8]
	LSR      r6, r6, #0x18
	MOV      r5, #0
	AND      r0, r6
	BEQ      |sub_08042F4C|
	LDR      r5, [pc, #0x70]
	LSL      r1, r4, #1
	LDRH     r0, [r5, #0x26]
	ADD      r1, r1, r5
	STRH     r0, [r1, #0x28]
	LDRB     r0, [r7, #4]
	ORR      r0, r6
	STRB     r0, [r7, #4]
	B        |loc_08042FFE|
|sub_08042F4C|
|unk_08042F4C|
; cited by 0x08042BFA (a pc-relative load targets 0x08042FAC)
		LDRB r0, [r7, #4]
		AND r0, r6
		BEQ      |loc_08042FFE|
		LDR r1, [pc, #0x60]
		LSL r0, r4, #2
		LDR r0, [r1, r0]
		LDRH r1, [r0, #0x34]
		CMP r1, #0x46
		BNE      |sub_08042FC2|
		ADD r0, #0x60
		LDRB r0, [r0, #1]
		CMP r0, #1
		BNE      |loc_08042FD6|
		LDR r1, [pc, #0x44]
		LDR r2, [pc, #0x44]
		LDR r0, [r1, #0x20]
		LDR r2, [r2]
		LSL r1, r4, #5
		MOV r5, #2
		ADD r3, r1, r2
		B        |loc_08042F98|
|loc_08042F76|
		LDRH r2, [r3, #0x18]
		CMP r2, r1
		BNE      |loc_08042F96|
		LDR r1, [pc, #0x2c]
		LDRB r0, [r1]
		ORR r0, r6
		STRB r0, [r1]
		LDRB r0, [r1, #1]
		ADD r0, #1
		STRB r0, [r1, #1]
		LDR r0, [sp, #4]
		ORR r0, r6
		STR r0, [sp, #4]
		MOV r0, #1
		ORR r5, r0
		B        |loc_08042FA0|
|loc_08042F96|
		ADD r0, #2
|loc_08042F98|
		LDRH r1, [r0]
		LDR r2, [pc, #0x20]
		CMP r1, r2
		BNE      |loc_08042F76|
|loc_08042FA0|
		LSL r0, r5, #0x1f
		BMI      |loc_08042FD6|
		MOV r0, #4
		ORR r5, r0
		B        |loc_08042FD6|
	INCBIN  baserom.gba_0x42faa_0x42fac.extracted
		DCD     0x03004CC8
		DCD     0x0300525C
		DCD     0x03005268
	INCBIN  baserom.gba_0x42fb8_0x42fbc.extracted
		DCD     0x0000FFFF
|loc_08042FC0|
|unk_08042FC0|
		B        |loc_0804306C|
|sub_08042FC2|
	LDR      r1, [pc, #0x390]
	LSL      r0, r4, #1
	ADD      r0, r0, r1
	LDRH     r1, [r0, #0x28]
	SUB      r1, #1
	LSL      r1, r1, #0x10
	LSR      r1, r1, #0x10
	STRH     r1, [r0, #0x28]
	BNE      |loc_08042FD6|
	MOV      r5, #6
|loc_08042FD6|
	LSL      r0, r5, #0x1e
	BPL      |loc_08042FF2|
	LDRB     r0, [r7, #4]
	LDR      r1, [pc, #0x374]
	MOV      r2, #0
	BIC      r0, r6
	STRB     r0, [r7, #4]
	LSL      r0, r4, #1
	ADD      r0, r0, r1
	STRH     r2, [r0, #0x28]
	ADD      r1, r4, #0
	MOV      r0, #8
	BL       |loc_080446a8|
|loc_08042FF2|
	LSL      r0, r5, #0x1d
	BPL      |loc_08042FFE|
	LDR      r1, [pc, #0x35c]
	LDRB     r0, [r1, #0xd]
	ORR      r0, r6
	STRB     r0, [r1, #0xd]
|loc_08042FFE|
	ADD      r4, #1
	LSL      r4, r4, #0x18
	LSR      r4, r4, #0x18
	CMP      r4, #4
	BCC      |loc_08042F2A|
	LDR      r0, [sp, #4]
	CMP      r0, #0
	BEQ      |loc_0804301C|
	LDR      r5, [pc, #0x344]
	LDR      r0, [sp, #4]
	MOV      r1, #1
	STRH     r0, [r5, #0x14]
	MOV      r0, #0x11
	BL       |loc_0804333c|
|loc_0804301C|
	LDR      r5, [pc, #0x334]
	LDRB     r0, [r5, #0xd]
	CMP      r0, #0
	BEQ      |loc_0804304C|
	LDR      r2, [pc, #0x330]
	LDR      r1, [r2]
	LDRB     r1, [r1, #6]
	CMP      r1, #0
	BEQ      |loc_08043038|
	LDRB     r2, [r5, #3]
	LDRB     r1, [r5]
	AND      r2, r1
	CMP      r2, r1
	BNE      |loc_0804304C|
|loc_08043038|
	BL       |inc_0x042118_0x049114| + 0x1264
	LDRB     r0, [r5, #0xd]
	MOV      r2, #0
	MOV      r1, #1
	STRH     r0, [r5, #0x14]
	STRB     r2, [r5, #0xd]
	MOV      r0, #0x12
	BL       |loc_0804333c|
|loc_0804304C|
	LDRB     r0, [r7, #4]
	CMP      r0, #0
	BNE      |loc_0804306C|
	LDRB     r1, [r5, #4]
	ADD      r0, r5, #0
	CMP      r1, #8
	BNE      |loc_0804306C|
	LDRB     r1, [r0, #7]
	CMP      r1, #0
	BNE      |sub_0804306E|
	MOV      r2, #0
	STRB     r2, [r0, #5]
	STRB     r2, [r0, #4]
	MOV      r0, #0x14
	BL       |loc_0804333c|
|loc_0804306C|
	POP      {r1, r2, r3, r4, r5, r6, r7, pc}
|sub_0804306E|
|unk_0804306E|
		ADD r2, r1, #0
		MOV r1, #5
		CMP r2, #2
		BNE      |loc_08043080|
		MOV r2, #3
		STRB r2, [r0, #7]
		MOV r2, #9
		STRB r2, [r0, #4]
		B        |loc_08043086|
|loc_08043080|
		MOV r2, #1
		STRB r2, [r0, #7]
		STRB r1, [r0, #4]
|loc_08043086|
		LDRB r2, [r0]
		CMP r2, #0
		BEQ      |loc_0804306C|
		MOV r2, #0
		STRH r2, [r0, #0x1a]
		MOV r2, #8
		STRB r2, [r0, #7]
		STRB r1, [r0, #4]
		B        |loc_0804306C|
|sub_08043098|
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x2b8]
	MOV      r2, #5
	LDRB     r3, [r4, #7]
	MOV      r1, #1
	CMP      r3, #5
	BNE      |loc_080430BA|
	STRB     r1, [r4, #6]
	STRB     r2, [r4, #4]
	LDRH     r3, [r4, #0x1c]
	STRH     r3, [r4, #0x1a]
	CMP      r3, #0
	BEQ      |loc_080430B8|
	MOV      r3, #6
	STRB     r3, [r4, #7]
	B        |loc_080430BA|
|loc_080430B8|
	STRB     r1, [r4, #7]
|loc_080430BA|
	LDRB     r3, [r4, #7]
	CMP      r3, #1
	BNE      |sub_080430E8|
	STRB     r1, [r4, #6]
	ADD      r1, r0, #0
	MOV      r0, #0x8c
	STRB     r2, [r4, #4]
	BL       |inc_0x046118_0x049114| + 0xe18
	LSL      r0, r1, #0x10
	LSR      r0, r0, #0x10
	MOV      r1, #0x8c
	SUB      r1, r1, r0
	STRH     r0, [r4, #0x1a]
	STRH     r1, [r4, #0x1c]
	CMP      r0, #0
	BEQ      |sub_080430E2|
	MOV      r0, #2
	STRB     r0, [r4, #7]
|loc_080430E0|
	POP      {r4, pc}
|sub_080430E2|
|unk_080430E2|
		MOV r0, #3
		STRB r0, [r4, #7]
		B        |inc_0x042118_0x049114| + 0xfd4
|sub_080430E8|
	CMP      r3, #3
	BNE      |loc_080430E0|
	MOV      r0, #0
	STRB     r0, [r4, #6]
	MOV      r0, #0x28
	STRH     r0, [r4, #0x1a]
	MOV      r0, #4
	STRB     r0, [r4, #7]
	MOV      r0, #9
	STRB     r0, [r4, #4]
	POP      {r4, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r4, [pc, #0x250]
	MOV      r5, #0
	LDR      r1, [r4, #0x40]
	CMP      r1, #0
	BNE      |sub_08043114|
	LDRB     r1, [r4, #4]
	CMP      r1, #0
	BEQ      |sub_08043114|
	STRB     r5, [r4, #4]
	POP      {r3, r4, r5, r6, r7, pc}
|sub_08043114|
|unk_08043114|
		LDRB r1, [r4, #7]
		CMP r1, #0