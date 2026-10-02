/* ###
 * IP: Webfoot SDK
 *
 * Applies only TOOL-001's already-established Thumb entry points and labels.
 * Run only after the blind calibration report has been captured.
 *
 * @category LOG1
 */

import java.math.BigInteger;

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.SourceType;

public class ApplyCalibrationMarkup extends GhidraScript {

    private static final String EXPECTED_MD5 =
        "3a74fce97f1ea2b28c2a50ec3df0acee";
    private static final String EXPECTED_SHA256 =
        "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e";
    private static final String EXPECTED_LANGUAGE = "ARM:LE:32:v4t";

    private static final long[] ENTRIES = {
        0x080126D4L,
        0x08007674L,
        0x08007768L,
        0x080125E8L,
        0x080075ACL,
    };

    private static final String[] LABELS = {
        "point_query_080126D4",
        "factory_08007674",
        "spatial_filter_08007768",
        "spatial_action_080125E8",
        "downstream_080075AC",
    };

    private static final long[] ESTABLISHED_POINT_QUERY_CALL_SITES = {
        0x08006E4EL,
        0x08021DFEL,
        0x08021E06L,
    };

    @Override
    public void run() throws Exception {
        requireExpectedProgram();

        Register tMode = currentProgram.getProgramContext().getRegister("TMode");
        if (tMode == null) {
            throw new IllegalStateException("ARM TMode context register not found");
        }

        int transaction = currentProgram.startTransaction("TOOL-001 proven Thumb markup");
        boolean commit = false;
        try {
            for (int i = 0; i < ENTRIES.length; i++) {
                Address entry = currentProgram.getAddressFactory().getDefaultAddressSpace()
                    .getAddress(ENTRIES[i]);
                Instruction existing = currentProgram.getListing().getInstructionAt(entry);
                BigInteger existingMode = currentProgram.getProgramContext()
                    .getValue(tMode, entry, false);
                if (existing != null && !BigInteger.ONE.equals(existingMode)) {
                    throw new IllegalStateException(
                        "existing instruction is not Thumb at " + entry);
                }
                if (existing == null) {
                    currentProgram.getProgramContext().setValue(
                        tMode, entry, entry, BigInteger.ONE);

                    DisassembleCommand disassemble = new DisassembleCommand(entry, null, true);
                    if (!disassemble.applyTo(currentProgram, monitor)) {
                        throw new IllegalStateException(
                            "disassembly failed at " + entry + ": " + disassemble.getStatusMsg());
                    }
                }

                Function function = currentProgram.getFunctionManager().getFunctionAt(entry);
                if (function == null) {
                    CreateFunctionCmd create = new CreateFunctionCmd(entry);
                    if (!create.applyTo(currentProgram, monitor)) {
                        throw new IllegalStateException("function creation failed at " + entry);
                    }
                    function = create.getFunction();
                }
                if (function == null) {
                    throw new IllegalStateException("function was not recovered at " + entry);
                }
                function.setName(LABELS[i], SourceType.USER_DEFINED);
                println(entry + " -> " + function.getName() + " " + function.getBody());
            }

            for (long rawCallSite : ESTABLISHED_POINT_QUERY_CALL_SITES) {
                Address callSite = currentProgram.getAddressFactory().getDefaultAddressSpace()
                    .getAddress(rawCallSite);
                Instruction existing = currentProgram.getListing().getInstructionAt(callSite);
                BigInteger existingMode = currentProgram.getProgramContext()
                    .getValue(tMode, callSite, false);
                if (existing != null && !BigInteger.ONE.equals(existingMode)) {
                    throw new IllegalStateException(
                        "existing callsite instruction is not Thumb at " + callSite);
                }
                if (existing == null) {
                    currentProgram.getProgramContext().setValue(
                        tMode, callSite, callSite, BigInteger.ONE);
                    DisassembleCommand disassemble = new DisassembleCommand(callSite, null, true);
                    if (!disassemble.applyTo(currentProgram, monitor)) {
                        throw new IllegalStateException(
                            "callsite disassembly failed at " + callSite + ": " +
                            disassemble.getStatusMsg());
                    }
                }
                println("seeded established point-query callsite " + callSite);
            }
            commit = true;
        }
        finally {
            currentProgram.endTransaction(transaction, commit);
        }
    }

    private void requireExpectedProgram() {
        String md5 = currentProgram.getExecutableMD5();
        String sha256 = currentProgram.getExecutableSHA256();
        String language = currentProgram.getLanguageID().toString();
        if (!EXPECTED_MD5.equalsIgnoreCase(md5) ||
                !EXPECTED_SHA256.equalsIgnoreCase(sha256) ||
                !EXPECTED_LANGUAGE.equals(language)) {
            throw new IllegalStateException(
                "refusing non-canonical program: md5=" + md5 +
                " sha256=" + sha256 + " language=" + language);
        }
    }
}
