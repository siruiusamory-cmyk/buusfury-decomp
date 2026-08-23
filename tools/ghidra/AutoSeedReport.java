/* ###
 * IP: LOG1-REMAKE
 *
 * Generic bounded Ghidra helper for the research lane:
 * seed Thumb functions at given addresses (optional names), then emit a
 * report (identity, body, callers/callees, disassembly preview,
 * decompilation) under build/ghidra/reports/.
 *
 * Args: <output-path> [addr[:name]] ...
 * Addresses accept 0x-prefixed hex. Bare addresses get candidate_ names.
 *
 * @category LOG1
 */

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRangeIterator;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.SourceType;

public class AutoSeedReport extends GhidraScript {

    private static final String EXPECTED_MD5 =
        "3a74fce97f1ea2b28c2a50ec3df0acee";
    private static final String EXPECTED_SHA256 =
        "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e";
    private static final String EXPECTED_LANGUAGE = "ARM:LE:32:v4t";

    private static final int DISASSEMBLY_LIMIT = 300;

    private PrintWriter out;

    @Override
    public void run() throws Exception {
        requireExpectedProgram();

        String[] args = getScriptArgs();
        if (args.length < 1) {
            throw new IllegalArgumentException(
                "expected output path followed by addr[:name] targets");
        }
        File report = requireIgnoredReportPath(args[0]);
        File parent = report.getParentFile();
        if (parent != null && !parent.isDirectory() && !parent.mkdirs()) {
            throw new IllegalStateException("cannot create report directory: " + parent);
        }

        Map<Long, String> targets = new LinkedHashMap<>();
        for (int i = 1; i < args.length; i++) {
            String[] parts = args[i].split(":", 2);
            long raw = Long.parseLong(parts[0].replaceFirst("^0x", ""), 16);
            targets.put(raw, parts.length > 1 ? parts[1]
                : "candidate_" + String.format("%08X", raw));
        }

        Register tMode = currentProgram.getProgramContext().getRegister("TMode");
        if (tMode == null) {
            throw new IllegalStateException("ARM TMode context register not found");
        }

        Map<Long, String> statuses = new LinkedHashMap<>();
        int transaction = currentProgram.startTransaction("AutoSeedReport seeding");
        boolean commit = false;
        try {
            for (Map.Entry<Long, String> t : targets.entrySet()) {
                statuses.put(t.getKey(),
                    ensureThumbFunction(t.getValue(), t.getKey(), tMode));
            }
            commit = statuses.values().stream().noneMatch(s -> s.startsWith("FAILED"));
        } finally {
            currentProgram.endTransaction(transaction, commit);
        }
        if (!commit) {
            throw new IllegalStateException("seeding failed; rolled back: " + statuses);
        }

        try (PrintWriter writer = new PrintWriter(new OutputStreamWriter(
                new FileOutputStream(report), StandardCharsets.UTF_8))) {
            out = writer;
            out.println("AUTO_SEED_REPORT");
            out.println("language=" + currentProgram.getLanguageID());
            out.println("executable_sha256=" + currentProgram.getExecutableSHA256());
            for (Map.Entry<Long, String> t : statuses.entrySet()) {
                out.printf("SEED %08X name=%s status=%s%n",
                    t.getKey(), targets.get(t.getKey()), t.getValue());
            }
            out.println();
            for (Long raw : targets.keySet()) {
                writeTarget(raw);
            }
        }
        println("AutoSeedReport written to " + report);
    }

    private String ensureThumbFunction(String desiredName, long raw, Register tMode)
            throws Exception {
        Address address = addr(raw);
        Instruction existing = currentProgram.getListing().getInstructionAt(address);
        BigInteger mode = currentProgram.getProgramContext()
            .getValue(tMode, address, false);
        if (existing != null && !BigInteger.ONE.equals(mode)) {
            return "FAILED_NOT_THUMB";
        }
        if (existing == null) {
            currentProgram.getProgramContext()
                .setValue(tMode, address, address, BigInteger.ONE);
            DisassembleCommand disassemble =
                new DisassembleCommand(address, null, true);
            if (!disassemble.applyTo(currentProgram, monitor)) {
                return "FAILED_DISASSEMBLE: " + disassemble.getStatusMsg();
            }
        }
        Function function = currentProgram.getFunctionManager().getFunctionAt(address);
        if (function == null) {
            Function containing =
                currentProgram.getFunctionManager().getFunctionContaining(address);
            if (containing != null) {
                return "MID_FUNCTION_OF " + containing.getEntryPoint();
            }
            CreateFunctionCmd create = new CreateFunctionCmd(address);
            if (!create.applyTo(currentProgram, monitor)) {
                return "FAILED_CREATE: " + create.getStatusMsg();
            }
            function = create.getFunction();
            if (function == null) {
                return "FAILED_CREATE_NO_FUNCTION";
            }
        }
        String currentName = function.getName();
        boolean force = desiredName.endsWith("!");
        String finalName = force ? desiredName.substring(0, desiredName.length() - 1)
            : desiredName;
        if (force || currentName.startsWith("FUN_") || currentName.startsWith("None")) {
            function.setName(finalName, SourceType.USER_DEFINED);
        } else if (!currentName.equals(finalName)) {
            return "EXISTING_NAME " + currentName;
        }
        return "OK";
    }

    private void writeTarget(long raw) throws Exception {
        Function function = currentProgram.getFunctionManager()
            .getFunctionContaining(addr(raw));
        out.println("TARGET " + String.format("%08X", raw));
        if (function == null) {
            out.println("function=NOT_RECOVERED");
            out.println();
            return;
        }
        out.println("function_name=" + function.getName());
        out.println("function_entry=" + function.getEntryPoint());
        out.println("function_body=" + formatBody(function));
        out.println("callers:");
        writeFunctionSet(function.getCallingFunctions(monitor));
        out.println("callees:");
        writeFunctionSet(function.getCalledFunctions(monitor));
        out.println("disassembly:");
        InstructionIterator instructions = currentProgram.getListing()
            .getInstructions(function.getBody(), true);
        int count = 0;
        while (instructions.hasNext() && count < DISASSEMBLY_LIMIT) {
            Instruction instruction = instructions.next();
            out.printf("  %s  %-10s %s%n", instruction.getAddress(),
                instruction.getMnemonicString(), instruction.toString());
            count++;
        }
        if (instructions.hasNext()) {
            out.println("  TRUNCATED_AFTER_" + DISASSEMBLY_LIMIT);
        }
        out.println("decompilation:");
        DecompInterface decompiler = new DecompInterface();
        try {
            decompiler.toggleCCode(true);
            if (!decompiler.openProgram(currentProgram)) {
                out.println("  OPEN_FAILED: " + decompiler.getLastMessage());
                return;
            }
            DecompileResults results =
                decompiler.decompileFunction(function, 120, monitor);
            if (!results.decompileCompleted() || results.getDecompiledFunction() == null) {
                out.println("  FAILED: " + results.getErrorMessage());
                return;
            }
            for (String line : results.getDecompiledFunction().getC().split("\\R", -1)) {
                out.println("  " + line);
            }
        } finally {
            decompiler.dispose();
        }
        out.println();
    }

    private void writeFunctionSet(Set<Function> functions) {
        if (functions.isEmpty()) {
            out.println("  NONE");
            return;
        }
        List<Function> sorted = new ArrayList<>(functions);
        sorted.sort(Comparator.comparing(Function::getEntryPoint));
        for (Function function : sorted) {
            out.printf("  %s %s%n", function.getEntryPoint(), function.getName());
        }
    }

    private String formatBody(Function function) {
        StringBuilder text = new StringBuilder();
        AddressRangeIterator ranges = function.getBody().getAddressRanges();
        while (ranges.hasNext()) {
            var range = ranges.next();
            if (text.length() != 0) {
                text.append(",");
            }
            text.append(range.getMinAddress()).append("..")
                .append(range.getMaxAddress());
        }
        return text.toString();
    }

    private Address addr(long raw) {
        return currentProgram.getAddressFactory().getDefaultAddressSpace()
            .getAddress(raw);
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

    private File requireIgnoredReportPath(String requestedPath) throws Exception {
        File source = getSourceFile().getFile(false);
        if (source == null || source.getParentFile() == null ||
                source.getParentFile().getParentFile() == null ||
                source.getParentFile().getParentFile().getParentFile() == null) {
            throw new IllegalStateException("cannot resolve repository from script path");
        }
        File repository = source.getParentFile().getParentFile().getParentFile();
        File allowedRoot = new File(repository, "build/ghidra/reports")
            .getCanonicalFile();
        File report = new File(requestedPath).getCanonicalFile();
        Path allowed = allowedRoot.toPath();
        Path candidate = report.toPath();
        if (candidate.equals(allowed) || !candidate.startsWith(allowed)) {
            throw new IllegalArgumentException(
                "report path must be below ignored directory " + allowedRoot);
        }
        return report;
    }
}
