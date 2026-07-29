package com.migration.generated.libcbor.model;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public final class CborByteString extends CborItem {
    private final boolean indefinite;
    private final byte[] bytes;
    private final List<CborByteString> chunks;

    public CborByteString(byte[] bytes) {
        this.indefinite = false;
        this.bytes = bytes == null ? new byte[0] : Arrays.copyOf(bytes, bytes.length);
        this.chunks = List.of();
    }

    public CborByteString() {
        this.indefinite = true;
        this.bytes = null;
        this.chunks = new ArrayList<>();
    }

    public boolean isIndefinite() {
        return indefinite;
    }

    public int length() {
        return indefinite ? chunks.stream().mapToInt(CborByteString::length).sum() : bytes.length;
    }

    public byte[] bytes() {
        if (indefinite) {
            throw new IllegalStateException("Indefinite byte string has no direct byte payload");
        }
        return Arrays.copyOf(bytes, bytes.length);
    }

    public void addChunk(CborByteString chunk) {
        if (!indefinite) {
            throw new IllegalStateException("Cannot add chunks to a definite byte string");
        }
        if (chunk == null || chunk.isIndefinite()) {
            throw new IllegalArgumentException("Byte string chunks must be definite");
        }
        chunks.add(chunk);
    }

    public List<CborByteString> chunks() {
        return indefinite ? Collections.unmodifiableList(chunks) : List.of();
    }

    @Override
    public CborType type() {
        return CborType.BYTE_STRING;
    }

    @Override
    public CborItem deepCopy() {
        if (!indefinite) {
            return new CborByteString(bytes);
        }
        CborByteString copy = new CborByteString();
        for (CborByteString chunk : chunks) {
            copy.addChunk((CborByteString) chunk.deepCopy());
        }
        return copy;
    }

    @Override
    public CborItem deepCopyDefinite() {
        if (!indefinite) {
            return deepCopy();
        }
        byte[] merged = new byte[length()];
        int offset = 0;
        for (CborByteString chunk : chunks) {
            byte[] chunkBytes = chunk.bytes();
            System.arraycopy(chunkBytes, 0, merged, offset, chunkBytes.length);
            offset += chunkBytes.length;
        }
        return new CborByteString(merged);
    }

    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof CborByteString other) || indefinite != other.indefinite) {
            return false;
        }
        return indefinite ? chunks.equals(other.chunks) : Arrays.equals(bytes, other.bytes);
    }

    @Override
    public int hashCode() {
        return indefinite ? chunks.hashCode() : Arrays.hashCode(bytes);
    }
}
