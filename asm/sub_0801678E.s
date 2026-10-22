	CODE16
|sub_0801678E|
	LSR      r3, r5, #1
	BCS      |loc_08016784|
	LSR      r3, r7, #0x20
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	LDR      r5, [sp, #0x120]
	LSR      r4, r0, #0x20
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
