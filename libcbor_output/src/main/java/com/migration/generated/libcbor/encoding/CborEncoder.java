package com.migration.generated.libcbor.encoding;

import java.io.ByteArrayOutputStream;

public final class CborEncoder {
    private CborEncoder() {
    }

    public static void writeUnsigned(ByteArrayOutputStream out, int majorType, long value) {
        if (value < 24) {
            out.write((majorType << 5) | (int) value);
            return;
        }
        if (value <= 0xFFL) {
            out.write((majorType << 5) | 24);
            out.write((int) value);
            return;
        }
        if (value <= 0xFFFFL) {
            out.write((majorType << 5) | 25);
            writeShort(out, (int) value);
            return;
        }
        if (value <= 0xFFFFFFFFL) {
            out.write((majorType << 5) | 26);
            writeInt(out, (int) value);
            return;
        }
        out.write((majorType << 5) | 27);
        writeLong(out, value);
    }

    public static void writeBreak(ByteArrayOutputStream out) {
        out.write(0xFF);
    }

    public static void writeShort(ByteArrayOutputStream out, int value) {
        out.write((value >>> 8) & 0xFF);
        out.write(value & 0xFF);
    }

    public static void writeInt(ByteArrayOutputStream out, int value) {
        out.write((value >>> 24) & 0xFF);
        out.write((value >>> 16) & 0xFF);
        out.write((value >>> 8) & 0xFF);
        out.write(value & 0xFF);
    }

    public static void writeLong(ByteArrayOutputStream out, long value) {
        for (int shift = 56; shift >= 0; shift -= 8) {
            out.write((int) (value >>> shift) & 0xFF);
        }
    }
}
