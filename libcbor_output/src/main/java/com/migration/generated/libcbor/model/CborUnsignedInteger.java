package com.migration.generated.libcbor.model;

public final class CborUnsignedInteger extends CborItem {
    private final long value;
    private final CborWidth width;

    public CborUnsignedInteger(long value, CborWidth width) {
        if (value < 0) {
            throw new IllegalArgumentException("Unsigned value must be non-negative");
        }
        this.value = value;
        this.width = requireWidth(width);
    }

    public long value() {
        return value;
    }

    public CborWidth width() {
        return width;
    }

    @Override
    public CborType type() {
        return CborType.UNSIGNED_INTEGER;
    }

    @Override
    public CborItem deepCopy() {
        return new CborUnsignedInteger(value, width);
    }

    @Override
    public boolean equals(Object obj) {
        return obj instanceof CborUnsignedInteger other && value == other.value && width == other.width;
    }

    @Override
    public int hashCode() {
        return Long.hashCode(value) * 31 + width.hashCode();
    }

    private static CborWidth requireWidth(CborWidth width) {
        if (width == null || width == CborWidth.INDEFINITE) {
            throw new IllegalArgumentException("Unsigned integers require a finite width");
        }
        return width;
    }
}
