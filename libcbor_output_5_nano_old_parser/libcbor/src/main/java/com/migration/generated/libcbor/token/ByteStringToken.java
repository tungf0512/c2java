package com.migration.generated.libcbor.token;

public final class ByteStringToken implements Token {
    public final byte[] data;
    public final int length;
    public ByteStringToken(byte[] data, int length) {
        this.data = data;
        this.length = length;
    }
}
