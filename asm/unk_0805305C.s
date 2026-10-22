	CODE16
|unk_0805305C|
; cited by 0x0805305C (a pc-relative load targets 0x08053078)
	CODE32
	LDR      r3, [pc, #0x14]
	MOV      r2, r0, ASR #0x1f
	SMULL    ip, r1, r3, r0
	LDR      r3, [pc, #0xc]
	RSB      r1, r2, r1, asr #6
	MLA      r0, r3, r1, r0
	BX       lr
|arm_08053078|
	DCD     0x10624DD3
|arm_0805307C|
	DCD     0xFFFFFC18
	CODE16
	CODE16
	EXPORT |sub_08053080|
