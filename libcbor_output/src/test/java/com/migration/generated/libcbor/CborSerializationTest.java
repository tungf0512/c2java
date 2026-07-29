package com.migration.generated.libcbor;

import com.migration.generated.libcbor.model.CborArray;
import com.migration.generated.libcbor.model.CborByteString;
import com.migration.generated.libcbor.model.CborNegativeInteger;
import com.migration.generated.libcbor.model.CborTag;
import com.migration.generated.libcbor.model.CborTextString;
import com.migration.generated.libcbor.model.CborUnsignedInteger;
import com.migration.generated.libcbor.model.CborWidth;
import java.util.HexFormat;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class CborSerializationTest {
    @Test
    void serializesEmbeddedUnsignedInteger() {
        CborUnsignedInteger item = new CborUnsignedInteger(0, CborWidth.ZERO);

        Assertions.assertArrayEquals(new byte[] {0x00}, Cbor.serialize(item));
        Assertions.assertEquals(1, Cbor.serializedSize(item));
    }

    @Test
    void serializesEightBitUnsignedInteger() {
        CborUnsignedInteger item = new CborUnsignedInteger(42, CborWidth.EIGHT);

        Assertions.assertArrayEquals(new byte[] {0x18, 0x2A}, Cbor.serialize(item));
        Assertions.assertEquals(2, Cbor.serializedSize(item));
    }

    @Test
    void serializesSixteenBitUnsignedInteger() {
        CborUnsignedInteger item = new CborUnsignedInteger(1000, CborWidth.SIXTEEN);

        Assertions.assertArrayEquals(new byte[] {0x19, 0x03, (byte) 0xE8}, Cbor.serialize(item));
        Assertions.assertEquals(3, Cbor.serializedSize(item));
    }

    @Test
    void serializesEightBitNegativeInteger() {
        CborNegativeInteger item = new CborNegativeInteger(42, CborWidth.EIGHT);

        Assertions.assertArrayEquals(new byte[] {0x38, 0x2A}, Cbor.serialize(item));
        Assertions.assertEquals(2, Cbor.serializedSize(item));
    }

    @Test
    void serializesDefiniteByteString() {
        byte[] payload = new byte[256];
        CborByteString item = new CborByteString(payload);

        byte[] serialized = Cbor.serialize(item);

        Assertions.assertEquals(259, serialized.length);
        Assertions.assertArrayEquals(new byte[] {0x59, 0x01, 0x00}, slice(serialized, 0, 3));
        Assertions.assertArrayEquals(payload, slice(serialized, 3, 256));
    }

    @Test
    void serializesIndefiniteByteString() {
        byte[] payload = new byte[256];
        CborByteString item = new CborByteString();
        item.addChunk(new CborByteString(payload));

        byte[] serialized = Cbor.serialize(item);

        Assertions.assertEquals(261, serialized.length);
        Assertions.assertArrayEquals(new byte[] {0x5F, 0x59, 0x01, 0x00}, slice(serialized, 0, 4));
        Assertions.assertArrayEquals(payload, slice(serialized, 4, 256));
        Assertions.assertEquals((byte) 0xFF, serialized[260]);
    }

    @Test
    void serializesDefiniteTextString() {
        CborTextString item = new CborTextString("Hello world!");

        Assertions.assertEquals(
            "6c48656c6c6f20776f726c6421",
            HexFormat.of().formatHex(Cbor.serialize(item))
        );
    }

    @Test
    void serializesArrayUsingEncodedArity() {
        CborArray array = new CborArray(2);
        array.add(new CborUnsignedInteger(1, CborWidth.ZERO));
        array.add(new CborUnsignedInteger(2, CborWidth.ZERO));

        Assertions.assertArrayEquals(new byte[] {(byte) 0x82, 0x01, 0x02}, Cbor.serialize(array));
    }

    @Test
    void rejectsTagWithoutNestedItem() {
        CborTag tag = new CborTag(42);

        CborSerializationException exception = Assertions.assertThrows(
            CborSerializationException.class,
            () -> Cbor.serialize(tag)
        );

        Assertions.assertTrue(exception.getMessage().contains("Tag without nested item"));
    }

    private static byte[] slice(byte[] source, int offset, int length) {
        byte[] result = new byte[length];
        System.arraycopy(source, offset, result, 0, length);
        return result;
    }
}
