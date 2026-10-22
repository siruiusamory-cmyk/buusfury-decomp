	IMPORT |GBARam_Free|
	IMPORT |GBARam_Malloc|
	CODE16
	EXPORT |sub_080301C0|
	EXPORT |loc_080301D8|
	EXPORT |loc_080301E2|
	EXPORT |loc_080301E4|
	EXPORT |sub_08030210|
	EXPORT |sub_08030274|
	EXPORT |loc_080302A2|
	EXPORT |loc_080302BC|
	EXPORT |loc_080302CC|
	EXPORT |loc_0803031C|
	EXPORT |loc_0803031E|
	EXPORT |sub_080303A0|
	EXPORT |sub_080303C4|
	EXPORT |loc_08030402|
	EXPORT |loc_08030424|
	EXPORT |loc_0803042E|
	EXPORT |sub_0803043A|
	EXPORT |sub_0803043E|
	EXPORT |sub_0803046E|
	EXPORT |sub_080304DE|
	EXPORT |loc_0803054E|
	EXPORT |loc_08030582|
	EXPORT |loc_080305A8|
	EXPORT |sub_08030604|
	EXPORT |sub_08030606|
	EXPORT |sub_08030630|
	EXPORT |sub_08030740|
	EXPORT |loc_0803076E|
	EXPORT |loc_080307B0|
	EXPORT |loc_080307F6|
	EXPORT |sub_080307FA|
	EXPORT |sub_08030838|
	EXPORT |loc_08030840|
	EXPORT |sub_0803084C|
	EXPORT |sub_08030850|
	EXPORT |loc_08030860|
	EXPORT |sub_0803087E|
	EXPORT |sub_08030950|
	EXPORT |loc_08030992|
	EXPORT |loc_080309CE|
	EXPORT |loc_080309D6|
	EXPORT |loc_080309E6|
	EXPORT |sub_08030A0C|
	EXPORT |sub_08030A42|
	EXPORT |loc_08030A64|
	EXPORT |sub_08030A68|
	EXPORT |sub_08030AA2|
	EXPORT |loc_08030AC4|
	EXPORT |loc_08030AD4|
	EXPORT |sub_08030AD8|
	EXPORT |loc_08030AE4|
	EXPORT |sub_08030B14|
	EXPORT |loc_08030B42|
	EXPORT |loc_08030B5A|
	EXPORT |loc_08030B66|
	EXPORT |loc_08030B90|
	EXPORT |loc_08030BA4|
	EXPORT |loc_08030BC2|
	EXPORT |sub_08030BCC|
	EXPORT |sub_08030BCE|
	EXPORT |loc_08030BE4|
	EXPORT |loc_08030BEE|
	EXPORT |loc_08030BF0|
	EXPORT |loc_08030C12|
	EXPORT |Bg_WriteScroll0AndBlendAlpha|
	EXPORT |Blend_WriteControlAndAlpha5|
	EXPORT |loc_08030FA4|
	EXPORT |loc_08030FB2|
	EXPORT |sub_08030FB4|
	EXPORT |sub_08030FB8|
	EXPORT |loc_08030FE6|
	EXPORT |loc_08030FFA|
	EXPORT |sub_0803101A|
	CODE16
|sub_080301C0|
	MOV      r3, #0xf3
	LDRH     r1, [r1, #4]
	AND      r1, r3
	LDR      r3, [r0, #0x20]
	BEQ      |loc_080301E4|
	ADD      r3, #0xa
	STR      r3, [r0, #0x20]
	CMP      r3, #0x55
	BLT      |loc_080301D8|
	MOV      r1, #0x55
	STR      r1, [r0, #0x20]
	STR      r2, [r0, #0x24]
|loc_080301D8|
	LDR      r1, [r0, #0x20]
	LDR      r2, [r0, #0x1c]
	CMP      r2, r1
	BGE      |loc_080301E2|
	STR      r1, [r0, #0x1c]
|loc_080301E2|
	BX       lr
|loc_080301E4|
	ADD      r1, r3, #0
	LSL      r3, r1, #5
	SUB      r1, r3, r1
	ASR      r1, r1, #5
	STR      r1, [r0, #0x20]
	BX       lr
	LDRB     r4, [r3, #0xd]
	LSR      r5, r6, #1
|unk_080301F4|
	INCBIN	baserom.gba_0x301f4_0x301f6.extracted
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08030210|
	MOV      r0, #0x24
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08030210|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
