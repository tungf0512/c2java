package com.migration.generated.libcbor.model;

import com.migration.generated.libcbor.serialization.CborSerializer;

public abstract class CborItem {
    public abstract CborType type();

    public abstract CborItem deepCopy();

    public CborItem deepCopyDefinite() {
        return deepCopy();
    }

    public final int encodedSize() {
        return CborSerializer.serializedSize(this);
    }

    public final byte[] serialize() {
        return CborSerializer.serialize(this);
    }

    public final boolean structurallyEqual(CborItem other) {
        return equals(other);
    }
}
