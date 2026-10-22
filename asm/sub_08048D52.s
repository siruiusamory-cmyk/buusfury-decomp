	CODE16
|sub_08048D52|
	LSL      r0, r0, #0xc
	BVS      |loc_08048C70|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
