	CODE16
|unk_08053014|
; cited by 0x08053014 (a pc-relative load targets 0x08053030)
	CODE32
	LDR      r3, [pc, #0x14]
	MOV      r2, r0, ASR #0x1f
	SMULL    ip, r1, r3, r0
	MVN      r3, #9
	RSB      r1, r2, r1, asr #2
	MLA      r0, r3, r1, r0
	BX       lr
|arm_08053030|
	DCD     0x66666667
	CODE16
	CODE16
	EXPORT |sub_08053034|
