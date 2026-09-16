/* ###
 * IP: LOG1-REMAKE
 *
 * Headless, read-only consumer report for LOGX-MAP-RENDER-001.
 *
 * Given a list of established Thumb instruction-fetch addresses, this script
 * reports the blind reference state, the seeded function boundary, direct
 * callers, outgoing code/data references, disassembly and decompilation.
 *
 * It is strictly read-only: no markup is written back to the program, no
 * memory is patched, and the report path must live under the ignored
 * build/ghidra/reports directory.
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
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressRangeIterator;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;

public class LogxRootConsumers extends GhidraScript {

    private static final String EXPECTED_MD5 =
        "3a74fce97f1ea2b28c2a50ec3df0acee";
    private static final String EXPECTED_SHA256 =
        "940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e";
    private static final String EXPECTED_LANGUAGE = "ARM:LE:32:v4t";

    private PrintWriter out;

    @Override
    public void run() throws Exception {
        requireExpectedProgram();

        String[] args = getScriptArgs();
        if (args.length < 2) {
            throw new IllegalArgumentException(
                "usage: <output-report-path> <thumb-address> [thumb-address ...]");
        }

        File report = requireIgnoredReportPath(args[0]);
        File parent = report.getParentFile();
        if (parent != null && !parent.isDirectory() && !parent.mkdirs()) {
            throw new IllegalStateException("cannot create report directory: " + parent);
        }

        List<Long> targets = new ArrayList<>();
        for (int i = 1; i < args.length; i++) {
            targets.add(Long.decode(args[i].trim()));
        }

        try (PrintWriter writer = new PrintWriter(new OutputStreamWriter(
                new FileOutputStream(report), StandardCharsets.UTF_8))) {
            out = writer;
            writeProgramSummary();
            for (Long target : targets) {
                writeTarget(target.longValue());
            }
        }

        println("LOGX-MAP-RENDER-001 consumer report written to " + report);
    }

    private void requireExpectedProgram() {
        String md5 = currentProgram.getExecutableMD5();
        String sha256 = currentProgram.getExecutableSHA256();
        String language = currentProgram.getLanguageID().toString();
        if (!EXPECTED_MD5.equalsIgnoreCase(md5)
                || !EXPECTED_SHA256.equalsIgnoreCase(sha256)
                || !EXPECTED_LANGUAGE.equals(language)) {
            throw new IllegalStateException(
                "refusing non-canonical program: md5=" + md5
                    + " sha256=" + sha256 + " language=" + language);
        }
    }

    private File requireIgnoredReportPath(String requestedPath) throws Exception {
        File source = getSourceFile().getFile(false);
        if (source == null || source.getParentFile() == null
                || source.getParentFile().getParentFile() == null
                || source.getParentFile().getParentFile().getParentFile() == null) {
            throw new IllegalStateException("cannot resolve repository from script path");
        }
        File repository = source.getParentFile().getParentFile().getParentFile();
        File allowedRoot = new File(repository, "build/ghidra/reports").getCanonicalFile();
        File report = new File(requestedPath).getCanonicalFile();
        Path allowed = allowedRoot.toPath();
        Path candidate = report.toPath();
        if (candidate.equals(allowed) || !candidate.startsWith(allowed)) {
            throw new IllegalArgumentException(
                "report path must be below ignored directory " + allowedRoot);
        }
        return report;
    }

    private void writeProgramSummary() {
        out.println("PROGRAM");
        out.println("name=" + currentProgram.getName());
        out.println("language=" + currentProgram.getLanguageID());
        out.println("executable_md5=" + currentProgram.getExecutableMD5());
        out.println("executable_sha256=" + currentProgram.getExecutableSHA256());
        out.println();
    }

    private void writeTarget(long rawAddress) {
        Address address = currentProgram.getAddressFactory().getDefaultAddressSpace()
            .getAddress(rawAddress);

        out.println("======================================================");
        out.println("TARGET " + address);

        Function blind = currentProgram.getFunctionManager().getFunctionContaining(address);
        out.println("blind_function=" + describe(blind));
        out.println("blind_instruction="
            + (currentProgram.getListing().getInstructionAt(address) == null
                ? "NONE" : currentProgram.getListing().getInstructionAt(address).toString()));
        writeContext(address);

        // Seed the established Thumb entry read-only, in-memory only.
        try {
            disassemble(address);
        }
        catch (Exception e) {
            out.println("seed_disassemble_error=" + e.getMessage());
        }
        Function function = currentProgram.getFunctionManager().getFunctionAt(address);
        if (function == null) {
            try {
                function = createFunction(address, null);
            }
            catch (Exception e) {
                out.println("seed_create_error=" + e.getMessage());
            }
        }
        if (function == null) {
            function = currentProgram.getFunctionManager().getFunctionContaining(address);
        }

        out.println("seeded_function=" + describe(function));
        if (function == null) {
            writeListingWindow(address, 40);
            out.println();
            return;
        }

        out.println("function_body=" + formatBody(function));
        out.println("parameter_count=" + function.getParameterCount());
        out.println("callers:");
        writeFunctionSet(function.getCallingFunctions(monitor));
        out.println("callees:");
        writeFunctionSet(function.getCalledFunctions(monitor));
        out.println("entry_references:");
        writeEntryReferences(function.getEntryPoint());
        out.println("outgoing_references:");
        writeOutgoingReferences(function);
        out.println("referenced_addresses:");
        writeReferencedAddresses(function);
        out.println("disassembly:");
        writeDisassembly(function);
        out.println("decompilation:");
        writeDecompilation(function);
        out.println();
    }

    private String describe(Function function) {
        if (function == null) {
            return "NONE";
        }
        return function.getEntryPoint() + " " + function.getName();
    }

    private void writeContext(Address address) {
        Register tMode = currentProgram.getProgramContext().getRegister("TMode");
        if (tMode == null) {
            out.println("tmode=REGISTER_NOT_FOUND");
            return;
        }
        BigInteger value = currentProgram.getProgramContext().getValue(tMode, address, false);
        out.println("tmode=" + (value == null ? "UNSET" : value.toString()));
    }

    private String formatBody(Function function) {
        StringBuilder text = new StringBuilder();
        AddressRangeIterator ranges = function.getBody().getAddressRanges();
        while (ranges.hasNext()) {
            AddressRange range = ranges.next();
            if (text.length() != 0) {
                text.append(",");
            }
            text.append(range.getMinAddress()).append("..").append(range.getMaxAddress());
        }
        return text.toString();
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

    private void writeEntryReferences(Address entry) {
        ReferenceIterator references =
            currentProgram.getReferenceManager().getReferencesTo(entry);
        boolean any = false;
        while (references.hasNext()) {
            any = true;
            Reference reference = references.next();
            Function from = currentProgram.getFunctionManager()
                .getFunctionContaining(reference.getFromAddress());
            out.printf("  from=%s type=%s source_function=%s%n",
                reference.getFromAddress(), reference.getReferenceType(),
                from == null ? "NONE" : from.getEntryPoint() + " " + from.getName());
        }
        if (!any) {
            out.println("  NONE");
        }
    }

    private void writeOutgoingReferences(Function function) {
        InstructionIterator instructions =
            currentProgram.getListing().getInstructions(function.getBody(), true);
        boolean any = false;
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            for (Reference reference : instruction.getReferencesFrom()) {
                any = true;
                out.printf("  from=%s to=%s type=%s%n",
                    reference.getFromAddress(), reference.getToAddress(),
                    reference.getReferenceType());
            }
        }
        if (!any) {
            out.println("  NONE");
        }
    }

    /**
     * Collect every concrete address appearing as an instruction operand in the
     * function body.  This is a read-only structural aid: no symbol names are
     * assigned and no markup is written back.
     */
    private void writeReferencedAddresses(Function function) {
        Set<String> found = new TreeSet<>();
        InstructionIterator instructions =
            currentProgram.getListing().getInstructions(function.getBody(), true);
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            int n = instruction.getNumOperands();
            for (int i = 0; i < n; i++) {
                Object[] objects = instruction.getOpObjects(i);
                for (Object object : objects) {
                    if (object instanceof Address) {
                        found.add(String.format("%s", object));
                    }
                    else if (object instanceof Scalar) {
                        long value = ((Scalar) object).getUnsignedValue();
                        if (value >= 0x08000000L && value <= 0x087FFFFFL) {
                            found.add(String.format("0x%08x", value));
                        }
                    }
                }
            }
        }
        if (found.isEmpty()) {
            out.println("  NONE");
            return;
        }
        for (String entry : found) {
            out.println("  " + entry);
        }
    }

    private void writeDisassembly(Function function) {
        InstructionIterator instructions =
            currentProgram.getListing().getInstructions(function.getBody(), true);
        int count = 0;
        while (instructions.hasNext() && count < 400) {
            Instruction instruction = instructions.next();
            out.printf("  %s  %-10s %s%n", instruction.getAddress(),
                instruction.getMnemonicString(), instruction.toString());
            count++;
        }
        if (instructions.hasNext()) {
            out.println("  TRUNCATED_AFTER_400_INSTRUCTIONS");
        }
    }

    private void writeListingWindow(Address address, int count) {
        out.println("listing_window:");
        Instruction instruction = currentProgram.getListing().getInstructionAt(address);
        if (instruction == null) {
            out.println("  NONE");
            return;
        }
        for (int i = 0; instruction != null && i < count; i++) {
            out.printf("  %s  %-10s %s%n", instruction.getAddress(),
                instruction.getMnemonicString(), instruction.toString());
            instruction = instruction.getNext();
        }
    }

    private void writeDecompilation(Function function) {
        DecompInterface decompiler = new DecompInterface();
        try {
            decompiler.toggleCCode(true);
            decompiler.toggleSyntaxTree(true);
            if (!decompiler.openProgram(currentProgram)) {
                out.println("  OPEN_FAILED: " + decompiler.getLastMessage());
                return;
            }
            DecompileResults results = decompiler.decompileFunction(function, 60, monitor);
            if (!results.decompileCompleted() || results.getDecompiledFunction() == null) {
                out.println("  FAILED: " + results.getErrorMessage());
                return;
            }
            String code = results.getDecompiledFunction().getC();
            for (String line : code.split("\\R", -1)) {
                out.println("  " + line);
            }
        }
        finally {
            decompiler.dispose();
        }
    }
}
