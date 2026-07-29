package com.migration.generated.libcbor;

import com.migration.generated.libcbor.model.CborArray;
import com.migration.generated.libcbor.model.CborByteString;
import com.migration.generated.libcbor.model.CborItem;
import com.migration.generated.libcbor.model.CborTag;
import com.migration.generated.libcbor.model.CborTextString;
import com.migration.generated.libcbor.model.CborUnsignedInteger;
import com.migration.generated.libcbor.model.CborWidth;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class CborRoundTripTest {
    @Test
    void roundTripsUnsignedIntegerThroughFacade() {
        CborUnsignedInteger source = new CborUnsignedInteger(42, CborWidth.EIGHT);

        CborItem decoded = Cbor.load(Cbor.serialize(source));

        Assertions.assertTrue(Cbor.structurallyEqual(source, decoded));
    }

    @Test
    void roundTripsNestedArrayAndTagThroughFacade() {
        CborArray array = new CborArray(2);
        array.add(new CborTextString("libcbor"));
        array.add(new CborByteString(new byte[] {0x01, 0x02, 0x03}));

        CborTag tag = new CborTag(24);
        tag.setTaggedItem(array);

        CborItem decoded = Cbor.load(Cbor.serialize(tag));

        Assertions.assertTrue(Cbor.structurallyEqual(tag, decoded));
    }

    @Test
    void loadRejectsTrailingBytes() {
        CborDecodeException exception = Assertions.assertThrows(
            CborDecodeException.class,
            () -> Cbor.load(new byte[] {0x18, 0x2A, 0x00})
        );

        Assertions.assertTrue(exception.getMessage().contains("Trailing bytes"));
    }

    @Test
    void loadPartialReportsConsumedBytes() {
        LoadResult result = Cbor.loadPartial(new byte[] {0x18, 0x2A, 0x00}, 0, 2);

        Assertions.assertEquals(2, result.bytesConsumed());
        Assertions.assertTrue(result.item() instanceof CborUnsignedInteger);
        Assertions.assertTrue(Cbor.structurallyEqual(
            new CborUnsignedInteger(42, CborWidth.EIGHT),
            result.item()
        ));
    }
}
