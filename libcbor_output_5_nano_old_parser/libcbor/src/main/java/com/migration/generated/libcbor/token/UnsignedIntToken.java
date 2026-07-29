package com.migration.generated.libcbor.token;

public final class UnsignedIntToken implements Token {
    public final long value;
    public UnsignedIntToken(long value) {
        if (value < 0) throw new IllegalArgumentException("Unsigned value cannot be negative");
        this.value = value;
    }
}
