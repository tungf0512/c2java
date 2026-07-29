package com.migration.generated.libcbor;

import com.migration.generated.libcbor.model.CborItem;
import com.migration.generated.libcbor.model.CborType;
import com.migration.generated.libcbor.model.CborNegativeInteger;
import com.migration.generated.libcbor.model.CborWidth;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Disabled;

class CborNegintTest {
    private static final byte[] data1 = {0x22, (byte) 0xFF};
    private static final byte[] data2 = {0x38, (byte) 0xFF, (byte) 0xFF};
    private static final byte[] data3 = {0x39, 0x01, (byte) 0xf4, (byte) 0xFF};
    private static final byte[] data4 = {0x3a, (byte) 0xa5, (byte) 0xf7, 0x02, (byte) 0xb3, (byte) 0xFF};
    private static final byte[] data5 = {0x3b, (byte) 0xa5, (byte) 0xf7, 0x02, (byte) 0xb3,
                                         (byte) 0xa5, (byte) 0xf7, 0x02, (byte) 0xb3, (byte) 0xFF};

    @Test
    void testVeryShortInt() {
        CborItem number = Cbor.loadPartial(data1, 0, 2).item();
        Assertions.assertEquals(CborType.NEGATIVE_INTEGER, number.type());
        Assertions.assertTrue(number instanceof CborNegativeInteger);
        CborNegativeInteger negint = (CborNegativeInteger) number;
        Assertions.assertEquals(CborWidth.ZERO, negint.width());
        Assertions.assertEquals(2L, negint.encodedMagnitude());
        Assertions.assertEquals(-3L, negint.value());
    }

    @Test
    void testShortInt() {
        CborItem number = Cbor.loadPartial(data2, 0, 3).item();
        Assertions.assertEquals(CborType.NEGATIVE_INTEGER, number.type());
        Assertions.assertTrue(number instanceof CborNegativeInteger);
        CborNegativeInteger negint = (CborNegativeInteger) number;
        Assertions.assertEquals(CborWidth.EIGHT, negint.width());
        Assertions.assertEquals(255L, negint.encodedMagnitude());
        Assertions.assertEquals(-256L, negint.value());
    }

    @Test
    void testHalfInt() {
        CborItem number = Cbor.loadPartial(data3, 0, data3.length).item();
        Assertions.assertEquals(CborType.NEGATIVE_INTEGER, number.type());
        Assertions.assertTrue(number instanceof CborNegativeInteger);
        CborNegativeInteger negint = (CborNegativeInteger) number;
        Assertions.assertEquals(CborWidth.SIXTEEN, negint.width());
        Assertions.assertEquals(500L, negint.encodedMagnitude());
        Assertions.assertEquals(-501L, negint.value());
    }

    @Test
    void testInt() {
        CborItem number = Cbor.loadPartial(data4, 0, data4.length).item();
        Assertions.assertEquals(CborType.NEGATIVE_INTEGER, number.type());
        Assertions.assertTrue(number instanceof CborNegativeInteger);
        CborNegativeInteger negint = (CborNegativeInteger) number;
        Assertions.assertEquals(CborWidth.THIRTY_TWO, negint.width());
        Assertions.assertEquals(2784428723L, negint.encodedMagnitude());
        Assertions.assertEquals(-2784428724L, negint.value());
    }

    @Test
    @Disabled("C vs Java semantic mismatch: Java uses signed long, throwing exception on values >= 2^63")
    void testLongInt() {
        Cbor.loadPartial(data5, 0, 10);
    }
}
