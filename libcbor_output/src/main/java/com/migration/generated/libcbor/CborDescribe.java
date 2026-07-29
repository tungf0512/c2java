package com.migration.generated.libcbor;

import com.migration.generated.libcbor.model.*;
import java.io.IOException;

public final class CborDescribe {
    private CborDescribe() {
    }

    public static void describe(CborItem item, Appendable out) {
        try {
            write(item, out, 0);
        } catch (IOException e) {
            throw new IllegalStateException("Failed to write CBOR description", e);
        }
    }

    public static String describe(CborItem item) {
        StringBuilder builder = new StringBuilder();
        describe(item, builder);
        return builder.toString();
    }

    private static void write(CborItem item, Appendable out, int depth) throws IOException {
        indent(out, depth);
        if (item instanceof CborUnsignedInteger value) {
            out.append("unsigned(").append(Long.toString(value.value())).append(")\n");
        } else if (item instanceof CborNegativeInteger value) {
            out.append("negative(").append(Long.toString(value.value())).append(")\n");
        } else if (item instanceof CborByteString value) {
            out.append(value.isIndefinite() ? "bytes*\n" : "bytes[" + value.length() + "]\n");
            for (CborByteString chunk : value.chunks()) {
                write(chunk, out, depth + 1);
            }
        } else if (item instanceof CborTextString value) {
            out.append(value.isIndefinite() ? "text*\n" : "text(\"").append(value.text()).append("\")\n");
            for (CborTextString chunk : value.chunks()) {
                write(chunk, out, depth + 1);
            }
        } else if (item instanceof CborArray value) {
            out.append(value.isIndefinite() ? "array*\n" : "array[" + value.size() + "]\n");
            for (CborItem child : value.items()) {
                write(child, out, depth + 1);
            }
        } else if (item instanceof CborMap value) {
            out.append(value.isIndefinite() ? "map*\n" : "map[" + value.size() + "]\n");
            for (CborPair pair : value.pairs()) {
                indent(out, depth + 1);
                out.append("key:\n");
                write(pair.key(), out, depth + 2);
                indent(out, depth + 1);
                out.append("value:\n");
                write(pair.value(), out, depth + 2);
            }
        } else if (item instanceof CborTag value) {
            out.append("tag(").append(Long.toString(value.value())).append(")\n");
            if (value.taggedItem() != null) {
                write(value.taggedItem(), out, depth + 1);
            }
        } else if (item instanceof CborFloatOrCtrl value) {
            out.append("float_or_ctrl(").append(value.kind().name()).append(")\n");
        }
    }

    private static void indent(Appendable out, int depth) throws IOException {
        for (int i = 0; i < depth; i++) {
            out.append("  ");
        }
    }
}
