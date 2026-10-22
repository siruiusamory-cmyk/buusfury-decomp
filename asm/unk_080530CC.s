	CODE16
|unk_080530CC|
	CODE32
	LDR      r3, [pc, #0x18]
	MOV      r2, r0, ASR #0x1f
	SMULL    ip, r1, r3, r0
	LDR      r3, [pc, #0x10]
	ADD      r1, r1, r0
	RSB      r1, r2, r1, asr #11
	MLA      r0, r3, r1, r0
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_080530EE|
|unk_080530EC|
	INCBIN	baserom.gba_0x530ec_0x530ee.extracted
