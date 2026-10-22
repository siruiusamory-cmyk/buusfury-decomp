	CODE16
|unk_08053038|
; cited by 0x08053038 (a pc-relative load targets 0x08053054)
	CODE32
	LDR      r3, [pc, #0x14]
	MOV      r2, r0, ASR #0x1f
	SMULL    ip, r1, r3, r0
	MVN      r3, #0x63
	RSB      r1, r2, r1, asr #5
	MLA      r0, r3, r1, r0
	BX       lr
|arm_08053054|
	DCD     0x51EB851F
	CODE16
	CODE16
	EXPORT |sub_08053058|
