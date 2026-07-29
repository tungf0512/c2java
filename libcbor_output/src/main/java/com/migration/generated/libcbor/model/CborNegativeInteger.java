package com.migration.generated.libcbor.model;

public final class CborNegativeInteger extends CborItem {
    private final long encodedMagnitude;
    private final CborWidth width;

    public CborNegativeInteger(long encodedMagnitude, CborWidth width) {
        if (encodedMagnitude < 0) {
            throw new IllegalArgumentException("Encoded magnitude must be non-negative");
        }
        this.encodedMagnitude = encodedMagnitude;
        this.width = requireWidth(width);
    }

    public long encodedMagnitude() {
        return encodedMagnitude;
    }

    public long value() {
        return -1L - encodedMagnitude;
    }

    public CborWidth width() {
        return width;
    }

    @Override
    public CborType type() {
        return CborType.NEGATIVE_INTEGER;
    }

    @Override
    public CborItem deepCopy() {
        return new CborNegativeInteger(encodedMagnitude, width);
    }

    @Override
    public boolean equals(Object obj) {
        return obj instanceof CborNegativeInteger other
            && encodedMagnitude == other.encodedMagnitude
            && width == other.width;
    }

    @Override
    public int hashCode() {
        return Long.hashCode(encodedMagnitude) * 31 + width.hashCode();
    }

    private static CborWidth requireWidth(CborWidth width) {
        if (width == null || width == CborWidth.INDEFINITE) {
            throw new IllegalArgumentException("Negative integers require a finite width");
        }
        return width;
    }
}
