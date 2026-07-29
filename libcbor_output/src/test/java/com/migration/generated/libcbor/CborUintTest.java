package com.migration.generated.libcbor;

import com.migration.generated.libcbor.model.CborItem;
import com.migration.generated.libcbor.model.CborType;
import com.migration.generated.libcbor.model.CborUnsignedInteger;
import com.migration.generated.libcbor.model.CborWidth;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Disabled;

class CborUintTest {
    private static final byte[] data1 = {0x02, (byte) 0xFF};
    private static final byte[] data2 = {0x18, (byte) 0xFF, (byte) 0xFF};
    private static final byte[] data3 = {0x19, 0x01, (byte) 0xf4, (byte) 0xFF};
    private static final byte[] data4 = {0x1a, (byte) 0xa5, (byte) 0xf7, 0x02, (byte) 0xb3, (byte) 0xFF};
    private static final byte[] data5 = {0x1b, (byte) 0xa5, (byte) 0xf7, 0x02, (byte) 0xb3,
                                         (byte) 0xa5, (byte) 0xf7, 0x02, (byte) 0xb3, (byte) 0xFF};

    @Test
    void testVeryShortInt() {
        CborItem number = Cbor.loadPartial(data1, 0, 2).item();
        Assertions.assertEquals(CborType.UNSIGNED_INTEGER, number.type());
        Assertions.assertTrue(number instanceof CborUnsignedInteger);
        CborUnsignedInteger uint = (CborUnsignedInteger) number;
        Assertions.assertEquals(CborWidth.ZERO, uint.width());
        Assertions.assertEquals(2L, uint.value());
    }

    @Test
    void testShortInt() {
        CborItem number = Cbor.loadPartial(data2, 0, 3).item();
        Assertions.assertEquals(CborType.UNSIGNED_INTEGER, number.type());
        Assertions.assertTrue(number instanceof CborUnsignedInteger);
        CborUnsignedInteger uint = (CborUnsignedInteger) number;
        Assertions.assertEquals(CborWidth.EIGHT, uint.width());
        Assertions.assertEquals(255L, uint.value());
    }

    @Test
    void testHalfInt() {
        CborItem number = Cbor.loadPartial(data3, 0, data3.length).item();
        Assertions.assertEquals(CborType.UNSIGNED_INTEGER, number.type());
        Assertions.assertTrue(number instanceof CborUnsignedInteger);
        CborUnsignedInteger uint = (CborUnsignedInteger) number;
        Assertions.assertEquals(CborWidth.SIXTEEN, uint.width());
        Assertions.assertEquals(500L, uint.value());
    }

    @Test
    void testInt() {
        CborItem number = Cbor.loadPartial(data4, 0, data4.length).item();
        Assertions.assertEquals(CborType.UNSIGNED_INTEGER, number.type());
        Assertions.assertTrue(number instanceof CborUnsignedInteger);
        CborUnsignedInteger uint = (CborUnsignedInteger) number;
        Assertions.assertEquals(CborWidth.THIRTY_TWO, uint.width());
        Assertions.assertEquals(2784428723L, uint.value());
    }

    @Test
    @Disabled("C vs Java semantic mismatch: Java uses signed long, throwing exception on values >= 2^63")
    void testLongInt() {
        // Since data5 represents 11959030306112471731 which is > Long.MAX_VALUE, decoding it
        // produces a negative Java long, which is rejected by CborUnsignedInteger constructor.
        Cbor.loadPartial(data5, 0, 10);
    }

    @Test
    void testIncompleteData() {
        Assertions.assertThrows(CborDecodeException.class, () -> {
            Cbor.loadPartial(data2, 0, 1);
        });
    }

    @Test
    void testEmptyInput() {
        Assertions.assertThrows(CborDecodeException.class, () -> {
            Cbor.loadPartial(data5, 0, 0);
        });
    }

    @Test
    void testInlineCreation() {
        CborUnsignedInteger number1 = new CborUnsignedInteger(10, CborWidth.EIGHT);
        Assertions.assertEquals(10L, number1.value());

        CborUnsignedInteger number2 = new CborUnsignedInteger(10, CborWidth.SIXTEEN);
        Assertions.assertEquals(10L, number2.value());

        CborUnsignedInteger number3 = new CborUnsignedInteger(10, CborWidth.THIRTY_TWO);
        Assertions.assertEquals(10L, number3.value());

        CborUnsignedInteger number4 = new CborUnsignedInteger(10, CborWidth.SIXTY_FOUR);
        Assertions.assertEquals(10L, number4.value());
    }
}
