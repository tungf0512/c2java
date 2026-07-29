package com.migration.generated.libcbor.token;

public final class NegativeIntToken implements Token {
    public final long value; // negative CBOR integer value actual value is -1 - value
    public NegativeIntToken(long value) {
        if (value > -1) throw new IllegalArgumentException("Negative int token requires negative value");
        this.value = value;
    }
}
