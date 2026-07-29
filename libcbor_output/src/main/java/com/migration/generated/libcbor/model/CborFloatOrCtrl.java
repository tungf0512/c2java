package com.migration.generated.libcbor.model;

public final class CborFloatOrCtrl extends CborItem {
    public enum Kind {
        SIMPLE,
        HALF_FLOAT,
        SINGLE_FLOAT,
        DOUBLE_FLOAT,
        BOOLEAN,
        NULL,
        UNDEFINED,
        BREAK
    }

    private final Kind kind;
    private final CborWidth width;
    private final long payloadBits;

    private CborFloatOrCtrl(Kind kind, CborWidth width, long payloadBits) {
        this.kind = kind;
        this.width = width;
        this.payloadBits = payloadBits;
    }

    public static CborFloatOrCtrl simple(int value) {
        return new CborFloatOrCtrl(Kind.SIMPLE, CborWidth.EIGHT, value & 0xFFL);
    }

    public static CborFloatOrCtrl halfFloat(int bits) {
        return new CborFloatOrCtrl(Kind.HALF_FLOAT, CborWidth.SIXTEEN, bits & 0xFFFFL);
    }

    public static CborFloatOrCtrl singleFloat(int bits) {
        return new CborFloatOrCtrl(Kind.SINGLE_FLOAT, CborWidth.THIRTY_TWO, bits & 0xFFFFFFFFL);
    }

    public static CborFloatOrCtrl doubleFloat(long bits) {
        return new CborFloatOrCtrl(Kind.DOUBLE_FLOAT, CborWidth.SIXTY_FOUR, bits);
    }

    public static CborFloatOrCtrl bool(boolean value) {
        return new CborFloatOrCtrl(Kind.BOOLEAN, CborWidth.ZERO, value ? 21 : 20);
    }

    public static CborFloatOrCtrl nullValue() {
        return new CborFloatOrCtrl(Kind.NULL, CborWidth.ZERO, 22);
    }

    public static CborFloatOrCtrl undefined() {
        return new CborFloatOrCtrl(Kind.UNDEFINED, CborWidth.ZERO, 23);
    }

    public static CborFloatOrCtrl breakStop() {
        return new CborFloatOrCtrl(Kind.BREAK, CborWidth.ZERO, 31);
    }

    public Kind kind() {
        return kind;
    }

    public CborWidth width() {
        return width;
    }

    public long payloadBits() {
        return payloadBits;
    }

    public boolean booleanValue() {
        if (kind != Kind.BOOLEAN) {
            throw new IllegalStateException("Not a boolean control item");
        }
        return payloadBits == 21;
    }

    @Override
    public CborType type() {
        return CborType.FLOAT_OR_CTRL;
    }

    @Override
    public CborItem deepCopy() {
        return new CborFloatOrCtrl(kind, width, payloadBits);
    }

    @Override
    public boolean equals(Object obj) {
        return obj instanceof CborFloatOrCtrl other
            && kind == other.kind
            && width == other.width
            && payloadBits == other.payloadBits;
    }

    @Override
    public int hashCode() {
        return ((kind.hashCode() * 31) + width.hashCode()) * 31 + Long.hashCode(payloadBits);
    }
}
