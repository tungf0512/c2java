package com.migration.generated.libcbor.model;

public enum CborWidth {
    ZERO(0),
    EIGHT(1),
    SIXTEEN(2),
    THIRTY_TWO(4),
    SIXTY_FOUR(8),
    INDEFINITE(-1);

    private final int bytes;

    CborWidth(int bytes) {
        this.bytes = bytes;
    }

    public int bytes() {
        return bytes;
    }
}
