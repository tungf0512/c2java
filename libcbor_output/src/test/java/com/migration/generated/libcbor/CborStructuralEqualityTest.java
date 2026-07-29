package com.migration.generated.libcbor;

import com.migration.generated.libcbor.model.CborArray;
import com.migration.generated.libcbor.model.CborByteString;
import com.migration.generated.libcbor.model.CborMap;
import com.migration.generated.libcbor.model.CborNegativeInteger;
import com.migration.generated.libcbor.model.CborTag;
import com.migration.generated.libcbor.model.CborTextString;
import com.migration.generated.libcbor.model.CborUnsignedInteger;
import com.migration.generated.libcbor.model.CborWidth;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class CborStructuralEqualityTest {
    @Test
    void unsignedIntegersMatchWhenValueAndWidthMatch() {
        Assertions.assertTrue(Cbor.structurallyEqual(
            new CborUnsignedInteger(10, CborWidth.EIGHT),
            new CborUnsignedInteger(10, CborWidth.EIGHT)
        ));
    }

    @Test
    void unsignedIntegersDifferWhenWidthsDiffer() {
        Assertions.assertFalse(Cbor.structurallyEqual(
            new CborUnsignedInteger(1, CborWidth.EIGHT),
            new CborUnsignedInteger(1, CborWidth.SIXTEEN)
        ));
    }

    @Test
    void unsignedAndNegativeIntegersAreStructurallyDifferent() {
        Assertions.assertFalse(Cbor.structurallyEqual(
            new CborUnsignedInteger(0, CborWidth.ZERO),
            new CborNegativeInteger(0, CborWidth.ZERO)
        ));
    }

    @Test
    void definiteByteStringsMatchOnExactBytes() {
        Assertions.assertTrue(Cbor.structurallyEqual(
            new CborByteString("hello".getBytes()),
            new CborByteString("hello".getBytes())
        ));
    }

    @Test
    void definiteAndIndefiniteByteStringsAreDistinct() {
        CborByteString definite = new CborByteString("hello".getBytes());
        CborByteString indefinite = new CborByteString();
        indefinite.addChunk(new CborByteString("hello".getBytes()));

        Assertions.assertFalse(Cbor.structurallyEqual(definite, indefinite));
    }

    @Test
    void indefiniteByteStringsPreserveChunkStructureInEquality() {
        CborByteString left = new CborByteString();
        left.addChunk(new CborByteString("he".getBytes()));
        left.addChunk(new CborByteString("llo".getBytes()));

        CborByteString right = new CborByteString();
        right.addChunk(new CborByteString("hello".getBytes()));

        Assertions.assertFalse(Cbor.structurallyEqual(left, right));
    }

    @Test
    void textStringAndByteStringAreStructurallyDifferent() {
        Assertions.assertFalse(Cbor.structurallyEqual(
            new CborTextString("hi"),
            new CborByteString("hi".getBytes())
        ));
    }

    @Test
    void arraysRequireSameElementOrder() {
        CborArray left = new CborArray(2);
        left.add(new CborUnsignedInteger(1, CborWidth.ZERO));
        left.add(new CborUnsignedInteger(2, CborWidth.ZERO));

        CborArray right = new CborArray(2);
        right.add(new CborUnsignedInteger(2, CborWidth.ZERO));
        right.add(new CborUnsignedInteger(1, CborWidth.ZERO));

        Assertions.assertFalse(Cbor.structurallyEqual(left, right));
    }

    @Test
    void mapsRequireSamePairOrder() {
        CborMap left = new CborMap(2);
        left.add(new CborTextString("x"), new CborUnsignedInteger(1, CborWidth.ZERO));
        left.add(new CborTextString("y"), new CborUnsignedInteger(2, CborWidth.ZERO));

        CborMap right = new CborMap(2);
        right.add(new CborTextString("y"), new CborUnsignedInteger(2, CborWidth.ZERO));
        right.add(new CborTextString("x"), new CborUnsignedInteger(1, CborWidth.ZERO));

        Assertions.assertFalse(Cbor.structurallyEqual(left, right));
    }

    @Test
    void equalTagsRequireMatchingNestedItems() {
        CborTag left = new CborTag(100);
        left.setTaggedItem(new CborTextString("payload"));

        CborTag right = new CborTag(100);
        right.setTaggedItem(new CborTextString("payload"));

        Assertions.assertTrue(Cbor.structurallyEqual(left, right));
    }
}
