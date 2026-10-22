	CODE16
|unk_08053084|
; cited by 0x08053084 (a pc-relative load targets 0x080530A0)
	CODE32
	LDR      r3, [pc, #0x14]
	MOV      r2, r0, ASR #0x1f
	SMULL    ip, r1, r3, r0
	MVN      r3, #0xb
	RSB      r1, r2, r1, asr #1
	MLA      r0, r3, r1, r0
	BX       lr
|arm_080530A0|
	DCD     0x2AAAAAAB
	CODE16
	CODE16
	EXPORT |sub_080530A4|
