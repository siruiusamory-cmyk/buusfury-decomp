	CODE16
|sub_08048A8A|
	LSL      r0, r0, #0xc
	LDMIA    r3!, {r4, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	MOV      r0, #0
|loc_08048A94|
	STR      r0, [r1]
	BX       lr
|sub_08048A98|
|unk_08048A98|
	INCBIN	baserom.gba_0x48a98_0x48a9a.extracted
