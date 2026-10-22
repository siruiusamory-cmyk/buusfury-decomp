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
	EXPORT |Bios_CpuSet1|
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
	EXPORT |Bios_CpuSet2|
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
	CODE16
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
