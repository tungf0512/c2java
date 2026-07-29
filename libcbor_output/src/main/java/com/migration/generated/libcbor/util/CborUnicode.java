package com.migration.generated.libcbor.util;

import java.nio.charset.StandardCharsets;

public final class CborUnicode {
    private CborUnicode() {
    }

    public static int validateAndCountCodePoints(byte[] utf8) {
        String text = new String(utf8, StandardCharsets.UTF_8);
        if (!java.util.Arrays.equals(text.getBytes(StandardCharsets.UTF_8), utf8)) {
            throw new IllegalArgumentException("Invalid UTF-8 data");
        }
        return text.codePointCount(0, text.length());
    }
}
