	CODE16
|unk_080530F8|
; cited by 0x080530F8 (a pc-relative load targets 0x08053118)
	CODE32
	LDR      r3, [pc, #0x18]
	MOV      r2, r0, ASR #0x1f
	SMULL    ip, r1, r3, r0
	MVN      r3, #0x3b
	ADD      r1, r1, r0
	RSB      r1, r2, r1, asr #5
	MLA      r0, r3, r1, r0
	BX       lr
|arm_08053118|
	DCD     0x88888889
	CODE16
	CODE16
	EXPORT |sub_0805311C|
