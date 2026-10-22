	CODE16
|unk_08046C2C|
	CODE32
	SUBS     r3, r2, #0x20
	BPL      |arm_08046C48|
	RSB      r3, r2, #0x20
	MOV      r0, r0, LSR r2
	ORR      r0, r0, r1, lsl r3
	MOV      r1, r1, ASR r2
	BX       lr
|arm_08046C48|
	MOV      r0, r1, ASR r3
	MOV      r1, r1, ASR #0x1f
	CODE16
	CODE16
	EXPORT |sub_08046C50|
	EXPORT |loc_08046C62|
	EXPORT |loc_08046C70|
	EXPORT |loc_08046C78|
	EXPORT |sub_08046C82|
	EXPORT |sub_08046CAA|
	EXPORT |sub_08046CBA|
	EXPORT |sub_08046CBC|
|sub_08046C50|
|unk_08046C50|
	INCBIN	baserom.gba_0x46c50_0x46c54.extracted
	PUSH     {r4}
	CMP      r2, #4
	BCC      |loc_08046C78|
	ADD      r3, r0, #0
	ORR      r3, r1
	LSL      r3, r3, #0x1e
	BNE      |loc_08046C78|
|loc_08046C62|
	LDMIA    r0!, {r3}
	LDMIA    r1!, {r4}
	CMP      r3, r4
	BNE      |loc_08046C70|
	SUB      r2, #4
	CMP      r2, #4
	BCS      |loc_08046C62|
|loc_08046C70|
	CMP      r3, r4
	BEQ      |loc_08046C78|
	SUB      r0, #4
	SUB      r1, #4
|loc_08046C78|
	CMP      r2, #0
	BNE      |sub_08046C82|
	MOV      r0, #0
	POP      {r4}
	BX       lr
