package com.migration.generated.libcbor.model;

import com.migration.generated.libcbor.util.CborUnicode;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public final class CborTextString extends CborItem {
    private final boolean indefinite;
    private final byte[] utf8;
    private final int codePointCount;
    private final List<CborTextString> chunks;
    private String cachedText;

    public CborTextString(byte[] utf8) {
        byte[] source = utf8 == null ? new byte[0] : Arrays.copyOf(utf8, utf8.length);
        this.indefinite = false;
        this.utf8 = source;
        this.codePointCount = CborUnicode.validateAndCountCodePoints(source);
        this.chunks = List.of();
    }

    public CborTextString(String text) {
        this(text == null ? new byte[0] : text.getBytes(StandardCharsets.UTF_8));
        this.cachedText = text == null ? "" : text;
    }

    public CborTextString() {
        this.indefinite = true;
        this.utf8 = null;
        this.codePointCount = -1;
        this.chunks = new ArrayList<>();
    }

    public boolean isIndefinite() {
        return indefinite;
    }

    public byte[] utf8() {
        if (indefinite) {
            throw new IllegalStateException("Indefinite text string has no direct byte payload");
        }
        return Arrays.copyOf(utf8, utf8.length);
    }

    public int length() {
        return indefinite ? chunks.stream().mapToInt(CborTextString::length).sum() : utf8.length;
    }

    public int codePointCount() {
        if (indefinite) {
            return chunks.stream().mapToInt(CborTextString::codePointCount).sum();
        }
        return codePointCount;
    }

    public String text() {
        if (indefinite) {
            StringBuilder builder = new StringBuilder();
            for (CborTextString chunk : chunks) {
                builder.append(chunk.text());
            }
            return builder.toString();
        }
        if (cachedText == null) {
            cachedText = new String(utf8, StandardCharsets.UTF_8);
        }
        return cachedText;
    }

    public void addChunk(CborTextString chunk) {
        if (!indefinite) {
            throw new IllegalStateException("Cannot add chunks to a definite text string");
        }
        if (chunk == null || chunk.isIndefinite()) {
            throw new IllegalArgumentException("Text string chunks must be definite");
        }
        chunks.add(chunk);
    }

    public List<CborTextString> chunks() {
        return indefinite ? Collections.unmodifiableList(chunks) : List.of();
    }

    @Override
    public CborType type() {
        return CborType.TEXT_STRING;
    }

    @Override
    public CborItem deepCopy() {
        if (!indefinite) {
            return new CborTextString(utf8);
        }
        CborTextString copy = new CborTextString();
        for (CborTextString chunk : chunks) {
            copy.addChunk((CborTextString) chunk.deepCopy());
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
        for (CborTextString chunk : chunks) {
            byte[] chunkBytes = chunk.utf8();
            System.arraycopy(chunkBytes, 0, merged, offset, chunkBytes.length);
            offset += chunkBytes.length;
        }
        return new CborTextString(merged);
    }

    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof CborTextString other) || indefinite != other.indefinite) {
            return false;
        }
        return indefinite ? chunks.equals(other.chunks) : Arrays.equals(utf8, other.utf8);
    }

    @Override
    public int hashCode() {
        return indefinite ? chunks.hashCode() : Arrays.hashCode(utf8);
    }
}
