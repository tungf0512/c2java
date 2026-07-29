package com.migration.generated.libcbor;

import com.migration.generated.libcbor.util.CborUnicode;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class CborUnicodeTest {
    private static final byte[] missingBytesData = {(byte) 0xC4, (byte) 0x8C};
    private static final byte[] invalidSequenceData = {0x65, (byte) 0xC4, 0x00};

    @Test
    void testMissingBytes() {
        // missingBytesData length 1 is incomplete sequence
        Assertions.assertThrows(IllegalArgumentException.class, () -> {
            CborUnicode.validateAndCountCodePoints(new byte[] {missingBytesData[0]});
        });

        // missingBytesData length 2 is capital accented C
        int count = CborUnicode.validateAndCountCodePoints(missingBytesData);
        Assertions.assertEquals(1, count);
    }

    @Test
    void testInvalidSequence() {
        Assertions.assertThrows(IllegalArgumentException.class, () -> {
            CborUnicode.validateAndCountCodePoints(invalidSequenceData);
        });
    }
}
